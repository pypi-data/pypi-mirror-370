from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class App(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    APP_UNSPECIFIED: _ClassVar[App]
    APP_TQ42: _ClassVar[App]

class PlanType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLAN_TYPE_UNSPECIFIED: _ClassVar[PlanType]
    PLAN_TYPE_DEFAULT_PRE_TRIAL: _ClassVar[PlanType]
    PLAN_TYPE_TRIAL: _ClassVar[PlanType]
    PLAN_TYPE_BASIC: _ClassVar[PlanType]
    PLAN_TYPE_PRO: _ClassVar[PlanType]
    PLAN_TYPE_ENTERPRISE: _ClassVar[PlanType]
    PLAN_TYPE_NO_PLAN: _ClassVar[PlanType]
APP_UNSPECIFIED: App
APP_TQ42: App
PLAN_TYPE_UNSPECIFIED: PlanType
PLAN_TYPE_DEFAULT_PRE_TRIAL: PlanType
PLAN_TYPE_TRIAL: PlanType
PLAN_TYPE_BASIC: PlanType
PLAN_TYPE_PRO: PlanType
PLAN_TYPE_ENTERPRISE: PlanType
PLAN_TYPE_NO_PLAN: PlanType

class GetPlanRequest(_message.Message):
    __slots__ = ("org_id", "app")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    APP_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    app: App
    def __init__(self, org_id: _Optional[str] = ..., app: _Optional[_Union[App, str]] = ...) -> None: ...

class Plan(_message.Message):
    __slots__ = ("id", "type", "start_date", "end_date")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: PlanType
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., type: _Optional[_Union[PlanType, str]] = ..., start_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
