from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class TrainDataProcessingParametersProto(_message.Message):
    __slots__ = ("input_columns", "output_columns", "timestamp_columns")
    INPUT_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    input_columns: _containers.RepeatedScalarFieldContainer[int]
    output_columns: _containers.RepeatedScalarFieldContainer[int]
    timestamp_columns: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, input_columns: _Optional[_Iterable[int]] = ..., output_columns: _Optional[_Iterable[int]] = ..., timestamp_columns: _Optional[_Iterable[int]] = ...) -> None: ...

class InferDataProcessingParametersProto(_message.Message):
    __slots__ = ("input_columns", "timestamp_columns")
    INPUT_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    input_columns: _containers.RepeatedScalarFieldContainer[int]
    timestamp_columns: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, input_columns: _Optional[_Iterable[int]] = ..., timestamp_columns: _Optional[_Iterable[int]] = ...) -> None: ...
