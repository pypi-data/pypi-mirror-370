from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FunctionalityTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FUNCTIONALITY_TYPE_UNSPECIFIED: _ClassVar[FunctionalityTypeProto]
    TQML: _ClassVar[FunctionalityTypeProto]
FUNCTIONALITY_TYPE_UNSPECIFIED: FunctionalityTypeProto
TQML: FunctionalityTypeProto

class FunctionalityProto(_message.Message):
    __slots__ = ("type", "version")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    type: FunctionalityTypeProto
    version: str
    def __init__(self, type: _Optional[_Union[FunctionalityTypeProto, str]] = ..., version: _Optional[str] = ...) -> None: ...

class CheckFunctionalityRequest(_message.Message):
    __slots__ = ("organization_id", "functionality")
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONALITY_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    functionality: FunctionalityProto
    def __init__(self, organization_id: _Optional[str] = ..., functionality: _Optional[_Union[FunctionalityProto, _Mapping]] = ...) -> None: ...
