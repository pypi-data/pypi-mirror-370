from Utils import utils_pb2 as _utils_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
CATEGORY_A: Category
CATEGORY_B: Category
CATEGORY_C: Category
CATEGORY_D: Category
CATEGORY_E: Category
CATEGORY_F: Category
CATEGORY_G: Category
CATEGORY_G2: Category
CATEGORY_H: Category
CATEGORY_I1: Category
CATEGORY_I2: Category
CATEGORY_I3: Category
CATEGORY_K: Category
CATEGORY_S1: Category
CATEGORY_S2: Category
CATEGORY_S3_C_G: Category
CATEGORY_S3_H_K: Category
CATEGORY_T: Category
CATEGORY_UNSPECIFIED: Category
DESCRIPTOR: _descriptor.FileDescriptor
DURATION_CLASS_INSTANTANEOUS: DurationClass
DURATION_CLASS_LONG: DurationClass
DURATION_CLASS_MEDIUM: DurationClass
DURATION_CLASS_PERMANENT: DurationClass
DURATION_CLASS_SHORT: DurationClass
DURATION_CLASS_UNSPECIFIED: DurationClass
OWNER_COMPANY: _utils_pb2.Owner
OWNER_OFFICE: _utils_pb2.Owner
OWNER_STRUSOFT: _utils_pb2.Owner
OWNER_UNSPECIFIED: _utils_pb2.Owner
OWNER_USER: _utils_pb2.Owner
TYPE_ACCIDENT_LOAD: Type
TYPE_CONSTRUCTION_LOAD: Type
TYPE_ICE_LOAD: Type
TYPE_IMPOSED_LOAD: Type
TYPE_PERMANENT_LOAD: Type
TYPE_SEISMIC_LOAD: Type
TYPE_SELF_WEIGHT: Type
TYPE_SNOW_LOAD: Type
TYPE_SOIL_LOAD: Type
TYPE_SOIL_SELF_WEIGHT: Type
TYPE_TEMPERATURE_LOAD: Type
TYPE_UNSPECIFIED: Type
TYPE_WIND_LOAD: Type

class Data(_message.Message):
    __slots__ = ["category", "description", "duration_class", "id", "number_of_storeys", "type"]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DURATION_CLASS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_STOREYS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    category: Category
    description: str
    duration_class: DurationClass
    id: _utils_pb2.ID
    number_of_storeys: int
    type: Type
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., type: _Optional[_Union[Type, str]] = ..., duration_class: _Optional[_Union[DurationClass, str]] = ..., category: _Optional[_Union[Category, str]] = ..., number_of_storeys: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DurationClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Category(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
