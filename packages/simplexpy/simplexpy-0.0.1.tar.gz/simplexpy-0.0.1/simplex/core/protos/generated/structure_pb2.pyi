from Utils import utils_pb2 as _utils_pb2
import element_pb2 as _element_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Geometry import geometry_pb2 as _geometry_pb2
from Geometry import beam_pb2 as _beam_pb2
from Geometry import foundation_pb2 as _foundation_pb2
from Geometry import retainingwall_pb2 as _retainingwall_pb2
from Geometry import pile_pb2 as _pile_pb2
from Design import design_pb2 as _design_pb2
import support_pb2 as _support_pb2
from Utils import utils_pb2 as _utils_pb2_1_1
import stage_pb2 as _stage_pb2
from Geometry import geometry_pb2 as _geometry_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1_1
from Loading import loading_pb2 as _loading_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1
from Loading import load_pb2 as _load_pb2
from Loading import loadcase_pb2 as _loadcase_pb2
from Loading import loadgroup_pb2 as _loadgroup_pb2
from Loading import loadcombination_pb2 as _loadcombination_pb2
from Design import design_pb2 as _design_pb2_1
from Design import load_pb2 as _load_pb2_1
from Design import concrete_pb2 as _concrete_pb2
from Design import steel_pb2 as _steel_pb2
from Design import timber_pb2 as _timber_pb2
from Design import soil_pb2 as _soil_pb2
from Design import general_pb2 as _general_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
from element_pb2 import Data
from element_pb2 import InspectionLevel
from support_pb2 import Data
from Geometry.geometry_pb2 import Vector2D
from Geometry.geometry_pb2 import VectorYZ
from Geometry.geometry_pb2 import VectorYZLT
from Geometry.geometry_pb2 import Point2D
from Geometry.geometry_pb2 import Line2D
from Geometry.geometry_pb2 import Arc2D
from Geometry.geometry_pb2 import Circle2D
from Geometry.geometry_pb2 import Curve2D
from Geometry.geometry_pb2 import PolyLine2D
from Geometry.geometry_pb2 import PolyCurve2D
from Geometry.geometry_pb2 import LineFace2D
from Geometry.geometry_pb2 import CurveFace2D
from Geometry.geometry_pb2 import Vector3D
from Geometry.geometry_pb2 import Point3D
from Geometry.geometry_pb2 import Orientation
from Geometry.geometry_pb2 import Line3D
from Geometry.geometry_pb2 import Arc3D
from Geometry.geometry_pb2 import Circle3D
from Geometry.geometry_pb2 import Curve3D
from Geometry.geometry_pb2 import PolyLine3D
from Geometry.geometry_pb2 import PolyCurve3D
from Geometry.geometry_pb2 import LineFace3D
from Geometry.geometry_pb2 import CurveFace3D
from Geometry.geometry_pb2 import Block
from Loading.loading_pb2 import Data
from Design.design_pb2 import ElementDesignSettings
from Design.design_pb2 import GeneralDesignSettings
CONSEQUENCE_CLASS_1: ConsequenceClass
CONSEQUENCE_CLASS_2: ConsequenceClass
CONSEQUENCE_CLASS_3: ConsequenceClass
CONSEQUENCE_CLASS_UNSPECIFIED: ConsequenceClass
DESCRIPTOR: _descriptor.FileDescriptor
INSPECTION_LEVEL_NORMAL: _element_pb2.InspectionLevel
INSPECTION_LEVEL_RELAXED: _element_pb2.InspectionLevel
INSPECTION_LEVEL_TIGHTENED: _element_pb2.InspectionLevel
INSPECTION_LEVEL_UNSPECIFIED: _element_pb2.InspectionLevel
OWNER_COMPANY: _utils_pb2_1_1_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1_1_1.Owner
OWNER_USER: _utils_pb2_1_1_1_1.Owner
RELIABILITY_CLASS_1: ReliabilityClass
RELIABILITY_CLASS_2: ReliabilityClass
RELIABILITY_CLASS_3: ReliabilityClass
RELIABILITY_CLASS_UNSPECIFIED: ReliabilityClass

class Data(_message.Message):
    __slots__ = ["cc", "cons", "description", "design_settings", "elements", "id", "loading", "nodes", "reliability_class", "stages", "sups"]
    CC_FIELD_NUMBER: _ClassVar[int]
    CONS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DESIGN_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LOADING_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    RELIABILITY_CLASS_FIELD_NUMBER: _ClassVar[int]
    STAGES_FIELD_NUMBER: _ClassVar[int]
    SUPS_FIELD_NUMBER: _ClassVar[int]
    cc: ConsequenceClass
    cons: _containers.RepeatedCompositeFieldContainer[_topology_pb2.ConNode]
    description: str
    design_settings: _design_pb2_1.GeneralDesignSettings
    elements: _containers.RepeatedCompositeFieldContainer[_element_pb2.Data]
    id: _utils_pb2_1_1_1_1.ID
    loading: _loading_pb2.Data
    nodes: _containers.RepeatedCompositeFieldContainer[_topology_pb2.ElementNode]
    reliability_class: ReliabilityClass
    stages: _containers.RepeatedCompositeFieldContainer[_stage_pb2.Data]
    sups: _containers.RepeatedCompositeFieldContainer[_support_pb2.Data]
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1_1_1.ID, _Mapping]] = ..., description: _Optional[str] = ..., elements: _Optional[_Iterable[_Union[_element_pb2.Data, _Mapping]]] = ..., nodes: _Optional[_Iterable[_Union[_topology_pb2.ElementNode, _Mapping]]] = ..., cons: _Optional[_Iterable[_Union[_topology_pb2.ConNode, _Mapping]]] = ..., sups: _Optional[_Iterable[_Union[_support_pb2.Data, _Mapping]]] = ..., stages: _Optional[_Iterable[_Union[_stage_pb2.Data, _Mapping]]] = ..., loading: _Optional[_Union[_loading_pb2.Data, _Mapping]] = ..., design_settings: _Optional[_Union[_design_pb2_1.GeneralDesignSettings, _Mapping]] = ..., cc: _Optional[_Union[ConsequenceClass, str]] = ..., reliability_class: _Optional[_Union[ReliabilityClass, str]] = ...) -> None: ...

class ConsequenceClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ReliabilityClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
