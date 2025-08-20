from com.terraquantum.experiment.v1.experimentrun.algorithm import data_processing_shared_pb2 as _data_processing_shared_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import ml_shared_pb2 as _ml_shared_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GenericMLInferParametersProto(_message.Message):
    __slots__ = ("data_processing_parameters",)
    DATA_PROCESSING_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    data_processing_parameters: _data_processing_shared_pb2.InferDataProcessingParametersProto
    def __init__(self, data_processing_parameters: _Optional[_Union[_data_processing_shared_pb2.InferDataProcessingParametersProto, _Mapping]] = ...) -> None: ...

class GenericMLInferMetadataProto(_message.Message):
    __slots__ = ("parameters", "inputs")
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    parameters: GenericMLInferParametersProto
    inputs: _ml_shared_pb2.TSEvalInputsProto
    def __init__(self, parameters: _Optional[_Union[GenericMLInferParametersProto, _Mapping]] = ..., inputs: _Optional[_Union[_ml_shared_pb2.TSEvalInputsProto, _Mapping]] = ...) -> None: ...

class GenericMLInferResultProto(_message.Message):
    __slots__ = ("version", "output_scales", "input_scales")
    class OutputScalesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    class InputScalesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    VERSION_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_SCALES_FIELD_NUMBER: _ClassVar[int]
    INPUT_SCALES_FIELD_NUMBER: _ClassVar[int]
    version: str
    output_scales: _containers.ScalarMap[str, float]
    input_scales: _containers.ScalarMap[str, float]
    def __init__(self, version: _Optional[str] = ..., output_scales: _Optional[_Mapping[str, float]] = ..., input_scales: _Optional[_Mapping[str, float]] = ...) -> None: ...

class GenericMLInferOutcomeProto(_message.Message):
    __slots__ = ("result", "outputs")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    result: GenericMLInferResultProto
    outputs: _ml_shared_pb2.TSEvalOutputsProto
    def __init__(self, result: _Optional[_Union[GenericMLInferResultProto, _Mapping]] = ..., outputs: _Optional[_Union[_ml_shared_pb2.TSEvalOutputsProto, _Mapping]] = ...) -> None: ...
