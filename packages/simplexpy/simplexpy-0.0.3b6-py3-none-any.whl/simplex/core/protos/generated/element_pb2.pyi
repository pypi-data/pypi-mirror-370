from Utils import utils_pb2 as _utils_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Geometry import beam_pb2 as _beam_pb2
from Utils import utils_pb2 as _utils_pb2_1_1
import stage_pb2 as _stage_pb2
from Geometry import geometry_pb2 as _geometry_pb2_1
from Geometry import foundation_pb2 as _foundation_pb2
from Design import design_pb2 as _design_pb2
from Geometry import rebar_pb2 as _rebar_pb2
from Geometry import strand_pb2 as _strand_pb2
from Geometry import link_pb2 as _link_pb2
from Design import concrete_pb2 as _concrete_pb2
from Geometry import foundation_pb2 as _foundation_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1_1
from Geometry import rebar_pb2 as _rebar_pb2_1
from Design import concrete_pb2 as _concrete_pb2_1
from Geometry import retainingwall_pb2 as _retainingwall_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1_1_1
from Geometry import rebar_pb2 as _rebar_pb2_1_1
from Geometry import pile_pb2 as _pile_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1_1_1_1
from Design import design_pb2 as _design_pb2_1
from Design import load_pb2 as _load_pb2
from Design import concrete_pb2 as _concrete_pb2_1_1
from Design import steel_pb2 as _steel_pb2
from Design import timber_pb2 as _timber_pb2
from Design import soil_pb2 as _soil_pb2
from Design import general_pb2 as _general_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
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
from Geometry.beam_pb2 import ConcreteElement
from Geometry.beam_pb2 import Stiffener
from Geometry.beam_pb2 import BucklingSpan
from Geometry.beam_pb2 import BucklingData
from Geometry.beam_pb2 import FlexBuckling
from Geometry.beam_pb2 import LTBuckling
from Geometry.beam_pb2 import LTSBuckling
from Geometry.beam_pb2 import SteelElement
from Geometry.beam_pb2 import TimberElement
from Geometry.beam_pb2 import MultiLayerSegment
from Geometry.beam_pb2 import Segment
from Geometry.beam_pb2 import Layer
from Geometry.beam_pb2 import MultiLayer
from Geometry.beam_pb2 import SecInPlane
from Geometry.beam_pb2 import Data
from Geometry.beam_pb2 import ConcreteBeamType
from Geometry.beam_pb2 import BucklingType
from Geometry.beam_pb2 import ActionType
from Geometry.beam_pb2 import Alignment
from Geometry.beam_pb2 import SupportCondition
from Geometry.foundation_pb2 import PointFoundation
from Geometry.foundation_pb2 import LineFoundation
from Geometry.foundation_pb2 import Circle
from Geometry.foundation_pb2 import Rectangle
from Geometry.foundation_pb2 import Elements
from Geometry.foundation_pb2 import FoundationGeometry
from Geometry.foundation_pb2 import ConcreteParameters
from Geometry.foundation_pb2 import SimpleFoundation
from Geometry.foundation_pb2 import AdvancedFoundation
from Geometry.foundation_pb2 import Data
from Geometry.retainingwall_pb2 import SimpleGeometry
from Geometry.retainingwall_pb2 import AdvancedGeometry
from Geometry.retainingwall_pb2 import Elements
from Geometry.retainingwall_pb2 import WallGeometry
from Geometry.retainingwall_pb2 import Data
from Geometry.retainingwall_pb2 import Type
from Geometry.pile_pb2 import Circle
from Geometry.pile_pb2 import Rectangle
from Geometry.pile_pb2 import Asphalt
from Geometry.pile_pb2 import Geometry
from Geometry.pile_pb2 import Data
from Geometry.pile_pb2 import Type
from Design.design_pb2 import ElementDesignSettings
from Design.design_pb2 import GeneralDesignSettings
ACTION_TYPE_BAR: _beam_pb2.ActionType
ACTION_TYPE_BEAM: _beam_pb2.ActionType
ACTION_TYPE_COLUMN: _beam_pb2.ActionType
ACTION_TYPE_UNSPECIFIED: _beam_pb2.ActionType
ALIGNMENT_BOTTOM: _beam_pb2.Alignment
ALIGNMENT_CENTER: _beam_pb2.Alignment
ALIGNMENT_TOP: _beam_pb2.Alignment
ALIGNMENT_UNSPECIFIED: _beam_pb2.Alignment
BUCKLING_TYPE_FLEXURAL_STIFF: _beam_pb2.BucklingType
BUCKLING_TYPE_FLEXURAL_WEAK: _beam_pb2.BucklingType
BUCKLING_TYPE_LATERAL_TORSIONAL: _beam_pb2.BucklingType
BUCKLING_TYPE_PRESSURED_BOTTOM_FLANGE: _beam_pb2.BucklingType
BUCKLING_TYPE_PRESSURED_TOP_FLANGE: _beam_pb2.BucklingType
BUCKLING_TYPE_UNSPECIFIED: _beam_pb2.BucklingType
CONCRETE_BEAM_TYPE_CONSTANT: _beam_pb2.ConcreteBeamType
CONCRETE_BEAM_TYPE_CUSTOM: _beam_pb2.ConcreteBeamType
CONCRETE_BEAM_TYPE_IB: _beam_pb2.ConcreteBeamType
CONCRETE_BEAM_TYPE_RBX: _beam_pb2.ConcreteBeamType
CONCRETE_BEAM_TYPE_SIB: _beam_pb2.ConcreteBeamType
CONCRETE_BEAM_TYPE_STT: _beam_pb2.ConcreteBeamType
CONCRETE_BEAM_TYPE_UNSPECIFIED: _beam_pb2.ConcreteBeamType
DESCRIPTOR: _descriptor.FileDescriptor
INSPECTION_LEVEL_NORMAL: InspectionLevel
INSPECTION_LEVEL_RELAXED: InspectionLevel
INSPECTION_LEVEL_TIGHTENED: InspectionLevel
INSPECTION_LEVEL_UNSPECIFIED: InspectionLevel
OWNER_COMPANY: _utils_pb2_1_1_1_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1_1_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1_1_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1_1_1_1.Owner
OWNER_USER: _utils_pb2_1_1_1_1_1.Owner
SUPPORT_CONDITION_CANTILEVER: _beam_pb2.SupportCondition
SUPPORT_CONDITION_SIMPLY: _beam_pb2.SupportCondition
SUPPORT_CONDITION_UNSPECIFIED: _beam_pb2.SupportCondition
TYPE_BORED: _pile_pb2.Type
TYPE_CFA: _pile_pb2.Type
TYPE_DRIVEN: _pile_pb2.Type
TYPE_L: _retainingwall_pb2.Type
TYPE_L_WITH_HAUNCH: _retainingwall_pb2.Type
TYPE_T: _retainingwall_pb2.Type
TYPE_T_WITH_HAUNCH: _retainingwall_pb2.Type
TYPE_UNSPECIFIED: _pile_pb2.Type

class Data(_message.Message):
    __slots__ = ["beam", "critical", "design_settings", "foundation", "id", "inspection_level", "perform_control_only", "pile", "retaining_wall"]
    BEAM_FIELD_NUMBER: _ClassVar[int]
    CRITICAL_FIELD_NUMBER: _ClassVar[int]
    DESIGN_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    FOUNDATION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    INSPECTION_LEVEL_FIELD_NUMBER: _ClassVar[int]
    PERFORM_CONTROL_ONLY_FIELD_NUMBER: _ClassVar[int]
    PILE_FIELD_NUMBER: _ClassVar[int]
    RETAINING_WALL_FIELD_NUMBER: _ClassVar[int]
    beam: _beam_pb2.Data
    critical: bool
    design_settings: _design_pb2_1.ElementDesignSettings
    foundation: _foundation_pb2_1.Data
    id: _utils_pb2_1_1_1_1_1.ID
    inspection_level: InspectionLevel
    perform_control_only: bool
    pile: _pile_pb2.Data
    retaining_wall: _retainingwall_pb2.Data
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1_1_1_1.ID, _Mapping]] = ..., beam: _Optional[_Union[_beam_pb2.Data, _Mapping]] = ..., foundation: _Optional[_Union[_foundation_pb2_1.Data, _Mapping]] = ..., retaining_wall: _Optional[_Union[_retainingwall_pb2.Data, _Mapping]] = ..., pile: _Optional[_Union[_pile_pb2.Data, _Mapping]] = ..., inspection_level: _Optional[_Union[InspectionLevel, str]] = ..., critical: bool = ..., design_settings: _Optional[_Union[_design_pb2_1.ElementDesignSettings, _Mapping]] = ..., perform_control_only: bool = ...) -> None: ...

class InspectionLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
