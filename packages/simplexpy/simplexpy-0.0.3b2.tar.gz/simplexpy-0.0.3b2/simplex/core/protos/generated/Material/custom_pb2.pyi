from Utils import utils_pb2 as _utils_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

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
    __slots__ = ["alpha", "density", "elasticity_modulus", "poissons_ratio"]
    ALPHA_FIELD_NUMBER: _ClassVar[int]
    DENSITY_FIELD_NUMBER: _ClassVar[int]
    ELASTICITY_MODULUS_FIELD_NUMBER: _ClassVar[int]
    POISSONS_RATIO_FIELD_NUMBER: _ClassVar[int]
    alpha: float
    density: float
    elasticity_modulus: float
    poissons_ratio: float
    def __init__(self, density: _Optional[float] = ..., elasticity_modulus: _Optional[float] = ..., poissons_ratio: _Optional[float] = ..., alpha: _Optional[float] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["id", "properties"]
    ID_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2.ID
    properties: CharacteristicData
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., properties: _Optional[_Union[CharacteristicData, _Mapping]] = ...) -> None: ...
