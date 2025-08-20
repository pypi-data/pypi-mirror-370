from com.terraquantum.storage.v1alpha1 import storage_pb2 as _storage_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateOutputStorageRequest(_message.Message):
    __slots__ = ("storage_id", "experiment_run_id", "project_id", "type", "created_by", "created_at", "storage_field_name")
    STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    STORAGE_FIELD_NAME_FIELD_NUMBER: _ClassVar[int]
    storage_id: str
    experiment_run_id: str
    project_id: str
    type: _storage_pb2.StorageType
    created_by: str
    created_at: _timestamp_pb2.Timestamp
    storage_field_name: str
    def __init__(self, storage_id: _Optional[str] = ..., experiment_run_id: _Optional[str] = ..., project_id: _Optional[str] = ..., type: _Optional[_Union[_storage_pb2.StorageType, str]] = ..., created_by: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., storage_field_name: _Optional[str] = ...) -> None: ...
