from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DeleteDatasetsRequest(_message.Message):
    __slots__ = ("ids", "request_id")
    IDS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ids: _containers.RepeatedScalarFieldContainer[str]
    request_id: str
    def __init__(self, ids: _Optional[_Iterable[str]] = ..., request_id: _Optional[str] = ...) -> None: ...
