import logging
import os
from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional

import attrs
import boto3
import requests  # type: ignore
from botocore.exceptions import ClientError
from google.protobuf.timestamp_pb2 import Timestamp
from readerwriterlock import rwlock

from tecton_proto.common.secret__client_pb2 import SecretReference
from tecton_proto.server_groups.transform_server_group_config__client_pb2 import SecretMetadata
from tecton_proto.server_groups.transform_server_group_config__client_pb2 import TransformServerGroupSecretsConfig


logger = logging.getLogger(__name__)


class CloudSecretsClientInterface:
    """
    CloudSecretsClientInterface provides an interface for reading secrets
    from a cloud secrets manager.
    """

    def get_secret_value(self, secret_id: str) -> Optional[str]:
        pass


class AWSSecretsClient(CloudSecretsClientInterface):
    """
    AWSSecretsManagerClient is a client to retrieve secrets from AWS Secrets Manager.
    """

    def __init__(self, region: str):
        self.session = boto3.session.Session()
        self.secrets_manager_client = self.session.client("secretsmanager", region_name=region)

    def get_secret_value(self, secret_id: str) -> Optional[str]:
        """
        Retrieves the secret value associated with the given secret_id.
        """
        try:
            response = self.secrets_manager_client.get_secret_value(SecretId=secret_id)
            if "SecretString" in response:
                return response["SecretString"]
            else:
                logger.warning(f"Binary secrets not supported: {secret_id}")
                return None
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                logger.warning(f"Secret {secret_id} not found in Secrets Manager")
                return None
            else:
                logger.error(f"Failed to retrieve secret {secret_id}: {str(e)}")
                return None


@dataclass(frozen=True)
class SecretCacheKey:
    """
    A class to store the secret cache key
    """

    scope: str
    key: str


class SecretWithTimestamp:
    """
    A class to store secret information, including value and last updated time.
    """

    def __init__(self, value: str, last_updated_time: Optional[datetime] = None):
        self.value = value
        self.last_updated_time = last_updated_time or datetime.utcnow()


@attrs.define
class TransformServerSecretsResolver:
    """
    A class to fetch secrets from the Secrets Service in MDS
    """

    auth_token_secret_client: CloudSecretsClientInterface = attrs.field(default=None, init=False)
    secrets_service_base_url: Optional[str] = None
    secrets_service_auth_token: Optional[str] = None
    service_account_secret_name: Optional[str] = None
    token_last_refreshed_time: Optional[datetime] = None
    session: requests.Session = attrs.field(init=False)

    def __attrs_post_init__(self):
        self.secrets_service_base_url = os.getenv("METADATA_SERVICE_BASE_URL", None)
        self.session = requests.Session()
        cloud_provider = os.getenv("CLOUD_PROVIDER", "aws")
        if cloud_provider == "aws":
            region = os.getenv("AWS_REGION", None)
            if not region:
                error_message = "AWS_REGION must be set for Secrets Manager"
                raise ValueError(error_message)
            self.auth_token_secret_client = AWSSecretsClient(region)

    def fetch_secret(self, secret_reference: SecretReference) -> Optional[str]:
        api_url = f"{self.secrets_service_base_url}/api/v1/secrets-service/scopes/{secret_reference.scope}/keys/{secret_reference.key}"
        headers = {"Authorization": f"Tecton-key {self.secrets_service_auth_token}", "Content-Type": "application/json"}
        response = self.session.get(api_url, headers=headers)
        response_json = response.json()
        if "value" in response_json:
            return response_json["value"]
        else:
            logger.warning(
                f"Failed to fetch secret {secret_reference.key} from scope {secret_reference.scope}. "
                f"Status Code: {response.status_code}. Error: {response.text}"
            )
            return None

    def refresh_auth_token(self, secrets_config: TransformServerGroupSecretsConfig):
        """
        Refreshes the auth token if the service account key or the last updated time has changed
        """
        if not secrets_config.service_account_secret_name:
            logger.warning("Service Account Secret Name not set in Secrets Config. Skipping refresh of auth token")
            return
        self.service_account_secret_name = secrets_config.service_account_secret_name
        assert self.service_account_secret_name is not None

        if self._should_refresh_auth_token(secrets_config.service_account_key_last_updated.ToDatetime()):
            auth_token = self.auth_token_secret_client.get_secret_value(self.service_account_secret_name)
            if auth_token:
                self.secrets_service_auth_token = auth_token
                self.token_last_refreshed_time = datetime.utcnow()
                logger.info("Successfully refreshed Service Account Auth Token for Secrets Manager")

    def _should_refresh_auth_token(self, last_updated_time: datetime) -> bool:
        """
        Checks if the service account auth token should be refreshed.
        """
        if (
            not self.secrets_service_auth_token
            or not self.service_account_secret_name
            or not self.token_last_refreshed_time
        ):
            return True
        return last_updated_time > self.token_last_refreshed_time


class CustomSecretsDict(dict):
    def __init__(self, last_refresh_time=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_refresh_time = last_refresh_time

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            msg = f"Unable to find Secret '{key}'. Newly updated Secrets may take upto 120 seconds to be propagated. Last refresh time is {self.last_refresh_time}"
            raise KeyError(msg)


@attrs.define
class SecretsManager:
    secrets_cache: Dict["SecretCacheKey", "SecretWithTimestamp"] = attrs.field(factory=dict)
    fco_secrets_map: Dict[str, Dict[str, SecretReference]] = attrs.field(factory=dict)
    secrets_cache_lock: rwlock.RWLockRead = attrs.field(factory=rwlock.RWLockRead, init=False)
    fco_secrets_map_lock: Lock = attrs.field(factory=Lock, init=False)
    secrets_resolver: TransformServerSecretsResolver = attrs.field(factory=TransformServerSecretsResolver)
    last_refresh_time: Optional[datetime] = None

    def get_secrets_for_fco(self, fco_id: str) -> Mapping[str, str]:
        """
        Fetches the secrets for the FCO (Feature View / Resource Provider) from the cache
        :return: The map of secret key to secret value for an FCO
        """
        with self.fco_secrets_map_lock:
            secrets_map = dict(self.fco_secrets_map.get(fco_id, {}))

        secrets_for_fco = CustomSecretsDict(self.last_refresh_time)
        for key, reference in secrets_map.items():
            secret_value = self.get_secret(reference)
            if secret_value:
                secrets_for_fco[key] = secret_value
        return secrets_for_fco

    def get_secret(self, secret_reference: SecretReference) -> Optional[str]:
        """
        Fetches the secret value from the cache or the Secrets Service
        :param secret_reference: The secret reference
        :return: The secret value
        """
        key = SecretCacheKey(secret_reference.scope, secret_reference.key)
        with self.secrets_cache_lock.gen_rlock():
            cached_secret = self.secrets_cache.get(key)
        if cached_secret:
            return cached_secret.value
        secret_value = self.secrets_resolver.fetch_secret(secret_reference)

        if secret_value:
            with self.secrets_cache_lock.gen_wlock():
                self.secrets_cache[key] = SecretWithTimestamp(secret_value)
        return secret_value

    def refresh_secrets_cache(
        self, secrets_config: TransformServerGroupSecretsConfig, config_last_updated_time: Timestamp
    ) -> None:
        """
        Refreshes the secrets cache if the secret have been updated since the last fetch
        Also refreshes the feature view secrets map and the Service Account
        :param secrets_config: The Transform Server Secrets Configuration
        """
        should_refresh = self.last_refresh_time is None or (
            config_last_updated_time.ToDatetime() > self.last_refresh_time
        )
        if should_refresh:
            self.secrets_resolver.refresh_auth_token(secrets_config)
            self._refresh_fco_secrets_map(secrets_config)
            self._refresh_secrets_cache(secrets_config.all_secrets_metadata)
            self.last_refresh_time = config_last_updated_time.ToDatetime()
            logger.info("Successfully refreshed Secrets Cache. Last Updated Time: %s", {str(self.last_refresh_time)})

    def _refresh_fco_secrets_map(self, config: TransformServerGroupSecretsConfig):
        """
        Refreshes the feature view secret map from the Transform Server Secrets Configuration
        :param config: The Transform Server Secrets Configuration
        """
        if config.feature_view_secret_references:
            updated_map = {
                fco_id: dict(feature_view_config.secrets_map)
                for fco_id, feature_view_config in config.feature_view_secret_references.items()
            }
            with self.fco_secrets_map_lock:
                self.fco_secrets_map = updated_map

    def _refresh_secrets_cache(self, all_secrets_metadata: List[SecretMetadata]):
        """
        Refreshes the secrets cache from the list of secret metadata
        :param all_secrets_metadata: The list of secret metadata
        """
        if not self.secrets_resolver.service_account_secret_name:
            logger.warning("Service Account Secret Name not set in Secrets Config. Skipping refresh of secrets cache")
            return
        updated_secrets_cache = {}
        updated_count = 0
        for secret_metadata in all_secrets_metadata:
            secret_reference = secret_metadata.secret_reference
            if not secret_reference:
                continue

            last_updated = secret_metadata.last_updated.ToDatetime()
            key = SecretCacheKey(secret_reference.scope, secret_reference.key)

            # If the secret exists in the cache and the last updated time in the metadata is not greater, skip fetching.
            if key in self.secrets_cache:
                cached_entry = self.secrets_cache[key]
                updated_secrets_cache[key] = cached_entry
                if last_updated <= cached_entry.last_updated_time:
                    continue

            secret_value = self.secrets_resolver.fetch_secret(secret_reference)
            if secret_value:
                updated_secrets_cache[key] = SecretWithTimestamp(secret_value)
                updated_count += 1

        if updated_count:
            logger.info(f"Successfully updated {updated_count} secrets")
        with self.secrets_cache_lock.gen_wlock():
            self.secrets_cache = updated_secrets_cache
