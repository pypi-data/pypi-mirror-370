from com.terraquantum.javalibs.logging.v1 import logging_extensions_pb2 as _logging_extensions_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UserRoleProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    USER_ROLE_UNSPECIFIED: _ClassVar[UserRoleProto]
    C_LEVEL_CVP: _ClassVar[UserRoleProto]
    VP_DIRECTOR: _ClassVar[UserRoleProto]
    MANAGER: _ClassVar[UserRoleProto]
    INDIVIDUAL_CONTRIBUTOR: _ClassVar[UserRoleProto]
    STUDENT_INTERN: _ClassVar[UserRoleProto]
    OTHER: _ClassVar[UserRoleProto]
    JOB_SEEKER: _ClassVar[UserRoleProto]
    FREELANCER: _ClassVar[UserRoleProto]
    ACCOUNT_MANAGER: _ClassVar[UserRoleProto]
    AGENCY_OWNER: _ClassVar[UserRoleProto]
    SALES_REP: _ClassVar[UserRoleProto]
    SALES_MANAGER: _ClassVar[UserRoleProto]
    CONTENT_STRATEGIST: _ClassVar[UserRoleProto]
    DESIGNER: _ClassVar[UserRoleProto]
    PROFESSOR: _ClassVar[UserRoleProto]

class AreaOfInterestProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AREA_OF_INTEREST_UNSPECIFIED: _ClassVar[AreaOfInterestProto]
    OPTIMIZATION: _ClassVar[AreaOfInterestProto]
    SIMULATION: _ClassVar[AreaOfInterestProto]
    MACHINE_LEARNING: _ClassVar[AreaOfInterestProto]
    I_AM_NOT_SURE: _ClassVar[AreaOfInterestProto]
USER_ROLE_UNSPECIFIED: UserRoleProto
C_LEVEL_CVP: UserRoleProto
VP_DIRECTOR: UserRoleProto
MANAGER: UserRoleProto
INDIVIDUAL_CONTRIBUTOR: UserRoleProto
STUDENT_INTERN: UserRoleProto
OTHER: UserRoleProto
JOB_SEEKER: UserRoleProto
FREELANCER: UserRoleProto
ACCOUNT_MANAGER: UserRoleProto
AGENCY_OWNER: UserRoleProto
SALES_REP: UserRoleProto
SALES_MANAGER: UserRoleProto
CONTENT_STRATEGIST: UserRoleProto
DESIGNER: UserRoleProto
PROFESSOR: UserRoleProto
AREA_OF_INTEREST_UNSPECIFIED: AreaOfInterestProto
OPTIMIZATION: AreaOfInterestProto
SIMULATION: AreaOfInterestProto
MACHINE_LEARNING: AreaOfInterestProto
I_AM_NOT_SURE: AreaOfInterestProto

class WaitingUserProto(_message.Message):
    __slots__ = ("id", "first_name", "last_name", "email", "company", "role", "primary_area_of_interest", "newsletter_sign_up")
    ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    COMPANY_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_AREA_OF_INTEREST_FIELD_NUMBER: _ClassVar[int]
    NEWSLETTER_SIGN_UP_FIELD_NUMBER: _ClassVar[int]
    id: str
    first_name: str
    last_name: str
    email: str
    company: str
    role: UserRoleProto
    primary_area_of_interest: AreaOfInterestProto
    newsletter_sign_up: bool
    def __init__(self, id: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., email: _Optional[str] = ..., company: _Optional[str] = ..., role: _Optional[_Union[UserRoleProto, str]] = ..., primary_area_of_interest: _Optional[_Union[AreaOfInterestProto, str]] = ..., newsletter_sign_up: bool = ...) -> None: ...
