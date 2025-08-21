import ast
import logging
from datetime import datetime
from types import FunctionType
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from readerwriterlock import rwlock

from tecton_core.id_helper import IdHelper
from tecton_proto.args.pipeline__client_pb2 import Pipeline
from tecton_proto.common.id__client_pb2 import Id
from tecton_proto.server_groups.transform_server_group_config__client_pb2 import TransformationOperation


logger = logging.getLogger(__name__)


class TransformServerException(Exception):
    def __init__(self, code: grpc.StatusCode, details: str):
        self.code = code
        self.details = details


class TransformationManager:
    """Manages the transformation functions and post processor pipelines for the transform server."""

    def __init__(self):
        self.transformations: Dict[str, FunctionType] = {}
        self.transformation_modes: Dict[str, Any] = {}
        self.rw_lock = rwlock.RWLockWrite()
        self.post_processor_pipelines: Dict[str, Pipeline] = {}
        self.transformation_status_map: Dict[str, str] = {}
        last_refresh_time: Optional[datetime] = None

    def refresh_transformation_cache(
        self, transformation_operations: List[TransformationOperation], config_last_updated_time: Timestamp
    ) -> None:
        """Refresh the transformation cache with new transformations."""
        new_transformations: Dict[str, FunctionType] = {}
        new_transformation_modes: Dict[str, Any] = {}
        new_post_processor_pipelines: Dict[str, Pipeline] = {}
        for transformation_op in transformation_operations:
            transformation_id = IdHelper.to_string(transformation_op.transformation_id)

            if transformation_id in self.transformations:
                new_transformations[transformation_id] = self.transformations[transformation_id]
                new_transformation_modes[transformation_id] = transformation_op.transformation_mode
            else:
                op_scope: Dict[str, Any] = {}
                name = transformation_op.user_defined_function.name
                try:
                    exec(transformation_op.user_defined_function.body, op_scope, op_scope)
                except Exception as e:
                    logger.warning(f"Error loading transformation {transformation_id}: {e}")
                    self.transformation_status_map[transformation_id] = str(e)

                new_transformations[transformation_id] = op_scope[name]
                new_transformation_modes[transformation_id] = transformation_op.transformation_mode
                logger.info(f"Successfully loaded transformation {transformation_id}")

            if transformation_op.is_post_processor_operation:
                new_post_processor_pipelines[transformation_id] = self._build_post_processor_pipeline(transformation_op)

        with self.rw_lock.gen_wlock():
            self.transformations = new_transformations
            self.transformation_modes = new_transformation_modes
            self.post_processor_pipelines = new_post_processor_pipelines
            self.last_refresh_time = config_last_updated_time.ToDatetime()

        logger.info("Successfully refreshed transformation cache. Last Updated Time: %s", {str(self.last_refresh_time)})

    def get_transformation(self, transformation_id: Id) -> Optional[Tuple[FunctionType, int]]:
        """Get the transformation function and mode for a given transformation ID."""
        transformation_id = IdHelper.to_string(transformation_id)
        if transformation_id in self.transformations:
            with self.rw_lock.gen_rlock():
                return self.transformations[transformation_id], int(self.transformation_modes[transformation_id])
        elif transformation_id in self.transformation_status_map:
            raise TransformServerException(
                grpc.StatusCode.INVALID_ARGUMENT, str(self.transformation_status_map[transformation_id])
            )
        return None

    def get_all_transformations(self) -> Dict[str, FunctionType]:
        """Get all transformations."""
        with self.rw_lock.gen_rlock():
            return self.transformations

    def get_all_transformation_modes(self) -> Dict[str, Any]:
        """Get all transformation modes."""
        with self.rw_lock.gen_rlock():
            return self.transformation_modes

    def get_post_processor_pipeline(self, transformation_id: Id) -> Optional[Pipeline]:
        """Get the post processor pipeline for a given transformation ID."""
        id = IdHelper.to_string(transformation_id)
        if id in self.post_processor_pipelines:
            with self.rw_lock.gen_rlock():
                return self.post_processor_pipelines[id]
        return None

    def _build_post_processor_pipeline(self, post_processor: TransformationOperation) -> Pipeline:
        """Build a pipeline for a post processor operation."""
        string_id = IdHelper.to_string(post_processor.transformation_id)
        pipeline = self.post_processor_pipelines.get(string_id)
        if pipeline:
            return pipeline

        pipeline = Pipeline()
        pipeline.root.transformation_node.transformation_id.CopyFrom(post_processor.transformation_id)
        input = pipeline.root.transformation_node.inputs.add()
        input.arg_name = self._get_param_name_for_function(post_processor)
        input.node.data_source_node.virtual_data_source_id.CopyFrom(post_processor.transformation_id)
        return pipeline

    def _get_param_name_for_function(self, post_processor):
        parsed_ast = ast.parse(post_processor.user_defined_function.body)
        input_name = next(node.args.args[0].arg for node in ast.walk(parsed_ast) if isinstance(node, ast.FunctionDef))
        return input_name
