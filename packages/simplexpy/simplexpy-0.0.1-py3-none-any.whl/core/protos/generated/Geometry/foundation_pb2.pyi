from Utils import utils_pb2 as _utils_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Geometry import rebar_pb2 as _rebar_pb2
from Utils import utils_pb2 as _utils_pb2_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1
from Geometry import reinf_pb2 as _reinf_pb2
from Design import concrete_pb2 as _concrete_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

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
from Geometry.rebar_pb2 import Data
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
FABRICATION_IN_SITU: _concrete_pb2.Fabrication
FABRICATION_PREFAB: _concrete_pb2.Fabrication
FABRICATION_UNSPECIFIED: _concrete_pb2.Fabrication
FCTM_TYPE_FCTM: _concrete_pb2.FctmType
FCTM_TYPE_FCTM_FL: _concrete_pb2.FctmType
FCTM_TYPE_FCTM_XI: _concrete_pb2.FctmType
FCTM_TYPE_UNSPECIFIED: _concrete_pb2.FctmType
OWNER_COMPANY: _utils_pb2_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1.Owner
OWNER_USER: _utils_pb2_1_1.Owner
SHEAR_DESIGN_TYPE_UNSPECIFIED: _concrete_pb2.ShearDesignType
SHEAR_DESIGN_TYPE_WITHOUT_SHEAR_REINFORCEMENT: _concrete_pb2.ShearDesignType
SHEAR_DESIGN_TYPE_WITH_SHEAR_REINFORCEMENT: _concrete_pb2.ShearDesignType
SURFACE_TYPE_INDENTED: _concrete_pb2.SurfaceType
SURFACE_TYPE_ROUGH: _concrete_pb2.SurfaceType
SURFACE_TYPE_SMOOTH: _concrete_pb2.SurfaceType
SURFACE_TYPE_UNSPECIFIED: _concrete_pb2.SurfaceType
SURFACE_TYPE_VERY_SMOOTH: _concrete_pb2.SurfaceType
WEB_SHEAR_CAPACITY_METHOD_ADVANCED: _concrete_pb2.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_SIMPLIFIED: _concrete_pb2.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_STANDARD: _concrete_pb2.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_UNSPECIFIED: _concrete_pb2.WebShearCapacityMethod

class AdvancedFoundation(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Circle(_message.Message):
    __slots__ = ["diameter", "diameter_top"]
    DIAMETER_FIELD_NUMBER: _ClassVar[int]
    DIAMETER_TOP_FIELD_NUMBER: _ClassVar[int]
    diameter: float
    diameter_top: float
    def __init__(self, diameter: _Optional[float] = ..., diameter_top: _Optional[float] = ...) -> None: ...

class ConcreteParameters(_message.Message):
    __slots__ = ["mtrl_guid", "rebars"]
    MTRL_GUID_FIELD_NUMBER: _ClassVar[int]
    REBARS_FIELD_NUMBER: _ClassVar[int]
    mtrl_guid: str
    rebars: _rebar_pb2.Data
    def __init__(self, mtrl_guid: _Optional[str] = ..., rebars: _Optional[_Union[_rebar_pb2.Data, _Mapping]] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["advanced_foundation", "id", "simple_foundation"]
    ADVANCED_FOUNDATION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    SIMPLE_FOUNDATION_FIELD_NUMBER: _ClassVar[int]
    advanced_foundation: AdvancedFoundation
    id: _utils_pb2_1_1.ID
    simple_foundation: SimpleFoundation
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1.ID, _Mapping]] = ..., simple_foundation: _Optional[_Union[SimpleFoundation, _Mapping]] = ..., advanced_foundation: _Optional[_Union[AdvancedFoundation, _Mapping]] = ...) -> None: ...

class Elements(_message.Message):
    __slots__ = ["length_guid", "length_section_forces", "top_guid", "width_guid", "width_section_forces"]
    LENGTH_GUID_FIELD_NUMBER: _ClassVar[int]
    LENGTH_SECTION_FORCES_FIELD_NUMBER: _ClassVar[int]
    TOP_GUID_FIELD_NUMBER: _ClassVar[int]
    WIDTH_GUID_FIELD_NUMBER: _ClassVar[int]
    WIDTH_SECTION_FORCES_FIELD_NUMBER: _ClassVar[int]
    length_guid: str
    length_section_forces: _containers.RepeatedScalarFieldContainer[float]
    top_guid: str
    width_guid: str
    width_section_forces: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, top_guid: _Optional[str] = ..., width_guid: _Optional[str] = ..., length_guid: _Optional[str] = ..., width_section_forces: _Optional[_Iterable[float]] = ..., length_section_forces: _Optional[_Iterable[float]] = ...) -> None: ...

class FoundationGeometry(_message.Message):
    __slots__ = ["center", "height", "line_foundation", "n", "point_foundation"]
    CENTER_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    LINE_FOUNDATION_FIELD_NUMBER: _ClassVar[int]
    N_FIELD_NUMBER: _ClassVar[int]
    POINT_FOUNDATION_FIELD_NUMBER: _ClassVar[int]
    center: _geometry_pb2_1.Point3D
    height: float
    line_foundation: LineFoundation
    n: _geometry_pb2_1.Vector2D
    point_foundation: PointFoundation
    def __init__(self, height: _Optional[float] = ..., point_foundation: _Optional[_Union[PointFoundation, _Mapping]] = ..., line_foundation: _Optional[_Union[LineFoundation, _Mapping]] = ..., center: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., n: _Optional[_Union[_geometry_pb2_1.Vector2D, _Mapping]] = ...) -> None: ...

class LineFoundation(_message.Message):
    __slots__ = ["eccentricity_width_top", "width", "width_top"]
    ECCENTRICITY_WIDTH_TOP_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    WIDTH_TOP_FIELD_NUMBER: _ClassVar[int]
    eccentricity_width_top: float
    width: float
    width_top: float
    def __init__(self, width: _Optional[float] = ..., width_top: _Optional[float] = ..., eccentricity_width_top: _Optional[float] = ...) -> None: ...

class PointFoundation(_message.Message):
    __slots__ = ["circle", "rectangle"]
    CIRCLE_FIELD_NUMBER: _ClassVar[int]
    RECTANGLE_FIELD_NUMBER: _ClassVar[int]
    circle: Circle
    rectangle: Rectangle
    def __init__(self, circle: _Optional[_Union[Circle, _Mapping]] = ..., rectangle: _Optional[_Union[Rectangle, _Mapping]] = ...) -> None: ...

class Rectangle(_message.Message):
    __slots__ = ["eccentricity_length_top", "eccentricity_width_top", "length", "length_top", "width", "width_top"]
    ECCENTRICITY_LENGTH_TOP_FIELD_NUMBER: _ClassVar[int]
    ECCENTRICITY_WIDTH_TOP_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    LENGTH_TOP_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    WIDTH_TOP_FIELD_NUMBER: _ClassVar[int]
    eccentricity_length_top: float
    eccentricity_width_top: float
    length: float
    length_top: float
    width: float
    width_top: float
    def __init__(self, width: _Optional[float] = ..., length: _Optional[float] = ..., width_top: _Optional[float] = ..., length_top: _Optional[float] = ..., eccentricity_width_top: _Optional[float] = ..., eccentricity_length_top: _Optional[float] = ...) -> None: ...

class SimpleFoundation(_message.Message):
    __slots__ = ["bed_module", "borehole_guid", "concrete_parameters", "elements", "geometry", "support_guid"]
    BED_MODULE_FIELD_NUMBER: _ClassVar[int]
    BOREHOLE_GUID_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    GEOMETRY_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_GUID_FIELD_NUMBER: _ClassVar[int]
    bed_module: float
    borehole_guid: str
    concrete_parameters: ConcreteParameters
    elements: Elements
    geometry: FoundationGeometry
    support_guid: str
    def __init__(self, bed_module: _Optional[float] = ..., borehole_guid: _Optional[str] = ..., geometry: _Optional[_Union[FoundationGeometry, _Mapping]] = ..., elements: _Optional[_Union[Elements, _Mapping]] = ..., support_guid: _Optional[str] = ..., concrete_parameters: _Optional[_Union[ConcreteParameters, _Mapping]] = ...) -> None: ...
