from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetExperimentRunsCountRequest(_message.Message):
    __slots__ = ("experiment_id",)
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    experiment_id: str
    def __init__(self, experiment_id: _Optional[str] = ...) -> None: ...

class GetExperimentRunsCountResponse(_message.Message):
    __slots__ = ("queued_count", "running_count", "completed_count", "failed_count")
    QUEUED_COUNT_FIELD_NUMBER: _ClassVar[int]
    RUNNING_COUNT_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_COUNT_FIELD_NUMBER: _ClassVar[int]
    FAILED_COUNT_FIELD_NUMBER: _ClassVar[int]
    queued_count: int
    running_count: int
    completed_count: int
    failed_count: int
    def __init__(self, queued_count: _Optional[int] = ..., running_count: _Optional[int] = ..., completed_count: _Optional[int] = ..., failed_count: _Optional[int] = ...) -> None: ...
