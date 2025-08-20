from com.terraquantum.experiment.v1.experimentrun.algorithm import ml_shared_pb2 as _ml_shared_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import shared_pb2 as _shared_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TSHQMLPEvalParametersProto(_message.Message):
    __slots__ = ("input_width", "label_width", "hidden_size", "num_qubits", "depth", "measurement_mode", "rotation", "entangling", "measure", "diff_method", "qubit_type", "act_func", "dropout", "dropout_p", "bn", "time_column")
    INPUT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    LABEL_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HIDDEN_SIZE_FIELD_NUMBER: _ClassVar[int]
    NUM_QUBITS_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    MEASUREMENT_MODE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    ENTANGLING_FIELD_NUMBER: _ClassVar[int]
    MEASURE_FIELD_NUMBER: _ClassVar[int]
    DIFF_METHOD_FIELD_NUMBER: _ClassVar[int]
    QUBIT_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACT_FUNC_FIELD_NUMBER: _ClassVar[int]
    DROPOUT_FIELD_NUMBER: _ClassVar[int]
    DROPOUT_P_FIELD_NUMBER: _ClassVar[int]
    BN_FIELD_NUMBER: _ClassVar[int]
    TIME_COLUMN_FIELD_NUMBER: _ClassVar[int]
    input_width: int
    label_width: int
    hidden_size: int
    num_qubits: int
    depth: int
    measurement_mode: _shared_pb2.MeasurementModeProto
    rotation: _shared_pb2.MeasureProto
    entangling: _shared_pb2.EntanglingProto
    measure: _shared_pb2.MeasureProto
    diff_method: _shared_pb2.DiffMethodProto
    qubit_type: _shared_pb2.QubitTypeProto
    act_func: _shared_pb2.ActFuncProto
    dropout: bool
    dropout_p: float
    bn: bool
    time_column: str
    def __init__(self, input_width: _Optional[int] = ..., label_width: _Optional[int] = ..., hidden_size: _Optional[int] = ..., num_qubits: _Optional[int] = ..., depth: _Optional[int] = ..., measurement_mode: _Optional[_Union[_shared_pb2.MeasurementModeProto, str]] = ..., rotation: _Optional[_Union[_shared_pb2.MeasureProto, str]] = ..., entangling: _Optional[_Union[_shared_pb2.EntanglingProto, str]] = ..., measure: _Optional[_Union[_shared_pb2.MeasureProto, str]] = ..., diff_method: _Optional[_Union[_shared_pb2.DiffMethodProto, str]] = ..., qubit_type: _Optional[_Union[_shared_pb2.QubitTypeProto, str]] = ..., act_func: _Optional[_Union[_shared_pb2.ActFuncProto, str]] = ..., dropout: bool = ..., dropout_p: _Optional[float] = ..., bn: bool = ..., time_column: _Optional[str] = ...) -> None: ...

class TSHQMLPEvalMetadataProto(_message.Message):
    __slots__ = ("parameters", "inputs")
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    parameters: TSHQMLPEvalParametersProto
    inputs: _ml_shared_pb2.TSEvalInputsProto
    def __init__(self, parameters: _Optional[_Union[TSHQMLPEvalParametersProto, _Mapping]] = ..., inputs: _Optional[_Union[_ml_shared_pb2.TSEvalInputsProto, _Mapping]] = ...) -> None: ...

class TSHQMLPEvalOutcomeProto(_message.Message):
    __slots__ = ("result", "outputs")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    result: _ml_shared_pb2.TSEvalResultProto
    outputs: _ml_shared_pb2.TSEvalOutputsProto
    def __init__(self, result: _Optional[_Union[_ml_shared_pb2.TSEvalResultProto, _Mapping]] = ..., outputs: _Optional[_Union[_ml_shared_pb2.TSEvalOutputsProto, _Mapping]] = ...) -> None: ...
