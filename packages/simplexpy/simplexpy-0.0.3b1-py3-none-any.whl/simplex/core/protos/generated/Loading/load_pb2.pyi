from Utils import utils_pb2 as _utils_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Utils import utils_pb2 as _utils_pb2_1
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
DESCRIPTOR: _descriptor.FileDescriptor
DISTRIBUTION_TYPE_LINE: DistributionType
DISTRIBUTION_TYPE_NODE: DistributionType
DISTRIBUTION_TYPE_POINT: DistributionType
DISTRIBUTION_TYPE_SURFACE: DistributionType
DISTRIBUTION_TYPE_UNSPECIFIED: DistributionType
DISTRIBUTION_TYPE_VOLUME: DistributionType
OWNER_COMPANY: _utils_pb2_1.Owner
OWNER_OFFICE: _utils_pb2_1.Owner
OWNER_STRUSOFT: _utils_pb2_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1.Owner
OWNER_USER: _utils_pb2_1.Owner
TYPE_BODY_FORCE: Type
TYPE_FORCE: Type
TYPE_MOMENT: Type
TYPE_PRESSURE: Type
TYPE_SOIL_FORCE: Type
TYPE_TEMPERATURE: Type
TYPE_UNSPECIFIED: Type

class Data(_message.Message):
    __slots__ = ["assigned_objects", "direction", "distribution", "id", "lcase_guid", "positions", "type", "values"]
    ASSIGNED_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LCASE_GUID_FIELD_NUMBER: _ClassVar[int]
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    assigned_objects: _containers.RepeatedScalarFieldContainer[str]
    direction: _geometry_pb2.Vector3D
    distribution: DistributionType
    id: _utils_pb2_1.ID
    lcase_guid: str
    positions: _containers.RepeatedCompositeFieldContainer[_geometry_pb2.Point3D]
    type: Type
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., type: _Optional[_Union[Type, str]] = ..., distribution: _Optional[_Union[DistributionType, str]] = ..., direction: _Optional[_Union[_geometry_pb2.Vector3D, _Mapping]] = ..., positions: _Optional[_Iterable[_Union[_geometry_pb2.Point3D, _Mapping]]] = ..., values: _Optional[_Iterable[float]] = ..., lcase_guid: _Optional[str] = ..., assigned_objects: _Optional[_Iterable[str]] = ...) -> None: ...

class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DistributionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
