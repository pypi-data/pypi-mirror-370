from com.terraquantum.experiment.v1.experimentrun.algorithm import ml_shared_pb2 as _ml_shared_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TSLSTMTrainParametersProto(_message.Message):
    __slots__ = ("input_width", "label_width", "hidden_size", "dropout_coef", "num_epochs", "batch_size", "learning_rate", "optim", "loss_func", "train_model_info", "time_column", "target_column")
    INPUT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    LABEL_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HIDDEN_SIZE_FIELD_NUMBER: _ClassVar[int]
    DROPOUT_COEF_FIELD_NUMBER: _ClassVar[int]
    NUM_EPOCHS_FIELD_NUMBER: _ClassVar[int]
    BATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    LEARNING_RATE_FIELD_NUMBER: _ClassVar[int]
    OPTIM_FIELD_NUMBER: _ClassVar[int]
    LOSS_FUNC_FIELD_NUMBER: _ClassVar[int]
    TRAIN_MODEL_INFO_FIELD_NUMBER: _ClassVar[int]
    TIME_COLUMN_FIELD_NUMBER: _ClassVar[int]
    TARGET_COLUMN_FIELD_NUMBER: _ClassVar[int]
    input_width: int
    label_width: int
    hidden_size: int
    dropout_coef: float
    num_epochs: int
    batch_size: int
    learning_rate: float
    optim: _ml_shared_pb2.OptimProto
    loss_func: _ml_shared_pb2.LossFuncProto
    train_model_info: _ml_shared_pb2.TrainModelInfoProto
    time_column: str
    target_column: str
    def __init__(self, input_width: _Optional[int] = ..., label_width: _Optional[int] = ..., hidden_size: _Optional[int] = ..., dropout_coef: _Optional[float] = ..., num_epochs: _Optional[int] = ..., batch_size: _Optional[int] = ..., learning_rate: _Optional[float] = ..., optim: _Optional[_Union[_ml_shared_pb2.OptimProto, str]] = ..., loss_func: _Optional[_Union[_ml_shared_pb2.LossFuncProto, str]] = ..., train_model_info: _Optional[_Union[_ml_shared_pb2.TrainModelInfoProto, _Mapping]] = ..., time_column: _Optional[str] = ..., target_column: _Optional[str] = ...) -> None: ...

class TSLSTMTrainMetadataProto(_message.Message):
    __slots__ = ("parameters", "inputs")
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    parameters: TSLSTMTrainParametersProto
    inputs: _ml_shared_pb2.MLTrainInputsProto
    def __init__(self, parameters: _Optional[_Union[TSLSTMTrainParametersProto, _Mapping]] = ..., inputs: _Optional[_Union[_ml_shared_pb2.MLTrainInputsProto, _Mapping]] = ...) -> None: ...

class TSLSTMTrainOutcomeProto(_message.Message):
    __slots__ = ("result", "outputs")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    result: _ml_shared_pb2.TSTrainResultProto
    outputs: _ml_shared_pb2.MLTrainOutputsProto
    def __init__(self, result: _Optional[_Union[_ml_shared_pb2.TSTrainResultProto, _Mapping]] = ..., outputs: _Optional[_Union[_ml_shared_pb2.MLTrainOutputsProto, _Mapping]] = ...) -> None: ...
