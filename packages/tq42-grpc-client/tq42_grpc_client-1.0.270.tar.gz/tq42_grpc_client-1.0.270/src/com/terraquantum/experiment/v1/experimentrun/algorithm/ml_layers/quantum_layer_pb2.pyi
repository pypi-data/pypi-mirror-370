from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import efq_pb2 as _efq_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import phn_pb2 as _phn_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import pqn_pb2 as _pqn_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import qdi_pb2 as _qdi_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QuantumLayer(_message.Message):
    __slots__ = ("phn_layer", "pqn_layer", "qdi_layer", "efq_layer")
    PHN_LAYER_FIELD_NUMBER: _ClassVar[int]
    PQN_LAYER_FIELD_NUMBER: _ClassVar[int]
    QDI_LAYER_FIELD_NUMBER: _ClassVar[int]
    EFQ_LAYER_FIELD_NUMBER: _ClassVar[int]
    phn_layer: _phn_pb2.PHNLayer
    pqn_layer: _pqn_pb2.PQNLayer
    qdi_layer: _qdi_pb2.QDILayer
    efq_layer: _efq_pb2.EFQLayer
    def __init__(self, phn_layer: _Optional[_Union[_phn_pb2.PHNLayer, _Mapping]] = ..., pqn_layer: _Optional[_Union[_pqn_pb2.PQNLayer, _Mapping]] = ..., qdi_layer: _Optional[_Union[_qdi_pb2.QDILayer, _Mapping]] = ..., efq_layer: _Optional[_Union[_efq_pb2.EFQLayer, _Mapping]] = ...) -> None: ...
