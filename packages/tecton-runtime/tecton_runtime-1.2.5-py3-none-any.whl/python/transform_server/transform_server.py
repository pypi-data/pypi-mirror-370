import ast
import contextlib
import functools
import hashlib
import logging
import os
import pathlib
import resource
import sys
import tempfile
import threading
import time
from concurrent import futures
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from threading import Lock
from threading import Thread
from threading import Timer
from time import sleep
from types import FunctionType
from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional
from typing import Protocol
from typing import Tuple

import grpc
import numpy
import pandas
import psutil
import schedule
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
from grpc_reflection.v1alpha import reflection
from prometheus_client import Gauge
from prometheus_client import start_http_server
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor
from statsd import StatsClient

from python.transform_server.config_manager import S3StorageClient
from python.transform_server.config_manager import TransformServerConfigManager
from python.transform_server.realtime_logger import AsyncLogger
from python.transform_server.realtime_logger import JSONStdoutWrapper
from python.transform_server.resource_providers_manager import ResourceProvidersManager
from python.transform_server.secrets_manager import SecretsManager
from python.transform_server.transformation_manager import TransformationManager
from tecton_core.realtime_context import RealtimeContext
from tecton_proto.args.pipeline__client_pb2 import Pipeline
from tecton_proto.args.transformation__client_pb2 import TransformationMode
from tecton_proto.common.id__client_pb2 import Id
from tecton_proto.feature_server.transform import transform_service__client_pb2 as transform_service_pb2
from tecton_proto.feature_server.transform import transform_service__client_pb2_grpc as transform_service_pb2_grpc
from tecton_proto.feature_server.transform import transform_value__client_pb2 as transform_value_pb2
from tecton_proto.server_groups.transform_server_group_config__client_pb2 import TransformationOperation


logger = logging.getLogger(__name__)


# Transform execution strategy protocol
class TransformExecutor(Protocol):
    """Protocol for transform execution strategies."""

    def execute_transforms(
        self,
        service_request: "transform_service_pb2.ServiceRequest",
        request_contexts_dict: Dict[str, Any],
        transformations: Dict[str, FunctionType],
        transformation_modes: Dict[str, Any],
        post_processor_pipelines: Dict[str, "Pipeline"],
        request_timestamp: Optional[datetime],
        secrets_map: Dict[str, Mapping[str, str]],
        resources_map: Dict[str, Mapping[str, Any]],
    ) -> List[Tuple[int, List, Optional[Exception], float]]:
        """Execute transform requests and return results."""
        ...


# Prometheus Gauges for System Metrics
cpu_usage_gauge = Gauge("transform_server_cpu_usage_percentage", "CPU Usage of the Transform Server", ["group_name"])

memory_usage_gauge = Gauge(
    "transform_server_memory_usage_percentage", "Memory Usage of the Transform Server", ["group_name"]
)
memory_total_gauge = Gauge("transform_server_memory_total", "Total Memory of the Transform Server", ["group_name"])
memory_available_gauge = Gauge(
    "transform_server_memory_available", "Available Memory of the Transform Server", ["group_name"]
)
swap_memory_usage_gauge = Gauge(
    "transform_server_swap_memory_usage_percentage", "Swap Memory Usage of the Transform Server", ["group_name"]
)
swap_memory_used_gauge = Gauge(
    "transform_server_swap_memory_used", "Used Swap Memory of the Transform Server", ["group_name"]
)
disk_usage_gauge = Gauge("transform_server_disk_usage_percentage", "Disk Usage of the Transform Server", ["group_name"])
disk_total_gauge = Gauge(
    "transform_server_disk_usage_total", "Total Disk Space of the Transform Server", ["group_name"]
)
disk_free_gauge = Gauge("transform_server_disk_usage_free", "Free Disk Space of the Transform Server", ["group_name"])
process_count_gauge = Gauge("transform_server_process_count", "Process Count of the Transform Server", ["group_name"])
concurrent_request_utilization_gauge = Gauge(
    "transform_server_request_utilization_percentage",
    "Utilization Percentage of the Transform Server",
    ["group_name"],
)
total_threads_gauge = Gauge(
    "transform_server_total_threads", "Total Thread Count in the Transform Server", ["group_name"]
)
busy_rpcs_gauge = Gauge("transform_server_busy_rpcs", "Busy RPCs Count in the Transform Server", ["group_name"])

total_rpcs_gauge = Gauge("transform_server_total_rpcs", "Total RPCs Count in the Transform Server", ["group_name"])

total_cores_gauge = Gauge("transform_server_total_cores", "Total CPU Cores in Instance", ["group_name"])


def _cpus_available(default=1) -> int:
    """Estimate the number of CPUs available to this program.

    Uses the scheduler API on platforms that support it (e.g. Linux),
    falling back on the total CPU count for platforms that don't (e.g. MacOS).
    Returns `default` if the platform does not support any CPU count query API.
    """
    if sched_getaffinity := getattr(os, "sched_getaffinity", None):
        return len(sched_getaffinity(0))
    return os.cpu_count() or default


def _parse_multiprocessing_max_workers() -> int:
    """Parse the multiprocessing max workers from environment variable.

    Returns the configured number of workers, defaulting to available CPUs
    if the environment variable is not set or invalid.
    """
    multiprocessing_workers_env = os.environ.get("TRANSFORM_SERVER_MULTIPROCESSING_MAX_WORKERS")
    if multiprocessing_workers_env:
        try:
            workers = int(multiprocessing_workers_env)
            # Use provided value if it's positive, otherwise default to cpu_count
            return workers if workers > 0 else _cpus_available()
        except ValueError:
            # If parsing fails, default to cpu_count
            logger.warning(
                f"Invalid TRANSFORM_SERVER_MULTIPROCESSING_MAX_WORKERS value: {multiprocessing_workers_env}. Using CPU count."
            )
            return _cpus_available()
    else:
        # Default to CPU count if no specific multiprocessing worker count is set
        return _cpus_available()


class IngestionRecord:
    def __init__(self, proto_request: transform_service_pb2.IngestionRecord, is_python_mode: bool):
        self.proto_request: transform_service_pb2.IngestionRecord = proto_request
        self.id: Id = self.proto_request.push_source_id
        self.payload = map_transform_value_to_python(self.proto_request.payload)
        if not is_python_mode:
            # In pandas mode, convert the dictionaries to dataframes with one row. Also need to convert top-level "list"
            # type values to numpy arrays for consistency with the offline behavior.
            np_arrays = convert_list_values_to_numpy_arrays(self.payload)
            self.payload = pandas.DataFrame.from_records([np_arrays])


def to_string(_id_proto: Id) -> str:
    return f"{_id_proto.most_significant_bits:016x}{_id_proto.least_significant_bits:016x}"


class UDFError(Exception):
    """An error in the definition of a UDF that could not be detected by the SDK/MDS."""


def eval_node(
    node,
    request_ds,
    intermediate_data,
    transforms: Dict[str, FunctionType],
    request_timestamp: Optional[datetime],
    is_python_mode: bool,
    ingestion_record: Optional[IngestionRecord] = None,
    secrets: Mapping[str, str] = {},
    resources: Mapping[str, Any] = {},
):
    if node.HasField("request_data_source_node"):
        return request_ds
    elif node.HasField("feature_view_node"):
        return intermediate_data[node.feature_view_node.input_name]
    elif (
        node.HasField("data_source_node")
        and ingestion_record
        and node.data_source_node.virtual_data_source_id == ingestion_record.id
    ):
        return ingestion_record.payload
    elif node.HasField("transformation_node"):
        t = transforms[to_string(node.transformation_node.transformation_id)]
        args = []
        kwargs = {}
        for i in node.transformation_node.inputs:
            val = eval_node(
                i.node,
                request_ds,
                intermediate_data,
                transforms,
                request_timestamp,
                is_python_mode,
                ingestion_record=ingestion_record,
                secrets=secrets,
                resources=resources,
            )
            if i.HasField("arg_index"):
                args.append(val)
            elif i.HasField("arg_name"):
                kwargs[i.arg_name] = val
        return t(*args, **kwargs)
    elif node.HasField("context_node"):
        transformation_mode = (
            TransformationMode.TRANSFORMATION_MODE_PYTHON
            if is_python_mode
            else TransformationMode.TRANSFORMATION_MODE_PANDAS
        )
        return RealtimeContext(
            _mode=transformation_mode, request_timestamp=request_timestamp, secrets=secrets, resources=resources
        )
    elif node.HasField("constant_node"):
        constant_node = node.constant_node
        if constant_node.HasField("string_const"):
            return constant_node.string_const
        elif constant_node.HasField("int_const"):
            return int(constant_node.int_const)
        elif constant_node.HasField("float_const"):
            return float(constant_node.float_const)
        elif constant_node.HasField("bool_const"):
            return constant_node.bool_constant
        elif constant_node.HasField("null_const"):
            return None
        msg = f"Unknown ConstantNode type: {constant_node}"
        raise KeyError(msg)
    else:
        msg = f"Found unexpected node type in pipeline {node}"
        raise Exception(msg)


# evaluate an individual rtfv in the feature service request
def transform(
    rtfv_request: transform_service_pb2.TransformRequest,
    request_context_input: Dict[str, Any],
    transforms: Dict[str, FunctionType],
    pipeline: Pipeline,
    is_python_mode: bool,
    request_timestamp: Optional[datetime],
    secrets: Mapping[str, str] = {},
    resources: Mapping[str, Any] = {},
) -> List:
    # Could be further optimized to clone rather than repeatedly convert from the transform proto.
    fv_intermediate_inputs: Dict[str, Any] = {
        k: map_transform_value_to_python(v) for k, v in rtfv_request.intermediate_data.items()
    }
    if not is_python_mode:
        # In pandas mode, convert the dictionaries to dataframes with one row. Also need to convert top-level "list"
        # type values to numpy arrays for consistency with the offline behavior.
        fv_intermediate_inputs = {k: convert_list_values_to_numpy_arrays(v) for k, v in fv_intermediate_inputs.items()}
        fv_intermediate_inputs = {k: pandas.DataFrame.from_records([v]) for k, v in fv_intermediate_inputs.items()}
        request_context_input = convert_list_values_to_numpy_arrays(request_context_input)
        request_context_input = pandas.DataFrame.from_records([request_context_input])

    _ingestion_record = (
        IngestionRecord(rtfv_request.ingestion_record, is_python_mode)
        if rtfv_request.HasField("ingestion_record")
        else None
    )

    out = eval_node(
        pipeline.root,
        request_context_input,
        fv_intermediate_inputs,
        transforms,
        request_timestamp,
        is_python_mode=is_python_mode,
        ingestion_record=_ingestion_record,
        secrets=secrets,
        resources=resources,
    )
    root_func_name = transforms[to_string(pipeline.root.transformation_node.transformation_id)].__name__

    if is_python_mode:
        if not isinstance(out, (dict, list, str)):
            msg = f"UDF for '{root_func_name}' returned type {type(out)}; expected one of type (`dict`, `list`, `str`)."
            raise UDFError(msg)
        # Prompt Feature Views can return a string
        if isinstance(out, str):
            out = {"prompt": out}
        if not isinstance(out, list):
            out = [out]
    else:
        # Convert the dataframe to a python dictionary.
        if len(out) != 1:
            root_func_name = transforms[to_string(pipeline.root.transformation_node.transformation_id)].__name__
            logger.debug(
                f"UDF for '{root_func_name}' returned a dataframe with an unexpected number of rows: {len(out)}."
            )
        out = out.to_dict("records")

    return [python_to_transform_value(r, "").map_value for r in out]


# Note that this method mutates the input dictionary. It does not make a copy.
def convert_list_values_to_numpy_arrays(dictionary):
    for k, v in dictionary.items():
        if isinstance(v, list):
            dictionary[k] = numpy.array(v)
    return dictionary


class TransformServerException(Exception):
    def __init__(self, code: grpc.StatusCode, details: str):
        self.code = code
        self.details = details


# Populates the transformations dictionary with the user-defined functions from the service request
# TODO(RT-Compute): This can be deleted once we migrate all Realtime Compute to use the Transform Server Groups
def populate_transformations(
    service_request: transform_service_pb2.ServiceRequest,
    transformations: Dict[str, TransformationOperation],
    transformation_modes: Dict[str, Any],
    post_processor_pipelines: Dict[str, Pipeline],
):
    if len(service_request.transformation_operations) > 0:
        for transformation_op in service_request.transformation_operations:
            transformation_id = to_string(transformation_op.transformation_id)
            if transformation_id in transformations:
                continue
            else:
                logger.debug(f"Encountered new transformation op {transformation_id}")

            # Store raw transformation operation instead of compiling
            transformations[transformation_id] = transformation_op
            transformation_modes[transformation_id] = transformation_op.transformation_mode
            if transformation_op.is_post_processor_operation:
                post_processor_pipelines[to_string(transformation_op.transformation_id)] = _post_processor_pipeline(
                    transformation_op
                )
    else:
        # Handle legacy transformation format - convert to TransformationOperation
        for transformation in service_request.transformations:
            transformation_id = to_string(transformation.transformation_id)
            if transformation_id in transformations:
                logger.debug(f"Using cached transformation {transformation_id}")
                continue
            else:
                logger.debug(f"Encountered new transformation {transformation_id}")

            # Convert legacy transformation to TransformationOperation format
            transformation_op = TransformationOperation()
            transformation_op.transformation_id.CopyFrom(transformation.transformation_id)
            transformation_op.user_defined_function.name = transformation.user_function.name
            transformation_op.user_defined_function.body = transformation.user_function.body
            transformation_op.transformation_mode = transformation.transformation_mode

            transformations[transformation_id] = transformation_op
            transformation_modes[transformation_id] = transformation.transformation_mode


# evaluate all rtfvs in the feature service request
def all_transforms(
    service_request: transform_service_pb2.ServiceRequest,
    should_cache_transformations: bool = False,
    secrets_map: Dict[str, Mapping[str, str]] = {},
    resources_map: Dict[str, Mapping[str, Any]] = {},
    post_processor_pipelines: Dict[str, Pipeline] = {},
    transformations: Dict[str, TransformationOperation] = {},
    transformation_modes: Dict[str, Any] = {},
    transform_executor: Optional[TransformExecutor] = None,
) -> transform_service_pb2.ServiceResponse:
    response = transform_service_pb2.ServiceResponse()

    if not should_cache_transformations:
        transformations = transformations.copy()
        transformation_modes = transformation_modes.copy()

    if not transformations and not transformation_modes:
        populate_transformations(service_request, transformations, transformation_modes, post_processor_pipelines)

    request_contexts_dict = map_transform_value_to_python(service_request.request_context)

    request_timestamp = None
    if service_request.HasField("request_timestamp"):
        request_timestamp = datetime.utcfromtimestamp(service_request.request_timestamp.seconds).replace(
            tzinfo=timezone.utc
        )

    # Use the provided executor or default to sequential
    executor = transform_executor or SequentialTransformExecutor()

    try:
        results = executor.execute_transforms(
            service_request=service_request,
            request_contexts_dict=request_contexts_dict,
            transformations=transformations,
            transformation_modes=transformation_modes,
            post_processor_pipelines=post_processor_pipelines,
            request_timestamp=request_timestamp,
            secrets_map=secrets_map,
            resources_map=resources_map,
        )

        # Process results and handle any exceptions
        for request_index, output, exception, execution_time_seconds in results:
            if exception:
                if isinstance(exception, UDFError):
                    raise TransformServerException(grpc.StatusCode.FAILED_PRECONDITION, str(exception))
                elif isinstance(exception, TransformServerException):
                    raise exception
                else:
                    # Find the corresponding request to get the feature view ID for error context
                    corresponding_request = next(
                        req for req in service_request.requests if req.request_index == request_index
                    )
                    error_fv_id = corresponding_request.feature_view_id
                    logger.warning("Unexpected error executing ODFV", exc_info=True)
                    raise TransformServerException(
                        grpc.StatusCode.INVALID_ARGUMENT,
                        f"{type(exception).__name__}: {str(exception)} (when evaluating ODFV {error_fv_id})",
                    )

            # Add successful outputs to response
            for o in output:
                result = transform_service_pb2.TransformResponse(request_index=request_index, outputs=o)
                response.outputs.append(result)

            # Add execution time
            corresponding_request = next(req for req in service_request.requests if req.request_index == request_index)
            fv_id = corresponding_request.feature_view_id
            response.execution_times[fv_id].FromTimedelta(timedelta(seconds=execution_time_seconds))

    except Exception as e:
        logger.error(f"Error in transform execution: {e}")
        raise

    response.error_code = 0
    return response


def preprocess_request(
    request: transform_service_pb2.TransformRequest,
    request_contexts_dict: Dict[str, Any],
    transformations: Dict[str, FunctionType],
    post_processor_pipeline: Pipeline,
    post_processor_mode: TransformationMode,
    request_timestamp: Optional[datetime],
) -> transform_service_pb2.ServiceRequest:
    post_processor_output = []
    if request.HasField("ingestion_record") and request.HasField("post_processor_id"):
        is_python_mode = post_processor_mode == TransformationMode.TRANSFORMATION_MODE_PYTHON
        post_processor_output = transform(
            request,
            request_contexts_dict.copy(),
            transformations,
            post_processor_pipeline,
            is_python_mode,
            request_timestamp,
        )
    return post_processor_output


def _execute_single_request(
    request: "transform_service_pb2.TransformRequest",
    request_contexts_dict: Dict[str, Any],
    transformations: Dict[str, FunctionType],
    transformation_modes: Dict[str, Any],
    pipeline: "Pipeline",
    post_processor_pipelines: Dict[str, "Pipeline"],
    request_timestamp: Optional[datetime],
    secrets_map: Dict[str, Mapping[str, str]],
    resources_map: Dict[str, Mapping[str, Any]],
) -> List:
    """Execute a single transform request - shared logic for both sequential and multiprocessing."""
    fv_id: str = request.feature_view_id
    output = []

    # Handle post-processor if present
    if request.HasField("post_processor_id"):
        post_processor_id = to_string(request.post_processor_id)
        post_processor_pipeline = post_processor_pipelines[post_processor_id]
        post_processor_mode = transformation_modes[post_processor_id]
        output = preprocess_request(
            request=request,
            request_contexts_dict=request_contexts_dict,
            transformations=transformations,
            post_processor_pipeline=post_processor_pipeline,
            post_processor_mode=post_processor_mode,
            request_timestamp=request_timestamp,
        )

    if request.HasField("feature_view_id"):
        # Post Processor is a row level transformation so the output should only have one record
        if output:
            request.ingestion_record.payload.CopyFrom(output[0])

        root_transformation_id = to_string(pipeline.root.transformation_node.transformation_id)
        rtfv_mode = transformation_modes[root_transformation_id]
        if rtfv_mode is None:
            raise TransformServerException(
                grpc.StatusCode.NOT_FOUND,
                f"Unable to find Feature View with ID {fv_id}. Please note that newly updated Feature Services may take upto 60s to be available.",
            )

        is_python_mode = rtfv_mode == TransformationMode.TRANSFORMATION_MODE_PYTHON
        cloned_rc_input = request_contexts_dict.copy()
        secrets_for_fv: Mapping[str, str] = (secrets_map or {}).get(fv_id, {})
        resources_for_fv: Mapping[str, Any] = (resources_map or {}).get(fv_id, {})

        output = transform(
            request,
            cloned_rc_input,
            transformations,
            pipeline,
            is_python_mode,
            request_timestamp,
            secrets=secrets_for_fv,
            resources=resources_for_fv,
        )

    return output


class SequentialTransformExecutor(TransformExecutor):
    """Sequential (single-threaded) transform execution - original behavior."""

    def __init__(self):
        # Cache compiled transformations using the same mechanism as multiprocessing workers
        @functools.lru_cache(maxsize=int(os.environ.get("TRANSFORM_SERVER_WORKER_CACHE_SIZE", "1000")))
        def _compile_transformation(
            transformation_id: str, function_body_hash: str, function_name: str, function_body: str
        ):
            """Compile and cache transformation functions using hash-based LRU cache."""
            scope: Dict[str, Any] = {}
            try:
                exec(function_body, scope, scope)
                return scope[function_name]
            except Exception as e:
                raise TransformServerException(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        self._compile_transformation = _compile_transformation

    def _get_compiled_transformations(
        self, raw_transformations: Dict[str, TransformationOperation]
    ) -> Dict[str, FunctionType]:
        """Convert raw transformation operations to compiled functions."""
        compiled_transformations = {}
        for transformation_id, transformation_op in raw_transformations.items():
            function_body = transformation_op.user_defined_function.body
            function_name = transformation_op.user_defined_function.name
            function_body_hash = hashlib.sha256(function_body.encode()).hexdigest()

            compiled_transformations[transformation_id] = self._compile_transformation(
                transformation_id, function_body_hash, function_name, function_body
            )
        return compiled_transformations

    def execute_transforms(
        self,
        service_request,
        request_contexts_dict,
        transformations,
        transformation_modes,
        post_processor_pipelines,
        request_timestamp,
        secrets_map,
        resources_map,
    ):
        """Execute transforms sequentially in the main thread."""
        # Compile raw transformations to functions
        compiled_transformations = self._get_compiled_transformations(transformations)

        results = []

        for request in service_request.requests:
            start = datetime.now()
            output = []
            exception = None

            try:
                fv_id: str = request.feature_view_id
                pipeline = service_request.pipelines[fv_id]

                output = _execute_single_request(
                    request=request,
                    request_contexts_dict=request_contexts_dict,
                    transformations=compiled_transformations,
                    transformation_modes=transformation_modes,
                    pipeline=pipeline,
                    post_processor_pipelines=post_processor_pipelines,
                    request_timestamp=request_timestamp,
                    secrets_map=secrets_map,
                    resources_map=resources_map,
                )

            except Exception as e:
                exception = e

            duration = datetime.now() - start
            execution_time_seconds = duration.total_seconds()
            results.append((request.request_index, output, exception, execution_time_seconds))

        return results


class MultiprocessingTransformExecutor(TransformExecutor):
    """Multiprocessing transform execution with optimizations."""

    def __init__(self, process_pool: ProcessPoolExecutor, max_concurrent_requests: int):
        self.process_pool = process_pool
        self.max_concurrent_requests = max_concurrent_requests

        # Simple semaphore for request-level admission control
        self._request_semaphore = threading.Semaphore(self.max_concurrent_requests)

    @contextlib.contextmanager
    def _acquire_request_permit(self):
        """Context manager for request semaphore acquisition.

        This implements admission control by using a semaphore to limit the number of
        concurrent requests that can be processed. The semaphore prevents overwhelming
        the process pool by rejecting new requests when at capacity.

        The yield statement marks the point where the protected code block executes -
        everything before yield is setup, everything after yield (in finally) is cleanup.
        This ensures the semaphore is always released even if an exception occurs.
        """
        acquired = self._request_semaphore.acquire(blocking=False)
        if not acquired:
            logger.debug(
                f"Rejected request - process pool at capacity ({self.max_concurrent_requests} max concurrent requests)"
            )
            raise TransformServerException(
                grpc.StatusCode.RESOURCE_EXHAUSTED, "Transform server process pool at capacity, please retry"
            )
        try:
            yield
        finally:
            self._request_semaphore.release()

    def execute_transforms(
        self,
        service_request,
        request_contexts_dict,
        transformations,
        transformation_modes,
        post_processor_pipelines,
        request_timestamp,
        secrets_map,
        resources_map,
    ):
        """Execute transforms in parallel using multiprocessing."""

        with self._acquire_request_permit():
            # Use the passed-in raw transformations (already TransformationOperation objects)
            # Serialize protobuf objects to bytes for multiprocessing
            transformation_operations_bytes = []
            for transformation_op in transformations.values():
                transformation_operations_bytes.append(transformation_op.SerializeToString())

            pipelines_bytes = {}
            for fv_id, pipeline in service_request.pipelines.items():
                pipelines_bytes[fv_id] = pipeline.SerializeToString()

            post_processor_pipelines_bytes = {}
            for pp_id, pp_pipeline in post_processor_pipelines.items():
                post_processor_pipelines_bytes[pp_id] = pp_pipeline.SerializeToString()

            worker_args = []
            for request in service_request.requests:
                args = (
                    request.SerializeToString(),  # Serialize request to bytes
                    request_contexts_dict,
                    transformation_operations_bytes,
                    transformation_modes,
                    pipelines_bytes,
                    post_processor_pipelines_bytes,
                    request_timestamp,
                    secrets_map,
                    resources_map,
                )
                worker_args.append(args)

            # Process requests in parallel using persistent process pool with timeout (Python 3.9+)
            timeout_seconds = int(os.environ.get("TRANSFORM_SERVER_MULTIPROCESSING_TIMEOUT_SECONDS", "60"))

            try:
                results_iter = self.process_pool.map(
                    _multiprocessing_worker_function, worker_args, timeout=timeout_seconds
                )
                return list(results_iter)
            except futures.TimeoutError:
                logger.error(f"Process pool timeout after {timeout_seconds}s - may need recreation")
                raise TransformServerException(grpc.StatusCode.DEADLINE_EXCEEDED, "Processing timeout")


# Multiprocessing worker function - uses functools.lru_cache for function caching
def _multiprocessing_worker_function(args: Tuple) -> Tuple[int, List, Optional[Exception], float]:
    """Worker function for processing a single RTFV request in a separate process."""

    # Create a cached function compilation function using functools.lru_cache with hash-based keys
    @functools.lru_cache(maxsize=int(os.environ.get("TRANSFORM_SERVER_WORKER_CACHE_SIZE", "1000")))
    def _compile_transformation(
        transformation_id: str, function_body_hash: str, function_name: str, function_body: str
    ):
        """Compile and cache transformation functions using hash-based LRU cache.

        Args:
            transformation_id: Unique ID for the transformation
            function_body_hash: SHA256 hash of the function body (used for cache key)
            function_name: Name of the function to extract from the compiled scope
            function_body: The actual function body to compile (not part of cache key)
        """
        scope: Dict[str, Any] = {}
        try:
            exec(function_body, scope, scope)
            return scope[function_name]
        except Exception as e:
            raise TransformServerException(grpc.StatusCode.INVALID_ARGUMENT, str(e))

    (
        request_bytes,
        request_contexts_dict,
        transformation_operations_bytes,
        transformation_modes,
        pipelines_bytes,
        post_processor_pipelines_bytes,
        request_timestamp,
        secrets_map,
        resources_map,
    ) = args

    start = datetime.now()
    output = []
    exception = None

    try:
        # Deserialize protobuf objects from bytes
        request = transform_service_pb2.TransformRequest()
        request.ParseFromString(request_bytes)

        transformation_operations = []
        for op_bytes in transformation_operations_bytes:
            op = transform_service_pb2.TransformationOperation()
            op.ParseFromString(op_bytes)
            transformation_operations.append(op)

        pipelines = {}
        for pipeline_fv_id, pipeline_bytes in pipelines_bytes.items():
            pipeline = Pipeline()
            pipeline.ParseFromString(pipeline_bytes)
            pipelines[pipeline_fv_id] = pipeline

        post_processor_pipelines = {}
        for pp_id, pp_bytes in post_processor_pipelines_bytes.items():
            pp_pipeline = Pipeline()
            pp_pipeline.ParseFromString(pp_bytes)
            post_processor_pipelines[pp_id] = pp_pipeline

        # Reconstruct transformations from operations using functools.lru_cache
        transformations = {}
        for transformation_op in transformation_operations:
            transformation_id = to_string(transformation_op.transformation_id)

            # Compute hash of function body for cache key (much smaller than full function body)
            function_body = transformation_op.user_defined_function.body
            function_body_hash = hashlib.sha256(function_body.encode("utf-8")).hexdigest()

            # Use the cached compilation function (automatically handles LRU caching)
            compiled_function = _compile_transformation(
                transformation_id,
                function_body_hash,
                transformation_op.user_defined_function.name,
                function_body,  # Pass the full body for compilation, but it's not part of cache key
            )
            transformations[transformation_id] = compiled_function

        fv_id: str = request.feature_view_id
        pipeline = pipelines[fv_id]

        # Use the shared execution logic
        output = _execute_single_request(
            request=request,
            request_contexts_dict=request_contexts_dict,
            transformations=transformations,
            transformation_modes=transformation_modes,
            pipeline=pipeline,
            post_processor_pipelines=post_processor_pipelines,
            request_timestamp=request_timestamp,
            secrets_map=secrets_map,
            resources_map=resources_map,
        )

    except Exception as e:
        exception = e

    duration = datetime.now() - start
    execution_time_seconds = duration.total_seconds()

    return (request.request_index, output, exception, execution_time_seconds)


def map_transform_value_to_python(value: transform_value_pb2.MapTransformValue) -> Dict[str, Any]:
    return {k: transform_value_to_python(v, k) for k, v in value.value_map.items()}


def transform_value_to_python(value: transform_value_pb2.TransformValue, field_name: str):
    value_type = value.WhichOneof("value")
    if value_type == "float64_value":
        return value.float64_value
    elif value_type == "int64_value":
        return value.int64_value
    elif value_type == "timestamp_value":
        # Timestamps are always stored in UTC, so we can safely set the tzinfo explicitly here
        datetime_value = value.timestamp_value.ToDatetime()
        utc_datetime = datetime_value.replace(tzinfo=timezone.utc)
        return utc_datetime
    elif value_type == "bool_value":
        return value.bool_value
    elif value_type == "string_value":
        return value.string_value
    elif value_type == "null_value":
        return None
    elif value_type == "map_value":
        return {k: transform_value_to_python(v, k) for k, v in value.map_value.value_map.items()}
    elif value_type == "array_value":
        return [transform_value_to_python(v, field_name) for v in value.array_value.elements]
    else:
        msg = (
            f"Unexpected type `{value_type}` for field `{field_name}`: '{value}'; must be one of type `float64`, "
            f"`int64`, `bool`, `null`, `string`, `timestamp`, `array` or `map`."
        )
        raise UDFError(msg)


def python_to_transform_value(python_value, field_name: str) -> transform_value_pb2.TransformValue:
    python_type = type(python_value)
    value_proto = transform_value_pb2.TransformValue()
    if python_value is None:
        # Return nulls explicitly.
        value_proto.null_value.CopyFrom(transform_value_pb2.NullTransformValue())
    elif python_type in (float, numpy.float64, numpy.float32):
        value_proto.float64_value = python_value
    elif python_type in (int, numpy.int32, numpy.int64):
        value_proto.int64_value = python_value
    elif python_type is bool:
        value_proto.bool_value = python_value
    elif python_type is str:
        value_proto.string_value = python_value
    elif python_type in (list, numpy.ndarray):
        value_proto.array_value.elements.extend([python_to_transform_value(v, field_name) for v in python_value])
    elif python_type is dict:
        if python_value:
            for k, v in python_value.items():
                value_proto.map_value.value_map[k].CopyFrom(python_to_transform_value(v, k))
        else:
            # An empty map is distinct from null, so fill an empty map value.
            value_proto.map_value.CopyFrom(transform_value_pb2.MapTransformValue())
    elif python_type is pandas.Timestamp:
        value_proto.timestamp_value.FromMilliseconds(int(python_value.timestamp() * 1000))
    elif python_type is datetime:
        value_proto.timestamp_value.seconds = int(python_value.timestamp())
        value_proto.timestamp_value.nanos = int((python_value.timestamp() - value_proto.timestamp_value.seconds) * 1e9)
    elif pandas.api.types.is_scalar(python_value) and pandas.isna(python_value):
        # Handle pandas.NA
        # numpy.nan should not reach here. It should've been converted to Python float and handled above
        value_proto.null_value.CopyFrom(transform_value_pb2.NullTransformValue())
    else:
        msg = (
            f"Unexpected python type `{python_type}` for field `{field_name}`: '{python_value}'; must be one of type "
            f"`float`, `int`, `bool`, `str`, `list`, `dict`, `timestamp` or `datetime`."
        )
        raise UDFError(msg)
    return value_proto


class TransformServer(transform_service_pb2_grpc.TransformServiceServicer):
    def __init__(self, thread_pool: Optional[ThreadPoolExecutor] = None):
        self.config_manager = None
        self.secrets_manager = None
        self.resource_providers_manager = None  # type: ignore
        self.transformation_manager = None

        transform_server_groups_enabled = os.environ.get("TRANSFORM_SERVER_GROUPS_ENABLED", "false") == "true"
        secrets_enabled = os.environ.get("SECRETS_IN_TRANSFORM_SERVER_GROUPS_ENABLED", "false") == "true"
        resource_providers_enabled = (
            os.environ.get("RESOURCE_PROVIDERS_IN_TRANSFORM_SERVER_GROUPS_ENABLED", "false") == "true"
        )

        # Parse configuration constants from environment variables
        multiprocessing_requested = os.environ.get("TRANSFORM_SERVER_ENABLE_MULTIPROCESSING", "false") == "true"
        self.request_queue_multiplier = int(os.environ.get("TRANSFORM_SERVER_REQUEST_QUEUE_MULTIPLIER", "4"))
        self.multiprocessing_enabled = multiprocessing_requested and transform_server_groups_enabled

        # Parse multiprocessing worker count - declare type once
        self.multiprocessing_max_workers: Optional[int] = None
        if self.multiprocessing_enabled:
            self.multiprocessing_max_workers = _parse_multiprocessing_max_workers()

        # Initialize transform executor based on final multiprocessing configuration
        self.transform_executor: TransformExecutor = SequentialTransformExecutor()
        if self.multiprocessing_enabled:
            # At this point, multiprocessing_max_workers is guaranteed to be set
            assert self.multiprocessing_max_workers is not None

            # Calculate resource limits for worker processes
            resource_limits = calculate_per_process_resource_limits(self.multiprocessing_max_workers)
            memory_limit_mb = resource_limits["memory_mb"]

            # Calculate max concurrent requests as process pool size * queue multiplier
            request_queue_multiplier = int(os.environ.get("TRANSFORM_SERVER_REQUEST_QUEUE_MULTIPLIER", "4"))
            max_concurrent_requests = int(
                os.environ.get(
                    "TRANSFORM_SERVER_MAX_CONCURRENT_REQUESTS",
                    str(self.multiprocessing_max_workers * request_queue_multiplier),
                )
            )

            # Create process pool with resource limits
            process_pool = ProcessPoolExecutor(
                max_workers=self.multiprocessing_max_workers,
                initializer=worker_process_initializer,
                initargs=(memory_limit_mb,),
            )
            self.transform_executor = MultiprocessingTransformExecutor(process_pool, max_concurrent_requests)
            logger.info(
                f"Initialized multiprocessing executor with {self.multiprocessing_max_workers} workers, "
                f"max concurrent requests: {self.transform_executor.max_concurrent_requests}, "
                f"memory limit per worker: {memory_limit_mb}MB"
            )
        else:
            logger.info("Multiprocessing disabled. Using sequential executor")

        self.thread_pool: ThreadPoolExecutor = thread_pool or futures.ThreadPoolExecutor(max_workers=4)
        self.evaluate_timeout = (
            int(os.environ.get("TRANSFORM_SERVER_REQUEST_TIMEOUT_SECONDS", "60"))
            if "TRANSFORM_SERVER_REQUEST_TIMEOUT_SECONDS" in os.environ
            else None
        )
        if transform_server_groups_enabled:
            config_file_path = os.environ.get("TRANSFORM_SERVER_GROUP_CONFIGURATION_PATH")
            self.config_manager = TransformServerConfigManager(
                storage_client=S3StorageClient(), config_file_path=config_file_path
            )
            if secrets_enabled:
                self.secrets_manager = SecretsManager()
            if resource_providers_enabled:
                self.resource_providers_manager = ResourceProvidersManager(
                    secrets_manager=self.secrets_manager if secrets_enabled else None  # type: ignore
                )
            self.transformation_manager = TransformationManager()
            self.start_periodic_refresh(secrets_enabled, resource_providers_enabled)

    def __del__(self):
        """Clean up resources when the server is destroyed."""
        if hasattr(self, "transform_executor") and isinstance(
            self.transform_executor, MultiprocessingTransformExecutor
        ):
            self.transform_executor.process_pool.shutdown(wait=False)

    def start_periodic_refresh(self, secrets_enabled: bool, resource_providers_enabled: bool):
        refresh_interval = int(os.environ.get("TRANSFORM_SERVER_CONFIG_REFRESH_INTERVAL", "60"))
        schedule.every(refresh_interval).seconds.do(self.periodic_refresh, secrets_enabled, resource_providers_enabled)
        thread = threading.Thread(target=lambda: self.run_scheduler(refresh_interval))
        thread.daemon = True
        thread.start()

    def periodic_refresh(self, secrets_enabled: bool, resource_providers_enabled: bool):
        """Fetches the latest config and refreshes secrets cache."""
        self.config_manager.update_config()  # type: ignore
        latest_config = self.config_manager.get_config()  # type: ignore
        if latest_config:
            if secrets_enabled:
                try:
                    self.secrets_manager.refresh_secrets_cache(  # type: ignore
                        secrets_config=latest_config.secrets_config,
                        config_last_updated_time=latest_config.computed_time,
                    )
                except Exception as e:
                    logger.warning(f"Error during periodic secrets refresh: {e}")
            if resource_providers_enabled:
                try:
                    self.resource_providers_manager.refresh_resource_store(  # type: ignore
                        resource_provider_config=latest_config.resource_providers_config,
                        config_last_updated_time=latest_config.computed_time,
                    )
                except Exception as e:
                    logger.warning(f"Error during periodic resource providers refresh: {e}")
            if self.transformation_manager:
                try:
                    transformations = latest_config.transformations
                    self.transformation_manager.refresh_transformation_cache(
                        transformation_operations=transformations, config_last_updated_time=latest_config.computed_time
                    )
                except Exception as e:
                    logger.warning(f"Error during periodic transformations refresh: {e}")

        else:
            logger.warning("No valid configuration available to refresh secrets and resource providers.")

    def run_scheduler(self, refresh_interval: int):
        logger.info(f"Running scheduler with refresh interval {refresh_interval}")
        while True:
            schedule.run_pending()
            time.sleep(5)

    def Evaluate(self, request: transform_service_pb2.ServiceRequest, context):
        fv_ids = [fv_request.feature_view_id for fv_request in request.requests]
        secrets_map_for_request = {}
        if self.secrets_manager:
            secrets_map_for_request = {
                fv_id: self.secrets_manager.get_secrets_for_fco(fco_id=fv_id) for fv_id in fv_ids
            }
        resource_map_for_request = {}
        if self.resource_providers_manager:
            resource_map_for_request = {
                fv_id: self.resource_providers_manager.get_resources(feature_view_id=fv_id) for fv_id in fv_ids
            }
        transformations = {}
        transformation_modes = {}
        post_processor_pipelines = {}
        if self.transformation_manager:
            transformations = self.transformation_manager.get_all_transformations()
            transformation_modes = self.transformation_manager.get_all_transformation_modes()
            post_processor_pipelines = self.transformation_manager.get_all_post_processors()

        try:
            f = self.thread_pool.submit(
                all_transforms,
                request,
                secrets_map=secrets_map_for_request,
                resources_map=resource_map_for_request,  # type: ignore
                post_processor_pipelines=post_processor_pipelines,
                transformations=transformations,
                transformation_modes=transformation_modes,
                transform_executor=self.transform_executor,
            )
            return f.result(timeout=self.evaluate_timeout)
        except futures.TimeoutError:
            context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, "Deadline exceeded")
        except TransformServerException as e:
            context.abort(e.code, e.details)


def _check_server_health(
    health_servicer: health.HealthServicer, server: grpc.Server, service: str, health_check_interval: int
):
    # Checks the status of the server, the different server are: STARTED, STOPPED, AND GRACE
    if server._state.stage == grpc._server._ServerStage.STARTED:
        status = health_pb2.HealthCheckResponse.SERVING
    else:
        status = health_pb2.HealthCheckResponse.NOT_SERVING

    health_servicer.set(service, status)
    Timer(
        health_check_interval, lambda: _check_server_health(health_servicer, server, service, health_check_interval)
    ).start()


class TrackingThreadPoolExecutor(futures.ThreadPoolExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._busy_count = 0
        self._lock = Lock()

    def submit(self, *args, **kwargs):
        with self._lock:
            self._busy_count += 1
        future = super().submit(*args, **kwargs)
        future.add_done_callback(self._task_done)
        return future

    def _task_done(self, _):
        with self._lock:
            self._busy_count -= 1

    @property
    def busy_count(self):
        with self._lock:
            return self._busy_count


def calculate_optimal_workers(multiplier: int = 1) -> int:
    """
    Calculate the optimal number of workers based on CPU cores and memory available on the system.
    The actual number of workers is determined as optimal_workers * multiplier, where multiplier is a configurable parameter.
    This approach ensures that the system can handle both CPU-bound and I/O-bound tasks efficiently.
    I/O operations often involve waiting (e.g., for disk or network responses), so having additional threads beyond the CPU-optimal count
    allows the system to remain productive during these wait times, thereby improving overall throughput.
    """

    # Get CPU count
    cpu_count = psutil.cpu_count(logical=True)  # Use logical=True to count hyperthreads

    # Get total memory
    total_memory = psutil.virtual_memory().total
    memory_gb = total_memory / (1024**3)  # Convert bytes to GB

    # Base number of workers on CPU cores
    cpu_based_value = cpu_count + 1  # CPU cores + 1 for I/O operations

    # Memory-based calculation: Assume 512MB per worker
    memory_based_value = int(memory_gb * 2)

    # Take the minimum of CPU-based and memory-based calculations
    optimal_workers = min(cpu_based_value, memory_based_value)
    return optimal_workers * multiplier


def calculate_max_concurrent_rpcs(max_workers: int, multiplier: int = 1) -> int:
    """
    Calculate the maximum number of concurrent RPCs based on the number of workers and a configurable multiplier.
    The actual number of concurrent RPCs is determined as max_workers * multiplier.
    This approach ensures that grPC can queue a limited number of additional requests beyond the number of workers.
    The multiplier must be set cautiously to avoid performance degradation due to excessive queuing.
    """
    return max_workers * multiplier


# Configuration constants moved to TransformServer.__init__ for better testability


def calculate_per_process_resource_limits(num_workers: int) -> Dict[str, int]:
    """Calculate memory limits per worker process.

    Checks for TRANSFORM_SERVER_MEMORY_LIMIT_MB environment variable first.
    If not set, divides available system resources among workers, leaving buffer for other processes.
    """
    # Check if user has overridden memory limit
    memory_limit_override = os.environ.get("TRANSFORM_SERVER_MEMORY_LIMIT_MB")
    if memory_limit_override:
        try:
            memory_per_worker_mb = int(memory_limit_override)
            logger.info(
                f"Using environment variable override: {memory_per_worker_mb}MB memory per worker "
                f"(workers: {num_workers})"
            )
            return {
                "memory_mb": memory_per_worker_mb,
            }
        except ValueError:
            logger.warning(
                f"Invalid TRANSFORM_SERVER_MEMORY_LIMIT_MB value: {memory_limit_override}. "
                f"Must be an integer. Falling back to automatic calculation."
            )

    # Get system resources for automatic calculation
    virtual_memory = psutil.virtual_memory()
    total_memory_bytes = virtual_memory.total
    available_memory_bytes = virtual_memory.available

    # Leave 25% buffer for the main process and other system activities
    usable_memory_bytes = int(available_memory_bytes * 0.75)

    # Divide memory among workers
    memory_per_worker_bytes = usable_memory_bytes // num_workers

    # Convert to MB for easier configuration
    memory_per_worker_mb = memory_per_worker_bytes // (1024 * 1024)

    logger.info(
        f"Resource limits per worker: {memory_per_worker_mb}MB memory "
        f"(total: {total_memory_bytes // (1024 * 1024)}MB, "
        f"available: {available_memory_bytes // (1024 * 1024)}MB, "
        f"workers: {num_workers})"
    )

    return {
        "memory_mb": memory_per_worker_mb,
    }


def worker_process_initializer(memory_limit_mb: int):
    """Initialize worker process with resource limits.

    Sets memory limits for the worker process to prevent individual processes
    from consuming too much memory and affecting other workers.
    """
    try:
        # Get current limits
        current_soft, current_hard = resource.getrlimit(resource.RLIMIT_AS)
        memory_limit_bytes = memory_limit_mb * 1024 * 1024
        current_hard_mb = current_hard // (1024 * 1024) if current_hard != -1 else "unlimited"

        # Only set limit if it's lower than current hard limit
        # If current limit is unlimited (-1), or our limit is lower, set it
        if current_hard == -1 or memory_limit_bytes < current_hard:
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit_bytes, memory_limit_bytes))
            logger.debug(f"Worker process initialized with {memory_limit_mb}MB memory limit")
        else:
            # Use the existing hard limit instead
            logger.debug(
                f"Worker process using existing limit of {current_hard_mb}MB (requested {memory_limit_mb}MB was too high)"
            )

    except (OSError, ValueError) as e:
        logger.debug(f"Could not set {memory_limit_mb}MB limit (current: {current_hard_mb}MB): {e}")


def main():
    log_filename = os.environ.get("TRANSFORM_SERVER_LOG_FILENAME")
    if log_filename is None:
        log_filename = tempfile.NamedTemporaryFile(prefix="transform_server_").name
        print(f"TRANSFORM_SERVER_LOG_DIR not set. Logging to {log_filename}")

    disable_console_logging = os.environ.get("TRANSFORM_SERVER_DISABLE_CONSOLE_LOGGING", "false") == "true"
    metrics_reporting_enabled = os.environ.get("TRANSFORM_SERVER_METRICS_REPORTING_ENABLED", "false") == "true"
    timing_historgam_enabled = os.environ.get("TRANSFORM_SERVER_TIMING_HISTOGRAM_ENABLED", "true") == "true"
    log_level = os.environ.get("TRANSFORM_SERVER_LOG_LEVEL", "INFO")
    prometheus_metrics_port = os.environ.get("TRANSFORM_SERVER_PROMETHEUS_METRICS_PORT", "50052")

    interceptors = []
    if metrics_reporting_enabled:
        start_http_server(int(prometheus_metrics_port))
        interceptors.append(PromServerInterceptor(enable_handling_time_histogram=timing_historgam_enabled))
    logging.basicConfig(
        filename=log_filename,
        level=logging.getLevelName(log_level),
        format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    if not disable_console_logging:
        console = logging.StreamHandler()
        console.setLevel(logging.getLevelName(log_level))
        # set a format which is simpler for console use
        formatter = logging.Formatter("[%(asctime)s] %(name)-12s: %(levelname)-8s %(message)s")
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger("").addHandler(console)

    if "TRANSFORM_SERVER_SOCKET" not in os.environ and "TRANSFORM_SERVER_ADDRESS" not in os.environ:
        listen = "[::]:50051"
        logger.warning(
            "Neither TRANSFORM_SERVER_SOCKET nor TRANSFORM_SERVER_ADDRESS set in the environment. Using default port 50051."
        )
    elif "TRANSFORM_SERVER_SOCKET" in os.environ:
        socket = pathlib.Path(os.environ["TRANSFORM_SERVER_SOCKET"])
        assert not socket.exists(), "TRANSFORM_SERVER_SOCKET points to an existing socket"
        listen = f"unix:/{socket.absolute()}"
    elif "TRANSFORM_SERVER_ADDRESS" in os.environ and os.environ["TRANSFORM_SERVER_ADDRESS"].isdigit():
        listen = f"[::]:{os.environ['TRANSFORM_SERVER_ADDRESS']}"
    else:
        listen = os.environ["TRANSFORM_SERVER_ADDRESS"]

    options = []
    # Set the maximum size of a request the server can receive from the client. Defaults to 4MB.
    max_recv_length = os.environ.get("MAX_TRANSFORM_SERVICE_REQUEST_SIZE_BYTES", None)
    if max_recv_length is not None:
        options.append(("grpc.max_receive_message_length", int(max_recv_length)))

    logger.info(f"Python server starting at {listen}")

    transform_server_groups_enabled = os.environ.get("TRANSFORM_SERVER_GROUPS_ENABLED", "false") == "true"
    logger.info(f"Transform Server Groups Enabled: {transform_server_groups_enabled}")
    multiprocessing_requested = os.environ.get("TRANSFORM_SERVER_ENABLE_MULTIPROCESSING", "false") == "true"
    logger.info(f"Transform Server Multiprocessing Requested: {multiprocessing_requested}")
    logger.info(f"TRANSFORM_SERVER_MAX_WORKERS: {os.environ.get('TRANSFORM_SERVER_MAX_WORKERS', 'auto')}")
    logger.info(
        f"TRANSFORM_SERVER_MAX_CONCURRENT_RPCS: {os.environ.get('TRANSFORM_SERVER_MAX_CONCURRENT_RPCS', 'auto')}"
    )
    logger.info(
        f"TRANSFORM_SERVER_MULTIPROCESSING_MAX_WORKERS: {os.environ.get('TRANSFORM_SERVER_MULTIPROCESSING_MAX_WORKERS', 'auto')}"
    )
    if transform_server_groups_enabled:
        max_workers_multiplier = int(os.environ.get("TRANSFORM_SERVER_MAX_WORKERS_MULTIPLIER", 1))
        max_workers = os.environ.get(
            "TRANSFORM_SERVER_MAX_WORKERS", calculate_optimal_workers(multiplier=max_workers_multiplier)
        )
        max_concurrent_rpcs_multiplier = int(os.environ.get("TRANSFORM_SERVER_MAX_CONCURRENT_RPCS_MULTIPLIER", 1))
        max_concurrent_rpcs = os.environ.get(
            "TRANSFORM_SERVER_MAX_CONCURRENT_RPCS",
            calculate_max_concurrent_rpcs(max_workers, max_concurrent_rpcs_multiplier),
        )
        try:
            max_workers = int(max_workers)
            logger.info(f"Using max_workers: {max_workers}")
        except ValueError:
            max_workers = calculate_optimal_workers()
            logger.warning(f"Invalid TRANSFORM_SERVER_MAX_WORKERS value. Using default: {max_workers}")
    else:
        max_workers = int(os.environ.get("TRANSFORM_SERVER_MAX_WORKERS", "4"))
        max_concurrent_rpcs = os.environ.get("TRANSFORM_SERVER_MAX_CONCURRENT_RPCS", None)

    grpc_threadpool = (
        TrackingThreadPoolExecutor(max_workers=max_workers)
        if transform_server_groups_enabled
        else futures.ThreadPoolExecutor(max_workers=max_workers)
    )
    server = grpc.server(
        grpc_threadpool,
        options=options,
        interceptors=interceptors,
        maximum_concurrent_rpcs=max_concurrent_rpcs,
    )
    server.add_insecure_port(listen)

    transformation_threadpool = futures.ThreadPoolExecutor(max_workers=max_workers)

    transform_service_pb2_grpc.add_TransformServiceServicer_to_server(
        TransformServer(transformation_threadpool), server
    )
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    SERVICE_NAMES = (
        transform_service_pb2.DESCRIPTOR.services_by_name["TransformService"].full_name,
        health_pb2.DESCRIPTOR.services_by_name["Health"].full_name,
        reflection.SERVICE_NAME,
    )

    tsg_name = os.environ.get("TRANSFORM_SERVER_GROUP_NAME", "default")

    if transform_server_groups_enabled:
        health_check_interval = int(os.environ.get("TRANSFORM_SERVER_HEALTH_STATUS_UPDATE_INTERVAL", "60"))
        metrics_reporting_frequency = int(os.environ.get("TRANSFORM_SERVER_METRICS_REPORTING_FREQUENCY", "60"))
        # alpha is the smoothing factor for the EMA Busy Percentage metric. It should be between 0 and 1.
        # A higher alpha will give more weight to recent data and react faster to changes,
        # while a lower value will give more weight to older data and provide a smoother metric.
        # Source: https://en.wikipedia.org/wiki/Exponential_smoothing
        ema_metric_alpha = float(os.environ.get("TRANSFORM_SERVER_UTILIZATION_EMA_METRIC_ALPHA", "0.3"))

        def report_metrics(system_metrics_reporting_enabled=False, ema_alpha=0.3):
            while True:
                statsd_client = StatsClient("host.docker.internal", 8125)
                ema_busy_percentage = None
                # Threadpool Utilization Metrics
                busy_rpcs = grpc_threadpool.busy_count
                busy_percentage = (busy_rpcs / max_concurrent_rpcs) * 100
                if ema_busy_percentage is None:
                    ema_busy_percentage = busy_percentage
                else:
                    ema_busy_percentage = (ema_alpha * busy_percentage) + (1 - ema_alpha) * ema_busy_percentage
                statsd_client.gauge("transform_server.busy_percentage", ema_busy_percentage)

                if system_metrics_reporting_enabled:
                    # Threadpool Utilization Metrics
                    total_threads_gauge.labels(group_name=tsg_name).set(max_workers)
                    total_rpcs_gauge.labels(group_name=tsg_name).set(max_concurrent_rpcs)
                    busy_rpcs_gauge.labels(group_name=tsg_name).set(busy_rpcs)
                    concurrent_request_utilization_gauge.labels(group_name=tsg_name).set(busy_percentage)

                    # Memory Utilization Metrics
                    memory = psutil.virtual_memory()
                    memory_usage_gauge.labels(group_name=tsg_name).set(memory.percent)
                    memory_total_gauge.labels(group_name=tsg_name).set(memory.total)
                    memory_available_gauge.labels(group_name=tsg_name).set(memory.available)

                    # Swap Memory Utilization Metrics
                    swap_memory = psutil.swap_memory()
                    swap_memory_usage_gauge.labels(group_name=tsg_name).set(swap_memory.percent)
                    swap_memory_used_gauge.labels(group_name=tsg_name).set(swap_memory.used)

                    # Disk Utilization Metrics
                    disk = psutil.disk_usage("/")
                    disk_usage_gauge.labels(group_name=tsg_name).set(disk.percent)
                    disk_total_gauge.labels(group_name=tsg_name).set(disk.total)
                    disk_free_gauge.labels(group_name=tsg_name).set(disk.free)

                    # Process Count
                    process_count = len(psutil.pids())
                    process_count_gauge.labels(group_name=tsg_name).set(process_count)

                    # CPU Utilization Metrics
                    cpu_usage = psutil.cpu_percent(interval=1)
                    cpu_usage_gauge.labels(group_name=tsg_name).set(cpu_usage)
                    total_cores = psutil.cpu_count(logical=False)
                    total_cores_gauge.labels(group_name=tsg_name).set(total_cores)

                sleep(metrics_reporting_frequency)

        _check_server_health(
            health_servicer,
            server,
            transform_service_pb2.DESCRIPTOR.services_by_name["TransformService"].full_name,
            health_check_interval,
        )

        metrics_thread = Thread(target=report_metrics, args=(metrics_reporting_enabled, ema_metric_alpha), daemon=True)
        metrics_thread.start()

    reflection.enable_server_reflection(SERVICE_NAMES, server)

    server.start()
    logger.info("Python server started")
    realtime_logging_enabled = os.environ.get("TRANSFORM_SERVER_ENABLE_REALTIME_LOGGING", "false") == "true"
    logger.info(f"Realtime Logging Enabled: {realtime_logging_enabled}")
    if realtime_logging_enabled:
        asynclogger = AsyncLogger()
        sys.stdout = JSONStdoutWrapper(asynclogger)
    server.wait_for_termination()


def _post_processor_pipeline(post_processor: transform_service_pb2.TransformationOperation):
    pipeline = Pipeline()
    pipeline.root.transformation_node.transformation_id.CopyFrom(post_processor.transformation_id)
    input = pipeline.root.transformation_node.inputs.add()
    input.arg_name = _get_param_name_for_function(post_processor)
    input.node.data_source_node.virtual_data_source_id.CopyFrom(post_processor.transformation_id)
    return pipeline


def _get_param_name_for_function(post_processor):
    parsed_ast = ast.parse(post_processor.user_defined_function.body)
    input_name = next(node.args.args[0].arg for node in ast.walk(parsed_ast) if isinstance(node, ast.FunctionDef))
    return input_name


if __name__ == "__main__":
    main()
