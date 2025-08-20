from com.terraquantum.user.v1.waiting_user import waiting_user_pb2 as _waiting_user_pb2
from com.terraquantum.javalibs.logging.v1 import logging_extensions_pb2 as _logging_extensions_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UserProfileProto(_message.Message):
    __slots__ = ("id", "first_name", "middle_name", "last_name", "company", "role", "primary_area_of_interest", "picture", "newsletter_sign_up")
    ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    COMPANY_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_AREA_OF_INTEREST_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    NEWSLETTER_SIGN_UP_FIELD_NUMBER: _ClassVar[int]
    id: str
    first_name: str
    middle_name: str
    last_name: str
    company: str
    role: _waiting_user_pb2.UserRoleProto
    primary_area_of_interest: _waiting_user_pb2.AreaOfInterestProto
    picture: str
    newsletter_sign_up: bool
    def __init__(self, id: _Optional[str] = ..., first_name: _Optional[str] = ..., middle_name: _Optional[str] = ..., last_name: _Optional[str] = ..., company: _Optional[str] = ..., role: _Optional[_Union[_waiting_user_pb2.UserRoleProto, str]] = ..., primary_area_of_interest: _Optional[_Union[_waiting_user_pb2.AreaOfInterestProto, str]] = ..., picture: _Optional[str] = ..., newsletter_sign_up: bool = ...) -> None: ...
