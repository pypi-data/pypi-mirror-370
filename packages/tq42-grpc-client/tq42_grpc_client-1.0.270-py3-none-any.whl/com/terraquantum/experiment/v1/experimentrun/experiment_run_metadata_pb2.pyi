from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MeasurementModeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_MEASUREMENT_MODE: _ClassVar[MeasurementModeProto]
    EVEN: _ClassVar[MeasurementModeProto]
    SINGLE: _ClassVar[MeasurementModeProto]
    NONE: _ClassVar[MeasurementModeProto]

class MeasureProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_MEASURE: _ClassVar[MeasureProto]
    X: _ClassVar[MeasureProto]
    Y: _ClassVar[MeasureProto]
    Z: _ClassVar[MeasureProto]

class EntanglingProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_ENTANGLING: _ClassVar[EntanglingProto]
    BASIC: _ClassVar[EntanglingProto]
    STRONG: _ClassVar[EntanglingProto]

class DiffMethodProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_DIFF_METHOD: _ClassVar[DiffMethodProto]
    ADJOINT: _ClassVar[DiffMethodProto]
    PARAMETER_SHIFT: _ClassVar[DiffMethodProto]

class QubitTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_QUBIT_TYPE: _ClassVar[QubitTypeProto]
    LIGHTNING_QUBIT: _ClassVar[QubitTypeProto]

class ActFuncProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_ACT_FUNC: _ClassVar[ActFuncProto]
    RELU: _ClassVar[ActFuncProto]
    LEAKYRELU: _ClassVar[ActFuncProto]
    SIGMOID: _ClassVar[ActFuncProto]

class OptimProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_OPTIM: _ClassVar[OptimProto]
    ADAM: _ClassVar[OptimProto]
    ADAMW: _ClassVar[OptimProto]
    SGD: _ClassVar[OptimProto]

class LossFuncProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_LOSS_FUNC: _ClassVar[LossFuncProto]
    MSE: _ClassVar[LossFuncProto]
    MAE: _ClassVar[LossFuncProto]

class CvaOptAimProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_AIM: _ClassVar[CvaOptAimProto]
    MINIMIZE: _ClassVar[CvaOptAimProto]
    MAXIMIZE: _ClassVar[CvaOptAimProto]

class CircuitRunnerBackendProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_BACKEND: _ClassVar[CircuitRunnerBackendProto]
    IBM: _ClassVar[CircuitRunnerBackendProto]
    IONQ: _ClassVar[CircuitRunnerBackendProto]
UNKNOWN_MEASUREMENT_MODE: MeasurementModeProto
EVEN: MeasurementModeProto
SINGLE: MeasurementModeProto
NONE: MeasurementModeProto
UNKNOWN_MEASURE: MeasureProto
X: MeasureProto
Y: MeasureProto
Z: MeasureProto
UNKNOWN_ENTANGLING: EntanglingProto
BASIC: EntanglingProto
STRONG: EntanglingProto
UNKNOWN_DIFF_METHOD: DiffMethodProto
ADJOINT: DiffMethodProto
PARAMETER_SHIFT: DiffMethodProto
UNKNOWN_QUBIT_TYPE: QubitTypeProto
LIGHTNING_QUBIT: QubitTypeProto
UNKNOWN_ACT_FUNC: ActFuncProto
RELU: ActFuncProto
LEAKYRELU: ActFuncProto
SIGMOID: ActFuncProto
UNKNOWN_OPTIM: OptimProto
ADAM: OptimProto
ADAMW: OptimProto
SGD: OptimProto
UNKNOWN_LOSS_FUNC: LossFuncProto
MSE: LossFuncProto
MAE: LossFuncProto
UNKNOWN_AIM: CvaOptAimProto
MINIMIZE: CvaOptAimProto
MAXIMIZE: CvaOptAimProto
UNKNOWN_BACKEND: CircuitRunnerBackendProto
IBM: CircuitRunnerBackendProto
IONQ: CircuitRunnerBackendProto

class ToyMetadataProto(_message.Message):
    __slots__ = ("n", "r", "msg")
    N_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    n: int
    r: float
    msg: str
    def __init__(self, n: _Optional[int] = ..., r: _Optional[float] = ..., msg: _Optional[str] = ...) -> None: ...

class TetraOptMetadataProto(_message.Message):
    __slots__ = ("dimensionality", "maximal_rank", "iteration_number", "quantization", "points_number", "tolerance", "lower_limits", "upper_limits", "grid", "objective_function")
    DIMENSIONALITY_FIELD_NUMBER: _ClassVar[int]
    MAXIMAL_RANK_FIELD_NUMBER: _ClassVar[int]
    ITERATION_NUMBER_FIELD_NUMBER: _ClassVar[int]
    QUANTIZATION_FIELD_NUMBER: _ClassVar[int]
    POINTS_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TOLERANCE_FIELD_NUMBER: _ClassVar[int]
    LOWER_LIMITS_FIELD_NUMBER: _ClassVar[int]
    UPPER_LIMITS_FIELD_NUMBER: _ClassVar[int]
    GRID_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVE_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    dimensionality: int
    maximal_rank: int
    iteration_number: int
    quantization: bool
    points_number: int
    tolerance: float
    lower_limits: _containers.RepeatedScalarFieldContainer[float]
    upper_limits: _containers.RepeatedScalarFieldContainer[float]
    grid: _containers.RepeatedScalarFieldContainer[int]
    objective_function: str
    def __init__(self, dimensionality: _Optional[int] = ..., maximal_rank: _Optional[int] = ..., iteration_number: _Optional[int] = ..., quantization: bool = ..., points_number: _Optional[int] = ..., tolerance: _Optional[float] = ..., lower_limits: _Optional[_Iterable[float]] = ..., upper_limits: _Optional[_Iterable[float]] = ..., grid: _Optional[_Iterable[int]] = ..., objective_function: _Optional[str] = ...) -> None: ...

class TSHQMLPTrainMetadataProto(_message.Message):
    __slots__ = ("input_width", "label_width", "hidden_size", "num_qubits", "depth", "measurement_mode", "rotation", "entangling", "measure", "diff_method", "qubit_type", "act_func", "dropout", "dropout_p", "bn", "num_epochs", "batch_size", "learning_rate", "optim", "loss_func")
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
    NUM_EPOCHS_FIELD_NUMBER: _ClassVar[int]
    BATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    LEARNING_RATE_FIELD_NUMBER: _ClassVar[int]
    OPTIM_FIELD_NUMBER: _ClassVar[int]
    LOSS_FUNC_FIELD_NUMBER: _ClassVar[int]
    input_width: int
    label_width: int
    hidden_size: int
    num_qubits: int
    depth: int
    measurement_mode: MeasurementModeProto
    rotation: MeasureProto
    entangling: EntanglingProto
    measure: MeasureProto
    diff_method: DiffMethodProto
    qubit_type: QubitTypeProto
    act_func: ActFuncProto
    dropout: bool
    dropout_p: float
    bn: bool
    num_epochs: int
    batch_size: int
    learning_rate: float
    optim: OptimProto
    loss_func: LossFuncProto
    def __init__(self, input_width: _Optional[int] = ..., label_width: _Optional[int] = ..., hidden_size: _Optional[int] = ..., num_qubits: _Optional[int] = ..., depth: _Optional[int] = ..., measurement_mode: _Optional[_Union[MeasurementModeProto, str]] = ..., rotation: _Optional[_Union[MeasureProto, str]] = ..., entangling: _Optional[_Union[EntanglingProto, str]] = ..., measure: _Optional[_Union[MeasureProto, str]] = ..., diff_method: _Optional[_Union[DiffMethodProto, str]] = ..., qubit_type: _Optional[_Union[QubitTypeProto, str]] = ..., act_func: _Optional[_Union[ActFuncProto, str]] = ..., dropout: bool = ..., dropout_p: _Optional[float] = ..., bn: bool = ..., num_epochs: _Optional[int] = ..., batch_size: _Optional[int] = ..., learning_rate: _Optional[float] = ..., optim: _Optional[_Union[OptimProto, str]] = ..., loss_func: _Optional[_Union[LossFuncProto, str]] = ...) -> None: ...

class TSHQMLPEvalMetadataProto(_message.Message):
    __slots__ = ("input_width", "label_width", "hidden_size", "num_qubits", "depth", "measurement_mode", "rotation", "entangling", "measure", "diff_method", "qubit_type", "act_func", "dropout", "dropout_p", "bn")
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
    input_width: int
    label_width: int
    hidden_size: int
    num_qubits: int
    depth: int
    measurement_mode: MeasurementModeProto
    rotation: MeasureProto
    entangling: EntanglingProto
    measure: MeasureProto
    diff_method: DiffMethodProto
    qubit_type: QubitTypeProto
    act_func: ActFuncProto
    dropout: bool
    dropout_p: float
    bn: bool
    def __init__(self, input_width: _Optional[int] = ..., label_width: _Optional[int] = ..., hidden_size: _Optional[int] = ..., num_qubits: _Optional[int] = ..., depth: _Optional[int] = ..., measurement_mode: _Optional[_Union[MeasurementModeProto, str]] = ..., rotation: _Optional[_Union[MeasureProto, str]] = ..., entangling: _Optional[_Union[EntanglingProto, str]] = ..., measure: _Optional[_Union[MeasureProto, str]] = ..., diff_method: _Optional[_Union[DiffMethodProto, str]] = ..., qubit_type: _Optional[_Union[QubitTypeProto, str]] = ..., act_func: _Optional[_Union[ActFuncProto, str]] = ..., dropout: bool = ..., dropout_p: _Optional[float] = ..., bn: bool = ...) -> None: ...

class TSHQLSTMTrainMetadataProto(_message.Message):
    __slots__ = ("input_width", "label_width", "hidden_size", "num_qubits", "depth", "n_qlayers", "dropout_coef", "num_epochs", "batch_size", "learning_rate", "optim", "loss_func")
    INPUT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    LABEL_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HIDDEN_SIZE_FIELD_NUMBER: _ClassVar[int]
    NUM_QUBITS_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    N_QLAYERS_FIELD_NUMBER: _ClassVar[int]
    DROPOUT_COEF_FIELD_NUMBER: _ClassVar[int]
    NUM_EPOCHS_FIELD_NUMBER: _ClassVar[int]
    BATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    LEARNING_RATE_FIELD_NUMBER: _ClassVar[int]
    OPTIM_FIELD_NUMBER: _ClassVar[int]
    LOSS_FUNC_FIELD_NUMBER: _ClassVar[int]
    input_width: int
    label_width: int
    hidden_size: int
    num_qubits: int
    depth: int
    n_qlayers: int
    dropout_coef: float
    num_epochs: int
    batch_size: int
    learning_rate: float
    optim: OptimProto
    loss_func: LossFuncProto
    def __init__(self, input_width: _Optional[int] = ..., label_width: _Optional[int] = ..., hidden_size: _Optional[int] = ..., num_qubits: _Optional[int] = ..., depth: _Optional[int] = ..., n_qlayers: _Optional[int] = ..., dropout_coef: _Optional[float] = ..., num_epochs: _Optional[int] = ..., batch_size: _Optional[int] = ..., learning_rate: _Optional[float] = ..., optim: _Optional[_Union[OptimProto, str]] = ..., loss_func: _Optional[_Union[LossFuncProto, str]] = ...) -> None: ...

class TSHQLSTMEvalMetadataProto(_message.Message):
    __slots__ = ("input_width", "label_width", "hidden_size", "num_qubits", "depth", "n_qlayers", "dropout_coef")
    INPUT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    LABEL_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HIDDEN_SIZE_FIELD_NUMBER: _ClassVar[int]
    NUM_QUBITS_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    N_QLAYERS_FIELD_NUMBER: _ClassVar[int]
    DROPOUT_COEF_FIELD_NUMBER: _ClassVar[int]
    input_width: int
    label_width: int
    hidden_size: int
    num_qubits: int
    depth: int
    n_qlayers: int
    dropout_coef: float
    def __init__(self, input_width: _Optional[int] = ..., label_width: _Optional[int] = ..., hidden_size: _Optional[int] = ..., num_qubits: _Optional[int] = ..., depth: _Optional[int] = ..., n_qlayers: _Optional[int] = ..., dropout_coef: _Optional[float] = ...) -> None: ...

class TSMLPTrainMetadataProto(_message.Message):
    __slots__ = ("input_width", "label_width", "dim_list", "act_func", "dropout", "dropout_p", "bn", "num_epochs", "batch_size", "learning_rate", "optim", "loss_func")
    INPUT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    LABEL_WIDTH_FIELD_NUMBER: _ClassVar[int]
    DIM_LIST_FIELD_NUMBER: _ClassVar[int]
    ACT_FUNC_FIELD_NUMBER: _ClassVar[int]
    DROPOUT_FIELD_NUMBER: _ClassVar[int]
    DROPOUT_P_FIELD_NUMBER: _ClassVar[int]
    BN_FIELD_NUMBER: _ClassVar[int]
    NUM_EPOCHS_FIELD_NUMBER: _ClassVar[int]
    BATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    LEARNING_RATE_FIELD_NUMBER: _ClassVar[int]
    OPTIM_FIELD_NUMBER: _ClassVar[int]
    LOSS_FUNC_FIELD_NUMBER: _ClassVar[int]
    input_width: int
    label_width: int
    dim_list: _containers.RepeatedScalarFieldContainer[int]
    act_func: ActFuncProto
    dropout: bool
    dropout_p: float
    bn: bool
    num_epochs: int
    batch_size: int
    learning_rate: float
    optim: OptimProto
    loss_func: LossFuncProto
    def __init__(self, input_width: _Optional[int] = ..., label_width: _Optional[int] = ..., dim_list: _Optional[_Iterable[int]] = ..., act_func: _Optional[_Union[ActFuncProto, str]] = ..., dropout: bool = ..., dropout_p: _Optional[float] = ..., bn: bool = ..., num_epochs: _Optional[int] = ..., batch_size: _Optional[int] = ..., learning_rate: _Optional[float] = ..., optim: _Optional[_Union[OptimProto, str]] = ..., loss_func: _Optional[_Union[LossFuncProto, str]] = ...) -> None: ...

class TSMLPEvalMetadataProto(_message.Message):
    __slots__ = ("input_width", "label_width", "dim_list", "act_func", "dropout", "dropout_p", "bn")
    INPUT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    LABEL_WIDTH_FIELD_NUMBER: _ClassVar[int]
    DIM_LIST_FIELD_NUMBER: _ClassVar[int]
    ACT_FUNC_FIELD_NUMBER: _ClassVar[int]
    DROPOUT_FIELD_NUMBER: _ClassVar[int]
    DROPOUT_P_FIELD_NUMBER: _ClassVar[int]
    BN_FIELD_NUMBER: _ClassVar[int]
    input_width: int
    label_width: int
    dim_list: _containers.RepeatedScalarFieldContainer[int]
    act_func: ActFuncProto
    dropout: bool
    dropout_p: float
    bn: bool
    def __init__(self, input_width: _Optional[int] = ..., label_width: _Optional[int] = ..., dim_list: _Optional[_Iterable[int]] = ..., act_func: _Optional[_Union[ActFuncProto, str]] = ..., dropout: bool = ..., dropout_p: _Optional[float] = ..., bn: bool = ...) -> None: ...

class TSLSTMTrainMetadataProto(_message.Message):
    __slots__ = ("input_width", "label_width", "hidden_size", "dropout_coef", "num_epochs", "batch_size", "learning_rate", "optim", "loss_func")
    INPUT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    LABEL_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HIDDEN_SIZE_FIELD_NUMBER: _ClassVar[int]
    DROPOUT_COEF_FIELD_NUMBER: _ClassVar[int]
    NUM_EPOCHS_FIELD_NUMBER: _ClassVar[int]
    BATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    LEARNING_RATE_FIELD_NUMBER: _ClassVar[int]
    OPTIM_FIELD_NUMBER: _ClassVar[int]
    LOSS_FUNC_FIELD_NUMBER: _ClassVar[int]
    input_width: int
    label_width: int
    hidden_size: int
    dropout_coef: float
    num_epochs: int
    batch_size: int
    learning_rate: float
    optim: OptimProto
    loss_func: LossFuncProto
    def __init__(self, input_width: _Optional[int] = ..., label_width: _Optional[int] = ..., hidden_size: _Optional[int] = ..., dropout_coef: _Optional[float] = ..., num_epochs: _Optional[int] = ..., batch_size: _Optional[int] = ..., learning_rate: _Optional[float] = ..., optim: _Optional[_Union[OptimProto, str]] = ..., loss_func: _Optional[_Union[LossFuncProto, str]] = ...) -> None: ...

class TSLSTMEvalMetadataProto(_message.Message):
    __slots__ = ("input_width", "label_width", "hidden_size", "dropout_coef")
    INPUT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    LABEL_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HIDDEN_SIZE_FIELD_NUMBER: _ClassVar[int]
    DROPOUT_COEF_FIELD_NUMBER: _ClassVar[int]
    input_width: int
    label_width: int
    hidden_size: int
    dropout_coef: float
    def __init__(self, input_width: _Optional[int] = ..., label_width: _Optional[int] = ..., hidden_size: _Optional[int] = ..., dropout_coef: _Optional[float] = ...) -> None: ...

class CvaOptMetadataProto(_message.Message):
    __slots__ = ("func_eval_worker_url", "objective_names", "objective_aims", "variable_names", "variable_lb", "variable_ub", "parameter_names", "parameter_values")
    FUNC_EVAL_WORKER_URL_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVE_NAMES_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVE_AIMS_FIELD_NUMBER: _ClassVar[int]
    VARIABLE_NAMES_FIELD_NUMBER: _ClassVar[int]
    VARIABLE_LB_FIELD_NUMBER: _ClassVar[int]
    VARIABLE_UB_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_NAMES_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_VALUES_FIELD_NUMBER: _ClassVar[int]
    func_eval_worker_url: str
    objective_names: _containers.RepeatedScalarFieldContainer[str]
    objective_aims: _containers.RepeatedScalarFieldContainer[CvaOptAimProto]
    variable_names: _containers.RepeatedScalarFieldContainer[str]
    variable_lb: _containers.RepeatedScalarFieldContainer[float]
    variable_ub: _containers.RepeatedScalarFieldContainer[float]
    parameter_names: _containers.RepeatedScalarFieldContainer[str]
    parameter_values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, func_eval_worker_url: _Optional[str] = ..., objective_names: _Optional[_Iterable[str]] = ..., objective_aims: _Optional[_Iterable[_Union[CvaOptAimProto, str]]] = ..., variable_names: _Optional[_Iterable[str]] = ..., variable_lb: _Optional[_Iterable[float]] = ..., variable_ub: _Optional[_Iterable[float]] = ..., parameter_names: _Optional[_Iterable[str]] = ..., parameter_values: _Optional[_Iterable[str]] = ...) -> None: ...

class TetraQuEncMetadataProto(_message.Message):
    __slots__ = ("circuit_type", "qubo", "number_layers", "steps", "velocity", "saved_circuit", "optimizer")
    CIRCUIT_TYPE_FIELD_NUMBER: _ClassVar[int]
    QUBO_FIELD_NUMBER: _ClassVar[int]
    NUMBER_LAYERS_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    VELOCITY_FIELD_NUMBER: _ClassVar[int]
    SAVED_CIRCUIT_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZER_FIELD_NUMBER: _ClassVar[int]
    circuit_type: str
    qubo: _containers.RepeatedScalarFieldContainer[float]
    number_layers: int
    steps: int
    velocity: float
    saved_circuit: bool
    optimizer: str
    def __init__(self, circuit_type: _Optional[str] = ..., qubo: _Optional[_Iterable[float]] = ..., number_layers: _Optional[int] = ..., steps: _Optional[int] = ..., velocity: _Optional[float] = ..., saved_circuit: bool = ..., optimizer: _Optional[str] = ...) -> None: ...

class CircuitRunMetadataProto(_message.Message):
    __slots__ = ("shots", "backend")
    SHOTS_FIELD_NUMBER: _ClassVar[int]
    BACKEND_FIELD_NUMBER: _ClassVar[int]
    shots: int
    backend: CircuitRunnerBackendProto
    def __init__(self, shots: _Optional[int] = ..., backend: _Optional[_Union[CircuitRunnerBackendProto, str]] = ...) -> None: ...
