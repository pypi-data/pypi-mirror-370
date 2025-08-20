from com.terraquantum.storage.v1alpha1 import storage_pb2 as _storage_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetStorageCountRequest(_message.Message):
    __slots__ = ("project_id", "type")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    type: _storage_pb2.StorageType
    def __init__(self, project_id: _Optional[str] = ..., type: _Optional[_Union[_storage_pb2.StorageType, str]] = ...) -> None: ...

class GetStorageCountResponse(_message.Message):
    __slots__ = ("count",)
    COUNT_FIELD_NUMBER: _ClassVar[int]
    count: int
    def __init__(self, count: _Optional[int] = ...) -> None: ...
