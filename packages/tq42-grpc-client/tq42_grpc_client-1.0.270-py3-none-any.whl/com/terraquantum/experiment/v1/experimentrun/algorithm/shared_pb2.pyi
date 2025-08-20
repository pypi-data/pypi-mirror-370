from google.protobuf import descriptor_pb2 as _descriptor_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AlgorithmProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALGORITHM_UNSPECIFIED: _ClassVar[AlgorithmProto]
    TETRA_OPT: _ClassVar[AlgorithmProto]
    TETRA_OPT_LINEAR: _ClassVar[AlgorithmProto]
    TETRA_OPT_QUBO: _ClassVar[AlgorithmProto]
    TETRA_OPT_TSP: _ClassVar[AlgorithmProto]
    TETRA_AML: _ClassVar[AlgorithmProto]
    TOY: _ClassVar[AlgorithmProto]
    TS_HQMLP_TRAIN: _ClassVar[AlgorithmProto]
    TS_HQMLP_EVAL: _ClassVar[AlgorithmProto]
    TS_HQLSTM_TRAIN: _ClassVar[AlgorithmProto]
    TS_HQLSTM_EVAL: _ClassVar[AlgorithmProto]
    CVA_OPT: _ClassVar[AlgorithmProto]
    TETRA_QUENC: _ClassVar[AlgorithmProto]
    TS_MLP_TRAIN: _ClassVar[AlgorithmProto]
    TS_MLP_EVAL: _ClassVar[AlgorithmProto]
    TS_LSTM_TRAIN: _ClassVar[AlgorithmProto]
    TS_LSTM_EVAL: _ClassVar[AlgorithmProto]
    CIRCUIT_RUN: _ClassVar[AlgorithmProto]
    GENERIC_ML_TRAIN: _ClassVar[AlgorithmProto]
    GENERIC_ML_INFER: _ClassVar[AlgorithmProto]
    ROUTING: _ClassVar[AlgorithmProto]
    TQML: _ClassVar[AlgorithmProto]
    OPTIMAX: _ClassVar[AlgorithmProto]
ALGORITHM_UNSPECIFIED: AlgorithmProto
TETRA_OPT: AlgorithmProto
TETRA_OPT_LINEAR: AlgorithmProto
TETRA_OPT_QUBO: AlgorithmProto
TETRA_OPT_TSP: AlgorithmProto
TETRA_AML: AlgorithmProto
TOY: AlgorithmProto
TS_HQMLP_TRAIN: AlgorithmProto
TS_HQMLP_EVAL: AlgorithmProto
TS_HQLSTM_TRAIN: AlgorithmProto
TS_HQLSTM_EVAL: AlgorithmProto
CVA_OPT: AlgorithmProto
TETRA_QUENC: AlgorithmProto
TS_MLP_TRAIN: AlgorithmProto
TS_MLP_EVAL: AlgorithmProto
TS_LSTM_TRAIN: AlgorithmProto
TS_LSTM_EVAL: AlgorithmProto
CIRCUIT_RUN: AlgorithmProto
GENERIC_ML_TRAIN: AlgorithmProto
GENERIC_ML_INFER: AlgorithmProto
ROUTING: AlgorithmProto
TQML: AlgorithmProto
OPTIMAX: AlgorithmProto
IN_TYPE_FIELD_NUMBER: _ClassVar[int]
in_type: _descriptor.FieldDescriptor
OUT_TYPE_FIELD_NUMBER: _ClassVar[int]
out_type: _descriptor.FieldDescriptor

class GenericStorageInfoProto(_message.Message):
    __slots__ = ("storage_id",)
    STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    storage_id: str
    def __init__(self, storage_id: _Optional[str] = ...) -> None: ...

class ModelStorageInfoProto(_message.Message):
    __slots__ = ("storage_id",)
    STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    storage_id: str
    def __init__(self, storage_id: _Optional[str] = ...) -> None: ...

class DatasetStorageInfoProto(_message.Message):
    __slots__ = ("storage_id",)
    STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    storage_id: str
    def __init__(self, storage_id: _Optional[str] = ...) -> None: ...

class PollingParametersProto(_message.Message):
    __slots__ = ("initial_delay", "retries", "delay", "backoff_factor")
    INITIAL_DELAY_FIELD_NUMBER: _ClassVar[int]
    RETRIES_FIELD_NUMBER: _ClassVar[int]
    DELAY_FIELD_NUMBER: _ClassVar[int]
    BACKOFF_FACTOR_FIELD_NUMBER: _ClassVar[int]
    initial_delay: float
    retries: int
    delay: float
    backoff_factor: float
    def __init__(self, initial_delay: _Optional[float] = ..., retries: _Optional[int] = ..., delay: _Optional[float] = ..., backoff_factor: _Optional[float] = ...) -> None: ...
