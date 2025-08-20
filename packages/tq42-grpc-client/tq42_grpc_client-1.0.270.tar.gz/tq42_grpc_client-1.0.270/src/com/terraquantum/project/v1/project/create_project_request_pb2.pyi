from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CreateProjectRequest(_message.Message):
    __slots__ = ("organization_id", "name", "description", "image_url", "request_id")
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    name: str
    description: str
    image_url: str
    request_id: str
    def __init__(self, organization_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., image_url: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...
