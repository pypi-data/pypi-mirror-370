from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PurchaseRequest(_message.Message):
    __slots__ = ("organization_id", "product_id")
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    product_id: str
    def __init__(self, organization_id: _Optional[str] = ..., product_id: _Optional[str] = ...) -> None: ...

class PurchaseResponse(_message.Message):
    __slots__ = ("payment_url",)
    PAYMENT_URL_FIELD_NUMBER: _ClassVar[int]
    payment_url: str
    def __init__(self, payment_url: _Optional[str] = ...) -> None: ...
