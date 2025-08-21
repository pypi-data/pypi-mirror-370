from Result import foundation_pb2 as _foundation_pb2
from Utils import utils_pb2 as _utils_pb2
import element_pb2 as _element_pb2
import sections_pb2 as _sections_pb2
from Loading import load_pb2 as _load_pb2
from Loading import loadcase_pb2 as _loadcase_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Result import concrete_pb2 as _concrete_pb2
from Result import control_pb2 as _control_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Result.foundation_pb2 import ConcreteInput
from Result.foundation_pb2 import EffectiveGeometry
from Result.foundation_pb2 import Stress
from Result.foundation_pb2 import FoundationForce
from Result.foundation_pb2 import SoilWaterLoads
from Result.foundation_pb2 import DetailedFoundationAnalysis
from Result.foundation_pb2 import BearingRes
from Result.foundation_pb2 import BearingResFormula
from Result.foundation_pb2 import DesignStrength
from Result.foundation_pb2 import SlidingRes
from Result.foundation_pb2 import SlidingResFormula
from Result.foundation_pb2 import DetailedFoundationDesign
from Result.foundation_pb2 import RCPunchingCheckConcreteCompression
from Result.foundation_pb2 import RCPunchingCheckConcreteShear
from Result.foundation_pb2 import RCUnreinforced
from Result.foundation_pb2 import Data
from Result.foundation_pb2 import Element
from Result.foundation_pb2 import DesignSummary
DESCRIPTOR: _descriptor.FileDescriptor

class ConcreteInput(_message.Message):
    __slots__ = ["concrete_haunch", "concrete_heel", "concrete_toe", "concrete_wall", "nodes", "sec_haunch_bottom", "sec_heel_left", "sec_heel_right", "sec_toe_left", "sec_toe_right", "sec_wall_bottom", "sec_wall_top"]
    CONCRETE_HAUNCH_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_HEEL_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_TOE_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_WALL_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    SEC_HAUNCH_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    SEC_HEEL_LEFT_FIELD_NUMBER: _ClassVar[int]
    SEC_HEEL_RIGHT_FIELD_NUMBER: _ClassVar[int]
    SEC_TOE_LEFT_FIELD_NUMBER: _ClassVar[int]
    SEC_TOE_RIGHT_FIELD_NUMBER: _ClassVar[int]
    SEC_WALL_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    SEC_WALL_TOP_FIELD_NUMBER: _ClassVar[int]
    concrete_haunch: _element_pb2.Data
    concrete_heel: _element_pb2.Data
    concrete_toe: _element_pb2.Data
    concrete_wall: _element_pb2.Data
    nodes: _containers.RepeatedCompositeFieldContainer[_topology_pb2.ElementNode]
    sec_haunch_bottom: _sections_pb2.Section
    sec_heel_left: _sections_pb2.Section
    sec_heel_right: _sections_pb2.Section
    sec_toe_left: _sections_pb2.Section
    sec_toe_right: _sections_pb2.Section
    sec_wall_bottom: _sections_pb2.Section
    sec_wall_top: _sections_pb2.Section
    def __init__(self, concrete_wall: _Optional[_Union[_element_pb2.Data, _Mapping]] = ..., concrete_haunch: _Optional[_Union[_element_pb2.Data, _Mapping]] = ..., concrete_toe: _Optional[_Union[_element_pb2.Data, _Mapping]] = ..., concrete_heel: _Optional[_Union[_element_pb2.Data, _Mapping]] = ..., nodes: _Optional[_Iterable[_Union[_topology_pb2.ElementNode, _Mapping]]] = ..., sec_wall_top: _Optional[_Union[_sections_pb2.Section, _Mapping]] = ..., sec_wall_bottom: _Optional[_Union[_sections_pb2.Section, _Mapping]] = ..., sec_haunch_bottom: _Optional[_Union[_sections_pb2.Section, _Mapping]] = ..., sec_toe_left: _Optional[_Union[_sections_pb2.Section, _Mapping]] = ..., sec_toe_right: _Optional[_Union[_sections_pb2.Section, _Mapping]] = ..., sec_heel_left: _Optional[_Union[_sections_pb2.Section, _Mapping]] = ..., sec_heel_right: _Optional[_Union[_sections_pb2.Section, _Mapping]] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["result_analysis", "result_design", "utilization"]
    RESULT_ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    RESULT_DESIGN_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    result_analysis: _containers.RepeatedCompositeFieldContainer[_foundation_pb2.DetailedFoundationAnalysis]
    result_design: _containers.RepeatedCompositeFieldContainer[_foundation_pb2.DetailedFoundationDesign]
    utilization: float
    def __init__(self, result_analysis: _Optional[_Iterable[_Union[_foundation_pb2.DetailedFoundationAnalysis, _Mapping]]] = ..., result_design: _Optional[_Iterable[_Union[_foundation_pb2.DetailedFoundationDesign, _Mapping]]] = ..., utilization: _Optional[float] = ...) -> None: ...

class DesignSummary(_message.Message):
    __slots__ = ["concrete_input", "elem_guid"]
    CONCRETE_INPUT_FIELD_NUMBER: _ClassVar[int]
    ELEM_GUID_FIELD_NUMBER: _ClassVar[int]
    concrete_input: ConcreteInput
    elem_guid: str
    def __init__(self, elem_guid: _Optional[str] = ..., concrete_input: _Optional[_Union[ConcreteInput, _Mapping]] = ...) -> None: ...

class Element(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
