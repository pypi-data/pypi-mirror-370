from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.args import transformation__client_pb2 as _transformation__client_pb2
from tecton_proto.args import user_defined_function__client_pb2 as _user_defined_function__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import secret__client_pb2 as _secret__client_pb2
from tecton_proto.data import resource_provider__client_pb2 as _resource_provider__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FeatureViewResourceProviderConfig(_message.Message):
    __slots__ = ["resource_providers_map"]
    class ResourceProvidersMapEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    RESOURCE_PROVIDERS_MAP_FIELD_NUMBER: _ClassVar[int]
    resource_providers_map: _containers.ScalarMap[str, str]
    def __init__(self, resource_providers_map: _Optional[_Mapping[str, str]] = ...) -> None: ...

class FeatureViewSecretConfig(_message.Message):
    __slots__ = ["secrets_map"]
    class SecretsMapEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _secret__client_pb2.SecretReference
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_secret__client_pb2.SecretReference, _Mapping]] = ...) -> None: ...
    SECRETS_MAP_FIELD_NUMBER: _ClassVar[int]
    secrets_map: _containers.MessageMap[str, _secret__client_pb2.SecretReference]
    def __init__(self, secrets_map: _Optional[_Mapping[str, _secret__client_pb2.SecretReference]] = ...) -> None: ...

class ResourceProviderMetadata(_message.Message):
    __slots__ = ["resource_provider", "secrets_last_updated"]
    RESOURCE_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    SECRETS_LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
    resource_provider: _resource_provider__client_pb2.ResourceProvider
    secrets_last_updated: _timestamp_pb2.Timestamp
    def __init__(self, resource_provider: _Optional[_Union[_resource_provider__client_pb2.ResourceProvider, _Mapping]] = ..., secrets_last_updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class SecretMetadata(_message.Message):
    __slots__ = ["last_updated", "secret_reference"]
    LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
    SECRET_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    last_updated: _timestamp_pb2.Timestamp
    secret_reference: _secret__client_pb2.SecretReference
    def __init__(self, secret_reference: _Optional[_Union[_secret__client_pb2.SecretReference, _Mapping]] = ..., last_updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TransformServerGroupConfiguration(_message.Message):
    __slots__ = ["computed_time", "resource_providers_config", "secrets_config", "server_group_id", "transformations", "workspace", "workspace_state_id"]
    COMPUTED_TIME_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_PROVIDERS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SECRETS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SERVER_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSFORMATIONS_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_STATE_ID_FIELD_NUMBER: _ClassVar[int]
    computed_time: _timestamp_pb2.Timestamp
    resource_providers_config: TransformServerResourceProviderConfig
    secrets_config: TransformServerGroupSecretsConfig
    server_group_id: str
    transformations: _containers.RepeatedCompositeFieldContainer[TransformationOperation]
    workspace: str
    workspace_state_id: str
    def __init__(self, server_group_id: _Optional[str] = ..., workspace: _Optional[str] = ..., workspace_state_id: _Optional[str] = ..., secrets_config: _Optional[_Union[TransformServerGroupSecretsConfig, _Mapping]] = ..., resource_providers_config: _Optional[_Union[TransformServerResourceProviderConfig, _Mapping]] = ..., transformations: _Optional[_Iterable[_Union[TransformationOperation, _Mapping]]] = ..., computed_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TransformServerGroupSecretsConfig(_message.Message):
    __slots__ = ["all_secrets_metadata", "feature_view_secret_references", "service_account_key_last_updated", "service_account_secret_name"]
    class FeatureViewSecretReferencesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: FeatureViewSecretConfig
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[FeatureViewSecretConfig, _Mapping]] = ...) -> None: ...
    ALL_SECRETS_METADATA_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_SECRET_REFERENCES_FIELD_NUMBER: _ClassVar[int]
    SERVICE_ACCOUNT_KEY_LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
    SERVICE_ACCOUNT_SECRET_NAME_FIELD_NUMBER: _ClassVar[int]
    all_secrets_metadata: _containers.RepeatedCompositeFieldContainer[SecretMetadata]
    feature_view_secret_references: _containers.MessageMap[str, FeatureViewSecretConfig]
    service_account_key_last_updated: _timestamp_pb2.Timestamp
    service_account_secret_name: str
    def __init__(self, service_account_secret_name: _Optional[str] = ..., service_account_key_last_updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., all_secrets_metadata: _Optional[_Iterable[_Union[SecretMetadata, _Mapping]]] = ..., feature_view_secret_references: _Optional[_Mapping[str, FeatureViewSecretConfig]] = ...) -> None: ...

class TransformServerResourceProviderConfig(_message.Message):
    __slots__ = ["all_resource_providers_metadata", "feature_view_resource_providers"]
    class FeatureViewResourceProvidersEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: FeatureViewResourceProviderConfig
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[FeatureViewResourceProviderConfig, _Mapping]] = ...) -> None: ...
    ALL_RESOURCE_PROVIDERS_METADATA_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_RESOURCE_PROVIDERS_FIELD_NUMBER: _ClassVar[int]
    all_resource_providers_metadata: _containers.RepeatedCompositeFieldContainer[ResourceProviderMetadata]
    feature_view_resource_providers: _containers.MessageMap[str, FeatureViewResourceProviderConfig]
    def __init__(self, feature_view_resource_providers: _Optional[_Mapping[str, FeatureViewResourceProviderConfig]] = ..., all_resource_providers_metadata: _Optional[_Iterable[_Union[ResourceProviderMetadata, _Mapping]]] = ...) -> None: ...

class TransformationOperation(_message.Message):
    __slots__ = ["is_post_processor_operation", "transformation_id", "transformation_mode", "user_defined_function"]
    IS_POST_PROCESSOR_OPERATION_FIELD_NUMBER: _ClassVar[int]
    TRANSFORMATION_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSFORMATION_MODE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    is_post_processor_operation: bool
    transformation_id: _id__client_pb2.Id
    transformation_mode: _transformation__client_pb2.TransformationMode
    user_defined_function: _user_defined_function__client_pb2.UserDefinedFunction
    def __init__(self, transformation_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., transformation_mode: _Optional[_Union[_transformation__client_pb2.TransformationMode, str]] = ..., user_defined_function: _Optional[_Union[_user_defined_function__client_pb2.UserDefinedFunction, _Mapping]] = ..., is_post_processor_operation: bool = ...) -> None: ...
