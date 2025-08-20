from com.terraquantum.experiment.v1.experimentrun.algorithm import shared_pb2 as _shared_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import generic_algo_pb2 as _generic_algo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RoutingInputsProto(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _shared_pb2.DatasetStorageInfoProto
    def __init__(self, data: _Optional[_Union[_shared_pb2.DatasetStorageInfoProto, _Mapping]] = ...) -> None: ...

class RoutingOutputsProto(_message.Message):
    __slots__ = ("solution",)
    SOLUTION_FIELD_NUMBER: _ClassVar[int]
    solution: _shared_pb2.DatasetStorageInfoProto
    def __init__(self, solution: _Optional[_Union[_shared_pb2.DatasetStorageInfoProto, _Mapping]] = ...) -> None: ...

class RoutingMetadataProto(_message.Message):
    __slots__ = ("parameters", "inputs")
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    parameters: _generic_algo_pb2.GenericParametersProto
    inputs: RoutingInputsProto
    def __init__(self, parameters: _Optional[_Union[_generic_algo_pb2.GenericParametersProto, _Mapping]] = ..., inputs: _Optional[_Union[RoutingInputsProto, _Mapping]] = ...) -> None: ...

class RoutingOutcomeProto(_message.Message):
    __slots__ = ("result", "outputs")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    result: _generic_algo_pb2.GenericResultProto
    outputs: RoutingOutputsProto
    def __init__(self, result: _Optional[_Union[_generic_algo_pb2.GenericResultProto, _Mapping]] = ..., outputs: _Optional[_Union[RoutingOutputsProto, _Mapping]] = ...) -> None: ...
