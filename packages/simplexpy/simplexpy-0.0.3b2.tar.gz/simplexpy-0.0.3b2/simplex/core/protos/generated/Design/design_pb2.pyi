from Design import load_pb2 as _load_pb2
from Loading import loadcombination_pb2 as _loadcombination_pb2
from Design import concrete_pb2 as _concrete_pb2
from Design import steel_pb2 as _steel_pb2
from Utils import utils_pb2 as _utils_pb2
from Design import timber_pb2 as _timber_pb2
from FireProtection import timber_pb2 as _timber_pb2_1
from Design import soil_pb2 as _soil_pb2
from Design import general_pb2 as _general_pb2
from Utils import utils_pb2 as _utils_pb2_1
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Design.load_pb2 import GammaSupInf
from Design.load_pb2 import GammaLoad
from Design.load_pb2 import GammaSet
from Design.load_pb2 import GeneralDesignSettings
from Design.load_pb2 import ElementDesignSettings
from Design.load_pb2 import Formula
from Design.concrete_pb2 import PartialCoefficient
from Design.concrete_pb2 import PartialCoefficients
from Design.concrete_pb2 import CoverAndSpace
from Design.concrete_pb2 import FireBeam
from Design.concrete_pb2 import Beam
from Design.concrete_pb2 import Column
from Design.concrete_pb2 import Wall
from Design.concrete_pb2 import PrestressedBeam
from Design.concrete_pb2 import HC
from Design.concrete_pb2 import Slab
from Design.concrete_pb2 import GeneralDesignSettings
from Design.concrete_pb2 import ElementDesignSettings
from Design.concrete_pb2 import Fabrication
from Design.concrete_pb2 import ColumnPlacement
from Design.concrete_pb2 import BeamSide
from Design.concrete_pb2 import ConstructionClass
from Design.concrete_pb2 import ShearDesignType
from Design.concrete_pb2 import WebShearCapacityMethod
from Design.concrete_pb2 import SurfaceType
from Design.concrete_pb2 import FctmType
from Design.concrete_pb2 import Commands
from Design.concrete_pb2 import Aggregates
from Design.steel_pb2 import PartialCoefficient
from Design.steel_pb2 import PartialCoefficients
from Design.steel_pb2 import GeneralDesignSettings
from Design.steel_pb2 import BeamSettings
from Design.steel_pb2 import ProtectingMaterial
from Design.steel_pb2 import Fire
from Design.steel_pb2 import ElementDesignSettings
from Design.steel_pb2 import SecondOrderAnalysis
from Design.steel_pb2 import InteractionMethod
from Design.steel_pb2 import LateralTorsionalMethod
from Design.steel_pb2 import BucklingCurveFlexural
from Design.steel_pb2 import BucklingCurveLateral
from Design.steel_pb2 import SectionExposure
from Design.timber_pb2 import PartialCoefficient
from Design.timber_pb2 import PartialCoefficients
from Design.timber_pb2 import GeneralDesignSettings
from Design.timber_pb2 import BeamSettings
from Design.timber_pb2 import CharringRate
from Design.timber_pb2 import FireProtection
from Design.timber_pb2 import Fire
from Design.timber_pb2 import ElementDesignSettings
from Design.timber_pb2 import ServiceClass
from Design.timber_pb2 import SecondOrderAnalysis
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
from Design.general_pb2 import PartialCoefficient
from Design.general_pb2 import PartialCoefficients
from Design.general_pb2 import FireGeneral
from Design.general_pb2 import FireRadiativeHeatFlux
from Design.general_pb2 import ElementDesignSettings
from Design.general_pb2 import GeneralDesignSettings
from Design.general_pb2 import TemperatureCurve
ACTIVE_EARTH_PRESSURE_TYPE_COMPACTION: _soil_pb2.ActiveEarthPressureType
ACTIVE_EARTH_PRESSURE_TYPE_PRESSURE: _soil_pb2.ActiveEarthPressureType
ACTIVE_EARTH_PRESSURE_TYPE_REST: _soil_pb2.ActiveEarthPressureType
ACTIVE_EARTH_PRESSURE_TYPE_UNSPECIFIED: _soil_pb2.ActiveEarthPressureType
AGGREGATE_CALCAREOUS: _concrete_pb2.Aggregates
AGGREGATE_DK_CALCAREOUS: _concrete_pb2.Aggregates
AGGREGATE_DK_SILICEOUS: _concrete_pb2.Aggregates
AGGREGATE_SILICEOUS: _concrete_pb2.Aggregates
AGGREGATE_UNSPECIFIED: _concrete_pb2.Aggregates
BEAM_SIDE_BOTTOM: _concrete_pb2.BeamSide
BEAM_SIDE_END: _concrete_pb2.BeamSide
BEAM_SIDE_LEFT: _concrete_pb2.BeamSide
BEAM_SIDE_RIGHT: _concrete_pb2.BeamSide
BEAM_SIDE_START: _concrete_pb2.BeamSide
BEAM_SIDE_TOP: _concrete_pb2.BeamSide
BEAM_SIDE_UNSPECIFIED: _concrete_pb2.BeamSide
BUCKLING_CURVE_FLEXURAL_A: _steel_pb2.BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_A0: _steel_pb2.BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_AUTO: _steel_pb2.BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_B: _steel_pb2.BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_C: _steel_pb2.BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_D: _steel_pb2.BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_UNSPECIFIED: _steel_pb2.BucklingCurveFlexural
BUCKLING_CURVE_LATERAL_A: _steel_pb2.BucklingCurveLateral
BUCKLING_CURVE_LATERAL_AUTO: _steel_pb2.BucklingCurveLateral
BUCKLING_CURVE_LATERAL_B: _steel_pb2.BucklingCurveLateral
BUCKLING_CURVE_LATERAL_C: _steel_pb2.BucklingCurveLateral
BUCKLING_CURVE_LATERAL_D: _steel_pb2.BucklingCurveLateral
BUCKLING_CURVE_LATERAL_UNSPECIFIED: _steel_pb2.BucklingCurveLateral
COLUMN_PLACEMENT_CENTER: _concrete_pb2.ColumnPlacement
COLUMN_PLACEMENT_CORNER: _concrete_pb2.ColumnPlacement
COLUMN_PLACEMENT_EDGE: _concrete_pb2.ColumnPlacement
COLUMN_PLACEMENT_UNSPECIFIED: _concrete_pb2.ColumnPlacement
COMMANDS_PUNCHING_CHECK: _concrete_pb2.Commands
COMMANDS_SPALLING_CHECK: _concrete_pb2.Commands
COMMANDS_STIRRUP_DESIGN: _concrete_pb2.Commands
COMMANDS_UNSPECIFIED: _concrete_pb2.Commands
CONSTRUCTION_CLASS_1: _concrete_pb2.ConstructionClass
CONSTRUCTION_CLASS_2: _concrete_pb2.ConstructionClass
CONSTRUCTION_CLASS_UNSPECIFIED: _concrete_pb2.ConstructionClass
DESCRIPTOR: _descriptor.FileDescriptor
DESIGN_APPROACH_1: _soil_pb2.DesignApproach
DESIGN_APPROACH_2: _soil_pb2.DesignApproach
DESIGN_APPROACH_3: _soil_pb2.DesignApproach
DESIGN_APPROACH_UNSPECIFIED: _soil_pb2.DesignApproach
FABRICATION_IN_SITU: _concrete_pb2.Fabrication
FABRICATION_PREFAB: _concrete_pb2.Fabrication
FABRICATION_UNSPECIFIED: _concrete_pb2.Fabrication
FCTM_TYPE_FCTM: _concrete_pb2.FctmType
FCTM_TYPE_FCTM_FL: _concrete_pb2.FctmType
FCTM_TYPE_FCTM_XI: _concrete_pb2.FctmType
FCTM_TYPE_UNSPECIFIED: _concrete_pb2.FctmType
FORMULA_812: _load_pb2.Formula
FORMULA_813: _load_pb2.Formula
FORMULA_814: _load_pb2.Formula
FORMULA_UNSPECIFIED: _load_pb2.Formula
FOUNDATION_DISTRIBUTION_ELASTIC: _soil_pb2.FoundationDistribution
FOUNDATION_DISTRIBUTION_PLASTIC: _soil_pb2.FoundationDistribution
FOUNDATION_DISTRIBUTION_UNSPECIFIED: _soil_pb2.FoundationDistribution
GEOTECHNICAL_CATEGORY_1: _soil_pb2.GeotechnicalCategory
GEOTECHNICAL_CATEGORY_2: _soil_pb2.GeotechnicalCategory
GEOTECHNICAL_CATEGORY_3: _soil_pb2.GeotechnicalCategory
GEOTECHNICAL_CATEGORY_UNSPECIFIED: _soil_pb2.GeotechnicalCategory
INTERACTION_METHOD_METHOD1: _steel_pb2.InteractionMethod
INTERACTION_METHOD_METHOD2: _steel_pb2.InteractionMethod
INTERACTION_METHOD_UNSPECIFIED: _steel_pb2.InteractionMethod
LATERAL_TORSIONAL_METHOD_GENERAL: _steel_pb2.LateralTorsionalMethod
LATERAL_TORSIONAL_METHOD_GENERAL_SPEC_FOR_I: _steel_pb2.LateralTorsionalMethod
LATERAL_TORSIONAL_METHOD_SIMPLIFIED: _steel_pb2.LateralTorsionalMethod
LATERAL_TORSIONAL_METHOD_UNSPECIFIED: _steel_pb2.LateralTorsionalMethod
MATERIAL_MODEL_BOTH_COMB: _soil_pb2.DesignApproach
MATERIAL_MODEL_SINGLE_COMB: _soil_pb2.DesignApproach
MAX_VALUES_ALPHA: _soil_pb2.MaxValues
MAX_VALUES_BETA: _soil_pb2.MaxValues
MAX_VALUES_DELTA_L: _soil_pb2.MaxValues
MAX_VALUES_DELTA_S: _soil_pb2.MaxValues
MAX_VALUES_OMEGA: _soil_pb2.MaxValues
MAX_VALUES_THETA: _soil_pb2.MaxValues
MAX_VALUES_UNSPECIFIED: _soil_pb2.MaxValues
PASSIVE_EARTH_PRESSURE_TYPE_PRESSURE: _soil_pb2.PassiveEarthPressureType
PASSIVE_EARTH_PRESSURE_TYPE_REST: _soil_pb2.PassiveEarthPressureType
PASSIVE_EARTH_PRESSURE_TYPE_UNSPECIFIED: _soil_pb2.PassiveEarthPressureType
RESISTANCE_MODEL: _soil_pb2.DesignApproach
SECOND_ORDER_ANALYSIS_CONSIDER: _timber_pb2.SecondOrderAnalysis
SECOND_ORDER_ANALYSIS_FIRST_ORDER_DESIGN: _timber_pb2.SecondOrderAnalysis
SECOND_ORDER_ANALYSIS_IGNORE: _timber_pb2.SecondOrderAnalysis
SECOND_ORDER_ANALYSIS_UNSPECIFIED: _timber_pb2.SecondOrderAnalysis
SECTION_EXPOSURE_ALL_SIDES: _steel_pb2.SectionExposure
SECTION_EXPOSURE_FLANGE_ONLY: _steel_pb2.SectionExposure
SECTION_EXPOSURE_THREE_SIDES: _steel_pb2.SectionExposure
SECTION_EXPOSURE_UNSPECIFIED: _steel_pb2.SectionExposure
SERVICE_CLASS_1: _timber_pb2.ServiceClass
SERVICE_CLASS_2: _timber_pb2.ServiceClass
SERVICE_CLASS_3: _timber_pb2.ServiceClass
SERVICE_CLASS_UNSPECIFIED: _timber_pb2.ServiceClass
SHEAR_DESIGN_TYPE_UNSPECIFIED: _concrete_pb2.ShearDesignType
SHEAR_DESIGN_TYPE_WITHOUT_SHEAR_REINFORCEMENT: _concrete_pb2.ShearDesignType
SHEAR_DESIGN_TYPE_WITH_SHEAR_REINFORCEMENT: _concrete_pb2.ShearDesignType
SOIL_PUNCHING_TYPE_1_2: _soil_pb2.SoilPunchingType
SOIL_PUNCHING_TYPE_1_3: _soil_pb2.SoilPunchingType
SOIL_PUNCHING_TYPE_1_4: _soil_pb2.SoilPunchingType
SOIL_PUNCHING_TYPE_8_DEGREE: _soil_pb2.SoilPunchingType
SOIL_PUNCHING_TYPE_UNSPECIFIED: _soil_pb2.SoilPunchingType
SOIL_PUNCHING_TYPE_WIDTH_1_2: _soil_pb2.SoilPunchingType
SURFACE_TYPE_INDENTED: _concrete_pb2.SurfaceType
SURFACE_TYPE_ROUGH: _concrete_pb2.SurfaceType
SURFACE_TYPE_SMOOTH: _concrete_pb2.SurfaceType
SURFACE_TYPE_UNSPECIFIED: _concrete_pb2.SurfaceType
SURFACE_TYPE_VERY_SMOOTH: _concrete_pb2.SurfaceType
TEMPERATURE_CURVE_EXTERNAL: _general_pb2.TemperatureCurve
TEMPERATURE_CURVE_HYDROCARBON: _general_pb2.TemperatureCurve
TEMPERATURE_CURVE_PARAMETRIC: _general_pb2.TemperatureCurve
TEMPERATURE_CURVE_STANDARD: _general_pb2.TemperatureCurve
TEMPERATURE_CURVE_UNSPECIFIED: _general_pb2.TemperatureCurve
WEB_SHEAR_CAPACITY_METHOD_ADVANCED: _concrete_pb2.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_SIMPLIFIED: _concrete_pb2.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_STANDARD: _concrete_pb2.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_UNSPECIFIED: _concrete_pb2.WebShearCapacityMethod

class ElementDesignSettings(_message.Message):
    __slots__ = ["general", "load", "rc", "soil", "steel", "timber"]
    GENERAL_FIELD_NUMBER: _ClassVar[int]
    LOAD_FIELD_NUMBER: _ClassVar[int]
    RC_FIELD_NUMBER: _ClassVar[int]
    SOIL_FIELD_NUMBER: _ClassVar[int]
    STEEL_FIELD_NUMBER: _ClassVar[int]
    TIMBER_FIELD_NUMBER: _ClassVar[int]
    general: _general_pb2.ElementDesignSettings
    load: _concrete_pb2.ElementDesignSettings
    rc: _concrete_pb2.ElementDesignSettings
    soil: _soil_pb2.ElementDesignSettings
    steel: _steel_pb2.ElementDesignSettings
    timber: _timber_pb2.ElementDesignSettings
    def __init__(self, load: _Optional[_Union[_concrete_pb2.ElementDesignSettings, _Mapping]] = ..., rc: _Optional[_Union[_concrete_pb2.ElementDesignSettings, _Mapping]] = ..., steel: _Optional[_Union[_steel_pb2.ElementDesignSettings, _Mapping]] = ..., timber: _Optional[_Union[_timber_pb2.ElementDesignSettings, _Mapping]] = ..., soil: _Optional[_Union[_soil_pb2.ElementDesignSettings, _Mapping]] = ..., general: _Optional[_Union[_general_pb2.ElementDesignSettings, _Mapping]] = ...) -> None: ...

class GeneralDesignSettings(_message.Message):
    __slots__ = ["general", "load", "rc", "soil", "steel", "timber"]
    GENERAL_FIELD_NUMBER: _ClassVar[int]
    LOAD_FIELD_NUMBER: _ClassVar[int]
    RC_FIELD_NUMBER: _ClassVar[int]
    SOIL_FIELD_NUMBER: _ClassVar[int]
    STEEL_FIELD_NUMBER: _ClassVar[int]
    TIMBER_FIELD_NUMBER: _ClassVar[int]
    general: _general_pb2.GeneralDesignSettings
    load: _load_pb2.GeneralDesignSettings
    rc: _concrete_pb2.GeneralDesignSettings
    soil: _soil_pb2.GeneralDesignSettings
    steel: _steel_pb2.GeneralDesignSettings
    timber: _timber_pb2.GeneralDesignSettings
    def __init__(self, load: _Optional[_Union[_load_pb2.GeneralDesignSettings, _Mapping]] = ..., rc: _Optional[_Union[_concrete_pb2.GeneralDesignSettings, _Mapping]] = ..., steel: _Optional[_Union[_steel_pb2.GeneralDesignSettings, _Mapping]] = ..., timber: _Optional[_Union[_timber_pb2.GeneralDesignSettings, _Mapping]] = ..., soil: _Optional[_Union[_soil_pb2.GeneralDesignSettings, _Mapping]] = ..., general: _Optional[_Union[_general_pb2.GeneralDesignSettings, _Mapping]] = ...) -> None: ...
