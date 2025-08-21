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
OWNER_COMPANY: _utils_pb2_1.Owner
OWNER_OFFICE: _utils_pb2_1.Owner
OWNER_STRUSOFT: _utils_pb2_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1.Owner
OWNER_USER: _utils_pb2_1.Owner
STIFFNESS_TYPE_FREE: StiffnessType
STIFFNESS_TYPE_RIGID: StiffnessType
STIFFNESS_TYPE_SPRING: StiffnessType
STIFFNESS_TYPE_UNSPECIFIED: StiffnessType

class Block(_message.Message):
    __slots__ = ["id", "surface"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SURFACE_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2_1.ID
    surface: Surface
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., surface: _Optional[_Union[Surface, _Mapping]] = ...) -> None: ...

class ConNode(_message.Message):
    __slots__ = ["coord", "guids", "id"]
    COORD_FIELD_NUMBER: _ClassVar[int]
    GUIDS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    coord: _geometry_pb2.Point3D
    guids: _containers.RepeatedScalarFieldContainer[str]
    id: _utils_pb2_1.ID
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., coord: _Optional[_Union[_geometry_pb2.Point3D, _Mapping]] = ..., guids: _Optional[_Iterable[str]] = ...) -> None: ...

class Connectivity(_message.Message):
    __slots__ = ["local_coord_sys", "rot_x", "rot_y", "rot_z", "trans_x", "trans_y", "trans_z"]
    LOCAL_COORD_SYS_FIELD_NUMBER: _ClassVar[int]
    ROT_X_FIELD_NUMBER: _ClassVar[int]
    ROT_Y_FIELD_NUMBER: _ClassVar[int]
    ROT_Z_FIELD_NUMBER: _ClassVar[int]
    TRANS_X_FIELD_NUMBER: _ClassVar[int]
    TRANS_Y_FIELD_NUMBER: _ClassVar[int]
    TRANS_Z_FIELD_NUMBER: _ClassVar[int]
    local_coord_sys: _geometry_pb2.Orientation
    rot_x: Stiffness
    rot_y: Stiffness
    rot_z: Stiffness
    trans_x: Stiffness
    trans_y: Stiffness
    trans_z: Stiffness
    def __init__(self, local_coord_sys: _Optional[_Union[_geometry_pb2.Orientation, _Mapping]] = ..., trans_x: _Optional[_Union[Stiffness, _Mapping]] = ..., trans_y: _Optional[_Union[Stiffness, _Mapping]] = ..., trans_z: _Optional[_Union[Stiffness, _Mapping]] = ..., rot_x: _Optional[_Union[Stiffness, _Mapping]] = ..., rot_y: _Optional[_Union[Stiffness, _Mapping]] = ..., rot_z: _Optional[_Union[Stiffness, _Mapping]] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["block", "face", "id", "line", "polyline"]
    BLOCK_FIELD_NUMBER: _ClassVar[int]
    FACE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    POLYLINE_FIELD_NUMBER: _ClassVar[int]
    block: Block
    face: Face
    id: _utils_pb2_1.ID
    line: Line
    polyline: PolyLine
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., line: _Optional[_Union[Line, _Mapping]] = ..., polyline: _Optional[_Union[PolyLine, _Mapping]] = ..., face: _Optional[_Union[Face, _Mapping]] = ..., block: _Optional[_Union[Block, _Mapping]] = ...) -> None: ...

class ElementNode(_message.Message):
    __slots__ = ["coord", "id"]
    COORD_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    coord: _geometry_pb2.Point3D
    id: _utils_pb2_1.ID
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., coord: _Optional[_Union[_geometry_pb2.Point3D, _Mapping]] = ...) -> None: ...

class Face(_message.Message):
    __slots__ = ["holes", "id", "orientation", "perimeter"]
    HOLES_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    PERIMETER_FIELD_NUMBER: _ClassVar[int]
    holes: _containers.RepeatedCompositeFieldContainer[PolyLine]
    id: _utils_pb2_1.ID
    orientation: _geometry_pb2.Orientation
    perimeter: PolyLine
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., perimeter: _Optional[_Union[PolyLine, _Mapping]] = ..., holes: _Optional[_Iterable[_Union[PolyLine, _Mapping]]] = ..., orientation: _Optional[_Union[_geometry_pb2.Orientation, _Mapping]] = ...) -> None: ...

class Line(_message.Message):
    __slots__ = ["end_node_guid", "id", "start_node_guid"]
    END_NODE_GUID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    START_NODE_GUID_FIELD_NUMBER: _ClassVar[int]
    end_node_guid: str
    id: _utils_pb2_1.ID
    start_node_guid: str
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., start_node_guid: _Optional[str] = ..., end_node_guid: _Optional[str] = ...) -> None: ...

class PolyLine(_message.Message):
    __slots__ = ["id", "node_guids"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NODE_GUIDS_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2_1.ID
    node_guids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., node_guids: _Optional[_Iterable[str]] = ...) -> None: ...

class Stiffness(_message.Message):
    __slots__ = ["type", "value"]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    type: StiffnessType
    value: float
    def __init__(self, value: _Optional[float] = ..., type: _Optional[_Union[StiffnessType, str]] = ...) -> None: ...

class Surface(_message.Message):
    __slots__ = ["id", "shells"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SHELLS_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2_1.ID
    shells: _containers.RepeatedCompositeFieldContainer[PolyLine]
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., shells: _Optional[_Iterable[_Union[PolyLine, _Mapping]]] = ...) -> None: ...

class StiffnessType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
