from com.terraquantum.experiment.v2.experimentrun import experiment_run_pb2 as _experiment_run_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListExperimentRunsResponse(_message.Message):
    __slots__ = ("experiment_runs",)
    EXPERIMENT_RUNS_FIELD_NUMBER: _ClassVar[int]
    experiment_runs: _containers.RepeatedCompositeFieldContainer[_experiment_run_pb2.ExperimentRunProto]
    def __init__(self, experiment_runs: _Optional[_Iterable[_Union[_experiment_run_pb2.ExperimentRunProto, _Mapping]]] = ...) -> None: ...
