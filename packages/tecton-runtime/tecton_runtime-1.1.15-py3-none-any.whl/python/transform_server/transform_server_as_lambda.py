import base64
import gzip
import logging
import os
from types import FunctionType
from typing import Any
from typing import Dict

import grpc
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from python.transform_server.transform_server import TransformServerException
from python.transform_server.transform_server import all_transforms
from python.transform_server.transform_server import to_string
from tecton_proto.feature_server.transform import transform_service__client_pb2 as transform_service_pb2


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

CONFIG_PATH = "/opt/config_latest"
transformations: Dict[str, FunctionType] = {}
modes: Dict[str, Any] = {}


def parse_config(config: transform_service_pb2.TransformServiceConfiguration):
    recent_transformations = sorted(
        config.transformations, key=lambda _t: _t.fco_metadata.last_updated_at.ToDatetime(), reverse=True
    )
    end = min(25, len(recent_transformations))
    logger.debug(f"Parsing config and loading {end} out of {len(config.transformations)} transformations")
    for t in recent_transformations[:end]:
        transformation_id = to_string(t.transformation_id)
        if transformation_id in transformations:
            continue
        name = t.user_function.name
        scope: Dict[str, Any] = {}
        try:
            exec(t.user_function.body, scope, scope)
            transformations[transformation_id] = scope[name]
            modes[transformation_id] = t.transformation_mode
        except BaseException as e:
            logger.error(f"Failed to load transformation {transformation_id}: {e}")


def reset_config():
    global transformations
    global modes
    transformations = {}
    modes = {}


if os.path.exists(CONFIG_PATH):
    try:
        with gzip.GzipFile(CONFIG_PATH, "rb") as f:
            config = transform_service_pb2.TransformServiceConfiguration()
            config.ParseFromString(f.read())
            parse_config(config)
    except BaseException as e:
        logger.warning(f"Failed to load config from {CONFIG_PATH}: {e}")


def handler(event: Dict[str, Any], context):
    # event can have different shapes depending on how the lambda is invoked.
    # If invoked with a compressed payload, the payload will be gzipped and base64 encoded and the event will have a key
    # "isCompressed" set to True. Something like:
    # { "isCompressed": True, "body": "H4sIAAAAAAAA/8tIzcnJVyjPL8pJUQQAlQYX5QMAAAA=", "shouldCompressResponse": True }
    # If invoked with an uncompressed payload, the payload will be a json representation of the ServiceRequest proto.
    if event.get("isCompressed"):
        compressed_data = base64.b64decode(event["body"])
        service_request = decompress_and_deserialize_input(compressed_data)
    else:
        service_request = ParseDict(event, transform_service_pb2.ServiceRequest(), ignore_unknown_fields=True)

    if service_request.warmup:
        # Return empty response for no-op requests
        return MessageToDict(transform_service_pb2.ServiceResponse())
    try:
        response = all_transforms(
            service_request,
            should_cache_transformations=event.get("shouldCacheTransformations", False),
        )
    except TransformServerException as e:
        response = transform_service_pb2.ServiceResponse()
        logger.warning("Encountered TransformServerException: %s", e)
        response.error_message = e.details
        response.error_code = e.code.value[0]
    except Exception as e:
        # Since this is invoked as a Lambda function, we need to catch all exceptions and return a valid
        # ServiceResponse message that the feature server can parse.
        response = transform_service_pb2.ServiceResponse()
        logger.warning("Encountered Exception: %s", e)
        response.error_message = str(e)
        # I'm choosing for `INTERNAL` to be the catch-all  error code
        # We should add more special handling once we have a better idea of what kinds of errors we expect to see
        response.error_code = grpc.StatusCode.INTERNAL.value[0]

    if event.get("shouldCompressResponse", False):
        return compress_and_serialize_output(response)
    else:
        return MessageToDict(response)


def decompress_and_deserialize_input(compressed_data):
    decompressed_data_bytes = gzip.decompress(compressed_data)
    service_request = transform_service_pb2.ServiceRequest()
    service_request.ParseFromString(decompressed_data_bytes)
    return service_request


def compress_and_serialize_output(response):
    response_bytes = response.SerializeToString()
    compressed_response = gzip.compress(response_bytes)
    encoded_response = base64.b64encode(compressed_response)
    return {"isCompressed": True, "body": encoded_response.decode("utf-8")}
