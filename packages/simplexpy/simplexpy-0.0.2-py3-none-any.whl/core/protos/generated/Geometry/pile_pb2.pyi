from Utils import utils_pb2 as _utils_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Utils import utils_pb2 as _utils_pb2_1
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
DESCRIPTOR: _descriptor.FileDescriptor
OWNER_COMPANY: _utils_pb2_1.Owner
OWNER_OFFICE: _utils_pb2_1.Owner
OWNER_STRUSOFT: _utils_pb2_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1.Owner
OWNER_USER: _utils_pb2_1.Owner
TYPE_BORED: Type
TYPE_CFA: Type
TYPE_DRIVEN: Type
TYPE_UNSPECIFIED: Type

class Asphalt(_message.Message):
    __slots__ = ["asphalt_bottom", "asphalt_top"]
    ASPHALT_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    ASPHALT_TOP_FIELD_NUMBER: _ClassVar[int]
    asphalt_bottom: float
    asphalt_top: float
    def __init__(self, asphalt_top: _Optional[float] = ..., asphalt_bottom: _Optional[float] = ...) -> None: ...

class Circle(_message.Message):
    __slots__ = ["diameter"]
    DIAMETER_FIELD_NUMBER: _ClassVar[int]
    diameter: float
    def __init__(self, diameter: _Optional[float] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["asphalt", "bed_module", "borehole_guid", "geometry", "id", "max_negative_force", "mtrl_guid", "negative_level", "pile_type", "support_guid"]
    ASPHALT_FIELD_NUMBER: _ClassVar[int]
    BED_MODULE_FIELD_NUMBER: _ClassVar[int]
    BOREHOLE_GUID_FIELD_NUMBER: _ClassVar[int]
    GEOMETRY_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MAX_NEGATIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    MTRL_GUID_FIELD_NUMBER: _ClassVar[int]
    NEGATIVE_LEVEL_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_GUID_FIELD_NUMBER: _ClassVar[int]
    asphalt: Asphalt
    bed_module: float
    borehole_guid: str
    geometry: Geometry
    id: _utils_pb2_1.ID
    max_negative_force: float
    mtrl_guid: str
    negative_level: float
    pile_type: Type
    support_guid: str
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., bed_module: _Optional[float] = ..., borehole_guid: _Optional[str] = ..., geometry: _Optional[_Union[Geometry, _Mapping]] = ..., support_guid: _Optional[str] = ..., asphalt: _Optional[_Union[Asphalt, _Mapping]] = ..., negative_level: _Optional[float] = ..., max_negative_force: _Optional[float] = ..., pile_type: _Optional[_Union[Type, str]] = ..., mtrl_guid: _Optional[str] = ...) -> None: ...

class Geometry(_message.Message):
    __slots__ = ["bottom", "circle", "n", "rectangle", "section_guid", "top"]
    BOTTOM_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_FIELD_NUMBER: _ClassVar[int]
    N_FIELD_NUMBER: _ClassVar[int]
    RECTANGLE_FIELD_NUMBER: _ClassVar[int]
    SECTION_GUID_FIELD_NUMBER: _ClassVar[int]
    TOP_FIELD_NUMBER: _ClassVar[int]
    bottom: _geometry_pb2.Point3D
    circle: Circle
    n: _geometry_pb2.Vector2D
    rectangle: Rectangle
    section_guid: str
    top: _geometry_pb2.Point3D
    def __init__(self, circle: _Optional[_Union[Circle, _Mapping]] = ..., rectangle: _Optional[_Union[Rectangle, _Mapping]] = ..., section_guid: _Optional[str] = ..., top: _Optional[_Union[_geometry_pb2.Point3D, _Mapping]] = ..., bottom: _Optional[_Union[_geometry_pb2.Point3D, _Mapping]] = ..., n: _Optional[_Union[_geometry_pb2.Vector2D, _Mapping]] = ...) -> None: ...

class Rectangle(_message.Message):
    __slots__ = ["height", "width"]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    height: float
    width: float
    def __init__(self, width: _Optional[float] = ..., height: _Optional[float] = ...) -> None: ...

class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
