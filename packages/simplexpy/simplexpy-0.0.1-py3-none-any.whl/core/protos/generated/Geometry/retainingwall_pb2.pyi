from Utils import utils_pb2 as _utils_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Geometry import rebar_pb2 as _rebar_pb2
from Utils import utils_pb2 as _utils_pb2_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1
from Geometry import reinf_pb2 as _reinf_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
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
DESCRIPTOR: _descriptor.FileDescriptor
OWNER_COMPANY: _utils_pb2_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1.Owner
OWNER_USER: _utils_pb2_1_1.Owner
TYPE_L: Type
TYPE_L_WITH_HAUNCH: Type
TYPE_T: Type
TYPE_T_WITH_HAUNCH: Type
TYPE_UNSPECIFIED: Type

class AdvancedGeometry(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Data(_message.Message):
    __slots__ = ["active_borehole_guid", "bed_module", "elements", "haunch_rebars", "heel_rebars", "id", "mtrl_guid", "passive_borehole__guid", "support_guid", "toe_rebars", "use_passive", "wall_geometry", "wall_rebars"]
    ACTIVE_BOREHOLE_GUID_FIELD_NUMBER: _ClassVar[int]
    BED_MODULE_FIELD_NUMBER: _ClassVar[int]
    ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    HAUNCH_REBARS_FIELD_NUMBER: _ClassVar[int]
    HEEL_REBARS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MTRL_GUID_FIELD_NUMBER: _ClassVar[int]
    PASSIVE_BOREHOLE__GUID_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_GUID_FIELD_NUMBER: _ClassVar[int]
    TOE_REBARS_FIELD_NUMBER: _ClassVar[int]
    USE_PASSIVE_FIELD_NUMBER: _ClassVar[int]
    WALL_GEOMETRY_FIELD_NUMBER: _ClassVar[int]
    WALL_REBARS_FIELD_NUMBER: _ClassVar[int]
    active_borehole_guid: str
    bed_module: float
    elements: Elements
    haunch_rebars: _rebar_pb2.Data
    heel_rebars: _rebar_pb2.Data
    id: _utils_pb2_1_1.ID
    mtrl_guid: str
    passive_borehole__guid: str
    support_guid: str
    toe_rebars: _rebar_pb2.Data
    use_passive: bool
    wall_geometry: WallGeometry
    wall_rebars: _rebar_pb2.Data
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1.ID, _Mapping]] = ..., bed_module: _Optional[float] = ..., active_borehole_guid: _Optional[str] = ..., passive_borehole__guid: _Optional[str] = ..., wall_geometry: _Optional[_Union[WallGeometry, _Mapping]] = ..., elements: _Optional[_Union[Elements, _Mapping]] = ..., use_passive: bool = ..., support_guid: _Optional[str] = ..., mtrl_guid: _Optional[str] = ..., wall_rebars: _Optional[_Union[_rebar_pb2.Data, _Mapping]] = ..., haunch_rebars: _Optional[_Union[_rebar_pb2.Data, _Mapping]] = ..., toe_rebars: _Optional[_Union[_rebar_pb2.Data, _Mapping]] = ..., heel_rebars: _Optional[_Union[_rebar_pb2.Data, _Mapping]] = ...) -> None: ...

class Elements(_message.Message):
    __slots__ = ["haunch_guid", "heel_guid", "heel_section_forces", "toe_guid", "toe_section_forces", "wall_guid", "wall_section_forces"]
    HAUNCH_GUID_FIELD_NUMBER: _ClassVar[int]
    HEEL_GUID_FIELD_NUMBER: _ClassVar[int]
    HEEL_SECTION_FORCES_FIELD_NUMBER: _ClassVar[int]
    TOE_GUID_FIELD_NUMBER: _ClassVar[int]
    TOE_SECTION_FORCES_FIELD_NUMBER: _ClassVar[int]
    WALL_GUID_FIELD_NUMBER: _ClassVar[int]
    WALL_SECTION_FORCES_FIELD_NUMBER: _ClassVar[int]
    haunch_guid: str
    heel_guid: str
    heel_section_forces: _containers.RepeatedScalarFieldContainer[float]
    toe_guid: str
    toe_section_forces: _containers.RepeatedScalarFieldContainer[float]
    wall_guid: str
    wall_section_forces: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, wall_guid: _Optional[str] = ..., haunch_guid: _Optional[str] = ..., toe_guid: _Optional[str] = ..., heel_guid: _Optional[str] = ..., toe_section_forces: _Optional[_Iterable[float]] = ..., heel_section_forces: _Optional[_Iterable[float]] = ..., wall_section_forces: _Optional[_Iterable[float]] = ...) -> None: ...

class SimpleGeometry(_message.Message):
    __slots__ = ["haunch_height", "haunch_rigth_width", "heel_heigth_right", "heel_width", "length", "toe_heel_height", "toe_height_left", "toe_width", "type", "wall_haunch_left_width", "wall_height", "wall_right_width", "wall_top_width"]
    HAUNCH_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    HAUNCH_RIGTH_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEEL_HEIGTH_RIGHT_FIELD_NUMBER: _ClassVar[int]
    HEEL_WIDTH_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    TOE_HEEL_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    TOE_HEIGHT_LEFT_FIELD_NUMBER: _ClassVar[int]
    TOE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    WALL_HAUNCH_LEFT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    WALL_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WALL_RIGHT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    WALL_TOP_WIDTH_FIELD_NUMBER: _ClassVar[int]
    haunch_height: float
    haunch_rigth_width: float
    heel_heigth_right: float
    heel_width: float
    length: float
    toe_heel_height: float
    toe_height_left: float
    toe_width: float
    type: Type
    wall_haunch_left_width: float
    wall_height: float
    wall_right_width: float
    wall_top_width: float
    def __init__(self, type: _Optional[_Union[Type, str]] = ..., toe_width: _Optional[float] = ..., heel_width: _Optional[float] = ..., toe_height_left: _Optional[float] = ..., toe_heel_height: _Optional[float] = ..., heel_heigth_right: _Optional[float] = ..., haunch_height: _Optional[float] = ..., wall_height: _Optional[float] = ..., wall_haunch_left_width: _Optional[float] = ..., wall_top_width: _Optional[float] = ..., wall_right_width: _Optional[float] = ..., haunch_rigth_width: _Optional[float] = ..., length: _Optional[float] = ...) -> None: ...

class WallGeometry(_message.Message):
    __slots__ = ["advanced", "center", "n", "simple"]
    ADVANCED_FIELD_NUMBER: _ClassVar[int]
    CENTER_FIELD_NUMBER: _ClassVar[int]
    N_FIELD_NUMBER: _ClassVar[int]
    SIMPLE_FIELD_NUMBER: _ClassVar[int]
    advanced: AdvancedGeometry
    center: _geometry_pb2_1.Point3D
    n: _geometry_pb2_1.Vector2D
    simple: SimpleGeometry
    def __init__(self, simple: _Optional[_Union[SimpleGeometry, _Mapping]] = ..., advanced: _Optional[_Union[AdvancedGeometry, _Mapping]] = ..., center: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., n: _Optional[_Union[_geometry_pb2_1.Vector2D, _Mapping]] = ...) -> None: ...

class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
