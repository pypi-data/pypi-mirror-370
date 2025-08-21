from Utils import utils_pb2 as _utils_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
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
TEMPERATURE_CURVE_EXTERNAL: TemperatureCurve
TEMPERATURE_CURVE_HYDROCARBON: TemperatureCurve
TEMPERATURE_CURVE_PARAMETRIC: TemperatureCurve
TEMPERATURE_CURVE_STANDARD: TemperatureCurve
TEMPERATURE_CURVE_UNSPECIFIED: TemperatureCurve

class ElementDesignSettings(_message.Message):
    __slots__ = ["deflection_check", "deflection_limit", "deflection_limit_factor", "general_fire"]
    DEFLECTION_CHECK_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_LIMIT_FACTOR_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_LIMIT_FIELD_NUMBER: _ClassVar[int]
    GENERAL_FIRE_FIELD_NUMBER: _ClassVar[int]
    deflection_check: bool
    deflection_limit: float
    deflection_limit_factor: float
    general_fire: FireGeneral
    def __init__(self, general_fire: _Optional[_Union[FireGeneral, _Mapping]] = ..., deflection_check: bool = ..., deflection_limit: _Optional[float] = ..., deflection_limit_factor: _Optional[float] = ...) -> None: ...

class FireGeneral(_message.Message):
    __slots__ = ["duration_of_fire", "gamma_parametric", "temperature_curve", "time_step"]
    DURATION_OF_FIRE_FIELD_NUMBER: _ClassVar[int]
    GAMMA_PARAMETRIC_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_CURVE_FIELD_NUMBER: _ClassVar[int]
    TIME_STEP_FIELD_NUMBER: _ClassVar[int]
    duration_of_fire: float
    gamma_parametric: float
    temperature_curve: TemperatureCurve
    time_step: float
    def __init__(self, duration_of_fire: _Optional[float] = ..., time_step: _Optional[float] = ..., temperature_curve: _Optional[_Union[TemperatureCurve, str]] = ..., gamma_parametric: _Optional[float] = ...) -> None: ...

class FireRadiativeHeatFlux(_message.Message):
    __slots__ = ["configuration_factor", "fire_emissivity"]
    CONFIGURATION_FACTOR_FIELD_NUMBER: _ClassVar[int]
    FIRE_EMISSIVITY_FIELD_NUMBER: _ClassVar[int]
    configuration_factor: float
    fire_emissivity: float
    def __init__(self, configuration_factor: _Optional[float] = ..., fire_emissivity: _Optional[float] = ...) -> None: ...

class GeneralDesignSettings(_message.Message):
    __slots__ = ["heat_flux", "partial_coeffs"]
    HEAT_FLUX_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_COEFFS_FIELD_NUMBER: _ClassVar[int]
    heat_flux: FireRadiativeHeatFlux
    partial_coeffs: PartialCoefficients
    def __init__(self, partial_coeffs: _Optional[_Union[PartialCoefficients, _Mapping]] = ..., heat_flux: _Optional[_Union[FireRadiativeHeatFlux, _Mapping]] = ...) -> None: ...

class PartialCoefficient(_message.Message):
    __slots__ = ["gamma_factor_critical", "gamma_factor_inspection_level_normal", "gamma_factor_inspection_level_relaxed", "gamma_factor_inspection_level_tightened"]
    GAMMA_FACTOR_CRITICAL_FIELD_NUMBER: _ClassVar[int]
    GAMMA_FACTOR_INSPECTION_LEVEL_NORMAL_FIELD_NUMBER: _ClassVar[int]
    GAMMA_FACTOR_INSPECTION_LEVEL_RELAXED_FIELD_NUMBER: _ClassVar[int]
    GAMMA_FACTOR_INSPECTION_LEVEL_TIGHTENED_FIELD_NUMBER: _ClassVar[int]
    gamma_factor_critical: float
    gamma_factor_inspection_level_normal: float
    gamma_factor_inspection_level_relaxed: float
    gamma_factor_inspection_level_tightened: float
    def __init__(self, gamma_factor_inspection_level_relaxed: _Optional[float] = ..., gamma_factor_inspection_level_normal: _Optional[float] = ..., gamma_factor_inspection_level_tightened: _Optional[float] = ..., gamma_factor_critical: _Optional[float] = ...) -> None: ...

class PartialCoefficients(_message.Message):
    __slots__ = ["accidental", "ultimate"]
    ACCIDENTAL_FIELD_NUMBER: _ClassVar[int]
    ULTIMATE_FIELD_NUMBER: _ClassVar[int]
    accidental: PartialCoefficient
    ultimate: PartialCoefficient
    def __init__(self, ultimate: _Optional[_Union[PartialCoefficient, _Mapping]] = ..., accidental: _Optional[_Union[PartialCoefficient, _Mapping]] = ...) -> None: ...

class TemperatureCurve(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
