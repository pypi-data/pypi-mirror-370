from Utils import utils_pb2 as _utils_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
DENSITY_CLASS_LIGHT10: DensityClass
DENSITY_CLASS_LIGHT12: DensityClass
DENSITY_CLASS_LIGHT14: DensityClass
DENSITY_CLASS_LIGHT16: DensityClass
DENSITY_CLASS_LIGHT18: DensityClass
DENSITY_CLASS_LIGHT20: DensityClass
DENSITY_CLASS_REGULAR: DensityClass
DENSITY_CLASS_UNSPECIFIED: DensityClass
DESCRIPTOR: _descriptor.FileDescriptor
OWNER_COMPANY: _utils_pb2.Owner
OWNER_OFFICE: _utils_pb2.Owner
OWNER_STRUSOFT: _utils_pb2.Owner
OWNER_UNSPECIFIED: _utils_pb2.Owner
OWNER_USER: _utils_pb2.Owner
TYPE_LIGHT: Type
TYPE_REGULAR: Type
TYPE_UNSPECIFIED: Type

class CharacteristicData(_message.Message):
    __slots__ = ["alpha", "compression", "compression_cube", "compression_mean", "compressive_strain1", "compressive_strain2", "compressive_strain3", "density", "density_class", "elasticity_modulus", "n", "poissons_ratio", "tension05", "tension95", "tension_mean", "ultimate_compressive_strain1", "ultimate_compressive_strain2", "ultimate_compressive_strain3"]
    ALPHA_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_CUBE_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_MEAN_FIELD_NUMBER: _ClassVar[int]
    COMPRESSIVE_STRAIN1_FIELD_NUMBER: _ClassVar[int]
    COMPRESSIVE_STRAIN2_FIELD_NUMBER: _ClassVar[int]
    COMPRESSIVE_STRAIN3_FIELD_NUMBER: _ClassVar[int]
    DENSITY_CLASS_FIELD_NUMBER: _ClassVar[int]
    DENSITY_FIELD_NUMBER: _ClassVar[int]
    ELASTICITY_MODULUS_FIELD_NUMBER: _ClassVar[int]
    N_FIELD_NUMBER: _ClassVar[int]
    POISSONS_RATIO_FIELD_NUMBER: _ClassVar[int]
    TENSION05_FIELD_NUMBER: _ClassVar[int]
    TENSION95_FIELD_NUMBER: _ClassVar[int]
    TENSION_MEAN_FIELD_NUMBER: _ClassVar[int]
    ULTIMATE_COMPRESSIVE_STRAIN1_FIELD_NUMBER: _ClassVar[int]
    ULTIMATE_COMPRESSIVE_STRAIN2_FIELD_NUMBER: _ClassVar[int]
    ULTIMATE_COMPRESSIVE_STRAIN3_FIELD_NUMBER: _ClassVar[int]
    alpha: float
    compression: float
    compression_cube: float
    compression_mean: float
    compressive_strain1: float
    compressive_strain2: float
    compressive_strain3: float
    density: float
    density_class: DensityClass
    elasticity_modulus: float
    n: float
    poissons_ratio: float
    tension05: float
    tension95: float
    tension_mean: float
    ultimate_compressive_strain1: float
    ultimate_compressive_strain2: float
    ultimate_compressive_strain3: float
    def __init__(self, compression: _Optional[float] = ..., compression_cube: _Optional[float] = ..., compression_mean: _Optional[float] = ..., tension_mean: _Optional[float] = ..., tension05: _Optional[float] = ..., tension95: _Optional[float] = ..., elasticity_modulus: _Optional[float] = ..., compressive_strain1: _Optional[float] = ..., ultimate_compressive_strain1: _Optional[float] = ..., compressive_strain2: _Optional[float] = ..., ultimate_compressive_strain2: _Optional[float] = ..., n: _Optional[float] = ..., compressive_strain3: _Optional[float] = ..., ultimate_compressive_strain3: _Optional[float] = ..., poissons_ratio: _Optional[float] = ..., alpha: _Optional[float] = ..., density: _Optional[float] = ..., density_class: _Optional[_Union[DensityClass, str]] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["id", "properties", "type"]
    ID_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2.ID
    properties: CharacteristicData
    type: Type
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., type: _Optional[_Union[Type, str]] = ..., properties: _Optional[_Union[CharacteristicData, _Mapping]] = ...) -> None: ...

class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DensityClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
