from com.terraquantum.user.v1.user import user_profile_pb2 as _user_profile_pb2
from com.terraquantum.javalibs.logging.v1 import logging_extensions_pb2 as _logging_extensions_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreatedUserProto(_message.Message):
    __slots__ = ("id", "profile", "email", "invitation_token", "organization_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    INVITATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    profile: _user_profile_pb2.UserProfileProto
    email: str
    invitation_token: str
    organization_id: str
    def __init__(self, id: _Optional[str] = ..., profile: _Optional[_Union[_user_profile_pb2.UserProfileProto, _Mapping]] = ..., email: _Optional[str] = ..., invitation_token: _Optional[str] = ..., organization_id: _Optional[str] = ...) -> None: ...
