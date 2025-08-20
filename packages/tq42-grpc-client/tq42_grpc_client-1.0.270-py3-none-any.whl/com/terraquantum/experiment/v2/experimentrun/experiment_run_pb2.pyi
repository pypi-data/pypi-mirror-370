from com.terraquantum.experiment.v1.experimentrun.algorithm import shared_pb2 as _shared_pb2
from com.terraquantum.experiment.v1.experimentrun import experiment_run_pb2 as _experiment_run_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExperimentRunProto(_message.Message):
    __slots__ = ("id", "experiment_id", "sequential_id", "status", "algorithm", "hardware", "metadata", "result", "created_by", "created_at", "started_at", "finished_at", "last_running_status", "error_message", "cancelled_by", "deleted")
    ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENTIAL_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    HARDWARE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_RUNNING_STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_BY_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    id: str
    experiment_id: str
    sequential_id: int
    status: _experiment_run_pb2.ExperimentRunStatusProto
    algorithm: _shared_pb2.AlgorithmProto
    hardware: _experiment_run_pb2.HardwareProto
    metadata: str
    result: _experiment_run_pb2.ExperimentRunResultProto
    created_by: str
    created_at: _timestamp_pb2.Timestamp
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    last_running_status: _timestamp_pb2.Timestamp
    error_message: str
    cancelled_by: str
    deleted: bool
    def __init__(self, id: _Optional[str] = ..., experiment_id: _Optional[str] = ..., sequential_id: _Optional[int] = ..., status: _Optional[_Union[_experiment_run_pb2.ExperimentRunStatusProto, str]] = ..., algorithm: _Optional[_Union[_shared_pb2.AlgorithmProto, str]] = ..., hardware: _Optional[_Union[_experiment_run_pb2.HardwareProto, str]] = ..., metadata: _Optional[str] = ..., result: _Optional[_Union[_experiment_run_pb2.ExperimentRunResultProto, _Mapping]] = ..., created_by: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_running_status: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., error_message: _Optional[str] = ..., cancelled_by: _Optional[str] = ..., deleted: bool = ...) -> None: ...
