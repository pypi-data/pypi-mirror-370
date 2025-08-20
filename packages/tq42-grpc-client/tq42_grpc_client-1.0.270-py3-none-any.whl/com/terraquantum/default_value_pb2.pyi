from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
default_value: _descriptor.FieldDescriptor

class DefaultValue(_message.Message):
    __slots__ = ("float", "double", "int32", "int64", "uint32", "uint64", "sint32", "sint64", "fixed32", "fixed64", "sfixed32", "sfixed64", "bool", "string", "enum", "map", "any")
    class MapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    FLOAT_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_FIELD_NUMBER: _ClassVar[int]
    INT32_FIELD_NUMBER: _ClassVar[int]
    INT64_FIELD_NUMBER: _ClassVar[int]
    UINT32_FIELD_NUMBER: _ClassVar[int]
    UINT64_FIELD_NUMBER: _ClassVar[int]
    SINT32_FIELD_NUMBER: _ClassVar[int]
    SINT64_FIELD_NUMBER: _ClassVar[int]
    FIXED32_FIELD_NUMBER: _ClassVar[int]
    FIXED64_FIELD_NUMBER: _ClassVar[int]
    SFIXED32_FIELD_NUMBER: _ClassVar[int]
    SFIXED64_FIELD_NUMBER: _ClassVar[int]
    BOOL_FIELD_NUMBER: _ClassVar[int]
    STRING_FIELD_NUMBER: _ClassVar[int]
    ENUM_FIELD_NUMBER: _ClassVar[int]
    MAP_FIELD_NUMBER: _ClassVar[int]
    ANY_FIELD_NUMBER: _ClassVar[int]
    float: _containers.RepeatedScalarFieldContainer[float]
    double: _containers.RepeatedScalarFieldContainer[float]
    int32: _containers.RepeatedScalarFieldContainer[int]
    int64: _containers.RepeatedScalarFieldContainer[int]
    uint32: _containers.RepeatedScalarFieldContainer[int]
    uint64: _containers.RepeatedScalarFieldContainer[int]
    sint32: _containers.RepeatedScalarFieldContainer[int]
    sint64: _containers.RepeatedScalarFieldContainer[int]
    fixed32: _containers.RepeatedScalarFieldContainer[int]
    fixed64: _containers.RepeatedScalarFieldContainer[int]
    sfixed32: _containers.RepeatedScalarFieldContainer[int]
    sfixed64: _containers.RepeatedScalarFieldContainer[int]
    bool: _containers.RepeatedScalarFieldContainer[bool]
    string: _containers.RepeatedScalarFieldContainer[str]
    enum: _containers.RepeatedScalarFieldContainer[int]
    map: _containers.ScalarMap[str, str]
    any: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    def __init__(self, float: _Optional[_Iterable[float]] = ..., double: _Optional[_Iterable[float]] = ..., int32: _Optional[_Iterable[int]] = ..., int64: _Optional[_Iterable[int]] = ..., uint32: _Optional[_Iterable[int]] = ..., uint64: _Optional[_Iterable[int]] = ..., sint32: _Optional[_Iterable[int]] = ..., sint64: _Optional[_Iterable[int]] = ..., fixed32: _Optional[_Iterable[int]] = ..., fixed64: _Optional[_Iterable[int]] = ..., sfixed32: _Optional[_Iterable[int]] = ..., sfixed64: _Optional[_Iterable[int]] = ..., bool: _Optional[_Iterable[bool]] = ..., string: _Optional[_Iterable[str]] = ..., enum: _Optional[_Iterable[int]] = ..., map: _Optional[_Mapping[str, str]] = ..., any: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ...) -> None: ...
