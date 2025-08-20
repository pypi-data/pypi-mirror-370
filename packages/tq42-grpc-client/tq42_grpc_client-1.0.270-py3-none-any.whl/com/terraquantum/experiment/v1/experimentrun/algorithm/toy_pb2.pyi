from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ToyParametersProto(_message.Message):
    __slots__ = ("n", "r", "msg")
    N_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    n: int
    r: float
    msg: str
    def __init__(self, n: _Optional[int] = ..., r: _Optional[float] = ..., msg: _Optional[str] = ...) -> None: ...

class ToyInputsProto(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ToyMetadataProto(_message.Message):
    __slots__ = ("parameters", "inputs")
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    parameters: ToyParametersProto
    inputs: ToyInputsProto
    def __init__(self, parameters: _Optional[_Union[ToyParametersProto, _Mapping]] = ..., inputs: _Optional[_Union[ToyInputsProto, _Mapping]] = ...) -> None: ...

class ToyResultProto(_message.Message):
    __slots__ = ("y", "msg", "version")
    Y_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    y: _containers.RepeatedScalarFieldContainer[int]
    msg: str
    version: str
    def __init__(self, y: _Optional[_Iterable[int]] = ..., msg: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class ToyOutputsProto(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ToyOutcomeProto(_message.Message):
    __slots__ = ("result", "outputs")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    result: ToyResultProto
    outputs: ToyOutputsProto
    def __init__(self, result: _Optional[_Union[ToyResultProto, _Mapping]] = ..., outputs: _Optional[_Union[ToyOutputsProto, _Mapping]] = ...) -> None: ...
