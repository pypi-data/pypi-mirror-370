from com.terraquantum.user.v1.waiting_user import waiting_user_pb2 as _waiting_user_pb2
from com.terraquantum.javalibs.logging.v1 import logging_extensions_pb2 as _logging_extensions_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JoinWaitingListRequest(_message.Message):
    __slots__ = ("first_name", "last_name", "email", "company", "role", "primary_area_of_interest", "newsletter_sign_up", "request_id")
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    COMPANY_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_AREA_OF_INTEREST_FIELD_NUMBER: _ClassVar[int]
    NEWSLETTER_SIGN_UP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    first_name: str
    last_name: str
    email: str
    company: str
    role: _waiting_user_pb2.UserRoleProto
    primary_area_of_interest: _waiting_user_pb2.AreaOfInterestProto
    newsletter_sign_up: bool
    request_id: str
    def __init__(self, first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., email: _Optional[str] = ..., company: _Optional[str] = ..., role: _Optional[_Union[_waiting_user_pb2.UserRoleProto, str]] = ..., primary_area_of_interest: _Optional[_Union[_waiting_user_pb2.AreaOfInterestProto, str]] = ..., newsletter_sign_up: bool = ..., request_id: _Optional[str] = ...) -> None: ...
