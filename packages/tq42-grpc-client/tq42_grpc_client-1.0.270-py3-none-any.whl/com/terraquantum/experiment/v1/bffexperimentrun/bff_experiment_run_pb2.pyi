from com.terraquantum.experiment.v1.experimentrun.algorithm import shared_pb2 as _shared_pb2
from com.terraquantum.experiment.v1.experimentrun import experiment_run_pb2 as _experiment_run_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from com.terraquantum.experiment.v1.experimentrun import create_experiment_run_request_pb2 as _create_experiment_run_request_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BffExperimentRunProto(_message.Message):
    __slots__ = ("id", "experiment_id", "status", "algorithm", "hardware", "metadata", "result", "error_message", "created_by", "cancelled_by", "created_at", "duration_millis", "sequential_id", "model_id", "model_name", "dataset_name", "model_description", "parent_id", "industry", "problem_type", "use_case", "outputs_json")
    ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    HARDWARE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    DURATION_MILLIS_FIELD_NUMBER: _ClassVar[int]
    SEQUENTIAL_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    DATASET_NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    INDUSTRY_FIELD_NUMBER: _ClassVar[int]
    PROBLEM_TYPE_FIELD_NUMBER: _ClassVar[int]
    USE_CASE_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_JSON_FIELD_NUMBER: _ClassVar[int]
    id: str
    experiment_id: str
    status: _experiment_run_pb2.ExperimentRunStatusProto
    algorithm: _shared_pb2.AlgorithmProto
    hardware: _experiment_run_pb2.HardwareProto
    metadata: str
    result: str
    error_message: str
    created_by: UserInfoProto
    cancelled_by: UserInfoProto
    created_at: _timestamp_pb2.Timestamp
    duration_millis: int
    sequential_id: str
    model_id: str
    model_name: str
    dataset_name: str
    model_description: str
    parent_id: str
    industry: _create_experiment_run_request_pb2.IndustryProto
    problem_type: _create_experiment_run_request_pb2.ProblemTypeProto
    use_case: _create_experiment_run_request_pb2.UseCaseProto
    outputs_json: str
    def __init__(self, id: _Optional[str] = ..., experiment_id: _Optional[str] = ..., status: _Optional[_Union[_experiment_run_pb2.ExperimentRunStatusProto, str]] = ..., algorithm: _Optional[_Union[_shared_pb2.AlgorithmProto, str]] = ..., hardware: _Optional[_Union[_experiment_run_pb2.HardwareProto, str]] = ..., metadata: _Optional[str] = ..., result: _Optional[str] = ..., error_message: _Optional[str] = ..., created_by: _Optional[_Union[UserInfoProto, _Mapping]] = ..., cancelled_by: _Optional[_Union[UserInfoProto, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., duration_millis: _Optional[int] = ..., sequential_id: _Optional[str] = ..., model_id: _Optional[str] = ..., model_name: _Optional[str] = ..., dataset_name: _Optional[str] = ..., model_description: _Optional[str] = ..., parent_id: _Optional[str] = ..., industry: _Optional[_Union[_create_experiment_run_request_pb2.IndustryProto, str]] = ..., problem_type: _Optional[_Union[_create_experiment_run_request_pb2.ProblemTypeProto, str]] = ..., use_case: _Optional[_Union[_create_experiment_run_request_pb2.UseCaseProto, str]] = ..., outputs_json: _Optional[str] = ...) -> None: ...

class UserInfoProto(_message.Message):
    __slots__ = ("email", "first_name", "last_name")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    email: str
    first_name: str
    last_name: str
    def __init__(self, email: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ...) -> None: ...
