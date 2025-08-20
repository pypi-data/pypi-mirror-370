from com.terraquantum.storage.v1alpha1 import storage_pb2 as _storage_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateStorageFromFileRequest(_message.Message):
    __slots__ = ("hash_md5", "file_name", "project_id", "name", "description", "sensitivity")
    HASH_MD5_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    hash_md5: str
    file_name: str
    project_id: str
    name: str
    description: str
    sensitivity: _storage_pb2.DatasetSensitivityProto
    def __init__(self, hash_md5: _Optional[str] = ..., file_name: _Optional[str] = ..., project_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., sensitivity: _Optional[_Union[_storage_pb2.DatasetSensitivityProto, str]] = ...) -> None: ...

class CreateStorageFromFileResponse(_message.Message):
    __slots__ = ("signed_url", "storage")
    SIGNED_URL_FIELD_NUMBER: _ClassVar[int]
    STORAGE_FIELD_NUMBER: _ClassVar[int]
    signed_url: str
    storage: _storage_pb2.StorageProto
    def __init__(self, signed_url: _Optional[str] = ..., storage: _Optional[_Union[_storage_pb2.StorageProto, _Mapping]] = ...) -> None: ...
