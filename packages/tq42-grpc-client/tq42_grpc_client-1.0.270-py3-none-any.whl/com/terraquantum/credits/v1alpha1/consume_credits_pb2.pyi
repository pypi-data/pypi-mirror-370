from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConsumeCreditsRequest(_message.Message):
    __slots__ = ("project_id", "created_at", "amount", "created_by", "entity_id")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    created_at: _timestamp_pb2.Timestamp
    amount: int
    created_by: str
    entity_id: str
    def __init__(self, project_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., amount: _Optional[int] = ..., created_by: _Optional[str] = ..., entity_id: _Optional[str] = ...) -> None: ...
