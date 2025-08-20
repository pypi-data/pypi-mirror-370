from com.terraquantum.organization.v2.organization import organization_pb2 as _organization_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListOrganizationsResponse(_message.Message):
    __slots__ = ("organizations",)
    ORGANIZATIONS_FIELD_NUMBER: _ClassVar[int]
    organizations: _containers.RepeatedCompositeFieldContainer[_organization_pb2.OrganizationProto]
    def __init__(self, organizations: _Optional[_Iterable[_Union[_organization_pb2.OrganizationProto, _Mapping]]] = ...) -> None: ...
