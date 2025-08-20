from com.terraquantum.storage.v1alpha1 import storage_pb2 as _storage_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ValidateStorageRequest(_message.Message):
    __slots__ = ("storage_id", "project_id", "type")
    STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    storage_id: str
    project_id: str
    type: _storage_pb2.StorageType
    def __init__(self, storage_id: _Optional[str] = ..., project_id: _Optional[str] = ..., type: _Optional[_Union[_storage_pb2.StorageType, str]] = ...) -> None: ...
