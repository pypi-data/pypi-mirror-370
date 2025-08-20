from com.terraquantum.experiment.v1.experimentactivity import experiment_activity_pb2 as _experiment_activity_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListExperimentActivitiesResponse(_message.Message):
    __slots__ = ("experiment_activities",)
    EXPERIMENT_ACTIVITIES_FIELD_NUMBER: _ClassVar[int]
    experiment_activities: _containers.RepeatedCompositeFieldContainer[_experiment_activity_pb2.ExperimentActivityProto]
    def __init__(self, experiment_activities: _Optional[_Iterable[_Union[_experiment_activity_pb2.ExperimentActivityProto, _Mapping]]] = ...) -> None: ...
