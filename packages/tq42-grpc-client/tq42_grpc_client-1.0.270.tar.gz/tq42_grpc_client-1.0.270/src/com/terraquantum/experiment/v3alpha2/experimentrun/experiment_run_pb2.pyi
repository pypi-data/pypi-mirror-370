from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import shared_pb2 as _shared_pb2
from com.terraquantum.experiment.v1.experimentrun import experiment_run_pb2 as _experiment_run_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExperimentRunProto(_message.Message):
    __slots__ = ("id", "experiment_id", "sequential_id", "status", "hardware", "created_by", "created_at", "started_at", "finished_at", "last_running_status", "error_message", "cancelled_by", "deleted_at", "project_id", "metadata", "algorithm", "version", "result")
    ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENTIAL_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    HARDWARE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_RUNNING_STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_BY_FIELD_NUMBER: _ClassVar[int]
    DELETED_AT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    id: str
    experiment_id: str
    sequential_id: int
    status: _experiment_run_pb2.ExperimentRunStatusProto
    hardware: _experiment_run_pb2.HardwareProto
    created_by: str
    created_at: _timestamp_pb2.Timestamp
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    last_running_status: _timestamp_pb2.Timestamp
    error_message: str
    cancelled_by: str
    deleted_at: _timestamp_pb2.Timestamp
    project_id: str
    metadata: _struct_pb2.Struct
    algorithm: str
    version: str
    result: ExperimentRunResultProto
    def __init__(self, id: _Optional[str] = ..., experiment_id: _Optional[str] = ..., sequential_id: _Optional[int] = ..., status: _Optional[_Union[_experiment_run_pb2.ExperimentRunStatusProto, str]] = ..., hardware: _Optional[_Union[_experiment_run_pb2.HardwareProto, str]] = ..., created_by: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_running_status: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., error_message: _Optional[str] = ..., cancelled_by: _Optional[str] = ..., deleted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., project_id: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., algorithm: _Optional[str] = ..., version: _Optional[str] = ..., result: _Optional[_Union[ExperimentRunResultProto, _Mapping]] = ...) -> None: ...

class ExperimentRunResultProto(_message.Message):
    __slots__ = ("result_json", "outcome")
    RESULT_JSON_FIELD_NUMBER: _ClassVar[int]
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    result_json: str
    outcome: _struct_pb2.Struct
    def __init__(self, result_json: _Optional[str] = ..., outcome: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class ExperimentRunStatusChangedProto(_message.Message):
    __slots__ = ("experiment_run_id", "status", "timestamp", "result", "error_message")
    EXPERIMENT_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    experiment_run_id: str
    status: _experiment_run_pb2.ExperimentRunStatusProto
    timestamp: _timestamp_pb2.Timestamp
    result: ExperimentRunResultProto
    error_message: str
    def __init__(self, experiment_run_id: _Optional[str] = ..., status: _Optional[_Union[_experiment_run_pb2.ExperimentRunStatusProto, str]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., result: _Optional[_Union[ExperimentRunResultProto, _Mapping]] = ..., error_message: _Optional[str] = ...) -> None: ...
