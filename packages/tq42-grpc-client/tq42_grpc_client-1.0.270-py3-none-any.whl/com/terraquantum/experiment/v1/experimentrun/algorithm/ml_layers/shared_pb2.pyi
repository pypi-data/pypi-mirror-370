from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class MeasurementModeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEASUREMENT_MODE_UNSPECIFIED: _ClassVar[MeasurementModeProto]
    EVEN: _ClassVar[MeasurementModeProto]
    SINGLE: _ClassVar[MeasurementModeProto]
    NONE: _ClassVar[MeasurementModeProto]

class MeasureProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEASURE_UNSPECIFIED: _ClassVar[MeasureProto]
    X: _ClassVar[MeasureProto]
    Y: _ClassVar[MeasureProto]
    Z: _ClassVar[MeasureProto]

class EntanglingProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ENTANGLING_UNSPECIFIED: _ClassVar[EntanglingProto]
    BASIC: _ClassVar[EntanglingProto]
    STRONG: _ClassVar[EntanglingProto]

class DiffMethodProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DIFF_METHOD_UNSPECIFIED: _ClassVar[DiffMethodProto]
    ADJOINT: _ClassVar[DiffMethodProto]
    PARAMETER_SHIFT: _ClassVar[DiffMethodProto]

class QubitTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QUBIT_TYPE_UNSPECIFIED: _ClassVar[QubitTypeProto]
    LIGHTNING_QUBIT: _ClassVar[QubitTypeProto]
    LIGHTNING_GPU: _ClassVar[QubitTypeProto]

class ActFuncProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACT_FUNC_UNSPECIFIED: _ClassVar[ActFuncProto]
    RELU: _ClassVar[ActFuncProto]
    LEAKYRELU: _ClassVar[ActFuncProto]
    SIGMOID: _ClassVar[ActFuncProto]
MEASUREMENT_MODE_UNSPECIFIED: MeasurementModeProto
EVEN: MeasurementModeProto
SINGLE: MeasurementModeProto
NONE: MeasurementModeProto
MEASURE_UNSPECIFIED: MeasureProto
X: MeasureProto
Y: MeasureProto
Z: MeasureProto
ENTANGLING_UNSPECIFIED: EntanglingProto
BASIC: EntanglingProto
STRONG: EntanglingProto
DIFF_METHOD_UNSPECIFIED: DiffMethodProto
ADJOINT: DiffMethodProto
PARAMETER_SHIFT: DiffMethodProto
QUBIT_TYPE_UNSPECIFIED: QubitTypeProto
LIGHTNING_QUBIT: QubitTypeProto
LIGHTNING_GPU: QubitTypeProto
ACT_FUNC_UNSPECIFIED: ActFuncProto
RELU: ActFuncProto
LEAKYRELU: ActFuncProto
SIGMOID: ActFuncProto
