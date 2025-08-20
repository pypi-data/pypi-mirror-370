from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChannelMessage(_message.Message):
    __slots__ = ("timestamp", "sequential_message_id", "acknowledge_data", "ask_data", "tell_data", "completion_data")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SEQUENTIAL_MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    ACKNOWLEDGE_DATA_FIELD_NUMBER: _ClassVar[int]
    ASK_DATA_FIELD_NUMBER: _ClassVar[int]
    TELL_DATA_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_DATA_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    sequential_message_id: int
    acknowledge_data: DataAcknowledge
    ask_data: Ask
    tell_data: Tell
    completion_data: Completion
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., sequential_message_id: _Optional[int] = ..., acknowledge_data: _Optional[_Union[DataAcknowledge, _Mapping]] = ..., ask_data: _Optional[_Union[Ask, _Mapping]] = ..., tell_data: _Optional[_Union[Tell, _Mapping]] = ..., completion_data: _Optional[_Union[Completion, _Mapping]] = ...) -> None: ...

class Completion(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DataAcknowledge(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class Parameter(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, values: _Optional[_Iterable[float]] = ...) -> None: ...

class Ask(_message.Message):
    __slots__ = ("parameters", "headers")
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    parameters: _containers.RepeatedCompositeFieldContainer[Parameter]
    headers: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, parameters: _Optional[_Iterable[_Union[Parameter, _Mapping]]] = ..., headers: _Optional[_Iterable[str]] = ...) -> None: ...

class Tell(_message.Message):
    __slots__ = ("parameters", "headers", "results", "candidates")
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    CANDIDATES_FIELD_NUMBER: _ClassVar[int]
    parameters: _containers.RepeatedCompositeFieldContainer[Parameter]
    headers: _containers.RepeatedScalarFieldContainer[str]
    results: _containers.RepeatedScalarFieldContainer[float]
    candidates: _containers.RepeatedCompositeFieldContainer[Parameter]
    def __init__(self, parameters: _Optional[_Iterable[_Union[Parameter, _Mapping]]] = ..., headers: _Optional[_Iterable[str]] = ..., results: _Optional[_Iterable[float]] = ..., candidates: _Optional[_Iterable[_Union[Parameter, _Mapping]]] = ...) -> None: ...
