from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import shared_pb2 as _shared_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CvaOptAimProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CVA_OPT_AIM_UNSPECIFIED: _ClassVar[CvaOptAimProto]
    MINIMIZE: _ClassVar[CvaOptAimProto]
    MAXIMIZE: _ClassVar[CvaOptAimProto]
    VALUE: _ClassVar[CvaOptAimProto]
CVA_OPT_AIM_UNSPECIFIED: CvaOptAimProto
MINIMIZE: CvaOptAimProto
MAXIMIZE: CvaOptAimProto
VALUE: CvaOptAimProto

class CvaOptParametersProto(_message.Message):
    __slots__ = ("func_eval_worker_url", "objectives", "variables", "parameters", "polling", "func_eval_worker_channel_id")
    FUNC_EVAL_WORKER_URL_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVES_FIELD_NUMBER: _ClassVar[int]
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    POLLING_FIELD_NUMBER: _ClassVar[int]
    FUNC_EVAL_WORKER_CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    func_eval_worker_url: str
    objectives: _containers.RepeatedCompositeFieldContainer[CvaOptObjectiveProto]
    variables: _containers.RepeatedCompositeFieldContainer[CvaOptVariableProto]
    parameters: CvaOptParameterProto
    polling: _shared_pb2.PollingParametersProto
    func_eval_worker_channel_id: str
    def __init__(self, func_eval_worker_url: _Optional[str] = ..., objectives: _Optional[_Iterable[_Union[CvaOptObjectiveProto, _Mapping]]] = ..., variables: _Optional[_Iterable[_Union[CvaOptVariableProto, _Mapping]]] = ..., parameters: _Optional[_Union[CvaOptParameterProto, _Mapping]] = ..., polling: _Optional[_Union[_shared_pb2.PollingParametersProto, _Mapping]] = ..., func_eval_worker_channel_id: _Optional[str] = ...) -> None: ...

class CvaOptObjectiveProto(_message.Message):
    __slots__ = ("name", "aim_type", "aim_value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    AIM_TYPE_FIELD_NUMBER: _ClassVar[int]
    AIM_VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    aim_type: CvaOptAimProto
    aim_value: float
    def __init__(self, name: _Optional[str] = ..., aim_type: _Optional[_Union[CvaOptAimProto, str]] = ..., aim_value: _Optional[float] = ...) -> None: ...

class CvaOptVariableProto(_message.Message):
    __slots__ = ("name", "info_real", "info_int", "info_class")
    NAME_FIELD_NUMBER: _ClassVar[int]
    INFO_REAL_FIELD_NUMBER: _ClassVar[int]
    INFO_INT_FIELD_NUMBER: _ClassVar[int]
    INFO_CLASS_FIELD_NUMBER: _ClassVar[int]
    name: str
    info_real: CvaOptVariableRealInfoProto
    info_int: CvaOptVariableIntInfoProto
    info_class: CvaOptVariableClassInfoProto
    def __init__(self, name: _Optional[str] = ..., info_real: _Optional[_Union[CvaOptVariableRealInfoProto, _Mapping]] = ..., info_int: _Optional[_Union[CvaOptVariableIntInfoProto, _Mapping]] = ..., info_class: _Optional[_Union[CvaOptVariableClassInfoProto, _Mapping]] = ...) -> None: ...

class CvaOptVariableRealInfoProto(_message.Message):
    __slots__ = ("lower_bound", "upper_bound")
    LOWER_BOUND_FIELD_NUMBER: _ClassVar[int]
    UPPER_BOUND_FIELD_NUMBER: _ClassVar[int]
    lower_bound: float
    upper_bound: float
    def __init__(self, lower_bound: _Optional[float] = ..., upper_bound: _Optional[float] = ...) -> None: ...

class CvaOptVariableIntInfoProto(_message.Message):
    __slots__ = ("lower_bound", "upper_bound")
    LOWER_BOUND_FIELD_NUMBER: _ClassVar[int]
    UPPER_BOUND_FIELD_NUMBER: _ClassVar[int]
    lower_bound: int
    upper_bound: int
    def __init__(self, lower_bound: _Optional[int] = ..., upper_bound: _Optional[int] = ...) -> None: ...

class CvaOptVariableClassInfoProto(_message.Message):
    __slots__ = ("class_values",)
    CLASS_VALUES_FIELD_NUMBER: _ClassVar[int]
    class_values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, class_values: _Optional[_Iterable[str]] = ...) -> None: ...

class CvaOptParameterProto(_message.Message):
    __slots__ = ("max_generation", "mue")
    MAX_GENERATION_FIELD_NUMBER: _ClassVar[int]
    MUE_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_FIELD_NUMBER: _ClassVar[int]
    max_generation: int
    mue: int
    def __init__(self, max_generation: _Optional[int] = ..., mue: _Optional[int] = ..., **kwargs) -> None: ...

class CvaOptInputsProto(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CvaOptMetadataProto(_message.Message):
    __slots__ = ("parameters", "inputs")
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    parameters: CvaOptParametersProto
    inputs: CvaOptInputsProto
    def __init__(self, parameters: _Optional[_Union[CvaOptParametersProto, _Mapping]] = ..., inputs: _Optional[_Union[CvaOptInputsProto, _Mapping]] = ...) -> None: ...

class CvaOptOutputsProto(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CvaOptOutcomeProto(_message.Message):
    __slots__ = ("result", "outputs")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    result: str
    outputs: CvaOptOutputsProto
    def __init__(self, result: _Optional[str] = ..., outputs: _Optional[_Union[CvaOptOutputsProto, _Mapping]] = ...) -> None: ...
