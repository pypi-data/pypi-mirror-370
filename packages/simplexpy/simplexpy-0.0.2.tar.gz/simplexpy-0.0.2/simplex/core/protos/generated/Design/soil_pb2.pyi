from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

ACTIVE_EARTH_PRESSURE_TYPE_COMPACTION: ActiveEarthPressureType
ACTIVE_EARTH_PRESSURE_TYPE_PRESSURE: ActiveEarthPressureType
ACTIVE_EARTH_PRESSURE_TYPE_REST: ActiveEarthPressureType
ACTIVE_EARTH_PRESSURE_TYPE_UNSPECIFIED: ActiveEarthPressureType
DESCRIPTOR: _descriptor.FileDescriptor
DESIGN_APPROACH_1: DesignApproach
DESIGN_APPROACH_2: DesignApproach
DESIGN_APPROACH_3: DesignApproach
DESIGN_APPROACH_UNSPECIFIED: DesignApproach
FOUNDATION_DISTRIBUTION_ELASTIC: FoundationDistribution
FOUNDATION_DISTRIBUTION_PLASTIC: FoundationDistribution
FOUNDATION_DISTRIBUTION_UNSPECIFIED: FoundationDistribution
GEOTECHNICAL_CATEGORY_1: GeotechnicalCategory
GEOTECHNICAL_CATEGORY_2: GeotechnicalCategory
GEOTECHNICAL_CATEGORY_3: GeotechnicalCategory
GEOTECHNICAL_CATEGORY_UNSPECIFIED: GeotechnicalCategory
MATERIAL_MODEL_BOTH_COMB: DesignApproach
MATERIAL_MODEL_SINGLE_COMB: DesignApproach
MAX_VALUES_ALPHA: MaxValues
MAX_VALUES_BETA: MaxValues
MAX_VALUES_DELTA_L: MaxValues
MAX_VALUES_DELTA_S: MaxValues
MAX_VALUES_OMEGA: MaxValues
MAX_VALUES_THETA: MaxValues
MAX_VALUES_UNSPECIFIED: MaxValues
PASSIVE_EARTH_PRESSURE_TYPE_PRESSURE: PassiveEarthPressureType
PASSIVE_EARTH_PRESSURE_TYPE_REST: PassiveEarthPressureType
PASSIVE_EARTH_PRESSURE_TYPE_UNSPECIFIED: PassiveEarthPressureType
RESISTANCE_MODEL: DesignApproach
SOIL_PUNCHING_TYPE_1_2: SoilPunchingType
SOIL_PUNCHING_TYPE_1_3: SoilPunchingType
SOIL_PUNCHING_TYPE_1_4: SoilPunchingType
SOIL_PUNCHING_TYPE_8_DEGREE: SoilPunchingType
SOIL_PUNCHING_TYPE_UNSPECIFIED: SoilPunchingType
SOIL_PUNCHING_TYPE_WIDTH_1_2: SoilPunchingType

class EarthPressureConfiguration(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class EarthPressureElementConfiguration(_message.Message):
    __slots__ = ["active_soil_friction_coef", "lambda_found_by_interpolation"]
    ACTIVE_SOIL_FRICTION_COEF_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_FOUND_BY_INTERPOLATION_FIELD_NUMBER: _ClassVar[int]
    active_soil_friction_coef: float
    lambda_found_by_interpolation: bool
    def __init__(self, active_soil_friction_coef: _Optional[float] = ..., lambda_found_by_interpolation: bool = ..., **kwargs) -> None: ...

class ElementDesignSettings(_message.Message):
    __slots__ = ["earth_pressure_element_configuration", "foundation_element_configuration", "pile_element_configuration"]
    EARTH_PRESSURE_ELEMENT_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    FOUNDATION_ELEMENT_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    PILE_ELEMENT_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    earth_pressure_element_configuration: EarthPressureElementConfiguration
    foundation_element_configuration: FoundationElementConfiguration
    pile_element_configuration: PileElementConfiguration
    def __init__(self, foundation_element_configuration: _Optional[_Union[FoundationElementConfiguration, _Mapping]] = ..., earth_pressure_element_configuration: _Optional[_Union[EarthPressureElementConfiguration, _Mapping]] = ..., pile_element_configuration: _Optional[_Union[PileElementConfiguration, _Mapping]] = ...) -> None: ...

class FoundationConfiguration(_message.Message):
    __slots__ = ["design_approach"]
    DESIGN_APPROACH_FIELD_NUMBER: _ClassVar[int]
    design_approach: DesignApproach
    def __init__(self, design_approach: _Optional[_Union[DesignApproach, str]] = ...) -> None: ...

class FoundationElementConfiguration(_message.Message):
    __slots__ = ["depht_factor", "foundation_distribution", "settlement_configuration", "soil_punching_type", "use_b6"]
    DEPHT_FACTOR_FIELD_NUMBER: _ClassVar[int]
    FOUNDATION_DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    SETTLEMENT_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    SOIL_PUNCHING_TYPE_FIELD_NUMBER: _ClassVar[int]
    USE_B6_FIELD_NUMBER: _ClassVar[int]
    depht_factor: bool
    foundation_distribution: FoundationDistribution
    settlement_configuration: SettlementConfiguration
    soil_punching_type: SoilPunchingType
    use_b6: bool
    def __init__(self, settlement_configuration: _Optional[_Union[SettlementConfiguration, _Mapping]] = ..., soil_punching_type: _Optional[_Union[SoilPunchingType, str]] = ..., foundation_distribution: _Optional[_Union[FoundationDistribution, str]] = ..., depht_factor: bool = ..., use_b6: bool = ...) -> None: ...

class GammaPermanent(_message.Message):
    __slots__ = ["unfavorable"]
    UNFAVORABLE_FIELD_NUMBER: _ClassVar[int]
    unfavorable: float
    def __init__(self, unfavorable: _Optional[float] = ...) -> None: ...

class GammaPile(_message.Message):
    __slots__ = ["gamma_b", "gamma_sc", "gamma_st", "gamma_t"]
    GAMMA_B_FIELD_NUMBER: _ClassVar[int]
    GAMMA_SC_FIELD_NUMBER: _ClassVar[int]
    GAMMA_ST_FIELD_NUMBER: _ClassVar[int]
    GAMMA_T_FIELD_NUMBER: _ClassVar[int]
    gamma_b: float
    gamma_sc: float
    gamma_st: float
    gamma_t: float
    def __init__(self, gamma_sc: _Optional[float] = ..., gamma_st: _Optional[float] = ..., gamma_b: _Optional[float] = ..., gamma_t: _Optional[float] = ...) -> None: ...

class GammaPiles(_message.Message):
    __slots__ = ["bored", "cfa", "driven"]
    BORED_FIELD_NUMBER: _ClassVar[int]
    CFA_FIELD_NUMBER: _ClassVar[int]
    DRIVEN_FIELD_NUMBER: _ClassVar[int]
    bored: GammaPile
    cfa: GammaPile
    driven: GammaPile
    def __init__(self, driven: _Optional[_Union[GammaPile, _Mapping]] = ..., cfa: _Optional[_Union[GammaPile, _Mapping]] = ..., bored: _Optional[_Union[GammaPile, _Mapping]] = ...) -> None: ...

class GammaResistance(_message.Message):
    __slots__ = ["gamma_rh", "gamma_rv"]
    GAMMA_RH_FIELD_NUMBER: _ClassVar[int]
    GAMMA_RV_FIELD_NUMBER: _ClassVar[int]
    gamma_rh: float
    gamma_rv: float
    def __init__(self, gamma_rv: _Optional[float] = ..., gamma_rh: _Optional[float] = ...) -> None: ...

class GammaSoil(_message.Message):
    __slots__ = ["gamma_c", "gamma_cu", "gamma_gamma", "gamma_phi", "gamma_qu"]
    GAMMA_CU_FIELD_NUMBER: _ClassVar[int]
    GAMMA_C_FIELD_NUMBER: _ClassVar[int]
    GAMMA_GAMMA_FIELD_NUMBER: _ClassVar[int]
    GAMMA_PHI_FIELD_NUMBER: _ClassVar[int]
    GAMMA_QU_FIELD_NUMBER: _ClassVar[int]
    gamma_c: float
    gamma_cu: float
    gamma_gamma: float
    gamma_phi: float
    gamma_qu: float
    def __init__(self, gamma_cu: _Optional[float] = ..., gamma_c: _Optional[float] = ..., gamma_phi: _Optional[float] = ..., gamma_gamma: _Optional[float] = ..., gamma_qu: _Optional[float] = ...) -> None: ...

class GeneralDesignSettings(_message.Message):
    __slots__ = ["earth_pressure_configuration", "foundation_configuration", "geotechnical_category", "partial_coeffs", "pile_configuration", "settlement_setup"]
    EARTH_PRESSURE_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    FOUNDATION_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    GEOTECHNICAL_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_COEFFS_FIELD_NUMBER: _ClassVar[int]
    PILE_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    SETTLEMENT_SETUP_FIELD_NUMBER: _ClassVar[int]
    earth_pressure_configuration: EarthPressureConfiguration
    foundation_configuration: FoundationConfiguration
    geotechnical_category: GeotechnicalCategory
    partial_coeffs: PartialCoefficients
    pile_configuration: PileConfiguration
    settlement_setup: _containers.RepeatedCompositeFieldContainer[SettlementSetup]
    def __init__(self, partial_coeffs: _Optional[_Union[PartialCoefficients, _Mapping]] = ..., geotechnical_category: _Optional[_Union[GeotechnicalCategory, str]] = ..., settlement_setup: _Optional[_Iterable[_Union[SettlementSetup, _Mapping]]] = ..., foundation_configuration: _Optional[_Union[FoundationConfiguration, _Mapping]] = ..., earth_pressure_configuration: _Optional[_Union[EarthPressureConfiguration, _Mapping]] = ..., pile_configuration: _Optional[_Union[PileConfiguration, _Mapping]] = ...) -> None: ...

class MaterialFactors(_message.Message):
    __slots__ = ["m_concrete", "m_other", "m_steel", "m_timber"]
    M_CONCRETE_FIELD_NUMBER: _ClassVar[int]
    M_OTHER_FIELD_NUMBER: _ClassVar[int]
    M_STEEL_FIELD_NUMBER: _ClassVar[int]
    M_TIMBER_FIELD_NUMBER: _ClassVar[int]
    m_concrete: float
    m_other: float
    m_steel: float
    m_timber: float
    def __init__(self, m_concrete: _Optional[float] = ..., m_timber: _Optional[float] = ..., m_steel: _Optional[float] = ..., m_other: _Optional[float] = ...) -> None: ...

class ModelFactor(_message.Message):
    __slots__ = ["gamma_alfa_drained", "gamma_alfa_undrained", "gamma_beta", "gamma_rock"]
    GAMMA_ALFA_DRAINED_FIELD_NUMBER: _ClassVar[int]
    GAMMA_ALFA_UNDRAINED_FIELD_NUMBER: _ClassVar[int]
    GAMMA_BETA_FIELD_NUMBER: _ClassVar[int]
    GAMMA_ROCK_FIELD_NUMBER: _ClassVar[int]
    gamma_alfa_drained: float
    gamma_alfa_undrained: float
    gamma_beta: float
    gamma_rock: float
    def __init__(self, gamma_beta: _Optional[float] = ..., gamma_alfa_drained: _Optional[float] = ..., gamma_alfa_undrained: _Optional[float] = ..., gamma_rock: _Optional[float] = ...) -> None: ...

class ModelFactors(_message.Message):
    __slots__ = ["modelfactor_b", "modelfactor_sc", "modelfactor_st"]
    MODELFACTOR_B_FIELD_NUMBER: _ClassVar[int]
    MODELFACTOR_SC_FIELD_NUMBER: _ClassVar[int]
    MODELFACTOR_ST_FIELD_NUMBER: _ClassVar[int]
    modelfactor_b: ModelFactor
    modelfactor_sc: ModelFactor
    modelfactor_st: ModelFactor
    def __init__(self, modelfactor_sc: _Optional[_Union[ModelFactor, _Mapping]] = ..., modelfactor_st: _Optional[_Union[ModelFactor, _Mapping]] = ..., modelfactor_b: _Optional[_Union[ModelFactor, _Mapping]] = ...) -> None: ...

class PartialCoefficient(_message.Message):
    __slots__ = ["a1", "a2", "gamma_factor_geotechnical_category_one", "m1", "m2", "p1", "p2", "p3", "p4", "r1", "r2", "r3"]
    A1_FIELD_NUMBER: _ClassVar[int]
    A2_FIELD_NUMBER: _ClassVar[int]
    GAMMA_FACTOR_GEOTECHNICAL_CATEGORY_ONE_FIELD_NUMBER: _ClassVar[int]
    M1_FIELD_NUMBER: _ClassVar[int]
    M2_FIELD_NUMBER: _ClassVar[int]
    P1_FIELD_NUMBER: _ClassVar[int]
    P2_FIELD_NUMBER: _ClassVar[int]
    P3_FIELD_NUMBER: _ClassVar[int]
    P4_FIELD_NUMBER: _ClassVar[int]
    R1_FIELD_NUMBER: _ClassVar[int]
    R2_FIELD_NUMBER: _ClassVar[int]
    R3_FIELD_NUMBER: _ClassVar[int]
    a1: GammaPermanent
    a2: GammaPermanent
    gamma_factor_geotechnical_category_one: float
    m1: GammaSoil
    m2: GammaSoil
    p1: GammaPiles
    p2: GammaPiles
    p3: GammaPiles
    p4: GammaPiles
    r1: GammaResistance
    r2: GammaResistance
    r3: GammaResistance
    def __init__(self, m1: _Optional[_Union[GammaSoil, _Mapping]] = ..., m2: _Optional[_Union[GammaSoil, _Mapping]] = ..., r1: _Optional[_Union[GammaResistance, _Mapping]] = ..., r2: _Optional[_Union[GammaResistance, _Mapping]] = ..., r3: _Optional[_Union[GammaResistance, _Mapping]] = ..., a1: _Optional[_Union[GammaPermanent, _Mapping]] = ..., a2: _Optional[_Union[GammaPermanent, _Mapping]] = ..., gamma_factor_geotechnical_category_one: _Optional[float] = ..., p1: _Optional[_Union[GammaPiles, _Mapping]] = ..., p2: _Optional[_Union[GammaPiles, _Mapping]] = ..., p3: _Optional[_Union[GammaPiles, _Mapping]] = ..., p4: _Optional[_Union[GammaPiles, _Mapping]] = ...) -> None: ...

class PartialCoefficients(_message.Message):
    __slots__ = ["accidental", "seismic", "ultimate"]
    ACCIDENTAL_FIELD_NUMBER: _ClassVar[int]
    SEISMIC_FIELD_NUMBER: _ClassVar[int]
    ULTIMATE_FIELD_NUMBER: _ClassVar[int]
    accidental: PartialCoefficient
    seismic: PartialCoefficient
    ultimate: PartialCoefficient
    def __init__(self, ultimate: _Optional[_Union[PartialCoefficient, _Mapping]] = ..., accidental: _Optional[_Union[PartialCoefficient, _Mapping]] = ..., seismic: _Optional[_Union[PartialCoefficient, _Mapping]] = ...) -> None: ...

class PileConfiguration(_message.Message):
    __slots__ = ["design_approach", "material_factors", "model_factors"]
    DESIGN_APPROACH_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_FACTORS_FIELD_NUMBER: _ClassVar[int]
    MODEL_FACTORS_FIELD_NUMBER: _ClassVar[int]
    design_approach: DesignApproach
    material_factors: MaterialFactors
    model_factors: ModelFactors
    def __init__(self, design_approach: _Optional[_Union[DesignApproach, str]] = ..., material_factors: _Optional[_Union[MaterialFactors, _Mapping]] = ..., model_factors: _Optional[_Union[ModelFactors, _Mapping]] = ...) -> None: ...

class PileElementConfiguration(_message.Message):
    __slots__ = ["coorolation_factor"]
    COOROLATION_FACTOR_FIELD_NUMBER: _ClassVar[int]
    coorolation_factor: float
    def __init__(self, coorolation_factor: _Optional[float] = ...) -> None: ...

class SettlementConfiguration(_message.Message):
    __slots__ = ["absolute_settlement", "check_absolute_settlement"]
    ABSOLUTE_SETTLEMENT_FIELD_NUMBER: _ClassVar[int]
    CHECK_ABSOLUTE_SETTLEMENT_FIELD_NUMBER: _ClassVar[int]
    absolute_settlement: float
    check_absolute_settlement: bool
    def __init__(self, check_absolute_settlement: bool = ..., absolute_settlement: _Optional[float] = ...) -> None: ...

class SettlementSetup(_message.Message):
    __slots__ = ["limit_type", "limit_value"]
    LIMIT_TYPE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_VALUE_FIELD_NUMBER: _ClassVar[int]
    limit_type: MaxValues
    limit_value: float
    def __init__(self, limit_type: _Optional[_Union[MaxValues, str]] = ..., limit_value: _Optional[float] = ...) -> None: ...

class FoundationDistribution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DesignApproach(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class GeotechnicalCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class SoilPunchingType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ActiveEarthPressureType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class PassiveEarthPressureType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class MaxValues(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
