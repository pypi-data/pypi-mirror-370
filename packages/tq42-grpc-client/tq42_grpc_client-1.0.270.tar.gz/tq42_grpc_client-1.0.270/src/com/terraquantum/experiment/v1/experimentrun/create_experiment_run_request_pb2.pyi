from com.terraquantum.experiment.v1.experimentrun.algorithm import circuit_run_pb2 as _circuit_run_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import cva_opt_pb2 as _cva_opt_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import shared_pb2 as _shared_pb2
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
from com.terraquantum.experiment.v1.experimentrun import experiment_run_pb2 as _experiment_run_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IndustryProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INDUSTRY_UNSPECIFIED: _ClassVar[IndustryProto]
    ENERGY: _ClassVar[IndustryProto]

class ProblemTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROBLEM_TYPE_UNSPECIFIED: _ClassVar[ProblemTypeProto]
    TIME_SERIES_PREDICTION: _ClassVar[ProblemTypeProto]

class UseCaseProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    USE_CASE_UNSPECIFIED: _ClassVar[UseCaseProto]
    PV_POWER: _ClassVar[UseCaseProto]
INDUSTRY_UNSPECIFIED: IndustryProto
ENERGY: IndustryProto
PROBLEM_TYPE_UNSPECIFIED: ProblemTypeProto
TIME_SERIES_PREDICTION: ProblemTypeProto
USE_CASE_UNSPECIFIED: UseCaseProto
PV_POWER: UseCaseProto

class CreateExperimentRunRequest(_message.Message):
    __slots__ = ("experiment_id", "request_id", "hardware", "algorithm", "parent_id", "industry", "problem_type", "use_case", "circuit_run_metadata", "cva_opt_metadata", "toy_metadata", "tetra_opt_metadata", "tetra_quenc_metadata", "ts_hqmlp_train_metadata", "ts_hqmlp_eval_metadata", "ts_hqlstm_train_metadata", "ts_hqlstm_eval_metadata", "ts_mlp_train_metadata", "ts_mlp_eval_metadata", "ts_lstm_train_metadata", "ts_lstm_eval_metadata", "generic_ml_train_metadata", "generic_ml_infer_metadata")
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    HARDWARE_FIELD_NUMBER: _ClassVar[int]
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    INDUSTRY_FIELD_NUMBER: _ClassVar[int]
    PROBLEM_TYPE_FIELD_NUMBER: _ClassVar[int]
    USE_CASE_FIELD_NUMBER: _ClassVar[int]
    CIRCUIT_RUN_METADATA_FIELD_NUMBER: _ClassVar[int]
    CVA_OPT_METADATA_FIELD_NUMBER: _ClassVar[int]
    TOY_METADATA_FIELD_NUMBER: _ClassVar[int]
    TETRA_OPT_METADATA_FIELD_NUMBER: _ClassVar[int]
    TETRA_QUENC_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_HQMLP_TRAIN_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_HQMLP_EVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_HQLSTM_TRAIN_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_HQLSTM_EVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_MLP_TRAIN_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_MLP_EVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_LSTM_TRAIN_METADATA_FIELD_NUMBER: _ClassVar[int]
    TS_LSTM_EVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    GENERIC_ML_TRAIN_METADATA_FIELD_NUMBER: _ClassVar[int]
    GENERIC_ML_INFER_METADATA_FIELD_NUMBER: _ClassVar[int]
    experiment_id: str
    request_id: str
    hardware: _experiment_run_pb2.HardwareProto
    algorithm: _shared_pb2.AlgorithmProto
    parent_id: str
    industry: IndustryProto
    problem_type: ProblemTypeProto
    use_case: UseCaseProto
    circuit_run_metadata: _circuit_run_pb2.CircuitRunMetadataProto
    cva_opt_metadata: _cva_opt_pb2.CvaOptMetadataProto
    toy_metadata: _toy_pb2.ToyMetadataProto
    tetra_opt_metadata: _tetra_opt_pb2.TetraOptMetadataProto
    tetra_quenc_metadata: _tetra_quenc_pb2.TetraQuEncMetadataProto
    ts_hqmlp_train_metadata: _ts_hqmlp_train_pb2.TSHQMLPTrainMetadataProto
    ts_hqmlp_eval_metadata: _ts_hqmlp_eval_pb2.TSHQMLPEvalMetadataProto
    ts_hqlstm_train_metadata: _ts_hqlstm_train_pb2.TSHQLSTMTrainMetadataProto
    ts_hqlstm_eval_metadata: _ts_hqlstm_eval_pb2.TSHQLSTMEvalMetadataProto
    ts_mlp_train_metadata: _ts_mlp_train_pb2.TSMLPTrainMetadataProto
    ts_mlp_eval_metadata: _ts_mlp_eval_pb2.TSMLPEvalMetadataProto
    ts_lstm_train_metadata: _ts_lstm_train_pb2.TSLSTMTrainMetadataProto
    ts_lstm_eval_metadata: _ts_lstm_eval_pb2.TSLSTMEvalMetadataProto
    generic_ml_train_metadata: _generic_ml_train_pb2.GenericMLTrainMetadataProto
    generic_ml_infer_metadata: _generic_ml_infer_pb2.GenericMLInferMetadataProto
    def __init__(self, experiment_id: _Optional[str] = ..., request_id: _Optional[str] = ..., hardware: _Optional[_Union[_experiment_run_pb2.HardwareProto, str]] = ..., algorithm: _Optional[_Union[_shared_pb2.AlgorithmProto, str]] = ..., parent_id: _Optional[str] = ..., industry: _Optional[_Union[IndustryProto, str]] = ..., problem_type: _Optional[_Union[ProblemTypeProto, str]] = ..., use_case: _Optional[_Union[UseCaseProto, str]] = ..., circuit_run_metadata: _Optional[_Union[_circuit_run_pb2.CircuitRunMetadataProto, _Mapping]] = ..., cva_opt_metadata: _Optional[_Union[_cva_opt_pb2.CvaOptMetadataProto, _Mapping]] = ..., toy_metadata: _Optional[_Union[_toy_pb2.ToyMetadataProto, _Mapping]] = ..., tetra_opt_metadata: _Optional[_Union[_tetra_opt_pb2.TetraOptMetadataProto, _Mapping]] = ..., tetra_quenc_metadata: _Optional[_Union[_tetra_quenc_pb2.TetraQuEncMetadataProto, _Mapping]] = ..., ts_hqmlp_train_metadata: _Optional[_Union[_ts_hqmlp_train_pb2.TSHQMLPTrainMetadataProto, _Mapping]] = ..., ts_hqmlp_eval_metadata: _Optional[_Union[_ts_hqmlp_eval_pb2.TSHQMLPEvalMetadataProto, _Mapping]] = ..., ts_hqlstm_train_metadata: _Optional[_Union[_ts_hqlstm_train_pb2.TSHQLSTMTrainMetadataProto, _Mapping]] = ..., ts_hqlstm_eval_metadata: _Optional[_Union[_ts_hqlstm_eval_pb2.TSHQLSTMEvalMetadataProto, _Mapping]] = ..., ts_mlp_train_metadata: _Optional[_Union[_ts_mlp_train_pb2.TSMLPTrainMetadataProto, _Mapping]] = ..., ts_mlp_eval_metadata: _Optional[_Union[_ts_mlp_eval_pb2.TSMLPEvalMetadataProto, _Mapping]] = ..., ts_lstm_train_metadata: _Optional[_Union[_ts_lstm_train_pb2.TSLSTMTrainMetadataProto, _Mapping]] = ..., ts_lstm_eval_metadata: _Optional[_Union[_ts_lstm_eval_pb2.TSLSTMEvalMetadataProto, _Mapping]] = ..., generic_ml_train_metadata: _Optional[_Union[_generic_ml_train_pb2.GenericMLTrainMetadataProto, _Mapping]] = ..., generic_ml_infer_metadata: _Optional[_Union[_generic_ml_infer_pb2.GenericMLInferMetadataProto, _Mapping]] = ...) -> None: ...
