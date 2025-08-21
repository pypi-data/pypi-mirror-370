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
    __slots__ = ["grps", "lays", "strands"]
    GRPS_FIELD_NUMBER: _ClassVar[int]
    LAYS_FIELD_NUMBER: _ClassVar[int]
    STRANDS_FIELD_NUMBER: _ClassVar[int]
    grps: _containers.RepeatedCompositeFieldContainer[_reinf_pb2.Group]
    lays: _containers.RepeatedCompositeFieldContainer[_reinf_pb2.Layer]
    strands: _containers.RepeatedCompositeFieldContainer[_reinf_pb2.Straight]
    def __init__(self, strands: _Optional[_Iterable[_Union[_reinf_pb2.Straight, _Mapping]]] = ..., grps: _Optional[_Iterable[_Union[_reinf_pb2.Group, _Mapping]]] = ..., lays: _Optional[_Iterable[_Union[_reinf_pb2.Layer, _Mapping]]] = ...) -> None: ...
