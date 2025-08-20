from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TransactionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TRANSACTION_TYPE_UNSPECIFIED: _ClassVar[TransactionType]
    CREDIT_INITIAL_ALLOCATION: _ClassVar[TransactionType]
    DEBIT_CONSUMPTION: _ClassVar[TransactionType]
    CREDIT_PURCHASE: _ClassVar[TransactionType]
TRANSACTION_TYPE_UNSPECIFIED: TransactionType
CREDIT_INITIAL_ALLOCATION: TransactionType
DEBIT_CONSUMPTION: TransactionType
CREDIT_PURCHASE: TransactionType

class CreditTransactionProto(_message.Message):
    __slots__ = ("id", "organization_id", "type", "parent_id", "amount", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    organization_id: str
    type: TransactionType
    parent_id: str
    amount: int
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., organization_id: _Optional[str] = ..., type: _Optional[_Union[TransactionType, str]] = ..., parent_id: _Optional[str] = ..., amount: _Optional[int] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
