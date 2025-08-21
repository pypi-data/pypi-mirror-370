from Utils import utils_pb2 as _utils_pb2
from Material import timber_solid_pb2 as _timber_solid_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Material import timber_board_pb2 as _timber_board_pb2
from Utils import utils_pb2 as _utils_pb2_1_1
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
from Material.timber_solid_pb2 import CharacteristicData
from Material.timber_board_pb2 import CharacteristicData
DESCRIPTOR: _descriptor.FileDescriptor
OWNER_COMPANY: _utils_pb2_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1.Owner
OWNER_USER: _utils_pb2_1_1.Owner
PRODUCT_TYPE_GL: ProductType
PRODUCT_TYPE_KERTO: ProductType
PRODUCT_TYPE_LVL: ProductType
PRODUCT_TYPE_OSB2: ProductType
PRODUCT_TYPE_OSB3: ProductType
PRODUCT_TYPE_OSB4: ProductType
PRODUCT_TYPE_REGULAR: ProductType
PRODUCT_TYPE_UNSPECIFIED: ProductType
WOOD_TYPE_ASH: WoodType
WOOD_TYPE_BIRCH: WoodType
WOOD_TYPE_OAK: WoodType
WOOD_TYPE_PINE: WoodType
WOOD_TYPE_UNSPECIFIED: WoodType

class Data(_message.Message):
    __slots__ = ["board_data", "id", "product", "solid_data", "wood"]
    BOARD_DATA_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    SOLID_DATA_FIELD_NUMBER: _ClassVar[int]
    WOOD_FIELD_NUMBER: _ClassVar[int]
    board_data: _timber_board_pb2.CharacteristicData
    id: _utils_pb2_1_1.ID
    product: ProductType
    solid_data: _timber_solid_pb2.CharacteristicData
    wood: WoodType
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1.ID, _Mapping]] = ..., product: _Optional[_Union[ProductType, str]] = ..., wood: _Optional[_Union[WoodType, str]] = ..., board_data: _Optional[_Union[_timber_board_pb2.CharacteristicData, _Mapping]] = ..., solid_data: _Optional[_Union[_timber_solid_pb2.CharacteristicData, _Mapping]] = ...) -> None: ...

class ProductType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class WoodType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
