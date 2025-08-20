from com.terraquantum.experiment.v1.bffexperimentrun import bff_experiment_run_pb2 as _bff_experiment_run_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListBffExperimentRunsResponse(_message.Message):
    __slots__ = ("experiment_runs", "total_pages", "total_size")
    EXPERIMENT_RUNS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PAGES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    experiment_runs: _containers.RepeatedCompositeFieldContainer[_bff_experiment_run_pb2.BffExperimentRunProto]
    total_pages: int
    total_size: int
    def __init__(self, experiment_runs: _Optional[_Iterable[_Union[_bff_experiment_run_pb2.BffExperimentRunProto, _Mapping]]] = ..., total_pages: _Optional[int] = ..., total_size: _Optional[int] = ...) -> None: ...
