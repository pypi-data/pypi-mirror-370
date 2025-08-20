from com.terraquantum.plan.v1.plan import plan_pb2 as _plan_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrganizationPlanProto(_message.Message):
    __slots__ = ("id", "organization_id", "plan")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    PLAN_FIELD_NUMBER: _ClassVar[int]
    id: str
    organization_id: str
    plan: _plan_pb2.PlanProto
    def __init__(self, id: _Optional[str] = ..., organization_id: _Optional[str] = ..., plan: _Optional[_Union[_plan_pb2.PlanProto, _Mapping]] = ...) -> None: ...
