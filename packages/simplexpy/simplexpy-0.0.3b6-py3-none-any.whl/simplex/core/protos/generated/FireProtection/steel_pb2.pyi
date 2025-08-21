from Utils import utils_pb2 as _utils_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
DESCRIPTOR: _descriptor.FileDescriptor
ENCASEMENT_CONTOUR: Encasement
ENCASEMENT_HOLLOW: Encasement
ENCASEMENT_UNSPECIFIED: Encasement
OWNER_COMPANY: _utils_pb2.Owner
OWNER_OFFICE: _utils_pb2.Owner
OWNER_STRUSOFT: _utils_pb2.Owner
OWNER_UNSPECIFIED: _utils_pb2.Owner
OWNER_USER: _utils_pb2.Owner

class CharacteristicData(_message.Message):
    __slots__ = ["density", "encasement", "specific_heat", "thermal_conductivity"]
    DENSITY_FIELD_NUMBER: _ClassVar[int]
    ENCASEMENT_FIELD_NUMBER: _ClassVar[int]
    SPECIFIC_HEAT_FIELD_NUMBER: _ClassVar[int]
    THERMAL_CONDUCTIVITY_FIELD_NUMBER: _ClassVar[int]
    density: float
    encasement: Encasement
    specific_heat: float
    thermal_conductivity: float
    def __init__(self, density: _Optional[float] = ..., specific_heat: _Optional[float] = ..., thermal_conductivity: _Optional[float] = ..., encasement: _Optional[_Union[Encasement, str]] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["id", "properties"]
    ID_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2.ID
    properties: CharacteristicData
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., properties: _Optional[_Union[CharacteristicData, _Mapping]] = ...) -> None: ...

class Encasement(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
