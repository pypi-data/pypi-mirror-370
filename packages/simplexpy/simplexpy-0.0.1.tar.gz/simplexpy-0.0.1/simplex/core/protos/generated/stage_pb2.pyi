from Utils import utils_pb2 as _utils_pb2
from Utils import topology_pb2 as _topology_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Geometry import geometry_pb2 as _geometry_pb2
from Geometry import geometry_pb2 as _geometry_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
from Utils.topology_pb2 import ElementNode
from Utils.topology_pb2 import ConNode
from Utils.topology_pb2 import Stiffness
from Utils.topology_pb2 import Connectivity
from Utils.topology_pb2 import Data
from Utils.topology_pb2 import Line
from Utils.topology_pb2 import PolyLine
from Utils.topology_pb2 import Face
from Utils.topology_pb2 import Surface
from Utils.topology_pb2 import Block
from Utils.topology_pb2 import StiffnessType
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
DESCRIPTOR: _descriptor.FileDescriptor
ENVIROMENTAL_CLASS_AGGRESSIVE: EnvironmentalClass
ENVIROMENTAL_CLASS_EXTRA_AGGRESSIVE: EnvironmentalClass
ENVIROMENTAL_CLASS_MODERATE: EnvironmentalClass
ENVIROMENTAL_CLASS_PASSIVE: EnvironmentalClass
ENVIROMENTAL_CLASS_UNSPECIFIED: EnvironmentalClass
EXPOSURE_CLASS_UNSPECIFIED: ExposureClass
EXPOSURE_CLASS_X0: ExposureClass
EXPOSURE_CLASS_XA1: ExposureClass
EXPOSURE_CLASS_XA2: ExposureClass
EXPOSURE_CLASS_XA3: ExposureClass
EXPOSURE_CLASS_XC1: ExposureClass
EXPOSURE_CLASS_XC2: ExposureClass
EXPOSURE_CLASS_XC3: ExposureClass
EXPOSURE_CLASS_XC4: ExposureClass
EXPOSURE_CLASS_XD1: ExposureClass
EXPOSURE_CLASS_XD2: ExposureClass
EXPOSURE_CLASS_XD3: ExposureClass
EXPOSURE_CLASS_XF1: ExposureClass
EXPOSURE_CLASS_XF2: ExposureClass
EXPOSURE_CLASS_XF3: ExposureClass
EXPOSURE_CLASS_XF4: ExposureClass
EXPOSURE_CLASS_XS1: ExposureClass
EXPOSURE_CLASS_XS2: ExposureClass
EXPOSURE_CLASS_XS3: ExposureClass
LIFE_CATEGORY_L100: LifeCategory
LIFE_CATEGORY_L20: LifeCategory
LIFE_CATEGORY_L50: LifeCategory
LIFE_CATEGORY_UNSPECIFIED: LifeCategory
OWNER_COMPANY: _utils_pb2_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1.Owner
OWNER_USER: _utils_pb2_1_1.Owner
STIFFNESS_TYPE_FREE: _topology_pb2.StiffnessType
STIFFNESS_TYPE_RIGID: _topology_pb2.StiffnessType
STIFFNESS_TYPE_SPRING: _topology_pb2.StiffnessType
STIFFNESS_TYPE_UNSPECIFIED: _topology_pb2.StiffnessType
SUPPORT_LEVEL_BOTTOM: SupportLevel
SUPPORT_LEVEL_CENTER: SupportLevel
SUPPORT_LEVEL_TOP: SupportLevel
SUPPORT_LEVEL_UNSPECIFIED: SupportLevel

class Beam(_message.Message):
    __slots__ = ["autogen_output_end", "end_con", "fraction", "positions", "start_con"]
    AUTOGEN_OUTPUT_END_FIELD_NUMBER: _ClassVar[int]
    END_CON_FIELD_NUMBER: _ClassVar[int]
    FRACTION_FIELD_NUMBER: _ClassVar[int]
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    START_CON_FIELD_NUMBER: _ClassVar[int]
    autogen_output_end: bool
    end_con: _topology_pb2.Connectivity
    fraction: bool
    positions: _containers.RepeatedScalarFieldContainer[float]
    start_con: _topology_pb2.Connectivity
    def __init__(self, fraction: bool = ..., positions: _Optional[_Iterable[float]] = ..., start_con: _Optional[_Union[_topology_pb2.Connectivity, _Mapping]] = ..., end_con: _Optional[_Union[_topology_pb2.Connectivity, _Mapping]] = ..., autogen_output_end: bool = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["dependent_stage_guid", "elems", "id", "lcomb_guids", "sups"]
    DEPENDENT_STAGE_GUID_FIELD_NUMBER: _ClassVar[int]
    ELEMS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LCOMB_GUIDS_FIELD_NUMBER: _ClassVar[int]
    SUPS_FIELD_NUMBER: _ClassVar[int]
    dependent_stage_guid: str
    elems: _containers.RepeatedCompositeFieldContainer[Element]
    id: _utils_pb2_1_1.ID
    lcomb_guids: _containers.RepeatedScalarFieldContainer[str]
    sups: _containers.RepeatedCompositeFieldContainer[Support]
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1.ID, _Mapping]] = ..., dependent_stage_guid: _Optional[str] = ..., elems: _Optional[_Iterable[_Union[Element, _Mapping]]] = ..., sups: _Optional[_Iterable[_Union[Support, _Mapping]]] = ..., lcomb_guids: _Optional[_Iterable[str]] = ...) -> None: ...

class Element(_message.Message):
    __slots__ = ["autogen_output_load", "beam", "foundation", "guid", "pile", "rc", "retaining_wall", "soil", "steel", "timber"]
    AUTOGEN_OUTPUT_LOAD_FIELD_NUMBER: _ClassVar[int]
    BEAM_FIELD_NUMBER: _ClassVar[int]
    FOUNDATION_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    PILE_FIELD_NUMBER: _ClassVar[int]
    RC_FIELD_NUMBER: _ClassVar[int]
    RETAINING_WALL_FIELD_NUMBER: _ClassVar[int]
    SOIL_FIELD_NUMBER: _ClassVar[int]
    STEEL_FIELD_NUMBER: _ClassVar[int]
    TIMBER_FIELD_NUMBER: _ClassVar[int]
    autogen_output_load: bool
    beam: Beam
    foundation: Foundation
    guid: str
    pile: Pile
    rc: RC
    retaining_wall: RetainingWall
    soil: SoilSpecific
    steel: SteelSpecific
    timber: TimberSpecific
    def __init__(self, guid: _Optional[str] = ..., beam: _Optional[_Union[Beam, _Mapping]] = ..., foundation: _Optional[_Union[Foundation, _Mapping]] = ..., retaining_wall: _Optional[_Union[RetainingWall, _Mapping]] = ..., pile: _Optional[_Union[Pile, _Mapping]] = ..., rc: _Optional[_Union[RC, _Mapping]] = ..., steel: _Optional[_Union[SteelSpecific, _Mapping]] = ..., timber: _Optional[_Union[TimberSpecific, _Mapping]] = ..., soil: _Optional[_Union[SoilSpecific, _Mapping]] = ..., autogen_output_load: bool = ...) -> None: ...

class Foundation(_message.Message):
    __slots__ = ["positions", "reference_point"]
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_POINT_FIELD_NUMBER: _ClassVar[int]
    positions: _containers.RepeatedCompositeFieldContainer[_geometry_pb2_1.Point3D]
    reference_point: _geometry_pb2_1.Point3D
    def __init__(self, reference_point: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., positions: _Optional[_Iterable[_Union[_geometry_pb2_1.Point3D, _Mapping]]] = ...) -> None: ...

class Pile(_message.Message):
    __slots__ = ["positions", "reference_point"]
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_POINT_FIELD_NUMBER: _ClassVar[int]
    positions: _containers.RepeatedCompositeFieldContainer[_geometry_pb2_1.Point3D]
    reference_point: _geometry_pb2_1.Point3D
    def __init__(self, reference_point: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., positions: _Optional[_Iterable[_Union[_geometry_pb2_1.Point3D, _Mapping]]] = ...) -> None: ...

class RC(_message.Message):
    __slots__ = ["life_category", "rc_specifics"]
    LIFE_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    RC_SPECIFICS_FIELD_NUMBER: _ClassVar[int]
    life_category: LifeCategory
    rc_specifics: _containers.RepeatedCompositeFieldContainer[RCSpecific]
    def __init__(self, rc_specifics: _Optional[_Iterable[_Union[RCSpecific, _Mapping]]] = ..., life_category: _Optional[_Union[LifeCategory, str]] = ...) -> None: ...

class RCSpecific(_message.Message):
    __slots__ = ["age", "creep", "environmental_class", "exposure_class", "guid", "shrinkage", "water_cement_ratio_index", "wet"]
    AGE_FIELD_NUMBER: _ClassVar[int]
    CREEP_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENTAL_CLASS_FIELD_NUMBER: _ClassVar[int]
    EXPOSURE_CLASS_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    SHRINKAGE_FIELD_NUMBER: _ClassVar[int]
    WATER_CEMENT_RATIO_INDEX_FIELD_NUMBER: _ClassVar[int]
    WET_FIELD_NUMBER: _ClassVar[int]
    age: int
    creep: float
    environmental_class: EnvironmentalClass
    exposure_class: ExposureClass
    guid: str
    shrinkage: float
    water_cement_ratio_index: int
    wet: bool
    def __init__(self, guid: _Optional[str] = ..., age: _Optional[int] = ..., creep: _Optional[float] = ..., shrinkage: _Optional[float] = ..., water_cement_ratio_index: _Optional[int] = ..., exposure_class: _Optional[_Union[ExposureClass, str]] = ..., environmental_class: _Optional[_Union[EnvironmentalClass, str]] = ..., wet: bool = ...) -> None: ...

class RetainingWall(_message.Message):
    __slots__ = ["positions", "reference_point"]
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_POINT_FIELD_NUMBER: _ClassVar[int]
    positions: _containers.RepeatedCompositeFieldContainer[_geometry_pb2_1.Point3D]
    reference_point: _geometry_pb2_1.Point3D
    def __init__(self, reference_point: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., positions: _Optional[_Iterable[_Union[_geometry_pb2_1.Point3D, _Mapping]]] = ...) -> None: ...

class SoilSpecific(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class SteelSpecific(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Support(_message.Message):
    __slots__ = ["con", "con_guid", "coord", "elem_con", "guid", "lateral", "support_level"]
    CON_FIELD_NUMBER: _ClassVar[int]
    CON_GUID_FIELD_NUMBER: _ClassVar[int]
    COORD_FIELD_NUMBER: _ClassVar[int]
    ELEM_CON_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    LATERAL_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_LEVEL_FIELD_NUMBER: _ClassVar[int]
    con: _topology_pb2.Connectivity
    con_guid: str
    coord: _geometry_pb2_1.Point3D
    elem_con: SupportElementConnection
    guid: str
    lateral: bool
    support_level: SupportLevel
    def __init__(self, guid: _Optional[str] = ..., coord: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., con_guid: _Optional[str] = ..., elem_con: _Optional[_Union[SupportElementConnection, _Mapping]] = ..., con: _Optional[_Union[_topology_pb2.Connectivity, _Mapping]] = ..., lateral: bool = ..., support_level: _Optional[_Union[SupportLevel, str]] = ...) -> None: ...

class SupportElementConnection(_message.Message):
    __slots__ = ["element_guid", "position"]
    ELEMENT_GUID_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    element_guid: str
    position: float
    def __init__(self, element_guid: _Optional[str] = ..., position: _Optional[float] = ...) -> None: ...

class TimberSpecific(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ExposureClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class LifeCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class EnvironmentalClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class SupportLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
