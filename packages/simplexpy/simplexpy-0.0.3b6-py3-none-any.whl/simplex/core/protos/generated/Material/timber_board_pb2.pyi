from Utils import utils_pb2 as _utils_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
DESCRIPTOR: _descriptor.FileDescriptor
OWNER_COMPANY: _utils_pb2.Owner
OWNER_OFFICE: _utils_pb2.Owner
OWNER_STRUSOFT: _utils_pb2.Owner
OWNER_UNSPECIFIED: _utils_pb2.Owner
OWNER_USER: _utils_pb2.Owner

class CharacteristicData(_message.Message):
    __slots__ = ["bending_parallel", "bending_perpendicular", "compression_parallel", "compression_perpendicular", "density", "elasticity_bending_parallel", "elasticity_bending_perpendicular", "elasticity_compression_parallel", "elasticity_compression_perpendicular", "elasticity_tension_parallel", "elasticity_tension_perpendicular", "panel_shear", "panel_shear_modulus", "planar_shear", "planar_shear_modulus", "tension_parallel", "tension_perpendicular"]
    BENDING_PARALLEL_FIELD_NUMBER: _ClassVar[int]
    BENDING_PERPENDICULAR_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_PARALLEL_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_PERPENDICULAR_FIELD_NUMBER: _ClassVar[int]
    DENSITY_FIELD_NUMBER: _ClassVar[int]
    ELASTICITY_BENDING_PARALLEL_FIELD_NUMBER: _ClassVar[int]
    ELASTICITY_BENDING_PERPENDICULAR_FIELD_NUMBER: _ClassVar[int]
    ELASTICITY_COMPRESSION_PARALLEL_FIELD_NUMBER: _ClassVar[int]
    ELASTICITY_COMPRESSION_PERPENDICULAR_FIELD_NUMBER: _ClassVar[int]
    ELASTICITY_TENSION_PARALLEL_FIELD_NUMBER: _ClassVar[int]
    ELASTICITY_TENSION_PERPENDICULAR_FIELD_NUMBER: _ClassVar[int]
    PANEL_SHEAR_FIELD_NUMBER: _ClassVar[int]
    PANEL_SHEAR_MODULUS_FIELD_NUMBER: _ClassVar[int]
    PLANAR_SHEAR_FIELD_NUMBER: _ClassVar[int]
    PLANAR_SHEAR_MODULUS_FIELD_NUMBER: _ClassVar[int]
    TENSION_PARALLEL_FIELD_NUMBER: _ClassVar[int]
    TENSION_PERPENDICULAR_FIELD_NUMBER: _ClassVar[int]
    bending_parallel: float
    bending_perpendicular: float
    compression_parallel: float
    compression_perpendicular: float
    density: float
    elasticity_bending_parallel: float
    elasticity_bending_perpendicular: float
    elasticity_compression_parallel: float
    elasticity_compression_perpendicular: float
    elasticity_tension_parallel: float
    elasticity_tension_perpendicular: float
    panel_shear: float
    panel_shear_modulus: float
    planar_shear: float
    planar_shear_modulus: float
    tension_parallel: float
    tension_perpendicular: float
    def __init__(self, bending_parallel: _Optional[float] = ..., bending_perpendicular: _Optional[float] = ..., tension_parallel: _Optional[float] = ..., tension_perpendicular: _Optional[float] = ..., compression_parallel: _Optional[float] = ..., compression_perpendicular: _Optional[float] = ..., panel_shear: _Optional[float] = ..., planar_shear: _Optional[float] = ..., elasticity_bending_parallel: _Optional[float] = ..., elasticity_bending_perpendicular: _Optional[float] = ..., elasticity_tension_parallel: _Optional[float] = ..., elasticity_tension_perpendicular: _Optional[float] = ..., elasticity_compression_parallel: _Optional[float] = ..., elasticity_compression_perpendicular: _Optional[float] = ..., panel_shear_modulus: _Optional[float] = ..., planar_shear_modulus: _Optional[float] = ..., density: _Optional[float] = ...) -> None: ...
