from Utils import utils_pb2 as _utils_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Geometry import reinf_pb2 as _reinf_pb2
from Utils import utils_pb2 as _utils_pb2_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1
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
from Geometry.reinf_pb2 import HorPos
from Geometry.reinf_pb2 import Straight
from Geometry.reinf_pb2 import Group
from Geometry.reinf_pb2 import Layer
from Geometry.reinf_pb2 import BarProfile
from Geometry.reinf_pb2 import WireProfile
from Geometry.reinf_pb2 import VertPos
from Geometry.reinf_pb2 import Distribution
BAR_PROFILE_RIBBED: _reinf_pb2.BarProfile
BAR_PROFILE_SMOOTH: _reinf_pb2.BarProfile
BAR_PROFILE_UNSPECIFIED: _reinf_pb2.BarProfile
DESCRIPTOR: _descriptor.FileDescriptor
DISTRIBUTION_DENSE_2A: _reinf_pb2.Distribution
DISTRIBUTION_DENSE_2B: _reinf_pb2.Distribution
DISTRIBUTION_DENSE_3: _reinf_pb2.Distribution
DISTRIBUTION_EVEN: _reinf_pb2.Distribution
DISTRIBUTION_MID: _reinf_pb2.Distribution
DISTRIBUTION_UNSPECIFIED: _reinf_pb2.Distribution
OWNER_COMPANY: _utils_pb2_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1.Owner
OWNER_USER: _utils_pb2_1_1.Owner
VERT_POS_BOTTOM: _reinf_pb2.VertPos
VERT_POS_CENTER: _reinf_pb2.VertPos
VERT_POS_TOP: _reinf_pb2.VertPos
VERT_POS_UNSPECIFIED: _reinf_pb2.VertPos
WIRE_PROFILE_K7: _reinf_pb2.WireProfile
WIRE_PROFILE_SINGLE: _reinf_pb2.WireProfile
WIRE_PROFILE_UNSPECIFIED: _reinf_pb2.WireProfile

class Data(_message.Message):
    __slots__ = ["link_grps"]
    LINK_GRPS_FIELD_NUMBER: _ClassVar[int]
    link_grps: _containers.RepeatedCompositeFieldContainer[Group]
    def __init__(self, link_grps: _Optional[_Iterable[_Union[Group, _Mapping]]] = ...) -> None: ...

class Group(_message.Message):
    __slots__ = ["angle", "diameter", "direction", "id", "legs", "length", "mtrl_guid", "s", "shape", "start"]
    ANGLE_FIELD_NUMBER: _ClassVar[int]
    DIAMETER_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LEGS_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    MTRL_GUID_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    S_FIELD_NUMBER: _ClassVar[int]
    angle: float
    diameter: float
    direction: _geometry_pb2_1.Vector3D
    id: _utils_pb2_1_1.ID
    legs: int
    length: float
    mtrl_guid: str
    s: float
    shape: _containers.RepeatedCompositeFieldContainer[_geometry_pb2_1.Point2D]
    start: float
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1.ID, _Mapping]] = ..., direction: _Optional[_Union[_geometry_pb2_1.Vector3D, _Mapping]] = ..., start: _Optional[float] = ..., s: _Optional[float] = ..., length: _Optional[float] = ..., mtrl_guid: _Optional[str] = ..., diameter: _Optional[float] = ..., shape: _Optional[_Iterable[_Union[_geometry_pb2_1.Point2D, _Mapping]]] = ..., legs: _Optional[int] = ..., angle: _Optional[float] = ...) -> None: ...
