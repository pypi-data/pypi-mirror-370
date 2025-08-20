from com.terraquantum.user.v1.waiting_user import waiting_user_pb2 as _waiting_user_pb2
from google.protobuf import field_mask_pb2 as _field_mask_pb2
from com.terraquantum.javalibs.logging.v1 import logging_extensions_pb2 as _logging_extensions_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpdateUserRequest(_message.Message):
    __slots__ = ("update_mask", "user", "request_id")
    UPDATE_MASK_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    update_mask: _field_mask_pb2.FieldMask
    user: UpdateUserProto
    request_id: str
    def __init__(self, update_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ..., user: _Optional[_Union[UpdateUserProto, _Mapping]] = ..., request_id: _Optional[str] = ...) -> None: ...

class UpdateUserProto(_message.Message):
    __slots__ = ("id", "wizard_finished", "profile", "organization_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    WIZARD_FINISHED_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    wizard_finished: bool
    profile: UpdateUserProfileProto
    organization_id: str
    def __init__(self, id: _Optional[str] = ..., wizard_finished: bool = ..., profile: _Optional[_Union[UpdateUserProfileProto, _Mapping]] = ..., organization_id: _Optional[str] = ...) -> None: ...

class UpdateUserProfileProto(_message.Message):
    __slots__ = ("first_name", "middle_name", "last_name", "company", "role", "primary_area_of_interest", "picture")
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    COMPANY_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_AREA_OF_INTEREST_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    first_name: str
    middle_name: str
    last_name: str
    company: str
    role: _waiting_user_pb2.UserRoleProto
    primary_area_of_interest: _waiting_user_pb2.AreaOfInterestProto
    picture: str
    def __init__(self, first_name: _Optional[str] = ..., middle_name: _Optional[str] = ..., last_name: _Optional[str] = ..., company: _Optional[str] = ..., role: _Optional[_Union[_waiting_user_pb2.UserRoleProto, str]] = ..., primary_area_of_interest: _Optional[_Union[_waiting_user_pb2.AreaOfInterestProto, str]] = ..., picture: _Optional[str] = ...) -> None: ...
