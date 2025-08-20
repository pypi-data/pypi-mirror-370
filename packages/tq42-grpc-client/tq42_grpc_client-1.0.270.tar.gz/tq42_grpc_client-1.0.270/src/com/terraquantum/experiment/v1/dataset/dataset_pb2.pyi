from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DatasetStatusProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DATASET_STATUS_UNSPECIFIED: _ClassVar[DatasetStatusProto]
    PENDING: _ClassVar[DatasetStatusProto]
    BUCKET_CREATED: _ClassVar[DatasetStatusProto]
    BUCKET_FAILED: _ClassVar[DatasetStatusProto]
    TRANSFER_PROGRESS: _ClassVar[DatasetStatusProto]
    TRANSFER_COMPLETED: _ClassVar[DatasetStatusProto]
    TRANSFER_FAILED: _ClassVar[DatasetStatusProto]
    DATASET_CREATED: _ClassVar[DatasetStatusProto]

class DatasetSensitivityProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PUBLIC: _ClassVar[DatasetSensitivityProto]
    GENERAL: _ClassVar[DatasetSensitivityProto]
    SENSITIVE: _ClassVar[DatasetSensitivityProto]
    CONFIDENTIAL: _ClassVar[DatasetSensitivityProto]
DATASET_STATUS_UNSPECIFIED: DatasetStatusProto
PENDING: DatasetStatusProto
BUCKET_CREATED: DatasetStatusProto
BUCKET_FAILED: DatasetStatusProto
TRANSFER_PROGRESS: DatasetStatusProto
TRANSFER_COMPLETED: DatasetStatusProto
TRANSFER_FAILED: DatasetStatusProto
DATASET_CREATED: DatasetStatusProto
PUBLIC: DatasetSensitivityProto
GENERAL: DatasetSensitivityProto
SENSITIVE: DatasetSensitivityProto
CONFIDENTIAL: DatasetSensitivityProto

class DatasetProto(_message.Message):
    __slots__ = ("id", "name", "description", "created_at", "size", "status", "progress", "sensitivity", "created_by", "project_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    created_at: _timestamp_pb2.Timestamp
    size: int
    status: DatasetStatusProto
    progress: int
    sensitivity: DatasetSensitivityProto
    created_by: str
    project_id: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., size: _Optional[int] = ..., status: _Optional[_Union[DatasetStatusProto, str]] = ..., progress: _Optional[int] = ..., sensitivity: _Optional[_Union[DatasetSensitivityProto, str]] = ..., created_by: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...
