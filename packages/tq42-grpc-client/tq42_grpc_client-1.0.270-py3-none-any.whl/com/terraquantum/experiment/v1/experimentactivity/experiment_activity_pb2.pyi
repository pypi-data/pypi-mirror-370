from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ActivityTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACTIVITY_TYPE_UNSPECIFIED: _ClassVar[ActivityTypeProto]
    EXPERIMENT_CREATED: _ClassVar[ActivityTypeProto]
    EXPERIMENT_RUN_CREATED: _ClassVar[ActivityTypeProto]
    EXPERIMENT_RUN_CANCELLED: _ClassVar[ActivityTypeProto]
ACTIVITY_TYPE_UNSPECIFIED: ActivityTypeProto
EXPERIMENT_CREATED: ActivityTypeProto
EXPERIMENT_RUN_CREATED: ActivityTypeProto
EXPERIMENT_RUN_CANCELLED: ActivityTypeProto

class ExperimentActivityProto(_message.Message):
    __slots__ = ("id", "project_id", "activity_type", "timestamp", "experiment_name", "experiment_run_name", "user_id", "experiment_id", "experiment_run_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_RUN_NAME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    project_id: str
    activity_type: ActivityTypeProto
    timestamp: _timestamp_pb2.Timestamp
    experiment_name: str
    experiment_run_name: str
    user_id: str
    experiment_id: str
    experiment_run_id: str
    def __init__(self, id: _Optional[str] = ..., project_id: _Optional[str] = ..., activity_type: _Optional[_Union[ActivityTypeProto, str]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., experiment_name: _Optional[str] = ..., experiment_run_name: _Optional[str] = ..., user_id: _Optional[str] = ..., experiment_id: _Optional[str] = ..., experiment_run_id: _Optional[str] = ...) -> None: ...
