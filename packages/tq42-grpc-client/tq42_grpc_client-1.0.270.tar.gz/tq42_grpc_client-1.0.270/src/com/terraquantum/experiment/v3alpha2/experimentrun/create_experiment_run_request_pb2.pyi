from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum.experiment.v1.experimentrun import experiment_run_pb2 as _experiment_run_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateExperimentRunRequest(_message.Message):
    __slots__ = ("experiment_id", "hardware", "parent_id", "algorithm", "version", "metadata")
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    HARDWARE_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    experiment_id: str
    hardware: _experiment_run_pb2.HardwareProto
    parent_id: str
    algorithm: str
    version: str
    metadata: _struct_pb2.Struct
    def __init__(self, experiment_id: _Optional[str] = ..., hardware: _Optional[_Union[_experiment_run_pb2.HardwareProto, str]] = ..., parent_id: _Optional[str] = ..., algorithm: _Optional[str] = ..., version: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
