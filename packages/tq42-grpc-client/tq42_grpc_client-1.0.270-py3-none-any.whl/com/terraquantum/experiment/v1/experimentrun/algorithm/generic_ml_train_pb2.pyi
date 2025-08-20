from com.terraquantum.experiment.v1.experimentrun.algorithm import data_processing_shared_pb2 as _data_processing_shared_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import ml_shared_pb2 as _ml_shared_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import shared_pb2 as _shared_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import standard_pb2 as _standard_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import classical_dense_pb2 as _classical_dense_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import classical_lstm_pb2 as _classical_lstm_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import pqn_pb2 as _pqn_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import phn_pb2 as _phn_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import efq_pb2 as _efq_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import qdi_pb2 as _qdi_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import qlstm_pb2 as _qlstm_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import dhn_pb2 as _dhn_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import cphn_pb2 as _cphn_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import custom_quantum_layer_pb2 as _custom_quantum_layer_pb2
from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum import default_value_pb2 as _default_value_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MLModelType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ML_MODEL_TYPE_UNSPECIFIED: _ClassVar[MLModelType]
    MLP: _ClassVar[MLModelType]
    RNN: _ClassVar[MLModelType]
ML_MODEL_TYPE_UNSPECIFIED: MLModelType
MLP: MLModelType
RNN: MLModelType

class Layer(_message.Message):
    __slots__ = ("activation_function_layer", "dropout_layer", "batch_normalization_layer", "classical_dense_layer", "classical_lstm_layer", "phn_layer", "pqn_layer", "qdi_layer", "efq_layer", "qlstm_layer", "dhn_layer", "cphn_layer", "custom_quantum_layer")
    ACTIVATION_FUNCTION_LAYER_FIELD_NUMBER: _ClassVar[int]
    DROPOUT_LAYER_FIELD_NUMBER: _ClassVar[int]
    BATCH_NORMALIZATION_LAYER_FIELD_NUMBER: _ClassVar[int]
    CLASSICAL_DENSE_LAYER_FIELD_NUMBER: _ClassVar[int]
    CLASSICAL_LSTM_LAYER_FIELD_NUMBER: _ClassVar[int]
    PHN_LAYER_FIELD_NUMBER: _ClassVar[int]
    PQN_LAYER_FIELD_NUMBER: _ClassVar[int]
    QDI_LAYER_FIELD_NUMBER: _ClassVar[int]
    EFQ_LAYER_FIELD_NUMBER: _ClassVar[int]
    QLSTM_LAYER_FIELD_NUMBER: _ClassVar[int]
    DHN_LAYER_FIELD_NUMBER: _ClassVar[int]
    CPHN_LAYER_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_QUANTUM_LAYER_FIELD_NUMBER: _ClassVar[int]
    activation_function_layer: _standard_pb2.ActivationFunctionLayer
    dropout_layer: _standard_pb2.DropoutLayer
    batch_normalization_layer: _standard_pb2.BatchNormalizationLayer
    classical_dense_layer: _classical_dense_pb2.ClassicalDenseLayer
    classical_lstm_layer: _classical_lstm_pb2.ClassicalLSTMLayer
    phn_layer: _phn_pb2.PHNLayer
    pqn_layer: _pqn_pb2.PQNLayer
    qdi_layer: _qdi_pb2.QDILayer
    efq_layer: _efq_pb2.EFQLayer
    qlstm_layer: _qlstm_pb2.QLSTMLayer
    dhn_layer: _dhn_pb2.DHNLayer
    cphn_layer: _cphn_pb2.CPHNLayer
    custom_quantum_layer: _custom_quantum_layer_pb2.CustomQuantumLayer
    def __init__(self, activation_function_layer: _Optional[_Union[_standard_pb2.ActivationFunctionLayer, _Mapping]] = ..., dropout_layer: _Optional[_Union[_standard_pb2.DropoutLayer, _Mapping]] = ..., batch_normalization_layer: _Optional[_Union[_standard_pb2.BatchNormalizationLayer, _Mapping]] = ..., classical_dense_layer: _Optional[_Union[_classical_dense_pb2.ClassicalDenseLayer, _Mapping]] = ..., classical_lstm_layer: _Optional[_Union[_classical_lstm_pb2.ClassicalLSTMLayer, _Mapping]] = ..., phn_layer: _Optional[_Union[_phn_pb2.PHNLayer, _Mapping]] = ..., pqn_layer: _Optional[_Union[_pqn_pb2.PQNLayer, _Mapping]] = ..., qdi_layer: _Optional[_Union[_qdi_pb2.QDILayer, _Mapping]] = ..., efq_layer: _Optional[_Union[_efq_pb2.EFQLayer, _Mapping]] = ..., qlstm_layer: _Optional[_Union[_qlstm_pb2.QLSTMLayer, _Mapping]] = ..., dhn_layer: _Optional[_Union[_dhn_pb2.DHNLayer, _Mapping]] = ..., cphn_layer: _Optional[_Union[_cphn_pb2.CPHNLayer, _Mapping]] = ..., custom_quantum_layer: _Optional[_Union[_custom_quantum_layer_pb2.CustomQuantumLayer, _Mapping]] = ...) -> None: ...

class GenericMLTrainParametersProto(_message.Message):
    __slots__ = ("model_type", "layers", "num_epochs", "batch_size", "learning_rate", "optim", "loss_func", "train_model_info", "data_processing_parameters", "k_fold", "diff_method")
    MODEL_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAYERS_FIELD_NUMBER: _ClassVar[int]
    NUM_EPOCHS_FIELD_NUMBER: _ClassVar[int]
    BATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    LEARNING_RATE_FIELD_NUMBER: _ClassVar[int]
    OPTIM_FIELD_NUMBER: _ClassVar[int]
    LOSS_FUNC_FIELD_NUMBER: _ClassVar[int]
    TRAIN_MODEL_INFO_FIELD_NUMBER: _ClassVar[int]
    DATA_PROCESSING_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    K_FOLD_FIELD_NUMBER: _ClassVar[int]
    DIFF_METHOD_FIELD_NUMBER: _ClassVar[int]
    model_type: MLModelType
    layers: _containers.RepeatedCompositeFieldContainer[Layer]
    num_epochs: int
    batch_size: int
    learning_rate: float
    optim: _ml_shared_pb2.OptimProto
    loss_func: _ml_shared_pb2.LossFuncProto
    train_model_info: _ml_shared_pb2.TrainModelInfoProto
    data_processing_parameters: _data_processing_shared_pb2.TrainDataProcessingParametersProto
    k_fold: int
    diff_method: _shared_pb2.DiffMethodProto
    def __init__(self, model_type: _Optional[_Union[MLModelType, str]] = ..., layers: _Optional[_Iterable[_Union[Layer, _Mapping]]] = ..., num_epochs: _Optional[int] = ..., batch_size: _Optional[int] = ..., learning_rate: _Optional[float] = ..., optim: _Optional[_Union[_ml_shared_pb2.OptimProto, str]] = ..., loss_func: _Optional[_Union[_ml_shared_pb2.LossFuncProto, str]] = ..., train_model_info: _Optional[_Union[_ml_shared_pb2.TrainModelInfoProto, _Mapping]] = ..., data_processing_parameters: _Optional[_Union[_data_processing_shared_pb2.TrainDataProcessingParametersProto, _Mapping]] = ..., k_fold: _Optional[int] = ..., diff_method: _Optional[_Union[_shared_pb2.DiffMethodProto, str]] = ...) -> None: ...

class GenericMLTrainMetadataProto(_message.Message):
    __slots__ = ("parameters", "inputs")
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    parameters: GenericMLTrainParametersProto
    inputs: _ml_shared_pb2.MLTrainInputsProto
    def __init__(self, parameters: _Optional[_Union[GenericMLTrainParametersProto, _Mapping]] = ..., inputs: _Optional[_Union[_ml_shared_pb2.MLTrainInputsProto, _Mapping]] = ...) -> None: ...

class TrainingResults(_message.Message):
    __slots__ = ("train_losses", "test_losses", "train_metrics", "test_metrics")
    TRAIN_LOSSES_FIELD_NUMBER: _ClassVar[int]
    TEST_LOSSES_FIELD_NUMBER: _ClassVar[int]
    TRAIN_METRICS_FIELD_NUMBER: _ClassVar[int]
    TEST_METRICS_FIELD_NUMBER: _ClassVar[int]
    train_losses: _containers.RepeatedScalarFieldContainer[float]
    test_losses: _containers.RepeatedScalarFieldContainer[float]
    train_metrics: _ml_shared_pb2.Metrics
    test_metrics: _ml_shared_pb2.Metrics
    def __init__(self, train_losses: _Optional[_Iterable[float]] = ..., test_losses: _Optional[_Iterable[float]] = ..., train_metrics: _Optional[_Union[_ml_shared_pb2.Metrics, _Mapping]] = ..., test_metrics: _Optional[_Union[_ml_shared_pb2.Metrics, _Mapping]] = ...) -> None: ...

class GenericMLTrainResultProto(_message.Message):
    __slots__ = ("version", "output_scales", "input_scales", "results")
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
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    version: str
    output_scales: _containers.ScalarMap[str, float]
    input_scales: _containers.ScalarMap[str, float]
    results: _containers.RepeatedCompositeFieldContainer[TrainingResults]
    def __init__(self, version: _Optional[str] = ..., output_scales: _Optional[_Mapping[str, float]] = ..., input_scales: _Optional[_Mapping[str, float]] = ..., results: _Optional[_Iterable[_Union[TrainingResults, _Mapping]]] = ...) -> None: ...

class GenericMLTrainOutcomeProto(_message.Message):
    __slots__ = ("result", "outputs")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    result: GenericMLTrainResultProto
    outputs: _ml_shared_pb2.MLTrainOutputsProto
    def __init__(self, result: _Optional[_Union[GenericMLTrainResultProto, _Mapping]] = ..., outputs: _Optional[_Union[_ml_shared_pb2.MLTrainOutputsProto, _Mapping]] = ...) -> None: ...
