from com.terraquantum.experiment.v1.experimentrun.algorithm import shared_pb2 as _shared_pb2
from com.terraquantum.experiment.v1.experimentrun import experiment_run_metadata_pb2 as _experiment_run_metadata_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import circuit_run_pb2 as _circuit_run_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import cva_opt_pb2 as _cva_opt_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import tetra_opt_pb2 as _tetra_opt_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import tetra_quenc_pb2 as _tetra_quenc_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import toy_pb2 as _toy_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import ts_hqlstm_eval_pb2 as _ts_hqlstm_eval_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import ts_hqlstm_train_pb2 as _ts_hqlstm_train_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import ts_hqmlp_eval_pb2 as _ts_hqmlp_eval_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import ts_hqmlp_train_pb2 as _ts_hqmlp_train_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import ts_lstm_eval_pb2 as _ts_lstm_eval_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import ts_lstm_train_pb2 as _ts_lstm_train_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import ts_mlp_eval_pb2 as _ts_mlp_eval_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import ts_mlp_train_pb2 as _ts_mlp_train_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import generic_ml_train_pb2 as _generic_ml_train_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import generic_ml_infer_pb2 as _generic_ml_infer_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import routing_pb2 as _routing_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import tq42_tqml_pb2 as _tq42_tqml_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import optimax_pb2 as _optimax_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExperimentRunStatusProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EXPERIMENT_RUN_STATUS_UNSPECIFIED: _ClassVar[ExperimentRunStatusProto]
    QUEUED: _ClassVar[ExperimentRunStatusProto]
    PENDING: _ClassVar[ExperimentRunStatusProto]
    RUNNING: _ClassVar[ExperimentRunStatusProto]
    CANCEL_PENDING: _ClassVar[ExperimentRunStatusProto]
    CANCELLED: _ClassVar[ExperimentRunStatusProto]
    COMPLETED: _ClassVar[ExperimentRunStatusProto]
    FAILED: _ClassVar[ExperimentRunStatusProto]

class HardwareProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HARDWARE_UNSPECIFIED: _ClassVar[HardwareProto]
    SMALL: _ClassVar[HardwareProto]
    LARGE: _ClassVar[HardwareProto]
    SMALL_GPU: _ClassVar[HardwareProto]
    LARGE_GPU: _ClassVar[HardwareProto]
EXPERIMENT_RUN_STATUS_UNSPECIFIED: ExperimentRunStatusProto
QUEUED: ExperimentRunStatusProto
PENDING: ExperimentRunStatusProto
RUNNING: ExperimentRunStatusProto
CANCEL_PENDING: ExperimentRunStatusProto
CANCELLED: ExperimentRunStatusProto
COMPLETED: ExperimentRunStatusProto
FAILED: ExperimentRunStatusProto
HARDWARE_UNSPECIFIED: HardwareProto
SMALL: HardwareProto
LARGE: HardwareProto
SMALL_GPU: HardwareProto
LARGE_GPU: HardwareProto

class ExperimentRunProto(_message.Message):
    __slots__ = ("id", "experiment_id", "status", "algorithm", "hardware", "tetra_opt_metadata", "toy_metadata", "ts_hqmlp_train_metadata", "ts_hqmlp_eval_metadata", "ts_hqlstm_train_metadata", "ts_hqlstm_eval_metadata", "cva_opt_metadata", "tetra_quenc_metadata", "ts_mlp_train_metadata", "ts_mlp_eval_metadata", "ts_lstm_train_metadata", "ts_lstm_eval_metadata", "circuit_run_metadata", "result", "error_message", "created_at", "started_at", "finished_at", "last_running_status", "created_by", "cancelled_by", "sequential_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    HARDWARE_FIELD_NUMBER: _ClassVar[int]
    TETRA_OPT_METADATA_FIELD_NUMBER: _ClassVar[int]
    TOY_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_HQMLP_TRAIN_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_HQMLP_EVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_HQLSTM_TRAIN_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_HQLSTM_EVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    CVA_OPT_METADATA_FIELD_NUMBER: _ClassVar[int]
    TETRA_QUENC_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_MLP_TRAIN_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_MLP_EVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_LSTM_TRAIN_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_LSTM_EVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    CIRCUIT_RUN_METADATA_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_RUNNING_STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_BY_FIELD_NUMBER: _ClassVar[int]
    SEQUENTIAL_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    experiment_id: str
    status: ExperimentRunStatusProto
    algorithm: _shared_pb2.AlgorithmProto
    hardware: HardwareProto
    tetra_opt_metadata: _experiment_run_metadata_pb2.TetraOptMetadataProto
    toy_metadata: _experiment_run_metadata_pb2.ToyMetadataProto
    ts_hqmlp_train_metadata: _experiment_run_metadata_pb2.TSHQMLPTrainMetadataProto
    ts_hqmlp_eval_metadata: _experiment_run_metadata_pb2.TSHQMLPEvalMetadataProto
    ts_hqlstm_train_metadata: _experiment_run_metadata_pb2.TSHQLSTMTrainMetadataProto
    ts_hqlstm_eval_metadata: _experiment_run_metadata_pb2.TSHQLSTMEvalMetadataProto
    cva_opt_metadata: _experiment_run_metadata_pb2.CvaOptMetadataProto
    tetra_quenc_metadata: _experiment_run_metadata_pb2.TetraQuEncMetadataProto
    ts_mlp_train_metadata: _experiment_run_metadata_pb2.TSMLPTrainMetadataProto
    ts_mlp_eval_metadata: _experiment_run_metadata_pb2.TSMLPEvalMetadataProto
    ts_lstm_train_metadata: _experiment_run_metadata_pb2.TSLSTMTrainMetadataProto
    ts_lstm_eval_metadata: _experiment_run_metadata_pb2.TSLSTMEvalMetadataProto
    circuit_run_metadata: _experiment_run_metadata_pb2.CircuitRunMetadataProto
    result: ExperimentRunResultProto
    error_message: str
    created_at: _timestamp_pb2.Timestamp
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    last_running_status: _timestamp_pb2.Timestamp
    created_by: str
    cancelled_by: str
    sequential_id: int
    def __init__(self, id: _Optional[str] = ..., experiment_id: _Optional[str] = ..., status: _Optional[_Union[ExperimentRunStatusProto, str]] = ..., algorithm: _Optional[_Union[_shared_pb2.AlgorithmProto, str]] = ..., hardware: _Optional[_Union[HardwareProto, str]] = ..., tetra_opt_metadata: _Optional[_Union[_experiment_run_metadata_pb2.TetraOptMetadataProto, _Mapping]] = ..., toy_metadata: _Optional[_Union[_experiment_run_metadata_pb2.ToyMetadataProto, _Mapping]] = ..., ts_hqmlp_train_metadata: _Optional[_Union[_experiment_run_metadata_pb2.TSHQMLPTrainMetadataProto, _Mapping]] = ..., ts_hqmlp_eval_metadata: _Optional[_Union[_experiment_run_metadata_pb2.TSHQMLPEvalMetadataProto, _Mapping]] = ..., ts_hqlstm_train_metadata: _Optional[_Union[_experiment_run_metadata_pb2.TSHQLSTMTrainMetadataProto, _Mapping]] = ..., ts_hqlstm_eval_metadata: _Optional[_Union[_experiment_run_metadata_pb2.TSHQLSTMEvalMetadataProto, _Mapping]] = ..., cva_opt_metadata: _Optional[_Union[_experiment_run_metadata_pb2.CvaOptMetadataProto, _Mapping]] = ..., tetra_quenc_metadata: _Optional[_Union[_experiment_run_metadata_pb2.TetraQuEncMetadataProto, _Mapping]] = ..., ts_mlp_train_metadata: _Optional[_Union[_experiment_run_metadata_pb2.TSMLPTrainMetadataProto, _Mapping]] = ..., ts_mlp_eval_metadata: _Optional[_Union[_experiment_run_metadata_pb2.TSMLPEvalMetadataProto, _Mapping]] = ..., ts_lstm_train_metadata: _Optional[_Union[_experiment_run_metadata_pb2.TSLSTMTrainMetadataProto, _Mapping]] = ..., ts_lstm_eval_metadata: _Optional[_Union[_experiment_run_metadata_pb2.TSLSTMEvalMetadataProto, _Mapping]] = ..., circuit_run_metadata: _Optional[_Union[_experiment_run_metadata_pb2.CircuitRunMetadataProto, _Mapping]] = ..., result: _Optional[_Union[ExperimentRunResultProto, _Mapping]] = ..., error_message: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_running_status: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_by: _Optional[str] = ..., cancelled_by: _Optional[str] = ..., sequential_id: _Optional[int] = ...) -> None: ...

class ExperimentRunNewStatus(_message.Message):
    __slots__ = ("experiment_run_id", "status", "timestamp", "result", "error_message")
    EXPERIMENT_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    experiment_run_id: str
    status: ExperimentRunStatusProto
    timestamp: _timestamp_pb2.Timestamp
    result: ExperimentRunResultProto
    error_message: str
    def __init__(self, experiment_run_id: _Optional[str] = ..., status: _Optional[_Union[ExperimentRunStatusProto, str]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., result: _Optional[_Union[ExperimentRunResultProto, _Mapping]] = ..., error_message: _Optional[str] = ...) -> None: ...

class ExperimentRunResultProto(_message.Message):
    __slots__ = ("result_json", "circuit_run_outcome", "cva_opt_outcome", "tetra_opt_outcome", "tetra_qu_enc_outcome", "toy_outcome", "ts_hqlstm_eval_outcome", "ts_hqlstm_train_outcome", "ts_hqmlp_eval_outcome", "ts_hqmlp_train_outcome", "ts_lstm_eval_outcome", "ts_lstm_train_outcome", "ts_mlp_eval_outcome", "ts_mlp_train_outcome", "generic_ml_train_outcome", "generic_ml_infer_outcome", "routing_outcome", "tqml_outcome", "optimax_outcome")
    RESULT_JSON_FIELD_NUMBER: _ClassVar[int]
    CIRCUIT_RUN_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    CVA_OPT_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    TETRA_OPT_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    TETRA_QU_ENC_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    TOY_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    TS_HQLSTM_EVAL_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    TS_HQLSTM_TRAIN_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    TS_HQMLP_EVAL_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    TS_HQMLP_TRAIN_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    TS_LSTM_EVAL_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    TS_LSTM_TRAIN_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    TS_MLP_EVAL_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    TS_MLP_TRAIN_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    GENERIC_ML_TRAIN_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    GENERIC_ML_INFER_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    ROUTING_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    TQML_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    OPTIMAX_OUTCOME_FIELD_NUMBER: _ClassVar[int]
    result_json: str
    circuit_run_outcome: _circuit_run_pb2.CircuitRunOutcomeProto
    cva_opt_outcome: _cva_opt_pb2.CvaOptOutcomeProto
    tetra_opt_outcome: _tetra_opt_pb2.TetraOptOutcomeProto
    tetra_qu_enc_outcome: _tetra_quenc_pb2.TetraQuEncOutcomeProto
    toy_outcome: _toy_pb2.ToyOutcomeProto
    ts_hqlstm_eval_outcome: _ts_hqlstm_eval_pb2.TSHQLSTMEvalOutcomeProto
    ts_hqlstm_train_outcome: _ts_hqlstm_train_pb2.TSHQLSTMTrainOutcomeProto
    ts_hqmlp_eval_outcome: _ts_hqmlp_eval_pb2.TSHQMLPEvalOutcomeProto
    ts_hqmlp_train_outcome: _ts_hqmlp_train_pb2.TSHQMLPTrainOutcomeProto
    ts_lstm_eval_outcome: _ts_lstm_eval_pb2.TSLSTMEvalOutcomeProto
    ts_lstm_train_outcome: _ts_lstm_train_pb2.TSLSTMTrainOutcomeProto
    ts_mlp_eval_outcome: _ts_mlp_eval_pb2.TSMLPEvalOutcomeProto
    ts_mlp_train_outcome: _ts_mlp_train_pb2.TSMLPTrainOutcomeProto
    generic_ml_train_outcome: _generic_ml_train_pb2.GenericMLTrainOutcomeProto
    generic_ml_infer_outcome: _generic_ml_infer_pb2.GenericMLInferOutcomeProto
    routing_outcome: _routing_pb2.RoutingOutcomeProto
    tqml_outcome: _tq42_tqml_pb2.TQmlOutcomeProto
    optimax_outcome: _optimax_pb2.OptimaxOutcomeProto
    def __init__(self, result_json: _Optional[str] = ..., circuit_run_outcome: _Optional[_Union[_circuit_run_pb2.CircuitRunOutcomeProto, _Mapping]] = ..., cva_opt_outcome: _Optional[_Union[_cva_opt_pb2.CvaOptOutcomeProto, _Mapping]] = ..., tetra_opt_outcome: _Optional[_Union[_tetra_opt_pb2.TetraOptOutcomeProto, _Mapping]] = ..., tetra_qu_enc_outcome: _Optional[_Union[_tetra_quenc_pb2.TetraQuEncOutcomeProto, _Mapping]] = ..., toy_outcome: _Optional[_Union[_toy_pb2.ToyOutcomeProto, _Mapping]] = ..., ts_hqlstm_eval_outcome: _Optional[_Union[_ts_hqlstm_eval_pb2.TSHQLSTMEvalOutcomeProto, _Mapping]] = ..., ts_hqlstm_train_outcome: _Optional[_Union[_ts_hqlstm_train_pb2.TSHQLSTMTrainOutcomeProto, _Mapping]] = ..., ts_hqmlp_eval_outcome: _Optional[_Union[_ts_hqmlp_eval_pb2.TSHQMLPEvalOutcomeProto, _Mapping]] = ..., ts_hqmlp_train_outcome: _Optional[_Union[_ts_hqmlp_train_pb2.TSHQMLPTrainOutcomeProto, _Mapping]] = ..., ts_lstm_eval_outcome: _Optional[_Union[_ts_lstm_eval_pb2.TSLSTMEvalOutcomeProto, _Mapping]] = ..., ts_lstm_train_outcome: _Optional[_Union[_ts_lstm_train_pb2.TSLSTMTrainOutcomeProto, _Mapping]] = ..., ts_mlp_eval_outcome: _Optional[_Union[_ts_mlp_eval_pb2.TSMLPEvalOutcomeProto, _Mapping]] = ..., ts_mlp_train_outcome: _Optional[_Union[_ts_mlp_train_pb2.TSMLPTrainOutcomeProto, _Mapping]] = ..., generic_ml_train_outcome: _Optional[_Union[_generic_ml_train_pb2.GenericMLTrainOutcomeProto, _Mapping]] = ..., generic_ml_infer_outcome: _Optional[_Union[_generic_ml_infer_pb2.GenericMLInferOutcomeProto, _Mapping]] = ..., routing_outcome: _Optional[_Union[_routing_pb2.RoutingOutcomeProto, _Mapping]] = ..., tqml_outcome: _Optional[_Union[_tq42_tqml_pb2.TQmlOutcomeProto, _Mapping]] = ..., optimax_outcome: _Optional[_Union[_optimax_pb2.OptimaxOutcomeProto, _Mapping]] = ...) -> None: ...
