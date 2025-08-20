from com.terraquantum.experiment.v1.experimentrun.algorithm import ml_shared_pb2 as _ml_shared_pb2
from com.terraquantum.experiment.v1.experimentrun import experiment_run_pb2 as _experiment_run_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EvaluateModelRequest(_message.Message):
    __slots__ = ("experiment_id", "request_id", "hardware", "inputs")
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    HARDWARE_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    experiment_id: str
    request_id: str
    hardware: _experiment_run_pb2.HardwareProto
    inputs: _ml_shared_pb2.TSEvalInputsProto
    def __init__(self, experiment_id: _Optional[str] = ..., request_id: _Optional[str] = ..., hardware: _Optional[_Union[_experiment_run_pb2.HardwareProto, str]] = ..., inputs: _Optional[_Union[_ml_shared_pb2.TSEvalInputsProto, _Mapping]] = ...) -> None: ...
