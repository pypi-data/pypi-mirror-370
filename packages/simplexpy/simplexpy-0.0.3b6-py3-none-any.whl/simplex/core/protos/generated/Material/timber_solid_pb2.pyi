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
    __slots__ = ["bending", "compression_parallel", "compression_perpendicular", "density", "elasticity05", "mean_density", "mean_elasticity_parallel", "mean_elasticity_perpendicular", "shear", "shear_modulus", "shear_modulus05", "tension_parallel", "tension_perpendicular"]
    BENDING_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_PARALLEL_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_PERPENDICULAR_FIELD_NUMBER: _ClassVar[int]
    DENSITY_FIELD_NUMBER: _ClassVar[int]
    ELASTICITY05_FIELD_NUMBER: _ClassVar[int]
    MEAN_DENSITY_FIELD_NUMBER: _ClassVar[int]
    MEAN_ELASTICITY_PARALLEL_FIELD_NUMBER: _ClassVar[int]
    MEAN_ELASTICITY_PERPENDICULAR_FIELD_NUMBER: _ClassVar[int]
    SHEAR_FIELD_NUMBER: _ClassVar[int]
    SHEAR_MODULUS05_FIELD_NUMBER: _ClassVar[int]
    SHEAR_MODULUS_FIELD_NUMBER: _ClassVar[int]
    TENSION_PARALLEL_FIELD_NUMBER: _ClassVar[int]
    TENSION_PERPENDICULAR_FIELD_NUMBER: _ClassVar[int]
    bending: float
    compression_parallel: float
    compression_perpendicular: float
    density: float
    elasticity05: float
    mean_density: float
    mean_elasticity_parallel: float
    mean_elasticity_perpendicular: float
    shear: float
    shear_modulus: float
    shear_modulus05: float
    tension_parallel: float
    tension_perpendicular: float
    def __init__(self, bending: _Optional[float] = ..., tension_parallel: _Optional[float] = ..., tension_perpendicular: _Optional[float] = ..., compression_parallel: _Optional[float] = ..., compression_perpendicular: _Optional[float] = ..., shear: _Optional[float] = ..., mean_elasticity_parallel: _Optional[float] = ..., elasticity05: _Optional[float] = ..., mean_elasticity_perpendicular: _Optional[float] = ..., shear_modulus: _Optional[float] = ..., shear_modulus05: _Optional[float] = ..., density: _Optional[float] = ..., mean_density: _Optional[float] = ...) -> None: ...
