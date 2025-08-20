from com.terraquantum.experiment.v1.dataset import dataset_pb2 as _dataset_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DatasetCreationRequestedProto(_message.Message):
    __slots__ = ("id", "name", "description", "url", "project_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    url: str
    project_id: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., url: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class DatasetCreatedProto(_message.Message):
    __slots__ = ("id", "name", "description", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DatasetStatusChangedProto(_message.Message):
    __slots__ = ("id", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: _dataset_pb2.DatasetStatusProto
    def __init__(self, id: _Optional[str] = ..., status: _Optional[_Union[_dataset_pb2.DatasetStatusProto, str]] = ...) -> None: ...

class DatasetProgressChangedProto(_message.Message):
    __slots__ = ("id", "progress")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    id: str
    progress: int
    def __init__(self, id: _Optional[str] = ..., progress: _Optional[int] = ...) -> None: ...

class DatasetDeletionRequestedProto(_message.Message):
    __slots__ = ("id", "project_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    project_id: str
    def __init__(self, id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...
