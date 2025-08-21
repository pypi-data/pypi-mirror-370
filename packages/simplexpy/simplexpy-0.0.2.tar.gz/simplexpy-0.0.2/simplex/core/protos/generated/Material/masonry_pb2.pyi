from Utils import utils_pb2 as _utils_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
CATEGORY_ANY_MORTAR_CATEGORY2: Category
CATEGORY_DESIGNED_MORTAR_CATEGORY1: Category
CATEGORY_PRESCRIBED_MORTAR_CATEGORY1: Category
CATEGORY_UNSPECIFIED: Category
CLASS_25: Class
CLASS_UNSPECIFIED: Class
DESCRIPTOR: _descriptor.FileDescriptor
GROUP_1: Group
GROUP_2: Group
GROUP_3: Group
GROUP_4: Group
GROUP_UNSPECIFIED: Group
MANNER_FJM: Manner
MANNER_SBM: Manner
MANNER_UMV: Manner
MANNER_UNSPECIFIED: Manner
OWNER_COMPANY: _utils_pb2.Owner
OWNER_OFFICE: _utils_pb2.Owner
OWNER_STRUSOFT: _utils_pb2.Owner
OWNER_UNSPECIFIED: _utils_pb2.Owner
OWNER_USER: _utils_pb2.Owner
PRODUCT_AUTOCLAVED_AERATED_CONCRETE_BLOCKS: Product
PRODUCT_CALCIUM_SILICATE_BRICKS: Product
PRODUCT_CLAY_BLOCKS: Product
PRODUCT_CONCRETE_BRICKS: Product
PRODUCT_CONCRETE_HOLE_BLOCKS: Product
PRODUCT_HOLE_BRICKS: Product
PRODUCT_LIGHTWEIGHT_CONCRETE_BLOCKS: Product
PRODUCT_LIGHT_EXPANDED_CLAY_AGGREGATE_BLOCKS: Product
PRODUCT_SOLID_BRICKS: Product
PRODUCT_SOLID_CONCRETE_BLOCKS: Product
PRODUCT_UNSPECIFIED: Product

class CharacteristicData(_message.Message):
    __slots__ = ["Ex", "Ey", "density", "fb", "fkx", "fky", "fm", "fmxk1", "fvk0", "fvlt", "fxk1", "fxk2"]
    DENSITY_FIELD_NUMBER: _ClassVar[int]
    EX_FIELD_NUMBER: _ClassVar[int]
    EY_FIELD_NUMBER: _ClassVar[int]
    Ex: float
    Ey: float
    FB_FIELD_NUMBER: _ClassVar[int]
    FKX_FIELD_NUMBER: _ClassVar[int]
    FKY_FIELD_NUMBER: _ClassVar[int]
    FMXK1_FIELD_NUMBER: _ClassVar[int]
    FM_FIELD_NUMBER: _ClassVar[int]
    FVK0_FIELD_NUMBER: _ClassVar[int]
    FVLT_FIELD_NUMBER: _ClassVar[int]
    FXK1_FIELD_NUMBER: _ClassVar[int]
    FXK2_FIELD_NUMBER: _ClassVar[int]
    density: float
    fb: float
    fkx: float
    fky: float
    fm: float
    fmxk1: float
    fvk0: float
    fvlt: float
    fxk1: float
    fxk2: float
    def __init__(self, fkx: _Optional[float] = ..., fky: _Optional[float] = ..., fxk1: _Optional[float] = ..., fxk2: _Optional[float] = ..., fvk0: _Optional[float] = ..., fvlt: _Optional[float] = ..., fb: _Optional[float] = ..., fm: _Optional[float] = ..., fmxk1: _Optional[float] = ..., Ex: _Optional[float] = ..., Ey: _Optional[float] = ..., density: _Optional[float] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["category", "group", "id", "manner", "mortar_slip_width", "product", "properties", "strength_class"]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    CLASS_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MANNER_FIELD_NUMBER: _ClassVar[int]
    MORTAR_SLIP_WIDTH_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    STRENGTH_CLASS_FIELD_NUMBER: _ClassVar[int]
    category: Category
    group: Group
    id: _utils_pb2.ID
    manner: Manner
    mortar_slip_width: float
    product: Product
    properties: CharacteristicData
    strength_class: int
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., product: _Optional[_Union[Product, str]] = ..., manner: _Optional[_Union[Manner, str]] = ..., group: _Optional[_Union[Group, str]] = ..., category: _Optional[_Union[Category, str]] = ..., strength_class: _Optional[int] = ..., mortar_slip_width: _Optional[float] = ..., properties: _Optional[_Union[CharacteristicData, _Mapping]] = ..., **kwargs) -> None: ...

class Product(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Manner(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Group(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Class(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Category(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
