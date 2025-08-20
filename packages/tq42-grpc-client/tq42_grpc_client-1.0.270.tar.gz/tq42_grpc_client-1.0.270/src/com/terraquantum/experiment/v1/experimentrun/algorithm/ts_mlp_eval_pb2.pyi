from com.terraquantum.experiment.v1.experimentrun.algorithm import ml_shared_pb2 as _ml_shared_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import shared_pb2 as _shared_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TSMLPEvalParametersProto(_message.Message):
    __slots__ = ("input_width", "label_width", "dim_list", "act_func", "dropout", "dropout_p", "bn", "time_column")
    INPUT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    LABEL_WIDTH_FIELD_NUMBER: _ClassVar[int]
    DIM_LIST_FIELD_NUMBER: _ClassVar[int]
    ACT_FUNC_FIELD_NUMBER: _ClassVar[int]
    DROPOUT_FIELD_NUMBER: _ClassVar[int]
    DROPOUT_P_FIELD_NUMBER: _ClassVar[int]
    BN_FIELD_NUMBER: _ClassVar[int]
    TIME_COLUMN_FIELD_NUMBER: _ClassVar[int]
    input_width: int
    label_width: int
    dim_list: _containers.RepeatedScalarFieldContainer[int]
    act_func: _shared_pb2.ActFuncProto
    dropout: bool
    dropout_p: float
    bn: bool
    time_column: str
    def __init__(self, input_width: _Optional[int] = ..., label_width: _Optional[int] = ..., dim_list: _Optional[_Iterable[int]] = ..., act_func: _Optional[_Union[_shared_pb2.ActFuncProto, str]] = ..., dropout: bool = ..., dropout_p: _Optional[float] = ..., bn: bool = ..., time_column: _Optional[str] = ...) -> None: ...

class TSMLPEvalMetadataProto(_message.Message):
    __slots__ = ("parameters", "inputs")
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    parameters: TSMLPEvalParametersProto
    inputs: _ml_shared_pb2.TSEvalInputsProto
    def __init__(self, parameters: _Optional[_Union[TSMLPEvalParametersProto, _Mapping]] = ..., inputs: _Optional[_Union[_ml_shared_pb2.TSEvalInputsProto, _Mapping]] = ...) -> None: ...

class TSMLPEvalOutcomeProto(_message.Message):
    __slots__ = ("result", "outputs")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    result: _ml_shared_pb2.TSEvalResultProto
    outputs: _ml_shared_pb2.TSEvalOutputsProto
    def __init__(self, result: _Optional[_Union[_ml_shared_pb2.TSEvalResultProto, _Mapping]] = ..., outputs: _Optional[_Union[_ml_shared_pb2.TSEvalOutputsProto, _Mapping]] = ...) -> None: ...
