from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UserProfileProto(_message.Message):
    __slots__ = ("first_name", "last_name", "picture")
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    first_name: str
    last_name: str
    picture: str
    def __init__(self, first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., picture: _Optional[str] = ...) -> None: ...

class UserSettingsProto(_message.Message):
    __slots__ = ("multi_factor_authentication",)
    MULTI_FACTOR_AUTHENTICATION_FIELD_NUMBER: _ClassVar[int]
    multi_factor_authentication: bool
    def __init__(self, multi_factor_authentication: bool = ...) -> None: ...

class UserProto(_message.Message):
    __slots__ = ("id", "email", "profile", "created_at", "settings", "is_active")
    ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    id: str
    email: str
    profile: UserProfileProto
    created_at: _timestamp_pb2.Timestamp
    settings: UserSettingsProto
    is_active: bool
    def __init__(self, id: _Optional[str] = ..., email: _Optional[str] = ..., profile: _Optional[_Union[UserProfileProto, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., settings: _Optional[_Union[UserSettingsProto, _Mapping]] = ..., is_active: bool = ...) -> None: ...
