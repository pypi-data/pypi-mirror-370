from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GenericParametersProto(_message.Message):
    __slots__ = ("parameter_string",)
    PARAMETER_STRING_FIELD_NUMBER: _ClassVar[int]
    parameter_string: str
    def __init__(self, parameter_string: _Optional[str] = ...) -> None: ...

class GenericResultProto(_message.Message):
    __slots__ = ("results_string",)
    RESULTS_STRING_FIELD_NUMBER: _ClassVar[int]
    results_string: str
    def __init__(self, results_string: _Optional[str] = ...) -> None: ...
