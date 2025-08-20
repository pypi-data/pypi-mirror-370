from com.terraquantum.storage.v1alpha1 import storage_pb2 as _storage_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpdateStorageStatusRequest(_message.Message):
    __slots__ = ("storage_id", "status")
    STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    storage_id: str
    status: _storage_pb2.StorageStatusProto
    def __init__(self, storage_id: _Optional[str] = ..., status: _Optional[_Union[_storage_pb2.StorageStatusProto, str]] = ...) -> None: ...
