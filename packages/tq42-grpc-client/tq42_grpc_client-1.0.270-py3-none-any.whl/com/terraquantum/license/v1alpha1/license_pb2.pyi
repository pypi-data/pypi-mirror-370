from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from com.terraquantum.license.v1alpha1 import contract_pb2 as _contract_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LicenseStatusType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LICENSE_STATUS_UNSPECIFIED: _ClassVar[LicenseStatusType]
    ACTIVE: _ClassVar[LicenseStatusType]
    INACTIVE: _ClassVar[LicenseStatusType]
    EXPIRING: _ClassVar[LicenseStatusType]
    EXPIRED: _ClassVar[LicenseStatusType]
    SUSPENDED: _ClassVar[LicenseStatusType]
    BANNED: _ClassVar[LicenseStatusType]
LICENSE_STATUS_UNSPECIFIED: LicenseStatusType
ACTIVE: LicenseStatusType
INACTIVE: LicenseStatusType
EXPIRING: LicenseStatusType
EXPIRED: LicenseStatusType
SUSPENDED: LicenseStatusType
BANNED: LicenseStatusType

class LicenseProto(_message.Message):
    __slots__ = ("id", "product", "status", "created_at", "expiry", "accepted_contracts", "contracts")
    ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_CONTRACTS_FIELD_NUMBER: _ClassVar[int]
    CONTRACTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    product: str
    status: LicenseStatusType
    created_at: _timestamp_pb2.Timestamp
    expiry: _timestamp_pb2.Timestamp
    accepted_contracts: _contract_pb2.ContractsProto
    contracts: _contract_pb2.ContractsProto
    def __init__(self, id: _Optional[str] = ..., product: _Optional[str] = ..., status: _Optional[_Union[LicenseStatusType, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., expiry: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., accepted_contracts: _Optional[_Union[_contract_pb2.ContractsProto, _Mapping]] = ..., contracts: _Optional[_Union[_contract_pb2.ContractsProto, _Mapping]] = ...) -> None: ...
