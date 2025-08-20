from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlanTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLAN_TYPE_UNSPECIFIED: _ClassVar[PlanTypeProto]
    BASIC: _ClassVar[PlanTypeProto]
    ENTERPRISE: _ClassVar[PlanTypeProto]
    ACADEMIC: _ClassVar[PlanTypeProto]
PLAN_TYPE_UNSPECIFIED: PlanTypeProto
BASIC: PlanTypeProto
ENTERPRISE: PlanTypeProto
ACADEMIC: PlanTypeProto

class PlanProto(_message.Message):
    __slots__ = ("id", "type", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: PlanTypeProto
    name: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[_Union[PlanTypeProto, str]] = ..., name: _Optional[str] = ...) -> None: ...
