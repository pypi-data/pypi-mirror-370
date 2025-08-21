from Utils import utils_pb2 as _utils_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
DESCRIPTOR: _descriptor.FileDescriptor
MATERIAL_TYPE_GYPSUM_BOARD_AH1_INTERNAL: MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_AH1_OTHER: MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_AH2_INTERNAL: MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_AH2_OTHER: MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F1_INTERNAL: MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F1_OTHER: MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F2_INTERNAL: MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F2_OTHER: MaterialType
MATERIAL_TYPE_NONE: MaterialType
MATERIAL_TYPE_ROCK_FIBER: MaterialType
MATERIAL_TYPE_UNSPECIFIED: MaterialType
MATERIAL_TYPE_USER_DEFINED: MaterialType
MATERIAL_TYPE_WOOD: MaterialType
OWNER_COMPANY: _utils_pb2.Owner
OWNER_OFFICE: _utils_pb2.Owner
OWNER_STRUSOFT: _utils_pb2.Owner
OWNER_UNSPECIFIED: _utils_pb2.Owner
OWNER_USER: _utils_pb2.Owner

class CharacteristicData(_message.Message):
    __slots__ = ["charring_rate", "charring_rate_mod_factor", "charring_start_time", "failure_time", "material_type", "thickness", "thickness_inner", "thickness_outer"]
    CHARRING_RATE_FIELD_NUMBER: _ClassVar[int]
    CHARRING_RATE_MOD_FACTOR_FIELD_NUMBER: _ClassVar[int]
    CHARRING_START_TIME_FIELD_NUMBER: _ClassVar[int]
    FAILURE_TIME_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_INNER_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_OUTER_FIELD_NUMBER: _ClassVar[int]
    charring_rate: float
    charring_rate_mod_factor: float
    charring_start_time: float
    failure_time: float
    material_type: MaterialType
    thickness: float
    thickness_inner: float
    thickness_outer: float
    def __init__(self, material_type: _Optional[_Union[MaterialType, str]] = ..., thickness: _Optional[float] = ..., thickness_inner: _Optional[float] = ..., thickness_outer: _Optional[float] = ..., charring_rate: _Optional[float] = ..., failure_time: _Optional[float] = ..., charring_start_time: _Optional[float] = ..., charring_rate_mod_factor: _Optional[float] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["id", "properties"]
    ID_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2.ID
    properties: CharacteristicData
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., properties: _Optional[_Union[CharacteristicData, _Mapping]] = ...) -> None: ...

class MaterialType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
