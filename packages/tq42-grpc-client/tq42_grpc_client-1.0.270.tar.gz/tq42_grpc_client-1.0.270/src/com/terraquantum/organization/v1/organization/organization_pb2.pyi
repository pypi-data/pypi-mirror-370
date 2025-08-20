from com.terraquantum.common.v1.organization import organization_user_status_pb2 as _organization_user_status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrganizationStateProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORGANIZATION_STATE_UNSPECIFIED: _ClassVar[OrganizationStateProto]
    ACTIVE: _ClassVar[OrganizationStateProto]
    PENDING_PAYMENT: _ClassVar[OrganizationStateProto]
    SUSPENDED: _ClassVar[OrganizationStateProto]
ORGANIZATION_STATE_UNSPECIFIED: OrganizationStateProto
ACTIVE: OrganizationStateProto
PENDING_PAYMENT: OrganizationStateProto
SUSPENDED: OrganizationStateProto

class OrganizationProto(_message.Message):
    __slots__ = ("id", "owner", "name", "description", "image_url", "state", "default_org", "is_personal_org")
    ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_ORG_FIELD_NUMBER: _ClassVar[int]
    IS_PERSONAL_ORG_FIELD_NUMBER: _ClassVar[int]
    id: str
    owner: str
    name: str
    description: str
    image_url: str
    state: OrganizationStateProto
    default_org: bool
    is_personal_org: bool
    def __init__(self, id: _Optional[str] = ..., owner: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., image_url: _Optional[str] = ..., state: _Optional[_Union[OrganizationStateProto, str]] = ..., default_org: bool = ..., is_personal_org: bool = ...) -> None: ...

class ListOrganizationsResponse(_message.Message):
    __slots__ = ("organizations", "active_organization_id", "active_organization_user_status")
    ORGANIZATIONS_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_ORGANIZATION_USER_STATUS_FIELD_NUMBER: _ClassVar[int]
    organizations: _containers.RepeatedCompositeFieldContainer[OrganizationProto]
    active_organization_id: str
    active_organization_user_status: _organization_user_status_pb2.OrganizationUserStatusProto
    def __init__(self, organizations: _Optional[_Iterable[_Union[OrganizationProto, _Mapping]]] = ..., active_organization_id: _Optional[str] = ..., active_organization_user_status: _Optional[_Union[_organization_user_status_pb2.OrganizationUserStatusProto, str]] = ...) -> None: ...
