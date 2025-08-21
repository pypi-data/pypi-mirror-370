from Result import result_pb2 as _result_pb2
from Utils import utils_pb2 as _utils_pb2
from Result import concrete_pb2 as _concrete_pb2
from Result import foundation_pb2 as _foundation_pb2
from Result import pile_pb2 as _pile_pb2
from Result import retainingwall_pb2 as _retainingwall_pb2
from Result import steel_pb2 as _steel_pb2
from Result import timber_pb2 as _timber_pb2
from Result import control_pb2 as _control_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Result.result_pb2 import ForceData
from Result.result_pb2 import DisplacementData
from Result.result_pb2 import StressData
from Result.result_pb2 import TemperatureData
from Result.result_pb2 import Data
from Result.result_pb2 import PositionResult
from Result.result_pb2 import ElementResult
from Result.result_pb2 import Element
from Result.result_pb2 import Node
from Result.result_pb2 import Force
from Result.result_pb2 import Displacement
from Result.result_pb2 import Stress
DESCRIPTOR: _descriptor.FileDescriptor
DISPLACEMENT_RU: _result_pb2.Displacement
DISPLACEMENT_RV: _result_pb2.Displacement
DISPLACEMENT_RW: _result_pb2.Displacement
DISPLACEMENT_RX: _result_pb2.Displacement
DISPLACEMENT_RY: _result_pb2.Displacement
DISPLACEMENT_RZ: _result_pb2.Displacement
DISPLACEMENT_U: _result_pb2.Displacement
DISPLACEMENT_UNSPECIFIED: _result_pb2.Displacement
DISPLACEMENT_V: _result_pb2.Displacement
DISPLACEMENT_W: _result_pb2.Displacement
DISPLACEMENT_X: _result_pb2.Displacement
DISPLACEMENT_Y: _result_pb2.Displacement
DISPLACEMENT_Z: _result_pb2.Displacement
FORCE_M1: _result_pb2.Force
FORCE_M2: _result_pb2.Force
FORCE_MX: _result_pb2.Force
FORCE_MY: _result_pb2.Force
FORCE_MZ: _result_pb2.Force
FORCE_N: _result_pb2.Force
FORCE_RX: _result_pb2.Force
FORCE_RY: _result_pb2.Force
FORCE_RZ: _result_pb2.Force
FORCE_T: _result_pb2.Force
FORCE_UNSPECIFIED: _result_pb2.Force
FORCE_V1: _result_pb2.Force
FORCE_V2: _result_pb2.Force
STRESS_MISES: _result_pb2.Stress
STRESS_S11: _result_pb2.Stress
STRESS_S12: _result_pb2.Stress
STRESS_S22: _result_pb2.Stress
STRESS_SP1: _result_pb2.Stress
STRESS_SP2: _result_pb2.Stress
STRESS_UNSPECIFIED: _result_pb2.Stress

class Data(_message.Message):
    __slots__ = ["foundation", "lcombs", "pile", "rc", "retaining_wall", "steel", "timber"]
    FOUNDATION_FIELD_NUMBER: _ClassVar[int]
    LCOMBS_FIELD_NUMBER: _ClassVar[int]
    PILE_FIELD_NUMBER: _ClassVar[int]
    RC_FIELD_NUMBER: _ClassVar[int]
    RETAINING_WALL_FIELD_NUMBER: _ClassVar[int]
    STEEL_FIELD_NUMBER: _ClassVar[int]
    TIMBER_FIELD_NUMBER: _ClassVar[int]
    foundation: _containers.RepeatedCompositeFieldContainer[_foundation_pb2.DesignSummary]
    lcombs: _containers.RepeatedCompositeFieldContainer[LoadCombinationOutput]
    pile: _containers.RepeatedCompositeFieldContainer[_pile_pb2.DesignSummary]
    rc: _containers.RepeatedCompositeFieldContainer[_concrete_pb2.DesignSummary]
    retaining_wall: _containers.RepeatedCompositeFieldContainer[_retainingwall_pb2.DesignSummary]
    steel: _containers.RepeatedCompositeFieldContainer[_steel_pb2.DesignSummary]
    timber: _containers.RepeatedCompositeFieldContainer[_timber_pb2.DesignSummary]
    def __init__(self, lcombs: _Optional[_Iterable[_Union[LoadCombinationOutput, _Mapping]]] = ..., rc: _Optional[_Iterable[_Union[_concrete_pb2.DesignSummary, _Mapping]]] = ..., steel: _Optional[_Iterable[_Union[_steel_pb2.DesignSummary, _Mapping]]] = ..., timber: _Optional[_Iterable[_Union[_timber_pb2.DesignSummary, _Mapping]]] = ..., foundation: _Optional[_Iterable[_Union[_foundation_pb2.DesignSummary, _Mapping]]] = ..., retaining_wall: _Optional[_Iterable[_Union[_retainingwall_pb2.DesignSummary, _Mapping]]] = ..., pile: _Optional[_Iterable[_Union[_pile_pb2.DesignSummary, _Mapping]]] = ...) -> None: ...

class ElementResult(_message.Message):
    __slots__ = ["elem_guid", "result"]
    ELEM_GUID_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    elem_guid: str
    result: _result_pb2.Element
    def __init__(self, elem_guid: _Optional[str] = ..., result: _Optional[_Union[_result_pb2.Element, _Mapping]] = ...) -> None: ...

class LoadCombinationOutput(_message.Message):
    __slots__ = ["element_results", "lcomb_guid", "support_results"]
    ELEMENT_RESULTS_FIELD_NUMBER: _ClassVar[int]
    LCOMB_GUID_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_RESULTS_FIELD_NUMBER: _ClassVar[int]
    element_results: _containers.RepeatedCompositeFieldContainer[ElementResult]
    lcomb_guid: str
    support_results: _containers.RepeatedCompositeFieldContainer[SupportResult]
    def __init__(self, lcomb_guid: _Optional[str] = ..., support_results: _Optional[_Iterable[_Union[SupportResult, _Mapping]]] = ..., element_results: _Optional[_Iterable[_Union[ElementResult, _Mapping]]] = ...) -> None: ...

class SupportResult(_message.Message):
    __slots__ = ["result", "sup_guid"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    SUP_GUID_FIELD_NUMBER: _ClassVar[int]
    result: _result_pb2.Node
    sup_guid: str
    def __init__(self, sup_guid: _Optional[str] = ..., result: _Optional[_Union[_result_pb2.Node, _Mapping]] = ...) -> None: ...
