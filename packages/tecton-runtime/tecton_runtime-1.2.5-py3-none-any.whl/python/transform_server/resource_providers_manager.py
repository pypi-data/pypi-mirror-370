import hashlib
import logging
import os
from datetime import datetime
from enum import Enum
from types import FunctionType
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import attrs
import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from prometheus_client import Gauge
from readerwriterlock import rwlock

from python.transform_server.secrets_manager import SecretsManager
from tecton_core.id_helper import IdHelper
from tecton_core.resource_provider_context import ResourceProviderContext
from tecton_proto.common.secret__client_pb2 import SecretReference
from tecton_proto.server_groups.transform_server_group_config__client_pb2 import ResourceProviderMetadata
from tecton_proto.server_groups.transform_server_group_config__client_pb2 import TransformServerResourceProviderConfig


logger = logging.getLogger(__name__)

resource_provider_last_refresh_time_gauge = Gauge(
    "transform_server_resource_provider_last_refresh_time",
    "Last Refresh Time of the Resource Providers in the Transform Server",
    ["group_name"],
)

resource_provider_refresh_latency_gauge = Gauge(
    "transform_server_resource_provider_refresh_latency",
    "Latency of the Resource Provider Refresh in the Transform Server",
    ["group_name"],
)


class ResourceProviderException(Exception):
    def __init__(self, code: grpc.StatusCode, details: str):
        self.code = code
        self.details = details


class ResourceProviderErrorType(Enum):
    """
    An enum to represent the type of error that occurred with the resource provider.
    """

    EXECUTION_ERROR = 0
    INVOCATION_ERROR = 1
    MISSING_SECRETS_ERROR = 2


@attrs.define(frozen=True)
class ResourceProviderError:
    error_type: ResourceProviderErrorType
    error_message: str


@attrs.define(frozen=True)
class FeatureViewResourceProviderIdentifier:  # type: ignore
    """
    A class to store the feature view id and unique resource name for a feature view.
    """

    feature_view_id: str
    resource_name: str


@attrs.define
class ResourceProviderInstance:
    """
    A class to store the resource provider, secrets, last updated time, and last invoked time.
    """

    id: str
    name: str
    secrets_last_updated_time: Optional[datetime] = None
    fn_hash: Optional[str] = None
    last_invoked_time: Optional[datetime] = None
    secrets: Optional[Dict[str, SecretReference]] = None


class CustomResourcesDict(dict):
    def __init__(self, last_refresh_time=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_refresh_time = last_refresh_time

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            msg = f"Unable to find Resource for Resource Provider '{key}'. Newly updated Resource Providers may take upto 120 seconds to be propagated. Last refresh time is {self.last_refresh_time}"
            raise KeyError(msg)


@attrs.define
class ResourceProvidersManager:
    resource_store_lock: rwlock.RWLockRead = attrs.field(factory=rwlock.RWLockRead, init=False)
    feature_view_resource_provider_map_lock: rwlock.RWLockRead = attrs.field(factory=rwlock.RWLockRead, init=False)
    # Map of feature view resource provider identifier to resource provider id
    feature_view_resource_provider_map: Dict[str, Dict[str, str]] = attrs.field(factory=dict)
    # Map of resource provider id to resource provider instance
    resource_provider_map: Dict[str, ResourceProviderInstance] = attrs.field(factory=dict)
    # Map of resource provider id to resource
    resource_store: Dict[str, Any] = attrs.field(factory=dict)
    # Map of resource provider id to resource provider error
    resource_error_table: Dict[str, ResourceProviderError] = attrs.field(factory=dict)
    secrets_manager: Optional[SecretsManager] = None
    # Last updated time of the resource store
    last_refresh_time: Optional[datetime] = None

    def get_resources(self, feature_view_id) -> Dict[str, Any]:
        """
        Get the resources for the feature view.
        :param feature_view_id:
        :return: Dictionary of resources
        """
        resources = CustomResourcesDict(last_refresh_time=self.last_refresh_time)
        with self.feature_view_resource_provider_map_lock.gen_rlock():
            feature_view_resource_providers = self.feature_view_resource_provider_map.get(feature_view_id, {})
        for resource_provider_name, resource_provider_id in feature_view_resource_providers.items():
            resource = self._get_resource(resource_provider_id, resource_provider_name)
            resources[resource_provider_name] = resource
        return resources

    def _get_resource(self, resource_provider_id: str, resource_provider_name) -> Any:
        """
        Get the resource from the resource store.
        :param resource_provider_id: Resource Provider ID
        :param resource_provider_name: Resource Provider Name Override for the Feature View
        :return: The stored resource
        """
        with self.resource_store_lock.gen_rlock():
            resource = self.resource_store.get(resource_provider_id)
        if not resource:
            if resource_provider_id in self.resource_error_table:
                e = self.resource_error_table[resource_provider_id]
                message = f'Error with resource provider "{resource_provider_name}": [{e.error_type}] {e.error_message}'
                raise ResourceProviderException(grpc.StatusCode.FAILED_PRECONDITION, message)
            else:
                message = f"Resource for Resource Provider {resource_provider_name} has not been initialized. Please note that newly updated Feature Services may take upto 120s to reflect changes. Using configuration generated at {self.last_refresh_time}."
                raise ResourceProviderException(grpc.StatusCode.NOT_FOUND, str(message))
        return resource

    def refresh_resource_store(
        self, resource_provider_config: TransformServerResourceProviderConfig, config_last_updated_time: Timestamp
    ):
        # TODO(RC-436): We will check the TTL of all resources and refresh the resource store if any resource has expired
        """
        Refreshes the resource store and the feature view resource provider map
        :param resource_provider_config: The Transform Server Resource Provider Configuration
        """
        should_refresh = self.last_refresh_time is None or (
            config_last_updated_time.ToDatetime() > self.last_refresh_time
        )
        if should_refresh:
            start_time = datetime.utcnow()
            self._refresh_feature_view_resource_provider_map(resource_provider_config)
            self._refresh_resource_store(resource_provider_config.all_resource_providers_metadata)
            self.last_refresh_time = config_last_updated_time.ToDatetime()
            elapsed_refresh_time = (datetime.utcnow() - start_time).total_seconds()
            # Reporting Resource Provider Metrics
            tsg_name = os.environ.get("TRANSFORM_SERVER_GROUP_NAME", "default")
            resource_provider_last_refresh_time_timestamp = (
                self.last_refresh_time.timestamp() if self.last_refresh_time else 0
            )
            resource_provider_last_refresh_time_gauge.labels(group_name=tsg_name).set(
                resource_provider_last_refresh_time_timestamp
            )
            resource_provider_refresh_latency_gauge.labels(group_name=tsg_name).set(elapsed_refresh_time)
            logger.info("Successfully refreshed Resource Store. Last Updated Time: %s", {str(self.last_refresh_time)})

    def _refresh_feature_view_resource_provider_map(self, config: TransformServerResourceProviderConfig):
        """
        Refresh the feature view resource provider map.
        :param: config: The Transform Server Group Resource Provider Configuration
        """
        updated_feature_view_resource_provider_map = {
            feature_view_id: dict(feature_view_resource_provider_config.resource_providers_map)
            for feature_view_id, feature_view_resource_provider_config in config.feature_view_resource_providers.items()
        }

        with self.feature_view_resource_provider_map_lock.gen_wlock():
            self.feature_view_resource_provider_map = updated_feature_view_resource_provider_map

    def _refresh_resource_store(self, all_resource_providers_metadata: List[ResourceProviderMetadata]):
        """
        If a resource provider is updated, we will refresh the resource providers map, invoke the resource provider, and store the resource
        :param all_resource_providers_metadata: The list of all resource providers metadata
        """
        updated_resource_provider_map = {}
        updated_resource_store = {}
        for resource_provider_metadata in all_resource_providers_metadata:
            resource_provider = resource_provider_metadata.resource_provider
            resource_provider_id = IdHelper.to_string(resource_provider.resource_provider_id)
            resource_provider_fn_hash = hashlib.sha256(resource_provider.function.body.encode()).hexdigest()
            if self._should_refresh_resource_provider(resource_provider_metadata, resource_provider_fn_hash):
                resource_provider = resource_provider_metadata.resource_provider

                resource_provider_instance = ResourceProviderInstance(  # type: ignore
                    id=resource_provider_id,
                    name=resource_provider.fco_metadata.name,
                    fn_hash=resource_provider_fn_hash,
                    secrets_last_updated_time=resource_provider_metadata.secrets_last_updated.ToDatetime()
                    if resource_provider_metadata.HasField("secrets_last_updated")
                    else None,
                    secrets=resource_provider.secrets or None,
                )

                # Deserialize and load the resource provider function
                scope: Dict[str, Any] = {}
                serialized_function = resource_provider.function.body
                function_name = resource_provider.function.name

                try:
                    exec(serialized_function, scope, scope)
                    resource_provider_function = scope[function_name]

                    # Invoke the resource provider function
                    resource = self._invoke_resource_provider(resource_provider_function, resource_provider_instance)
                    resource_provider_instance.last_invoked_time = datetime.utcnow()

                    if resource is not None:
                        updated_resource_store[resource_provider_id] = resource

                except Exception as e:
                    logger.error(f"Error loading resource provider {resource_provider.fco_metadata.name}: {e}")
                    self.resource_error_table[resource_provider_id] = ResourceProviderError(
                        ResourceProviderErrorType.EXECUTION_ERROR,
                        str(e),  # type: ignore
                    )

                updated_resource_provider_map[resource_provider_id] = resource_provider_instance

            else:
                updated_resource_provider_map[resource_provider_id] = self.resource_provider_map[resource_provider_id]
                updated_resource_store[resource_provider_id] = self.resource_store.get(resource_provider_id)

        self.resource_provider_map = updated_resource_provider_map

        with self.resource_store_lock.gen_wlock():
            self.resource_store = updated_resource_store

    def _should_refresh_resource_provider(
        self, resource_provider_metadata: ResourceProviderMetadata, resource_provider_fn_hash: str
    ) -> bool:
        resource_provider_id = IdHelper.to_string(resource_provider_metadata.resource_provider.resource_provider_id)
        if resource_provider_id not in self.resource_provider_map:
            return True

        stored_resource_provider = self.resource_provider_map[resource_provider_id]
        if self._has_secrets_updated(resource_provider_metadata, stored_resource_provider):
            return True

        if resource_provider_fn_hash != stored_resource_provider.fn_hash:
            return True

        return False

    def _has_secrets_updated(
        self, resource_provider_metadata: ResourceProviderMetadata, stored_resource_provider: ResourceProviderInstance
    ) -> bool:
        if (resource_provider_metadata.resource_provider.secrets or None) != stored_resource_provider.secrets:
            return True

        secrets_last_updated_time = (
            resource_provider_metadata.secrets_last_updated
            if resource_provider_metadata.HasField("secrets_last_updated")
            else None
        )
        stored_secrets_last_updated_time = stored_resource_provider.secrets_last_updated_time

        # Secrets are updated if it is more recent than the stored resource_provider's secret_last_updated_time
        if secrets_last_updated_time and stored_secrets_last_updated_time:
            return secrets_last_updated_time.ToDatetime() > stored_secrets_last_updated_time
        else:
            return False

    def _invoke_resource_provider(
        self, resource_provider_fn: FunctionType, resource_provider_instance: ResourceProviderInstance
    ) -> Any:
        """
        Invoke the provided resource provider function and return the resource
        :param resource_provider_instance: The stored resource provider instance
        :return The resource returned from the resource provider function
        """
        resource = None
        try:
            resource_provider_code = resource_provider_fn.__code__
            n_args = resource_provider_code.co_argcount
            argument_names = resource_provider_code.co_varnames[:n_args]
            if "context" in argument_names:
                secrets = {}
                if self.secrets_manager and resource_provider_instance.secrets:
                    secrets = {
                        secret_name: self.secrets_manager.get_secret(secret_reference)
                        for secret_name, secret_reference in resource_provider_instance.secrets.items()
                    }
                    missing_secrets = [secret_name for secret_name, value in secrets.items() if value is None]
                    if missing_secrets:
                        message = f'The following secrets for resource provider "{resource_provider_instance.name}" could not be retrieved: [{", ".join(missing_secrets)}]. Please note that newly updated Secrets may take upto 120s to reflect changes. Using configuration generated at {self.last_refresh_time}.'
                        self.resource_error_table[resource_provider_instance.id] = ResourceProviderError(
                            ResourceProviderErrorType.MISSING_SECRETS_ERROR,
                            str(message),  # type: ignore
                        )
                        return None
                context = ResourceProviderContext(secrets=secrets)
                resource = resource_provider_fn(context)
            else:
                resource = resource_provider_fn()

        except Exception as e:
            logger.warning(f'Error invoking resource provider "{resource_provider_instance.name}": {e}')
            self.resource_error_table[resource_provider_instance.id] = ResourceProviderError(
                ResourceProviderErrorType.INVOCATION_ERROR,
                str(e),  # type: ignore
            )
        return resource
