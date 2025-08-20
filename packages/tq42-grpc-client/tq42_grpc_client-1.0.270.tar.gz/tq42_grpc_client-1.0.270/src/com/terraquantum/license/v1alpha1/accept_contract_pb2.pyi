from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from com.terraquantum.license.v1alpha1 import contract_pb2 as _contract_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ContractAcceptanceProto(_message.Message):
    __slots__ = ("email", "license_id", "url", "etag", "type", "created_at")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    LICENSE_ID_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    ETAG_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    email: str
    license_id: str
    url: str
    etag: str
    type: _contract_pb2.ContractTypeProto
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, email: _Optional[str] = ..., license_id: _Optional[str] = ..., url: _Optional[str] = ..., etag: _Optional[str] = ..., type: _Optional[_Union[_contract_pb2.ContractTypeProto, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AcceptContractRequest(_message.Message):
    __slots__ = ("license_id", "url", "type")
    LICENSE_ID_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    license_id: str
    url: str
    type: _contract_pb2.ContractTypeProto
    def __init__(self, license_id: _Optional[str] = ..., url: _Optional[str] = ..., type: _Optional[_Union[_contract_pb2.ContractTypeProto, str]] = ...) -> None: ...
