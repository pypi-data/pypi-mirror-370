from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CreateOrganizationRequest(_message.Message):
    __slots__ = ("request_id", "owner", "name", "description", "image_url")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    owner: str
    name: str
    description: str
    image_url: str
    def __init__(self, request_id: _Optional[str] = ..., owner: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., image_url: _Optional[str] = ...) -> None: ...
