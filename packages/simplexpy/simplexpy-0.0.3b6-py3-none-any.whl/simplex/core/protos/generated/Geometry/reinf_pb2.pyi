from Utils import utils_pb2 as _utils_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Design import concrete_pb2 as _concrete_pb2
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
from Design.concrete_pb2 import PartialCoefficient
from Design.concrete_pb2 import PartialCoefficients
from Design.concrete_pb2 import CoverAndSpace
from Design.concrete_pb2 import FireBeam
from Design.concrete_pb2 import Beam
from Design.concrete_pb2 import Column
from Design.concrete_pb2 import Wall
from Design.concrete_pb2 import PrestressedBeam
from Design.concrete_pb2 import HC
from Design.concrete_pb2 import Slab
from Design.concrete_pb2 import GeneralDesignSettings
from Design.concrete_pb2 import ElementDesignSettings
from Design.concrete_pb2 import Fabrication
from Design.concrete_pb2 import ColumnPlacement
from Design.concrete_pb2 import BeamSide
from Design.concrete_pb2 import ConstructionClass
from Design.concrete_pb2 import ShearDesignType
from Design.concrete_pb2 import WebShearCapacityMethod
from Design.concrete_pb2 import SurfaceType
from Design.concrete_pb2 import FctmType
from Design.concrete_pb2 import Commands
from Design.concrete_pb2 import Aggregates
AGGREGATE_CALCAREOUS: _concrete_pb2.Aggregates
AGGREGATE_DK_CALCAREOUS: _concrete_pb2.Aggregates
AGGREGATE_DK_SILICEOUS: _concrete_pb2.Aggregates
AGGREGATE_SILICEOUS: _concrete_pb2.Aggregates
AGGREGATE_UNSPECIFIED: _concrete_pb2.Aggregates
BAR_PROFILE_RIBBED: BarProfile
BAR_PROFILE_SMOOTH: BarProfile
BAR_PROFILE_UNSPECIFIED: BarProfile
BEAM_SIDE_BOTTOM: _concrete_pb2.BeamSide
BEAM_SIDE_END: _concrete_pb2.BeamSide
BEAM_SIDE_LEFT: _concrete_pb2.BeamSide
BEAM_SIDE_RIGHT: _concrete_pb2.BeamSide
BEAM_SIDE_START: _concrete_pb2.BeamSide
BEAM_SIDE_TOP: _concrete_pb2.BeamSide
BEAM_SIDE_UNSPECIFIED: _concrete_pb2.BeamSide
COLUMN_PLACEMENT_CENTER: _concrete_pb2.ColumnPlacement
COLUMN_PLACEMENT_CORNER: _concrete_pb2.ColumnPlacement
COLUMN_PLACEMENT_EDGE: _concrete_pb2.ColumnPlacement
COLUMN_PLACEMENT_UNSPECIFIED: _concrete_pb2.ColumnPlacement
COMMANDS_PUNCHING_CHECK: _concrete_pb2.Commands
COMMANDS_SPALLING_CHECK: _concrete_pb2.Commands
COMMANDS_STIRRUP_DESIGN: _concrete_pb2.Commands
COMMANDS_UNSPECIFIED: _concrete_pb2.Commands
CONSTRUCTION_CLASS_1: _concrete_pb2.ConstructionClass
CONSTRUCTION_CLASS_2: _concrete_pb2.ConstructionClass
CONSTRUCTION_CLASS_UNSPECIFIED: _concrete_pb2.ConstructionClass
DESCRIPTOR: _descriptor.FileDescriptor
DISTRIBUTION_DENSE_2A: Distribution
DISTRIBUTION_DENSE_2B: Distribution
DISTRIBUTION_DENSE_3: Distribution
DISTRIBUTION_EVEN: Distribution
DISTRIBUTION_MID: Distribution
DISTRIBUTION_UNSPECIFIED: Distribution
FABRICATION_IN_SITU: _concrete_pb2.Fabrication
FABRICATION_PREFAB: _concrete_pb2.Fabrication
FABRICATION_UNSPECIFIED: _concrete_pb2.Fabrication
FCTM_TYPE_FCTM: _concrete_pb2.FctmType
FCTM_TYPE_FCTM_FL: _concrete_pb2.FctmType
FCTM_TYPE_FCTM_XI: _concrete_pb2.FctmType
FCTM_TYPE_UNSPECIFIED: _concrete_pb2.FctmType
OWNER_COMPANY: _utils_pb2_1.Owner
OWNER_OFFICE: _utils_pb2_1.Owner
OWNER_STRUSOFT: _utils_pb2_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1.Owner
OWNER_USER: _utils_pb2_1.Owner
SHEAR_DESIGN_TYPE_UNSPECIFIED: _concrete_pb2.ShearDesignType
SHEAR_DESIGN_TYPE_WITHOUT_SHEAR_REINFORCEMENT: _concrete_pb2.ShearDesignType
SHEAR_DESIGN_TYPE_WITH_SHEAR_REINFORCEMENT: _concrete_pb2.ShearDesignType
SURFACE_TYPE_INDENTED: _concrete_pb2.SurfaceType
SURFACE_TYPE_ROUGH: _concrete_pb2.SurfaceType
SURFACE_TYPE_SMOOTH: _concrete_pb2.SurfaceType
SURFACE_TYPE_UNSPECIFIED: _concrete_pb2.SurfaceType
SURFACE_TYPE_VERY_SMOOTH: _concrete_pb2.SurfaceType
VERT_POS_BOTTOM: VertPos
VERT_POS_CENTER: VertPos
VERT_POS_TOP: VertPos
VERT_POS_UNSPECIFIED: VertPos
WEB_SHEAR_CAPACITY_METHOD_ADVANCED: _concrete_pb2.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_SIMPLIFIED: _concrete_pb2.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_STANDARD: _concrete_pb2.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_UNSPECIFIED: _concrete_pb2.WebShearCapacityMethod
WIRE_PROFILE_K7: WireProfile
WIRE_PROFILE_SINGLE: WireProfile
WIRE_PROFILE_UNSPECIFIED: WireProfile

class Group(_message.Message):
    __slots__ = ["diameter", "direction", "id", "length", "mtrl_guid", "pre_stress", "start"]
    DIAMETER_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    MTRL_GUID_FIELD_NUMBER: _ClassVar[int]
    PRE_STRESS_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    diameter: float
    direction: _geometry_pb2.Vector3D
    id: _utils_pb2_1.ID
    length: float
    mtrl_guid: str
    pre_stress: float
    start: float
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., direction: _Optional[_Union[_geometry_pb2.Vector3D, _Mapping]] = ..., start: _Optional[float] = ..., length: _Optional[float] = ..., mtrl_guid: _Optional[str] = ..., diameter: _Optional[float] = ..., pre_stress: _Optional[float] = ...) -> None: ...

class HorPos(_message.Message):
    __slots__ = ["end", "start"]
    END_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    end: int
    start: int
    def __init__(self, start: _Optional[int] = ..., end: _Optional[int] = ...) -> None: ...

class Layer(_message.Message):
    __slots__ = ["d", "distr", "grp_guid", "id", "level", "min_free_space", "num", "s", "zone"]
    DISTR_FIELD_NUMBER: _ClassVar[int]
    D_FIELD_NUMBER: _ClassVar[int]
    GRP_GUID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    MIN_FREE_SPACE_FIELD_NUMBER: _ClassVar[int]
    NUM_FIELD_NUMBER: _ClassVar[int]
    S_FIELD_NUMBER: _ClassVar[int]
    ZONE_FIELD_NUMBER: _ClassVar[int]
    d: int
    distr: Distribution
    grp_guid: str
    id: _utils_pb2_1.ID
    level: int
    min_free_space: int
    num: int
    s: int
    zone: _concrete_pb2.BeamSide
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., grp_guid: _Optional[str] = ..., level: _Optional[int] = ..., num: _Optional[int] = ..., s: _Optional[int] = ..., zone: _Optional[_Union[_concrete_pb2.BeamSide, str]] = ..., min_free_space: _Optional[int] = ..., d: _Optional[int] = ..., distr: _Optional[_Union[Distribution, str]] = ...) -> None: ...

class Straight(_message.Message):
    __slots__ = ["guid", "h_pos", "lay_guid", "pre_stress", "v_pos"]
    GUID_FIELD_NUMBER: _ClassVar[int]
    H_POS_FIELD_NUMBER: _ClassVar[int]
    LAY_GUID_FIELD_NUMBER: _ClassVar[int]
    PRE_STRESS_FIELD_NUMBER: _ClassVar[int]
    V_POS_FIELD_NUMBER: _ClassVar[int]
    guid: str
    h_pos: HorPos
    lay_guid: str
    pre_stress: float
    v_pos: VertPos
    def __init__(self, guid: _Optional[str] = ..., lay_guid: _Optional[str] = ..., v_pos: _Optional[_Union[VertPos, str]] = ..., h_pos: _Optional[_Union[HorPos, _Mapping]] = ..., pre_stress: _Optional[float] = ...) -> None: ...

class BarProfile(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class WireProfile(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class VertPos(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Distribution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
