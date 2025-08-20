from google.protobuf import field_mask_pb2 as _field_mask_pb2
from com.terraquantum.user.v3alpha1.user import user_pb2 as _user_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpdateUserRequest(_message.Message):
    __slots__ = ("update_mask", "user", "user_id")
    UPDATE_MASK_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    update_mask: _field_mask_pb2.FieldMask
    user: UpdateUserProto
    user_id: str
    def __init__(self, update_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ..., user: _Optional[_Union[UpdateUserProto, _Mapping]] = ..., user_id: _Optional[str] = ...) -> None: ...

class UpdateUserProto(_message.Message):
    __slots__ = ("profile", "email", "settings")
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    profile: _user_pb2.UserProfileProto
    email: str
    settings: _user_pb2.UserSettingsProto
    def __init__(self, profile: _Optional[_Union[_user_pb2.UserProfileProto, _Mapping]] = ..., email: _Optional[str] = ..., settings: _Optional[_Union[_user_pb2.UserSettingsProto, _Mapping]] = ...) -> None: ...
