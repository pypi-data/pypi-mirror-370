from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import generic_algo_pb2 as _generic_algo_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OptimaxInputsProto(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class OptimaxOutputsProto(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class OptimaxMetadataProto(_message.Message):
    __slots__ = ("parameters", "inputs")
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    parameters: _generic_algo_pb2.GenericParametersProto
    inputs: OptimaxInputsProto
    def __init__(self, parameters: _Optional[_Union[_generic_algo_pb2.GenericParametersProto, _Mapping]] = ..., inputs: _Optional[_Union[OptimaxInputsProto, _Mapping]] = ...) -> None: ...

class OptimaxOutcomeProto(_message.Message):
    __slots__ = ("result", "outputs")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    result: _generic_algo_pb2.GenericResultProto
    outputs: OptimaxOutputsProto
    def __init__(self, result: _Optional[_Union[_generic_algo_pb2.GenericResultProto, _Mapping]] = ..., outputs: _Optional[_Union[OptimaxOutputsProto, _Mapping]] = ...) -> None: ...
