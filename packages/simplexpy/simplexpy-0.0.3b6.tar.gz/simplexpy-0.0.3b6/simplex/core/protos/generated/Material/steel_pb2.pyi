from Utils import utils_pb2 as _utils_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
DESCRIPTOR: _descriptor.FileDescriptor
DUCTILITY_CLASS_A: DuctilityClass
DUCTILITY_CLASS_B: DuctilityClass
DUCTILITY_CLASS_C: DuctilityClass
DUCTILITY_CLASS_UNSPECIFIED: DuctilityClass
OWNER_COMPANY: _utils_pb2.Owner
OWNER_OFFICE: _utils_pb2.Owner
OWNER_STRUSOFT: _utils_pb2.Owner
OWNER_UNSPECIFIED: _utils_pb2.Owner
OWNER_USER: _utils_pb2.Owner
PRODUCTION_TYPE_COLD_WORKED: ProductionType
PRODUCTION_TYPE_ROLLED: ProductionType
PRODUCTION_TYPE_UNSPECIFIED: ProductionType
PRODUCTION_TYPE_WELDED: ProductionType
PRODUCT_PLAIN: Product
PRODUCT_REINFORCEMENT: Product
PRODUCT_UNSPECIFIED: Product
SORT_REGULAR: Sort
SORT_STAINLESS: Sort
SORT_UNSPECIFIED: Sort

class CharacteristicData(_message.Message):
    __slots__ = ["alpha", "c1", "c2", "density", "elasticity_modulus", "failure_strain", "hardening_strain", "k", "poissons_ratio", "shear_modulus", "ultimate_strain", "ultimate_tensile_strengths", "yield_strain", "yield_strengths"]
    ALPHA_FIELD_NUMBER: _ClassVar[int]
    C1_FIELD_NUMBER: _ClassVar[int]
    C2_FIELD_NUMBER: _ClassVar[int]
    DENSITY_FIELD_NUMBER: _ClassVar[int]
    ELASTICITY_MODULUS_FIELD_NUMBER: _ClassVar[int]
    FAILURE_STRAIN_FIELD_NUMBER: _ClassVar[int]
    HARDENING_STRAIN_FIELD_NUMBER: _ClassVar[int]
    K_FIELD_NUMBER: _ClassVar[int]
    POISSONS_RATIO_FIELD_NUMBER: _ClassVar[int]
    SHEAR_MODULUS_FIELD_NUMBER: _ClassVar[int]
    ULTIMATE_STRAIN_FIELD_NUMBER: _ClassVar[int]
    ULTIMATE_TENSILE_STRENGTHS_FIELD_NUMBER: _ClassVar[int]
    YIELD_STRAIN_FIELD_NUMBER: _ClassVar[int]
    YIELD_STRENGTHS_FIELD_NUMBER: _ClassVar[int]
    alpha: float
    c1: float
    c2: float
    density: float
    elasticity_modulus: float
    failure_strain: float
    hardening_strain: float
    k: float
    poissons_ratio: float
    shear_modulus: float
    ultimate_strain: float
    ultimate_tensile_strengths: _containers.RepeatedCompositeFieldContainer[StrengthValue]
    yield_strain: float
    yield_strengths: _containers.RepeatedCompositeFieldContainer[StrengthValue]
    def __init__(self, elasticity_modulus: _Optional[float] = ..., shear_modulus: _Optional[float] = ..., yield_strain: _Optional[float] = ..., ultimate_strain: _Optional[float] = ..., failure_strain: _Optional[float] = ..., poissons_ratio: _Optional[float] = ..., density: _Optional[float] = ..., alpha: _Optional[float] = ..., k: _Optional[float] = ..., yield_strengths: _Optional[_Iterable[_Union[StrengthValue, _Mapping]]] = ..., ultimate_tensile_strengths: _Optional[_Iterable[_Union[StrengthValue, _Mapping]]] = ..., hardening_strain: _Optional[float] = ..., c1: _Optional[float] = ..., c2: _Optional[float] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["id", "properties", "type"]
    CLASS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2.ID
    properties: CharacteristicData
    type: Type
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., type: _Optional[_Union[Type, _Mapping]] = ..., properties: _Optional[_Union[CharacteristicData, _Mapping]] = ..., **kwargs) -> None: ...

class StrengthValue(_message.Message):
    __slots__ = ["strength", "thickness"]
    STRENGTH_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_FIELD_NUMBER: _ClassVar[int]
    strength: float
    thickness: float
    def __init__(self, thickness: _Optional[float] = ..., strength: _Optional[float] = ...) -> None: ...

class Type(_message.Message):
    __slots__ = ["product", "production", "sort"]
    PRODUCTION_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    product: Product
    production: ProductionType
    sort: Sort
    def __init__(self, sort: _Optional[_Union[Sort, str]] = ..., production: _Optional[_Union[ProductionType, str]] = ..., product: _Optional[_Union[Product, str]] = ...) -> None: ...

class ProductionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Sort(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Product(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DuctilityClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
