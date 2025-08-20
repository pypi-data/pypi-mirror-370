from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ExportStorageRequest(_message.Message):
    __slots__ = ("storage_id",)
    STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    storage_id: str
    def __init__(self, storage_id: _Optional[str] = ...) -> None: ...

class ExportStorageResponse(_message.Message):
    __slots__ = ("signed_urls",)
    SIGNED_URLS_FIELD_NUMBER: _ClassVar[int]
    signed_urls: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, signed_urls: _Optional[_Iterable[str]] = ...) -> None: ...
