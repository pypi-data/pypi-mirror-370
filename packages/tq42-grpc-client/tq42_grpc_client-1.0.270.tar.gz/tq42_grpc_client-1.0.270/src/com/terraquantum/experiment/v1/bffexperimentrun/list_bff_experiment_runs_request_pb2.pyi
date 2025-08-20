from com.terraquantum.experiment.v1.experimentrun.algorithm import shared_pb2 as _shared_pb2
from com.terraquantum.experiment.v1.experimentrun import experiment_run_pb2 as _experiment_run_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListBffExperimentRunsRequest(_message.Message):
    __slots__ = ("search_term", "experiment_id", "page", "page_size", "sort_column", "sort_asc", "algorithms", "project_id", "status")
    SEARCH_TERM_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    SORT_COLUMN_FIELD_NUMBER: _ClassVar[int]
    SORT_ASC_FIELD_NUMBER: _ClassVar[int]
    ALGORITHMS_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    search_term: str
    experiment_id: str
    page: int
    page_size: int
    sort_column: str
    sort_asc: bool
    algorithms: _containers.RepeatedScalarFieldContainer[_shared_pb2.AlgorithmProto]
    project_id: str
    status: _experiment_run_pb2.ExperimentRunStatusProto
    def __init__(self, search_term: _Optional[str] = ..., experiment_id: _Optional[str] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., sort_column: _Optional[str] = ..., sort_asc: bool = ..., algorithms: _Optional[_Iterable[_Union[_shared_pb2.AlgorithmProto, str]]] = ..., project_id: _Optional[str] = ..., status: _Optional[_Union[_experiment_run_pb2.ExperimentRunStatusProto, str]] = ...) -> None: ...
