from google.protobuf import field_mask_pb2 as _field_mask_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListOrganizationMembersByOrganizationIdAndOrganizationMembersIdsRequest(_message.Message):
    __slots__ = ("organization_id", "organization_members_ids", "query_mask")
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_MEMBERS_IDS_FIELD_NUMBER: _ClassVar[int]
    QUERY_MASK_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    organization_members_ids: _containers.RepeatedScalarFieldContainer[str]
    query_mask: _field_mask_pb2.FieldMask
    def __init__(self, organization_id: _Optional[str] = ..., organization_members_ids: _Optional[_Iterable[str]] = ..., query_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ...) -> None: ...
