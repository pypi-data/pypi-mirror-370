from Utils import utils_pb2 as _utils_pb2
from Geometry import reinf_pb2 as _reinf_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Geometry import geometry_pb2 as _geometry_pb2
from Design import concrete_pb2 as _concrete_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
from Geometry.reinf_pb2 import HorPos
from Geometry.reinf_pb2 import Straight
from Geometry.reinf_pb2 import Group
from Geometry.reinf_pb2 import Layer
from Geometry.reinf_pb2 import BarProfile
from Geometry.reinf_pb2 import WireProfile
from Geometry.reinf_pb2 import VertPos
from Geometry.reinf_pb2 import Distribution
BAR_PROFILE_RIBBED: _reinf_pb2.BarProfile
BAR_PROFILE_SMOOTH: _reinf_pb2.BarProfile
BAR_PROFILE_UNSPECIFIED: _reinf_pb2.BarProfile
DESCRIPTOR: _descriptor.FileDescriptor
DISTRIBUTION_DENSE_2A: _reinf_pb2.Distribution
DISTRIBUTION_DENSE_2B: _reinf_pb2.Distribution
DISTRIBUTION_DENSE_3: _reinf_pb2.Distribution
DISTRIBUTION_EVEN: _reinf_pb2.Distribution
DISTRIBUTION_MID: _reinf_pb2.Distribution
DISTRIBUTION_UNSPECIFIED: _reinf_pb2.Distribution
OWNER_COMPANY: _utils_pb2_1.Owner
OWNER_OFFICE: _utils_pb2_1.Owner
OWNER_STRUSOFT: _utils_pb2_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1.Owner
OWNER_USER: _utils_pb2_1.Owner
VERT_POS_BOTTOM: _reinf_pb2.VertPos
VERT_POS_CENTER: _reinf_pb2.VertPos
VERT_POS_TOP: _reinf_pb2.VertPos
VERT_POS_UNSPECIFIED: _reinf_pb2.VertPos
WIRE_PROFILE_K7: _reinf_pb2.WireProfile
WIRE_PROFILE_SINGLE: _reinf_pb2.WireProfile
WIRE_PROFILE_UNSPECIFIED: _reinf_pb2.WireProfile

class CharacteristicData(_message.Message):
    __slots__ = ["density", "elasticity_modulus", "epsilon_failure", "epsilon_ultimate", "k", "ultimate_strength", "yield_strength"]
    DENSITY_FIELD_NUMBER: _ClassVar[int]
    ELASTICITY_MODULUS_FIELD_NUMBER: _ClassVar[int]
    EPSILON_FAILURE_FIELD_NUMBER: _ClassVar[int]
    EPSILON_ULTIMATE_FIELD_NUMBER: _ClassVar[int]
    K_FIELD_NUMBER: _ClassVar[int]
    ULTIMATE_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    YIELD_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    density: float
    elasticity_modulus: float
    epsilon_failure: float
    epsilon_ultimate: float
    k: float
    ultimate_strength: float
    yield_strength: float
    def __init__(self, elasticity_modulus: _Optional[float] = ..., yield_strength: _Optional[float] = ..., ultimate_strength: _Optional[float] = ..., density: _Optional[float] = ..., k: _Optional[float] = ..., epsilon_ultimate: _Optional[float] = ..., epsilon_failure: _Optional[float] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["bar_profile", "diameters", "id", "properties", "wire_profile"]
    BAR_PROFILE_FIELD_NUMBER: _ClassVar[int]
    DIAMETERS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    WIRE_PROFILE_FIELD_NUMBER: _ClassVar[int]
    bar_profile: _reinf_pb2.BarProfile
    diameters: _containers.RepeatedCompositeFieldContainer[DiameterItem]
    id: _utils_pb2_1.ID
    properties: CharacteristicData
    wire_profile: _reinf_pb2.WireProfile
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., properties: _Optional[_Union[CharacteristicData, _Mapping]] = ..., diameters: _Optional[_Iterable[_Union[DiameterItem, _Mapping]]] = ..., bar_profile: _Optional[_Union[_reinf_pb2.BarProfile, str]] = ..., wire_profile: _Optional[_Union[_reinf_pb2.WireProfile, str]] = ...) -> None: ...

class DiameterItem(_message.Message):
    __slots__ = ["bar_area", "diameter"]
    BAR_AREA_FIELD_NUMBER: _ClassVar[int]
    DIAMETER_FIELD_NUMBER: _ClassVar[int]
    bar_area: float
    diameter: float
    def __init__(self, diameter: _Optional[float] = ..., bar_area: _Optional[float] = ...) -> None: ...
