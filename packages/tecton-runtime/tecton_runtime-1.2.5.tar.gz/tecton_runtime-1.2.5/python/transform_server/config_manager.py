#!/usr/bin/env python
import logging
import threading
from datetime import datetime
from datetime import timezone
from typing import Optional
from typing import Tuple

import boto3

from tecton_proto.server_groups import transform_server_group_config__client_pb2 as transform_server_group_config_pb2


logger = logging.getLogger(__name__)

EPOCH_TIME = datetime(1970, 1, 1, tzinfo=timezone.utc)
CONFIG_FILE_NAME = "config_latest"


class CloudStorageClientInterface:
    def read_from_storage_path(self, path: str) -> Optional[bytes]:
        pass


class S3StorageClient(CloudStorageClientInterface):
    """
    S3StorageClient is a client to read objects from S3 Storage
    """

    def __init__(self):
        self.s3_client = boto3.client("s3")
        self.s3_resource = boto3.resource("s3")

    def read_from_storage_path(self, path: str) -> Optional[bytes]:
        """
        Reads the object from the provided S3 path into a byte array. The object is read in chunks to avoid memory issues.
        """
        object_size = 0
        if not path.startswith("s3://"):
            # Read from local file for non S3 paths
            with open(path, "rb") as f:
                return f.read()
        else:
            bucket, key = _get_storage_bucket_and_key(path)
            if not bucket or not key:
                msg = f"Invalid S3 Path: {path}"
                raise ValueError(msg)
            try:
                object_metadata = self.s3_client.head_object(Bucket=bucket, Key=key)
                object_size = object_metadata["ContentLength"]
            except Exception as e:
                msg = f"Failed to get object metadata for {path}"
                raise ValueError(msg)

            try:
                obj = self.s3_resource.Object(bucket, key)
                buffer = bytearray(object_size)

                # Download the file in chunks
                byte_offset = 0
                for chunk in obj.get()["Body"].iter_chunks():
                    buffer[byte_offset : byte_offset + len(chunk)] = chunk
                    byte_offset += len(chunk)
                return bytes(buffer)
            except Exception as e:
                msg = f"Failed to download object from {path}"
                raise ValueError(msg)


def _get_storage_bucket_and_key(path: str) -> Tuple[str, str]:
    """
    Extracts the bucket and key from the storage path
    """
    if path.startswith("s3://"):
        path = path[len("s3://") :]
    elif path.startswith("gs://"):
        path = path[len("gs://") :]
    parts = path.split("/", 1)
    if len(parts) != 2:
        msg = f"Malformed Storage Path: {path}"
        raise ValueError(msg)
    bucket = parts[0]
    key = parts[1].rstrip("/")
    return bucket, key


class TransformServerConfigManager:
    """
    TransformServerConfigManager is a class to fetch and manage the configuration for the Transform Server Group.
    """

    def __init__(
        self,
        storage_client: CloudStorageClientInterface,
        config_file_path: Optional[str],
    ):
        """
        Initializes the TransformServerConfigManager with the provided storage client, bucket, and key
        """
        self.cloud_storage_client = storage_client
        self.config_file_path = config_file_path or ""
        self.mutex = threading.Lock()
        self.config = None
        self.last_computed_time: Optional[datetime] = None

    def update_config(self):
        """Fetch the configuration from Cloud Storage and update local state."""
        try:
            config_file = f"{self.config_file_path}/{CONFIG_FILE_NAME}"
            config_str = self.cloud_storage_client.read_from_storage_path(config_file)
            config_proto = transform_server_group_config_pb2.TransformServerGroupConfiguration()
            config_proto.ParseFromString(config_str)
            with self.mutex:
                self.config = config_proto
            computed_time = config_proto.computed_time.ToDatetime()
            if computed_time != EPOCH_TIME:
                self.last_updated_time = computed_time

        except Exception as e:
            logger.warning(f"Failed to fetch configuration: {e}")
            return

    def get_config(self) -> Optional[transform_server_group_config_pb2.TransformServerGroupConfiguration]:
        """Returns the current Transform Server Group configuration."""
        with self.mutex:
            return self.config
