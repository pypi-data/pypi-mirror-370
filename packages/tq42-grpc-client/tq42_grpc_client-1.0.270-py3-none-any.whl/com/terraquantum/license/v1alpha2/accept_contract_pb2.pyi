from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ContractAcceptanceProto(_message.Message):
    __slots__ = ("email", "license_id", "created_at", "software_version", "entitlement_id")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    LICENSE_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    SOFTWARE_VERSION_FIELD_NUMBER: _ClassVar[int]
    ENTITLEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    email: str
    license_id: str
    created_at: _timestamp_pb2.Timestamp
    software_version: str
    entitlement_id: str
    def __init__(self, email: _Optional[str] = ..., license_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., software_version: _Optional[str] = ..., entitlement_id: _Optional[str] = ...) -> None: ...

class AcceptContractRequest(_message.Message):
    __slots__ = ("software_version", "entitlement_id")
    SOFTWARE_VERSION_FIELD_NUMBER: _ClassVar[int]
    ENTITLEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    software_version: str
    entitlement_id: str
    def __init__(self, software_version: _Optional[str] = ..., entitlement_id: _Optional[str] = ...) -> None: ...
