from Utils import utils_pb2 as _utils_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
DESCRIPTOR: _descriptor.FileDescriptor
OWNER_COMPANY: _utils_pb2.Owner
OWNER_OFFICE: _utils_pb2.Owner
OWNER_STRUSOFT: _utils_pb2.Owner
OWNER_UNSPECIFIED: _utils_pb2.Owner
OWNER_USER: _utils_pb2.Owner

class Arc2D(_message.Message):
    __slots__ = ["center", "end_angle", "id", "radius", "start_angle"]
    CENTER_FIELD_NUMBER: _ClassVar[int]
    END_ANGLE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    START_ANGLE_FIELD_NUMBER: _ClassVar[int]
    center: Point2D
    end_angle: float
    id: _utils_pb2.ID
    radius: float
    start_angle: float
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., center: _Optional[_Union[Point2D, _Mapping]] = ..., radius: _Optional[float] = ..., start_angle: _Optional[float] = ..., end_angle: _Optional[float] = ...) -> None: ...

class Arc3D(_message.Message):
    __slots__ = ["center", "end_angle", "id", "normal", "radius", "start_angle"]
    CENTER_FIELD_NUMBER: _ClassVar[int]
    END_ANGLE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NORMAL_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    START_ANGLE_FIELD_NUMBER: _ClassVar[int]
    center: Point3D
    end_angle: float
    id: _utils_pb2.ID
    normal: Vector3D
    radius: float
    start_angle: float
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., center: _Optional[_Union[Point3D, _Mapping]] = ..., normal: _Optional[_Union[Vector3D, _Mapping]] = ..., radius: _Optional[float] = ..., start_angle: _Optional[float] = ..., end_angle: _Optional[float] = ...) -> None: ...

class Block(_message.Message):
    __slots__ = ["id", "surfaces"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SURFACES_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2.ID
    surfaces: _containers.RepeatedCompositeFieldContainer[LineFace3D]
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., surfaces: _Optional[_Iterable[_Union[LineFace3D, _Mapping]]] = ...) -> None: ...

class Circle2D(_message.Message):
    __slots__ = ["center", "id", "radius"]
    CENTER_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    center: Point2D
    id: _utils_pb2.ID
    radius: float
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., center: _Optional[_Union[Point2D, _Mapping]] = ..., radius: _Optional[float] = ...) -> None: ...

class Circle3D(_message.Message):
    __slots__ = ["center", "id", "normal", "radius"]
    CENTER_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NORMAL_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    center: Point3D
    id: _utils_pb2.ID
    normal: Vector3D
    radius: float
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., center: _Optional[_Union[Point3D, _Mapping]] = ..., normal: _Optional[_Union[Vector3D, _Mapping]] = ..., radius: _Optional[float] = ...) -> None: ...

class Curve2D(_message.Message):
    __slots__ = ["arc_segment", "circle_segment", "id", "line_segment"]
    ARC_SEGMENT_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_SEGMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LINE_SEGMENT_FIELD_NUMBER: _ClassVar[int]
    arc_segment: Arc2D
    circle_segment: Circle2D
    id: _utils_pb2.ID
    line_segment: Line2D
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., arc_segment: _Optional[_Union[Arc2D, _Mapping]] = ..., circle_segment: _Optional[_Union[Circle2D, _Mapping]] = ..., line_segment: _Optional[_Union[Line2D, _Mapping]] = ...) -> None: ...

class Curve3D(_message.Message):
    __slots__ = ["arc_segment", "circle_segments", "id", "line_segment"]
    ARC_SEGMENT_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_SEGMENTS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LINE_SEGMENT_FIELD_NUMBER: _ClassVar[int]
    arc_segment: Arc3D
    circle_segments: Circle3D
    id: _utils_pb2.ID
    line_segment: Line3D
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., arc_segment: _Optional[_Union[Arc3D, _Mapping]] = ..., circle_segments: _Optional[_Union[Circle3D, _Mapping]] = ..., line_segment: _Optional[_Union[Line3D, _Mapping]] = ...) -> None: ...

class CurveFace2D(_message.Message):
    __slots__ = ["additional_perimeters", "holes", "id", "perimeter"]
    ADDITIONAL_PERIMETERS_FIELD_NUMBER: _ClassVar[int]
    HOLES_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PERIMETER_FIELD_NUMBER: _ClassVar[int]
    additional_perimeters: _containers.RepeatedCompositeFieldContainer[PolyCurve2D]
    holes: _containers.RepeatedCompositeFieldContainer[PolyCurve2D]
    id: _utils_pb2.ID
    perimeter: PolyCurve2D
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., perimeter: _Optional[_Union[PolyCurve2D, _Mapping]] = ..., holes: _Optional[_Iterable[_Union[PolyCurve2D, _Mapping]]] = ..., additional_perimeters: _Optional[_Iterable[_Union[PolyCurve2D, _Mapping]]] = ...) -> None: ...

class CurveFace3D(_message.Message):
    __slots__ = ["holes", "id", "perimeter"]
    HOLES_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PERIMETER_FIELD_NUMBER: _ClassVar[int]
    holes: _containers.RepeatedCompositeFieldContainer[PolyCurve3D]
    id: _utils_pb2.ID
    perimeter: PolyCurve3D
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., perimeter: _Optional[_Union[PolyCurve3D, _Mapping]] = ..., holes: _Optional[_Iterable[_Union[PolyCurve3D, _Mapping]]] = ...) -> None: ...

class Line2D(_message.Message):
    __slots__ = ["end", "id", "start"]
    END_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    end: Point2D
    id: _utils_pb2.ID
    start: Point2D
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., start: _Optional[_Union[Point2D, _Mapping]] = ..., end: _Optional[_Union[Point2D, _Mapping]] = ...) -> None: ...

class Line3D(_message.Message):
    __slots__ = ["end", "id", "start"]
    END_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    end: Point3D
    id: _utils_pb2.ID
    start: Point3D
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., start: _Optional[_Union[Point3D, _Mapping]] = ..., end: _Optional[_Union[Point3D, _Mapping]] = ...) -> None: ...

class LineFace2D(_message.Message):
    __slots__ = ["additional_perimeters", "holes", "id", "perimeter"]
    ADDITIONAL_PERIMETERS_FIELD_NUMBER: _ClassVar[int]
    HOLES_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PERIMETER_FIELD_NUMBER: _ClassVar[int]
    additional_perimeters: _containers.RepeatedCompositeFieldContainer[PolyLine2D]
    holes: _containers.RepeatedCompositeFieldContainer[PolyLine2D]
    id: _utils_pb2.ID
    perimeter: PolyLine2D
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., perimeter: _Optional[_Union[PolyLine2D, _Mapping]] = ..., holes: _Optional[_Iterable[_Union[PolyLine2D, _Mapping]]] = ..., additional_perimeters: _Optional[_Iterable[_Union[PolyLine2D, _Mapping]]] = ...) -> None: ...

class LineFace3D(_message.Message):
    __slots__ = ["holes", "id", "perimeter"]
    HOLES_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PERIMETER_FIELD_NUMBER: _ClassVar[int]
    holes: _containers.RepeatedCompositeFieldContainer[PolyLine3D]
    id: _utils_pb2.ID
    perimeter: PolyLine3D
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., perimeter: _Optional[_Union[PolyLine3D, _Mapping]] = ..., holes: _Optional[_Iterable[_Union[PolyLine3D, _Mapping]]] = ...) -> None: ...

class Orientation(_message.Message):
    __slots__ = ["x_dir", "y_dir", "z_dir"]
    X_DIR_FIELD_NUMBER: _ClassVar[int]
    Y_DIR_FIELD_NUMBER: _ClassVar[int]
    Z_DIR_FIELD_NUMBER: _ClassVar[int]
    x_dir: Vector3D
    y_dir: Vector3D
    z_dir: Vector3D
    def __init__(self, x_dir: _Optional[_Union[Vector3D, _Mapping]] = ..., y_dir: _Optional[_Union[Vector3D, _Mapping]] = ..., z_dir: _Optional[_Union[Vector3D, _Mapping]] = ...) -> None: ...

class Point2D(_message.Message):
    __slots__ = ["x", "y"]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ...) -> None: ...

class Point3D(_message.Message):
    __slots__ = ["x", "y", "z"]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...

class PolyCurve2D(_message.Message):
    __slots__ = ["curves", "id"]
    CURVES_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    curves: _containers.RepeatedCompositeFieldContainer[Curve2D]
    id: _utils_pb2.ID
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., curves: _Optional[_Iterable[_Union[Curve2D, _Mapping]]] = ...) -> None: ...

class PolyCurve3D(_message.Message):
    __slots__ = ["curves", "id"]
    CURVES_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    curves: _containers.RepeatedCompositeFieldContainer[Curve3D]
    id: _utils_pb2.ID
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., curves: _Optional[_Iterable[_Union[Curve3D, _Mapping]]] = ...) -> None: ...

class PolyLine2D(_message.Message):
    __slots__ = ["id", "points"]
    ID_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2.ID
    points: _containers.RepeatedCompositeFieldContainer[Point2D]
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., points: _Optional[_Iterable[_Union[Point2D, _Mapping]]] = ...) -> None: ...

class PolyLine3D(_message.Message):
    __slots__ = ["id", "points"]
    ID_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2.ID
    points: _containers.RepeatedCompositeFieldContainer[Point3D]
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., points: _Optional[_Iterable[_Union[Point3D, _Mapping]]] = ...) -> None: ...

class Vector2D(_message.Message):
    __slots__ = ["one", "two"]
    ONE_FIELD_NUMBER: _ClassVar[int]
    TWO_FIELD_NUMBER: _ClassVar[int]
    one: float
    two: float
    def __init__(self, one: _Optional[float] = ..., two: _Optional[float] = ...) -> None: ...

class Vector3D(_message.Message):
    __slots__ = ["x", "y", "z"]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...

class VectorYZ(_message.Message):
    __slots__ = ["y", "z"]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    y: float
    z: float
    def __init__(self, y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...

class VectorYZLT(_message.Message):
    __slots__ = ["l_t", "y", "z"]
    L_T_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    l_t: float
    y: float
    z: float
    def __init__(self, y: _Optional[float] = ..., z: _Optional[float] = ..., l_t: _Optional[float] = ...) -> None: ...
