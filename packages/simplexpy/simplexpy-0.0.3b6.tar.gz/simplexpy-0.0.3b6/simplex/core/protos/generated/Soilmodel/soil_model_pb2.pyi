from Utils import utils_pb2 as _utils_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Utils import utils_pb2 as _utils_pb2_1
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
DESCRIPTOR: _descriptor.FileDescriptor
OWNER_COMPANY: _utils_pb2_1.Owner
OWNER_OFFICE: _utils_pb2_1.Owner
OWNER_STRUSOFT: _utils_pb2_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1.Owner
OWNER_USER: _utils_pb2_1.Owner

class AllowedSoilPressure(_message.Message):
    __slots__ = ["allowed_soil_pressure_sls", "allowed_soil_pressure_uls", "friction_coef"]
    ALLOWED_SOIL_PRESSURE_SLS_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_SOIL_PRESSURE_ULS_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEF_FIELD_NUMBER: _ClassVar[int]
    allowed_soil_pressure_sls: float
    allowed_soil_pressure_uls: float
    friction_coef: float
    def __init__(self, allowed_soil_pressure_sls: _Optional[float] = ..., allowed_soil_pressure_uls: _Optional[float] = ..., friction_coef: _Optional[float] = ...) -> None: ...

class Borehole(_message.Message):
    __slots__ = ["beta", "final_ground_level", "ground_water_levels", "id", "placement", "soil_guid", "soil_stratum_top_levels", "top_of_slope_final_ground_level"]
    BETA_FIELD_NUMBER: _ClassVar[int]
    FINAL_GROUND_LEVEL_FIELD_NUMBER: _ClassVar[int]
    GROUND_WATER_LEVELS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PLACEMENT_FIELD_NUMBER: _ClassVar[int]
    SOIL_GUID_FIELD_NUMBER: _ClassVar[int]
    SOIL_STRATUM_TOP_LEVELS_FIELD_NUMBER: _ClassVar[int]
    TOP_OF_SLOPE_FINAL_GROUND_LEVEL_FIELD_NUMBER: _ClassVar[int]
    beta: float
    final_ground_level: float
    ground_water_levels: _containers.RepeatedScalarFieldContainer[float]
    id: _utils_pb2_1.ID
    placement: _geometry_pb2.Point2D
    soil_guid: str
    soil_stratum_top_levels: _containers.RepeatedScalarFieldContainer[float]
    top_of_slope_final_ground_level: float
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., soil_guid: _Optional[str] = ..., placement: _Optional[_Union[_geometry_pb2.Point2D, _Mapping]] = ..., final_ground_level: _Optional[float] = ..., beta: _Optional[float] = ..., top_of_slope_final_ground_level: _Optional[float] = ..., ground_water_levels: _Optional[_Iterable[float]] = ..., soil_stratum_top_levels: _Optional[_Iterable[float]] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["bore_holes", "ground_waters", "soil_stratums", "soils"]
    BORE_HOLES_FIELD_NUMBER: _ClassVar[int]
    GROUND_WATERS_FIELD_NUMBER: _ClassVar[int]
    SOILS_FIELD_NUMBER: _ClassVar[int]
    SOIL_STRATUMS_FIELD_NUMBER: _ClassVar[int]
    bore_holes: _containers.RepeatedCompositeFieldContainer[Borehole]
    ground_waters: _containers.RepeatedCompositeFieldContainer[GroundWater]
    soil_stratums: _containers.RepeatedCompositeFieldContainer[SoilStratum]
    soils: _containers.RepeatedCompositeFieldContainer[Soil]
    def __init__(self, soils: _Optional[_Iterable[_Union[Soil, _Mapping]]] = ..., bore_holes: _Optional[_Iterable[_Union[Borehole, _Mapping]]] = ..., soil_stratums: _Optional[_Iterable[_Union[SoilStratum, _Mapping]]] = ..., ground_waters: _Optional[_Iterable[_Union[GroundWater, _Mapping]]] = ...) -> None: ...

class GroundWater(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2_1.ID
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ...) -> None: ...

class Soil(_message.Message):
    __slots__ = ["allowed_soil_pressure", "default_filling_guid", "ground_water_guids", "id", "limit_depth", "perform_soil_calculations", "soil_stratum_guids"]
    ALLOWED_SOIL_PRESSURE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_FILLING_GUID_FIELD_NUMBER: _ClassVar[int]
    GROUND_WATER_GUIDS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_DEPTH_FIELD_NUMBER: _ClassVar[int]
    PERFORM_SOIL_CALCULATIONS_FIELD_NUMBER: _ClassVar[int]
    SOIL_STRATUM_GUIDS_FIELD_NUMBER: _ClassVar[int]
    allowed_soil_pressure: AllowedSoilPressure
    default_filling_guid: str
    ground_water_guids: _containers.RepeatedScalarFieldContainer[str]
    id: _utils_pb2_1.ID
    limit_depth: float
    perform_soil_calculations: bool
    soil_stratum_guids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., perform_soil_calculations: bool = ..., limit_depth: _Optional[float] = ..., default_filling_guid: _Optional[str] = ..., ground_water_guids: _Optional[_Iterable[str]] = ..., soil_stratum_guids: _Optional[_Iterable[str]] = ..., allowed_soil_pressure: _Optional[_Union[AllowedSoilPressure, _Mapping]] = ...) -> None: ...

class SoilStratum(_message.Message):
    __slots__ = ["id", "soil_material_guid"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_MATERIAL_GUID_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2_1.ID
    soil_material_guid: str
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., soil_material_guid: _Optional[str] = ...) -> None: ...
