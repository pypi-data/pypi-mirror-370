from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ContractTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONTRACT_TYPE_UNSPECIFIED: _ClassVar[ContractTypeProto]
    EULA: _ClassVar[ContractTypeProto]
    TOS: _ClassVar[ContractTypeProto]
CONTRACT_TYPE_UNSPECIFIED: ContractTypeProto
EULA: ContractTypeProto
TOS: ContractTypeProto

class ContractsProto(_message.Message):
    __slots__ = ("eula", "tos")
    EULA_FIELD_NUMBER: _ClassVar[int]
    TOS_FIELD_NUMBER: _ClassVar[int]
    eula: str
    tos: str
    def __init__(self, eula: _Optional[str] = ..., tos: _Optional[str] = ...) -> None: ...
