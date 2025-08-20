from com.terraquantum.credits.v1alpha1 import credits_event_pb2 as _credits_event_pb2
from com.terraquantum.plan.v1.plan import plan_pb2 as _plan_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListTransactionsByOrgRequest(_message.Message):
    __slots__ = ("organization_id", "page_size", "page")
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    page_size: int
    page: int
    def __init__(self, organization_id: _Optional[str] = ..., page_size: _Optional[int] = ..., page: _Optional[int] = ...) -> None: ...

class ListTransactionsByOrgResponse(_message.Message):
    __slots__ = ("transactions", "total_count", "total_pages", "current_page")
    TRANSACTIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PAGES_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PAGE_FIELD_NUMBER: _ClassVar[int]
    transactions: _containers.RepeatedCompositeFieldContainer[Transaction]
    total_count: int
    total_pages: int
    current_page: int
    def __init__(self, transactions: _Optional[_Iterable[_Union[Transaction, _Mapping]]] = ..., total_count: _Optional[int] = ..., total_pages: _Optional[int] = ..., current_page: _Optional[int] = ...) -> None: ...

class Transaction(_message.Message):
    __slots__ = ("type", "amount", "created_at", "app_id", "balance")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    APP_ID_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    type: _credits_event_pb2.TransactionType
    amount: int
    created_at: _timestamp_pb2.Timestamp
    app_id: str
    balance: int
    def __init__(self, type: _Optional[_Union[_credits_event_pb2.TransactionType, str]] = ..., amount: _Optional[int] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., app_id: _Optional[str] = ..., balance: _Optional[int] = ...) -> None: ...

class ConsumptionEvent(_message.Message):
    __slots__ = ("entity_id", "project_id")
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    entity_id: str
    project_id: str
    def __init__(self, entity_id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class InitialAllocationEvent(_message.Message):
    __slots__ = ("plan_type",)
    PLAN_TYPE_FIELD_NUMBER: _ClassVar[int]
    plan_type: _plan_pb2.PlanTypeProto
    def __init__(self, plan_type: _Optional[_Union[_plan_pb2.PlanTypeProto, str]] = ...) -> None: ...
