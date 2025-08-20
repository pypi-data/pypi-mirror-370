from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DomainEventProto(_message.Message):
    __slots__ = ("event_type", "entity", "entity_class", "trace_id", "span_id", "timestamp", "id")
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_CLASS_FIELD_NUMBER: _ClassVar[int]
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    SPAN_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    event_type: str
    entity: _any_pb2.Any
    entity_class: str
    trace_id: str
    span_id: str
    timestamp: _timestamp_pb2.Timestamp
    id: str
    def __init__(self, event_type: _Optional[str] = ..., entity: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., entity_class: _Optional[str] = ..., trace_id: _Optional[str] = ..., span_id: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., id: _Optional[str] = ...) -> None: ...
