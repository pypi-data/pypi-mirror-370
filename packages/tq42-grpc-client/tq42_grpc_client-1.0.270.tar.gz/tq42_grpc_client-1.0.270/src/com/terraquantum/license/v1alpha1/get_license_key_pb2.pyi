from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetLicenseKeyRequest(_message.Message):
    __slots__ = ("license_id",)
    LICENSE_ID_FIELD_NUMBER: _ClassVar[int]
    license_id: str
    def __init__(self, license_id: _Optional[str] = ...) -> None: ...

class GetLicenseKeyResponse(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...
