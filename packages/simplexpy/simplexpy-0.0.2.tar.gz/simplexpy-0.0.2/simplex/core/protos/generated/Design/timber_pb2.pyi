from FireProtection import timber_pb2 as _timber_pb2
from Utils import utils_pb2 as _utils_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from FireProtection.timber_pb2 import CharacteristicData
from FireProtection.timber_pb2 import Data
from FireProtection.timber_pb2 import MaterialType
DESCRIPTOR: _descriptor.FileDescriptor
MATERIAL_TYPE_GYPSUM_BOARD_AH1_INTERNAL: _timber_pb2.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_AH1_OTHER: _timber_pb2.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_AH2_INTERNAL: _timber_pb2.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_AH2_OTHER: _timber_pb2.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F1_INTERNAL: _timber_pb2.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F1_OTHER: _timber_pb2.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F2_INTERNAL: _timber_pb2.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F2_OTHER: _timber_pb2.MaterialType
MATERIAL_TYPE_NONE: _timber_pb2.MaterialType
MATERIAL_TYPE_ROCK_FIBER: _timber_pb2.MaterialType
MATERIAL_TYPE_UNSPECIFIED: _timber_pb2.MaterialType
MATERIAL_TYPE_USER_DEFINED: _timber_pb2.MaterialType
MATERIAL_TYPE_WOOD: _timber_pb2.MaterialType
SECOND_ORDER_ANALYSIS_CONSIDER: SecondOrderAnalysis
SECOND_ORDER_ANALYSIS_FIRST_ORDER_DESIGN: SecondOrderAnalysis
SECOND_ORDER_ANALYSIS_IGNORE: SecondOrderAnalysis
SECOND_ORDER_ANALYSIS_UNSPECIFIED: SecondOrderAnalysis
SERVICE_CLASS_1: ServiceClass
SERVICE_CLASS_2: ServiceClass
SERVICE_CLASS_3: ServiceClass
SERVICE_CLASS_UNSPECIFIED: ServiceClass

class BeamSettings(_message.Message):
    __slots__ = ["ksys", "lamination_thickness", "second_order_analysis"]
    KSYS_FIELD_NUMBER: _ClassVar[int]
    LAMINATION_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    SECOND_ORDER_ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    ksys: float
    lamination_thickness: float
    second_order_analysis: SecondOrderAnalysis
    def __init__(self, second_order_analysis: _Optional[_Union[SecondOrderAnalysis, str]] = ..., lamination_thickness: _Optional[float] = ..., ksys: _Optional[float] = ...) -> None: ...

class CharringRate(_message.Message):
    __slots__ = ["beta_n", "calculate_auto"]
    BETA_N_FIELD_NUMBER: _ClassVar[int]
    CALCULATE_AUTO_FIELD_NUMBER: _ClassVar[int]
    beta_n: float
    calculate_auto: bool
    def __init__(self, calculate_auto: bool = ..., beta_n: _Optional[float] = ...) -> None: ...

class ElementDesignSettings(_message.Message):
    __slots__ = ["beam", "fire", "kcr", "kdef", "serviceclass"]
    BEAM_FIELD_NUMBER: _ClassVar[int]
    FIRE_FIELD_NUMBER: _ClassVar[int]
    KCR_FIELD_NUMBER: _ClassVar[int]
    KDEF_FIELD_NUMBER: _ClassVar[int]
    SERVICECLASS_FIELD_NUMBER: _ClassVar[int]
    beam: BeamSettings
    fire: Fire
    kcr: float
    kdef: float
    serviceclass: ServiceClass
    def __init__(self, serviceclass: _Optional[_Union[ServiceClass, str]] = ..., kdef: _Optional[float] = ..., beam: _Optional[_Union[BeamSettings, _Mapping]] = ..., kcr: _Optional[float] = ..., fire: _Optional[_Union[Fire, _Mapping]] = ...) -> None: ...

class Fire(_message.Message):
    __slots__ = ["charring_rate", "protected", "protection"]
    CHARRING_RATE_FIELD_NUMBER: _ClassVar[int]
    PROTECTED_FIELD_NUMBER: _ClassVar[int]
    PROTECTION_FIELD_NUMBER: _ClassVar[int]
    charring_rate: CharringRate
    protected: bool
    protection: FireProtection
    def __init__(self, charring_rate: _Optional[_Union[CharringRate, _Mapping]] = ..., protected: bool = ..., protection: _Optional[_Union[FireProtection, _Mapping]] = ...) -> None: ...

class FireProtection(_message.Message):
    __slots__ = ["charring_start_time_bottom", "charring_start_time_left", "charring_start_time_right", "charring_start_time_top", "mtrl", "struct_protection_bottom", "struct_protection_left", "struct_protection_right", "struct_protection_top"]
    CHARRING_START_TIME_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    CHARRING_START_TIME_LEFT_FIELD_NUMBER: _ClassVar[int]
    CHARRING_START_TIME_RIGHT_FIELD_NUMBER: _ClassVar[int]
    CHARRING_START_TIME_TOP_FIELD_NUMBER: _ClassVar[int]
    MTRL_FIELD_NUMBER: _ClassVar[int]
    STRUCT_PROTECTION_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    STRUCT_PROTECTION_LEFT_FIELD_NUMBER: _ClassVar[int]
    STRUCT_PROTECTION_RIGHT_FIELD_NUMBER: _ClassVar[int]
    STRUCT_PROTECTION_TOP_FIELD_NUMBER: _ClassVar[int]
    charring_start_time_bottom: float
    charring_start_time_left: float
    charring_start_time_right: float
    charring_start_time_top: float
    mtrl: _timber_pb2.Data
    struct_protection_bottom: bool
    struct_protection_left: bool
    struct_protection_right: bool
    struct_protection_top: bool
    def __init__(self, struct_protection_top: bool = ..., struct_protection_bottom: bool = ..., struct_protection_left: bool = ..., struct_protection_right: bool = ..., charring_start_time_top: _Optional[float] = ..., charring_start_time_bottom: _Optional[float] = ..., charring_start_time_left: _Optional[float] = ..., charring_start_time_right: _Optional[float] = ..., mtrl: _Optional[_Union[_timber_pb2.Data, _Mapping]] = ...) -> None: ...

class GeneralDesignSettings(_message.Message):
    __slots__ = ["member_surface_emissivity_timber", "partial_coeffs"]
    MEMBER_SURFACE_EMISSIVITY_TIMBER_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_COEFFS_FIELD_NUMBER: _ClassVar[int]
    member_surface_emissivity_timber: float
    partial_coeffs: PartialCoefficients
    def __init__(self, partial_coeffs: _Optional[_Union[PartialCoefficients, _Mapping]] = ..., member_surface_emissivity_timber: _Optional[float] = ...) -> None: ...

class PartialCoefficient(_message.Message):
    __slots__ = ["gamma_m", "gamma_m_gl", "gamma_m_lvl", "gamma_m_plate"]
    GAMMA_M_FIELD_NUMBER: _ClassVar[int]
    GAMMA_M_GL_FIELD_NUMBER: _ClassVar[int]
    GAMMA_M_LVL_FIELD_NUMBER: _ClassVar[int]
    GAMMA_M_PLATE_FIELD_NUMBER: _ClassVar[int]
    gamma_m: float
    gamma_m_gl: float
    gamma_m_lvl: float
    gamma_m_plate: float
    def __init__(self, gamma_m: _Optional[float] = ..., gamma_m_gl: _Optional[float] = ..., gamma_m_lvl: _Optional[float] = ..., gamma_m_plate: _Optional[float] = ...) -> None: ...

class PartialCoefficients(_message.Message):
    __slots__ = ["accidental", "gamma_fire", "ultimate"]
    ACCIDENTAL_FIELD_NUMBER: _ClassVar[int]
    GAMMA_FIRE_FIELD_NUMBER: _ClassVar[int]
    ULTIMATE_FIELD_NUMBER: _ClassVar[int]
    accidental: PartialCoefficient
    gamma_fire: float
    ultimate: PartialCoefficient
    def __init__(self, ultimate: _Optional[_Union[PartialCoefficient, _Mapping]] = ..., accidental: _Optional[_Union[PartialCoefficient, _Mapping]] = ..., gamma_fire: _Optional[float] = ...) -> None: ...

class ServiceClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class SecondOrderAnalysis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
