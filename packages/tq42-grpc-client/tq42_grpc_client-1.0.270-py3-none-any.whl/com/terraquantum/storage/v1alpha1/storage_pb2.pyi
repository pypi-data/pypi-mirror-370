from google.protobuf import timestamp_pb2 as _timestamp_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StorageType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STORAGE_TYPE_UNSPECIFIED: _ClassVar[StorageType]
    DATASET: _ClassVar[StorageType]
    MODEL: _ClassVar[StorageType]

class StorageStatusProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STORAGE_STATUS_UNSPECIFIED: _ClassVar[StorageStatusProto]
    PENDING: _ClassVar[StorageStatusProto]
    INITIALIZED: _ClassVar[StorageStatusProto]
    TRANSFERRING: _ClassVar[StorageStatusProto]
    FAILED: _ClassVar[StorageStatusProto]
    COMPLETED: _ClassVar[StorageStatusProto]
    PENDING_DELETION: _ClassVar[StorageStatusProto]
    DELETED: _ClassVar[StorageStatusProto]
    EMPTY: _ClassVar[StorageStatusProto]

class DatasetSensitivityProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DATASET_SENSITIVITY_UNSPECIFIED: _ClassVar[DatasetSensitivityProto]
    PUBLIC: _ClassVar[DatasetSensitivityProto]
    GENERAL: _ClassVar[DatasetSensitivityProto]
    SENSITIVE: _ClassVar[DatasetSensitivityProto]
    CONFIDENTIAL: _ClassVar[DatasetSensitivityProto]
STORAGE_TYPE_UNSPECIFIED: StorageType
DATASET: StorageType
MODEL: StorageType
STORAGE_STATUS_UNSPECIFIED: StorageStatusProto
PENDING: StorageStatusProto
INITIALIZED: StorageStatusProto
TRANSFERRING: StorageStatusProto
FAILED: StorageStatusProto
COMPLETED: StorageStatusProto
PENDING_DELETION: StorageStatusProto
DELETED: StorageStatusProto
EMPTY: StorageStatusProto
DATASET_SENSITIVITY_UNSPECIFIED: DatasetSensitivityProto
PUBLIC: DatasetSensitivityProto
GENERAL: DatasetSensitivityProto
SENSITIVE: DatasetSensitivityProto
CONFIDENTIAL: DatasetSensitivityProto

class StorageProto(_message.Message):
    __slots__ = ("id", "name", "description", "type", "project_id", "created_by", "status", "created_at", "deleted_at", "dataset_metadata", "model_metadata")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    DELETED_AT_FIELD_NUMBER: _ClassVar[int]
    DATASET_METADATA_FIELD_NUMBER: _ClassVar[int]
    MODEL_METADATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    type: StorageType
    project_id: str
    created_by: str
    status: StorageStatusProto
    created_at: _timestamp_pb2.Timestamp
    deleted_at: _timestamp_pb2.Timestamp
    dataset_metadata: DatasetMetadataProto
    model_metadata: ModelMetadataProto
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[StorageType, str]] = ..., project_id: _Optional[str] = ..., created_by: _Optional[str] = ..., status: _Optional[_Union[StorageStatusProto, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., deleted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., dataset_metadata: _Optional[_Union[DatasetMetadataProto, _Mapping]] = ..., model_metadata: _Optional[_Union[ModelMetadataProto, _Mapping]] = ...) -> None: ...

class DatasetMetadataProto(_message.Message):
    __slots__ = ("sensitivity",)
    SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    sensitivity: DatasetSensitivityProto
    def __init__(self, sensitivity: _Optional[_Union[DatasetSensitivityProto, str]] = ...) -> None: ...

class ModelMetadataProto(_message.Message):
    __slots__ = ("experiment_run_id",)
    EXPERIMENT_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    experiment_run_id: str
    def __init__(self, experiment_run_id: _Optional[str] = ...) -> None: ...
