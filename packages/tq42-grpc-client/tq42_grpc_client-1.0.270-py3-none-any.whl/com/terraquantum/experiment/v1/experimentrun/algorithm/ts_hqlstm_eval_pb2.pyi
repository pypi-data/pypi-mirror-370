from com.terraquantum.experiment.v1.experimentrun.algorithm import ml_shared_pb2 as _ml_shared_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TSHQLSTMEvalParametersProto(_message.Message):
    __slots__ = ("input_width", "label_width", "hidden_size", "num_qubits", "depth", "n_qlayers", "dropout_coef", "time_column")
    INPUT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    LABEL_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HIDDEN_SIZE_FIELD_NUMBER: _ClassVar[int]
    NUM_QUBITS_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    N_QLAYERS_FIELD_NUMBER: _ClassVar[int]
    DROPOUT_COEF_FIELD_NUMBER: _ClassVar[int]
    TIME_COLUMN_FIELD_NUMBER: _ClassVar[int]
    input_width: int
    label_width: int
    hidden_size: int
    num_qubits: int
    depth: int
    n_qlayers: int
    dropout_coef: float
    time_column: str
    def __init__(self, input_width: _Optional[int] = ..., label_width: _Optional[int] = ..., hidden_size: _Optional[int] = ..., num_qubits: _Optional[int] = ..., depth: _Optional[int] = ..., n_qlayers: _Optional[int] = ..., dropout_coef: _Optional[float] = ..., time_column: _Optional[str] = ...) -> None: ...

class TSHQLSTMEvalMetadataProto(_message.Message):
    __slots__ = ("parameters", "inputs")
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    parameters: TSHQLSTMEvalParametersProto
    inputs: _ml_shared_pb2.TSEvalInputsProto
    def __init__(self, parameters: _Optional[_Union[TSHQLSTMEvalParametersProto, _Mapping]] = ..., inputs: _Optional[_Union[_ml_shared_pb2.TSEvalInputsProto, _Mapping]] = ...) -> None: ...

class TSHQLSTMEvalOutcomeProto(_message.Message):
    __slots__ = ("result", "outputs")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    result: _ml_shared_pb2.TSEvalResultProto
    outputs: _ml_shared_pb2.TSEvalOutputsProto
    def __init__(self, result: _Optional[_Union[_ml_shared_pb2.TSEvalResultProto, _Mapping]] = ..., outputs: _Optional[_Union[_ml_shared_pb2.TSEvalOutputsProto, _Mapping]] = ...) -> None: ...
