from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CancelExperimentRunRequest(_message.Message):
    __slots__ = ("experiment_run_id",)
    EXPERIMENT_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    experiment_run_id: str
    def __init__(self, experiment_run_id: _Optional[str] = ...) -> None: ...
