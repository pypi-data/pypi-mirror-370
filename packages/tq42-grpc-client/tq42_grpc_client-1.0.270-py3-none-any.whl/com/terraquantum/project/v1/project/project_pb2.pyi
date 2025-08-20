from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProjectStateProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROJECT_STATE_UNSPECIFIED: _ClassVar[ProjectStateProto]
    ACTIVE: _ClassVar[ProjectStateProto]
    ARCHIVED: _ClassVar[ProjectStateProto]
PROJECT_STATE_UNSPECIFIED: ProjectStateProto
ACTIVE: ProjectStateProto
ARCHIVED: ProjectStateProto

class ProjectProto(_message.Message):
    __slots__ = ("id", "organization_id", "name", "description", "image_url", "state", "created_at", "created_by", "default_project")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PROJECT_FIELD_NUMBER: _ClassVar[int]
    id: str
    organization_id: str
    name: str
    description: str
    image_url: str
    state: ProjectStateProto
    created_at: _timestamp_pb2.Timestamp
    created_by: str
    default_project: bool
    def __init__(self, id: _Optional[str] = ..., organization_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., image_url: _Optional[str] = ..., state: _Optional[_Union[ProjectStateProto, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_by: _Optional[str] = ..., default_project: bool = ...) -> None: ...
