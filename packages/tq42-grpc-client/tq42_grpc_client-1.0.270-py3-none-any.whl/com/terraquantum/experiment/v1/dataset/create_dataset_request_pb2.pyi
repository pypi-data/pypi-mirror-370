from com.terraquantum.experiment.v1.dataset import dataset_pb2 as _dataset_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateDatasetRequest(_message.Message):
    __slots__ = ("request_id", "project_id", "name", "description", "url", "sensitivity")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    project_id: str
    name: str
    description: str
    url: str
    sensitivity: _dataset_pb2.DatasetSensitivityProto
    def __init__(self, request_id: _Optional[str] = ..., project_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., url: _Optional[str] = ..., sensitivity: _Optional[_Union[_dataset_pb2.DatasetSensitivityProto, str]] = ...) -> None: ...
