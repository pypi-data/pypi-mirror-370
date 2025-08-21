from Utils import utils_pb2 as _utils_pb2
from Design import soil_pb2 as _soil_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
from Design.soil_pb2 import GammaSoil
from Design.soil_pb2 import GammaResistance
from Design.soil_pb2 import GammaPile
from Design.soil_pb2 import GammaPiles
from Design.soil_pb2 import GammaPermanent
from Design.soil_pb2 import PartialCoefficient
from Design.soil_pb2 import PartialCoefficients
from Design.soil_pb2 import SettlementSetup
from Design.soil_pb2 import MaterialFactors
from Design.soil_pb2 import ModelFactor
from Design.soil_pb2 import ModelFactors
from Design.soil_pb2 import SettlementConfiguration
from Design.soil_pb2 import FoundationConfiguration
from Design.soil_pb2 import FoundationElementConfiguration
from Design.soil_pb2 import EarthPressureConfiguration
from Design.soil_pb2 import EarthPressureElementConfiguration
from Design.soil_pb2 import PileConfiguration
from Design.soil_pb2 import PileElementConfiguration
from Design.soil_pb2 import GeneralDesignSettings
from Design.soil_pb2 import ElementDesignSettings
from Design.soil_pb2 import FoundationDistribution
from Design.soil_pb2 import DesignApproach
from Design.soil_pb2 import GeotechnicalCategory
from Design.soil_pb2 import SoilPunchingType
from Design.soil_pb2 import ActiveEarthPressureType
from Design.soil_pb2 import PassiveEarthPressureType
from Design.soil_pb2 import MaxValues
ACTIVE_EARTH_PRESSURE_TYPE_COMPACTION: _soil_pb2.ActiveEarthPressureType
ACTIVE_EARTH_PRESSURE_TYPE_PRESSURE: _soil_pb2.ActiveEarthPressureType
ACTIVE_EARTH_PRESSURE_TYPE_REST: _soil_pb2.ActiveEarthPressureType
ACTIVE_EARTH_PRESSURE_TYPE_UNSPECIFIED: _soil_pb2.ActiveEarthPressureType
COA_TYPE_610: CoaType
COA_TYPE_6105: CoaType
COA_TYPE_610A: CoaType
COA_TYPE_610A3: CoaType
COA_TYPE_610B: CoaType
COA_TYPE_610B4: CoaType
COA_TYPE_611AB: CoaType
COA_TYPE_614B: CoaType
COA_TYPE_615B: CoaType
COA_TYPE_616B: CoaType
COA_TYPE_812: CoaType
COA_TYPE_813A: CoaType
COA_TYPE_813B: CoaType
COA_TYPE_814A: CoaType
COA_TYPE_814B: CoaType
COA_TYPE_815: CoaType
COA_TYPE_816: CoaType
COA_TYPE_829: CoaType
COA_TYPE_830: CoaType
COA_TYPE_831: CoaType
COA_TYPE_UNSPECIFIED: CoaType
COEFFICIENT_TYPE_BASE: CoefficientType
COEFFICIENT_TYPE_CHI_FACTOR: CoefficientType
COEFFICIENT_TYPE_ETA: CoefficientType
COEFFICIENT_TYPE_GAMMA: CoefficientType
COEFFICIENT_TYPE_KFI: CoefficientType
COEFFICIENT_TYPE_PSI: CoefficientType
COEFFICIENT_TYPE_STOREY: CoefficientType
COEFFICIENT_TYPE_UNSPECIFIED: CoefficientType
DESCRIPTOR: _descriptor.FileDescriptor
DESIGN_APPROACH_1: _soil_pb2.DesignApproach
DESIGN_APPROACH_2: _soil_pb2.DesignApproach
DESIGN_APPROACH_3: _soil_pb2.DesignApproach
DESIGN_APPROACH_UNSPECIFIED: _soil_pb2.DesignApproach
FOUNDATION_DISTRIBUTION_ELASTIC: _soil_pb2.FoundationDistribution
FOUNDATION_DISTRIBUTION_PLASTIC: _soil_pb2.FoundationDistribution
FOUNDATION_DISTRIBUTION_UNSPECIFIED: _soil_pb2.FoundationDistribution
GEOTECHNICAL_CATEGORY_1: _soil_pb2.GeotechnicalCategory
GEOTECHNICAL_CATEGORY_2: _soil_pb2.GeotechnicalCategory
GEOTECHNICAL_CATEGORY_3: _soil_pb2.GeotechnicalCategory
GEOTECHNICAL_CATEGORY_UNSPECIFIED: _soil_pb2.GeotechnicalCategory
GEO_TYPE_1: GeoType
GEO_TYPE_2: GeoType
GEO_TYPE_UNSPECIFIED: GeoType
LIMIT_STATE_EQU: LimitState
LIMIT_STATE_GEO: LimitState
LIMIT_STATE_STR: LimitState
LIMIT_STATE_UNSPECIFIED: LimitState
LIMIT_STATE_VC1: LimitState
LIMIT_STATE_VC2A: LimitState
LIMIT_STATE_VC2B: LimitState
LIMIT_STATE_VC3: LimitState
LIMIT_STATE_VC4: LimitState
MATERIAL_MODEL_BOTH_COMB: _soil_pb2.DesignApproach
MATERIAL_MODEL_SINGLE_COMB: _soil_pb2.DesignApproach
MAX_VALUES_ALPHA: _soil_pb2.MaxValues
MAX_VALUES_BETA: _soil_pb2.MaxValues
MAX_VALUES_DELTA_L: _soil_pb2.MaxValues
MAX_VALUES_DELTA_S: _soil_pb2.MaxValues
MAX_VALUES_OMEGA: _soil_pb2.MaxValues
MAX_VALUES_THETA: _soil_pb2.MaxValues
MAX_VALUES_UNSPECIFIED: _soil_pb2.MaxValues
OWNER_COMPANY: _utils_pb2.Owner
OWNER_OFFICE: _utils_pb2.Owner
OWNER_STRUSOFT: _utils_pb2.Owner
OWNER_UNSPECIFIED: _utils_pb2.Owner
OWNER_USER: _utils_pb2.Owner
PASSIVE_EARTH_PRESSURE_TYPE_PRESSURE: _soil_pb2.PassiveEarthPressureType
PASSIVE_EARTH_PRESSURE_TYPE_REST: _soil_pb2.PassiveEarthPressureType
PASSIVE_EARTH_PRESSURE_TYPE_UNSPECIFIED: _soil_pb2.PassiveEarthPressureType
RESISTANCE_MODEL: _soil_pb2.DesignApproach
SERVICEABILITY_TYPE_LONG: ServiceabilityType
SERVICEABILITY_TYPE_SHORT: ServiceabilityType
SERVICEABILITY_TYPE_UNSPECIFIED: ServiceabilityType
SOIL_PUNCHING_TYPE_1_2: _soil_pb2.SoilPunchingType
SOIL_PUNCHING_TYPE_1_3: _soil_pb2.SoilPunchingType
SOIL_PUNCHING_TYPE_1_4: _soil_pb2.SoilPunchingType
SOIL_PUNCHING_TYPE_8_DEGREE: _soil_pb2.SoilPunchingType
SOIL_PUNCHING_TYPE_UNSPECIFIED: _soil_pb2.SoilPunchingType
SOIL_PUNCHING_TYPE_WIDTH_1_2: _soil_pb2.SoilPunchingType
TYPE_ACCIDENTAL: Type
TYPE_CHARACTERISTIC: Type
TYPE_FIRE: Type
TYPE_FREQUENT: Type
TYPE_QUASI_PERMANENT: Type
TYPE_SEISMIC: Type
TYPE_ULTIMATE: Type
TYPE_UNSPECIFIED: Type

class ActiveEarthPressureConfiguration(_message.Message):
    __slots__ = ["active_earth_pressure_type", "active_ground_water_guid", "compaction", "overload", "vibration_coef"]
    ACTIVE_EARTH_PRESSURE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_GROUND_WATER_GUID_FIELD_NUMBER: _ClassVar[int]
    COMPACTION_FIELD_NUMBER: _ClassVar[int]
    OVERLOAD_FIELD_NUMBER: _ClassVar[int]
    VIBRATION_COEF_FIELD_NUMBER: _ClassVar[int]
    active_earth_pressure_type: _soil_pb2.ActiveEarthPressureType
    active_ground_water_guid: str
    compaction: Compaction
    overload: bool
    vibration_coef: float
    def __init__(self, active_earth_pressure_type: _Optional[_Union[_soil_pb2.ActiveEarthPressureType, str]] = ..., compaction: _Optional[_Union[Compaction, _Mapping]] = ..., vibration_coef: _Optional[float] = ..., overload: bool = ..., active_ground_water_guid: _Optional[str] = ...) -> None: ...

class BeamConfiguration(_message.Message):
    __slots__ = ["psi2", "second_order"]
    PSI2_FIELD_NUMBER: _ClassVar[int]
    SECOND_ORDER_FIELD_NUMBER: _ClassVar[int]
    psi2: float
    second_order: bool
    def __init__(self, second_order: bool = ..., psi2: _Optional[float] = ...) -> None: ...

class Coefficient(_message.Message):
    __slots__ = ["type", "value"]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    type: CoefficientType
    value: float
    def __init__(self, value: _Optional[float] = ..., type: _Optional[_Union[CoefficientType, str]] = ...) -> None: ...

class CombinationPart(_message.Message):
    __slots__ = ["coefficients", "favourable_permanent_load", "lcase_guid"]
    COEFFICIENTS_FIELD_NUMBER: _ClassVar[int]
    FAVOURABLE_PERMANENT_LOAD_FIELD_NUMBER: _ClassVar[int]
    LCASE_GUID_FIELD_NUMBER: _ClassVar[int]
    coefficients: _containers.RepeatedCompositeFieldContainer[Coefficient]
    favourable_permanent_load: bool
    lcase_guid: str
    def __init__(self, lcase_guid: _Optional[str] = ..., coefficients: _Optional[_Iterable[_Union[Coefficient, _Mapping]]] = ..., favourable_permanent_load: bool = ...) -> None: ...

class Compaction(_message.Message):
    __slots__ = ["pcmax", "zp"]
    PCMAX_FIELD_NUMBER: _ClassVar[int]
    ZP_FIELD_NUMBER: _ClassVar[int]
    pcmax: float
    zp: float
    def __init__(self, zp: _Optional[float] = ..., pcmax: _Optional[float] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["beam_config", "coa", "deactive", "dependent_lcomb_guid", "description", "dominating_lcase_guid", "earth_pressure_config", "foundation_config", "geo_type", "id", "kfi", "limit_state", "parts", "pile_config", "type", "user_defined"]
    BEAM_CONFIG_FIELD_NUMBER: _ClassVar[int]
    COA_FIELD_NUMBER: _ClassVar[int]
    DEACTIVE_FIELD_NUMBER: _ClassVar[int]
    DEPENDENT_LCOMB_GUID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DOMINATING_LCASE_GUID_FIELD_NUMBER: _ClassVar[int]
    EARTH_PRESSURE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    FOUNDATION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    GEO_TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    KFI_FIELD_NUMBER: _ClassVar[int]
    LIMIT_STATE_FIELD_NUMBER: _ClassVar[int]
    PARTS_FIELD_NUMBER: _ClassVar[int]
    PILE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_FIELD_NUMBER: _ClassVar[int]
    beam_config: BeamConfiguration
    coa: CoaType
    deactive: bool
    dependent_lcomb_guid: str
    description: str
    dominating_lcase_guid: str
    earth_pressure_config: EarthPressureConfiguration
    foundation_config: FoundationConfiguration
    geo_type: GeoType
    id: _utils_pb2.ID
    kfi: float
    limit_state: LimitState
    parts: _containers.RepeatedCompositeFieldContainer[CombinationPart]
    pile_config: PileConfiguration
    type: Type
    user_defined: bool
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., type: _Optional[_Union[Type, str]] = ..., limit_state: _Optional[_Union[LimitState, str]] = ..., dependent_lcomb_guid: _Optional[str] = ..., parts: _Optional[_Iterable[_Union[CombinationPart, _Mapping]]] = ..., coa: _Optional[_Union[CoaType, str]] = ..., deactive: bool = ..., description: _Optional[str] = ..., geo_type: _Optional[_Union[GeoType, str]] = ..., kfi: _Optional[float] = ..., beam_config: _Optional[_Union[BeamConfiguration, _Mapping]] = ..., foundation_config: _Optional[_Union[FoundationConfiguration, _Mapping]] = ..., earth_pressure_config: _Optional[_Union[EarthPressureConfiguration, _Mapping]] = ..., pile_config: _Optional[_Union[PileConfiguration, _Mapping]] = ..., dominating_lcase_guid: _Optional[str] = ..., user_defined: bool = ...) -> None: ...

class EarthPressureConfiguration(_message.Message):
    __slots__ = ["active", "passive"]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    PASSIVE_FIELD_NUMBER: _ClassVar[int]
    active: ActiveEarthPressureConfiguration
    passive: PassiveEarthPressureConfiguration
    def __init__(self, active: _Optional[_Union[ActiveEarthPressureConfiguration, _Mapping]] = ..., passive: _Optional[_Union[PassiveEarthPressureConfiguration, _Mapping]] = ...) -> None: ...

class FoundationConfiguration(_message.Message):
    __slots__ = ["ground_water_guid"]
    GROUND_WATER_GUID_FIELD_NUMBER: _ClassVar[int]
    ground_water_guid: str
    def __init__(self, ground_water_guid: _Optional[str] = ...) -> None: ...

class PassiveEarthPressureConfiguration(_message.Message):
    __slots__ = ["passive_earth_pressure_type", "passive_ground_water_guid"]
    PASSIVE_EARTH_PRESSURE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PASSIVE_GROUND_WATER_GUID_FIELD_NUMBER: _ClassVar[int]
    passive_earth_pressure_type: _soil_pb2.PassiveEarthPressureType
    passive_ground_water_guid: str
    def __init__(self, passive_earth_pressure_type: _Optional[_Union[_soil_pb2.PassiveEarthPressureType, str]] = ..., passive_ground_water_guid: _Optional[str] = ...) -> None: ...

class PileConfiguration(_message.Message):
    __slots__ = ["ground_water_guid", "is_negative"]
    GROUND_WATER_GUID_FIELD_NUMBER: _ClassVar[int]
    IS_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    ground_water_guid: str
    is_negative: bool
    def __init__(self, is_negative: bool = ..., ground_water_guid: _Optional[str] = ...) -> None: ...

class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class CoaType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ServiceabilityType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class LimitState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class CoefficientType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class GeoType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
