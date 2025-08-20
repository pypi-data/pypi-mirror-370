from com.terraquantum.license.v1alpha2 import license_pb2 as _license_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListLicensesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListLicensesResponse(_message.Message):
    __slots__ = ("licenses",)
    LICENSES_FIELD_NUMBER: _ClassVar[int]
    licenses: _containers.RepeatedCompositeFieldContainer[_license_pb2.LicenseProto]
    def __init__(self, licenses: _Optional[_Iterable[_Union[_license_pb2.LicenseProto, _Mapping]]] = ...) -> None: ...
