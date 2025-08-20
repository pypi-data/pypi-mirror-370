from com.terraquantum.experiment.v1.experiment import experiment_pb2 as _experiment_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListExperimentsResponse(_message.Message):
    __slots__ = ("experiments",)
    EXPERIMENTS_FIELD_NUMBER: _ClassVar[int]
    experiments: _containers.RepeatedCompositeFieldContainer[_experiment_pb2.ExperimentProto]
    def __init__(self, experiments: _Optional[_Iterable[_Union[_experiment_pb2.ExperimentProto, _Mapping]]] = ...) -> None: ...
