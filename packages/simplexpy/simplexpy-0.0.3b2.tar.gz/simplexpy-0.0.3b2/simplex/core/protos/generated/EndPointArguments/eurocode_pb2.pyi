from Design import concrete_pb2 as _concrete_pb2
from Loading import loadcombination_pb2 as _loadcombination_pb2
from Utils import utils_pb2 as _utils_pb2
from Design import soil_pb2 as _soil_pb2
from Utils import eurocode_pb2 as _eurocode_pb2
from Utils import log_pb2 as _log_pb2
import element_pb2 as _element_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Geometry import geometry_pb2 as _geometry_pb2
from Geometry import beam_pb2 as _beam_pb2
from Geometry import foundation_pb2 as _foundation_pb2
from Geometry import retainingwall_pb2 as _retainingwall_pb2
from Geometry import pile_pb2 as _pile_pb2
from Design import design_pb2 as _design_pb2
import structure_pb2 as _structure_pb2
from Utils import utils_pb2 as _utils_pb2_1_1
import element_pb2 as _element_pb2_1
import support_pb2 as _support_pb2
from Geometry import geometry_pb2 as _geometry_pb2_1
from Loading import loading_pb2 as _loading_pb2
from Design import design_pb2 as _design_pb2_1
import input_pb2 as _input_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1
import structure_pb2 as _structure_pb2_1
from Utils import eurocode_pb2 as _eurocode_pb2_1
import sections_pb2 as _sections_pb2
from Material import material_pb2 as _material_pb2
from FireProtection import steel_pb2 as _steel_pb2
from FireProtection import timber_pb2 as _timber_pb2
from Soilmodel import soil_model_pb2 as _soil_model_pb2
from Loading import loadgroup_pb2 as _loadgroup_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1
from Loading import loadcase_pb2 as _loadcase_pb2
from Loading import loadcombination_pb2 as _loadcombination_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

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
from Loading.loadcombination_pb2 import CombinationPart
from Loading.loadcombination_pb2 import BeamConfiguration
from Loading.loadcombination_pb2 import FoundationConfiguration
from Loading.loadcombination_pb2 import ActiveEarthPressureConfiguration
from Loading.loadcombination_pb2 import PassiveEarthPressureConfiguration
from Loading.loadcombination_pb2 import EarthPressureConfiguration
from Loading.loadcombination_pb2 import PileConfiguration
from Loading.loadcombination_pb2 import Compaction
from Loading.loadcombination_pb2 import Coefficient
from Loading.loadcombination_pb2 import Data
from Loading.loadcombination_pb2 import Type
from Loading.loadcombination_pb2 import CoaType
from Loading.loadcombination_pb2 import ServiceabilityType
from Loading.loadcombination_pb2 import LimitState
from Loading.loadcombination_pb2 import CoefficientType
from Loading.loadcombination_pb2 import GeoType
from Utils.eurocode_pb2 import DesignConfiguration
from Utils.eurocode_pb2 import Annex
from Utils.eurocode_pb2 import SnowZone
from Utils.eurocode_pb2 import Generation
from Utils.log_pb2 import LogValue
from Utils.log_pb2 import LogEntry
from Utils.log_pb2 import Log
from Utils.log_pb2 import LogType
from element_pb2 import Data
from element_pb2 import InspectionLevel
from structure_pb2 import Data
from structure_pb2 import ConsequenceClass
from structure_pb2 import ReliabilityClass
from input_pb2 import Data
from Loading.loadgroup_pb2 import Permanent
from Loading.loadgroup_pb2 import Stress
from Loading.loadgroup_pb2 import Temporary
from Loading.loadgroup_pb2 import Accidental
from Loading.loadgroup_pb2 import Fire
from Loading.loadgroup_pb2 import Seismic
from Loading.loadgroup_pb2 import Group
from Loading.loadgroup_pb2 import Groups
from Loading.loadgroup_pb2 import LoadcaseRelationship
AGGREGATE_CALCAREOUS: _concrete_pb2.Aggregates
AGGREGATE_DK_CALCAREOUS: _concrete_pb2.Aggregates
AGGREGATE_DK_SILICEOUS: _concrete_pb2.Aggregates
AGGREGATE_SILICEOUS: _concrete_pb2.Aggregates
AGGREGATE_UNSPECIFIED: _concrete_pb2.Aggregates
ANNEX_BELGIUM: _eurocode_pb2_1.Annex
ANNEX_COMMON: _eurocode_pb2_1.Annex
ANNEX_DENMARK: _eurocode_pb2_1.Annex
ANNEX_ESTONIA: _eurocode_pb2_1.Annex
ANNEX_FINLAND: _eurocode_pb2_1.Annex
ANNEX_GERMANY: _eurocode_pb2_1.Annex
ANNEX_GREAT_BRITAIN: _eurocode_pb2_1.Annex
ANNEX_HUNGARY: _eurocode_pb2_1.Annex
ANNEX_LATVIA: _eurocode_pb2_1.Annex
ANNEX_NETHERLAND: _eurocode_pb2_1.Annex
ANNEX_NORWAY: _eurocode_pb2_1.Annex
ANNEX_POLAND: _eurocode_pb2_1.Annex
ANNEX_ROMANIA: _eurocode_pb2_1.Annex
ANNEX_SPAIN: _eurocode_pb2_1.Annex
ANNEX_SWEDEN: _eurocode_pb2_1.Annex
ANNEX_TURKEY: _eurocode_pb2_1.Annex
ANNEX_UNSPECIFIED: _eurocode_pb2_1.Annex
BEAM_SIDE_BOTTOM: _concrete_pb2.BeamSide
BEAM_SIDE_END: _concrete_pb2.BeamSide
BEAM_SIDE_LEFT: _concrete_pb2.BeamSide
BEAM_SIDE_RIGHT: _concrete_pb2.BeamSide
BEAM_SIDE_START: _concrete_pb2.BeamSide
BEAM_SIDE_TOP: _concrete_pb2.BeamSide
BEAM_SIDE_UNSPECIFIED: _concrete_pb2.BeamSide
COA_TYPE_610: _loadcombination_pb2_1.CoaType
COA_TYPE_6105: _loadcombination_pb2_1.CoaType
COA_TYPE_610A: _loadcombination_pb2_1.CoaType
COA_TYPE_610A3: _loadcombination_pb2_1.CoaType
COA_TYPE_610B: _loadcombination_pb2_1.CoaType
COA_TYPE_610B4: _loadcombination_pb2_1.CoaType
COA_TYPE_611AB: _loadcombination_pb2_1.CoaType
COA_TYPE_614B: _loadcombination_pb2_1.CoaType
COA_TYPE_615B: _loadcombination_pb2_1.CoaType
COA_TYPE_616B: _loadcombination_pb2_1.CoaType
COA_TYPE_812: _loadcombination_pb2_1.CoaType
COA_TYPE_813A: _loadcombination_pb2_1.CoaType
COA_TYPE_813B: _loadcombination_pb2_1.CoaType
COA_TYPE_814A: _loadcombination_pb2_1.CoaType
COA_TYPE_814B: _loadcombination_pb2_1.CoaType
COA_TYPE_815: _loadcombination_pb2_1.CoaType
COA_TYPE_816: _loadcombination_pb2_1.CoaType
COA_TYPE_829: _loadcombination_pb2_1.CoaType
COA_TYPE_830: _loadcombination_pb2_1.CoaType
COA_TYPE_831: _loadcombination_pb2_1.CoaType
COA_TYPE_UNSPECIFIED: _loadcombination_pb2_1.CoaType
COEFFICIENT_TYPE_BASE: _loadcombination_pb2_1.CoefficientType
COEFFICIENT_TYPE_CHI_FACTOR: _loadcombination_pb2_1.CoefficientType
COEFFICIENT_TYPE_ETA: _loadcombination_pb2_1.CoefficientType
COEFFICIENT_TYPE_GAMMA: _loadcombination_pb2_1.CoefficientType
COEFFICIENT_TYPE_KFI: _loadcombination_pb2_1.CoefficientType
COEFFICIENT_TYPE_PSI: _loadcombination_pb2_1.CoefficientType
COEFFICIENT_TYPE_STOREY: _loadcombination_pb2_1.CoefficientType
COEFFICIENT_TYPE_UNSPECIFIED: _loadcombination_pb2_1.CoefficientType
COLUMN_PLACEMENT_CENTER: _concrete_pb2.ColumnPlacement
COLUMN_PLACEMENT_CORNER: _concrete_pb2.ColumnPlacement
COLUMN_PLACEMENT_EDGE: _concrete_pb2.ColumnPlacement
COLUMN_PLACEMENT_UNSPECIFIED: _concrete_pb2.ColumnPlacement
COMMANDS_PUNCHING_CHECK: _concrete_pb2.Commands
COMMANDS_SPALLING_CHECK: _concrete_pb2.Commands
COMMANDS_STIRRUP_DESIGN: _concrete_pb2.Commands
COMMANDS_UNSPECIFIED: _concrete_pb2.Commands
CONSEQUENCE_CLASS_1: _structure_pb2_1.ConsequenceClass
CONSEQUENCE_CLASS_2: _structure_pb2_1.ConsequenceClass
CONSEQUENCE_CLASS_3: _structure_pb2_1.ConsequenceClass
CONSEQUENCE_CLASS_UNSPECIFIED: _structure_pb2_1.ConsequenceClass
CONSTRUCTION_CLASS_1: _concrete_pb2.ConstructionClass
CONSTRUCTION_CLASS_2: _concrete_pb2.ConstructionClass
CONSTRUCTION_CLASS_UNSPECIFIED: _concrete_pb2.ConstructionClass
DESCRIPTOR: _descriptor.FileDescriptor
FABRICATION_IN_SITU: _concrete_pb2.Fabrication
FABRICATION_PREFAB: _concrete_pb2.Fabrication
FABRICATION_UNSPECIFIED: _concrete_pb2.Fabrication
FCTM_TYPE_FCTM: _concrete_pb2.FctmType
FCTM_TYPE_FCTM_FL: _concrete_pb2.FctmType
FCTM_TYPE_FCTM_XI: _concrete_pb2.FctmType
FCTM_TYPE_UNSPECIFIED: _concrete_pb2.FctmType
GENERATION_1: _eurocode_pb2_1.Generation
GENERATION_2: _eurocode_pb2_1.Generation
GENERATION_UNSPECIFIED: _eurocode_pb2_1.Generation
GEO_TYPE_1: _loadcombination_pb2_1.GeoType
GEO_TYPE_2: _loadcombination_pb2_1.GeoType
GEO_TYPE_UNSPECIFIED: _loadcombination_pb2_1.GeoType
INSPECTION_LEVEL_NORMAL: _element_pb2_1.InspectionLevel
INSPECTION_LEVEL_RELAXED: _element_pb2_1.InspectionLevel
INSPECTION_LEVEL_TIGHTENED: _element_pb2_1.InspectionLevel
INSPECTION_LEVEL_UNSPECIFIED: _element_pb2_1.InspectionLevel
LIMIT_STATE_EQU: _loadcombination_pb2_1.LimitState
LIMIT_STATE_GEO: _loadcombination_pb2_1.LimitState
LIMIT_STATE_STR: _loadcombination_pb2_1.LimitState
LIMIT_STATE_UNSPECIFIED: _loadcombination_pb2_1.LimitState
LIMIT_STATE_VC1: _loadcombination_pb2_1.LimitState
LIMIT_STATE_VC2A: _loadcombination_pb2_1.LimitState
LIMIT_STATE_VC2B: _loadcombination_pb2_1.LimitState
LIMIT_STATE_VC3: _loadcombination_pb2_1.LimitState
LIMIT_STATE_VC4: _loadcombination_pb2_1.LimitState
LOG_TYPE_ERROR: _log_pb2.LogType
LOG_TYPE_INFORMATION: _log_pb2.LogType
LOG_TYPE_UNSPECIFIED: _log_pb2.LogType
LOG_TYPE_WARNING: _log_pb2.LogType
RELIABILITY_CLASS_1: _structure_pb2_1.ReliabilityClass
RELIABILITY_CLASS_2: _structure_pb2_1.ReliabilityClass
RELIABILITY_CLASS_3: _structure_pb2_1.ReliabilityClass
RELIABILITY_CLASS_UNSPECIFIED: _structure_pb2_1.ReliabilityClass
SERVICEABILITY_TYPE_LONG: _loadcombination_pb2_1.ServiceabilityType
SERVICEABILITY_TYPE_SHORT: _loadcombination_pb2_1.ServiceabilityType
SERVICEABILITY_TYPE_UNSPECIFIED: _loadcombination_pb2_1.ServiceabilityType
SHEAR_DESIGN_TYPE_UNSPECIFIED: _concrete_pb2.ShearDesignType
SHEAR_DESIGN_TYPE_WITHOUT_SHEAR_REINFORCEMENT: _concrete_pb2.ShearDesignType
SHEAR_DESIGN_TYPE_WITH_SHEAR_REINFORCEMENT: _concrete_pb2.ShearDesignType
SNOW_ZONE_1: _eurocode_pb2_1.SnowZone
SNOW_ZONE_2: _eurocode_pb2_1.SnowZone
SNOW_ZONE_3: _eurocode_pb2_1.SnowZone
SNOW_ZONE_UNSPECIFIED: _eurocode_pb2_1.SnowZone
SURFACE_TYPE_INDENTED: _concrete_pb2.SurfaceType
SURFACE_TYPE_ROUGH: _concrete_pb2.SurfaceType
SURFACE_TYPE_SMOOTH: _concrete_pb2.SurfaceType
SURFACE_TYPE_UNSPECIFIED: _concrete_pb2.SurfaceType
SURFACE_TYPE_VERY_SMOOTH: _concrete_pb2.SurfaceType
TYPE_ACCIDENTAL: _loadcombination_pb2_1.Type
TYPE_CHARACTERISTIC: _loadcombination_pb2_1.Type
TYPE_FIRE: _loadcombination_pb2_1.Type
TYPE_FREQUENT: _loadcombination_pb2_1.Type
TYPE_QUASI_PERMANENT: _loadcombination_pb2_1.Type
TYPE_SEISMIC: _loadcombination_pb2_1.Type
TYPE_ULTIMATE: _loadcombination_pb2_1.Type
TYPE_UNSPECIFIED: _loadcombination_pb2_1.Type
WEB_SHEAR_CAPACITY_METHOD_ADVANCED: _concrete_pb2.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_SIMPLIFIED: _concrete_pb2.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_STANDARD: _concrete_pb2.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_UNSPECIFIED: _concrete_pb2.WebShearCapacityMethod
alternative: _loadgroup_pb2.LoadcaseRelationship
entire: _loadgroup_pb2.LoadcaseRelationship
simultaneous: _loadgroup_pb2.LoadcaseRelationship
unspecified: _loadgroup_pb2.LoadcaseRelationship

class Advanced(_message.Message):
    __slots__ = ["all_loadgroups", "loadgroups"]
    ALL_LOADGROUPS_FIELD_NUMBER: _ClassVar[int]
    LOADGROUPS_FIELD_NUMBER: _ClassVar[int]
    all_loadgroups: bool
    loadgroups: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, all_loadgroups: bool = ..., loadgroups: _Optional[_Iterable[str]] = ...) -> None: ...

class EN1990Gamma0ArgsIn(_message.Message):
    __slots__ = ["combination_of_actions", "consequences_class", "generation", "national_annex"]
    COMBINATION_OF_ACTIONS_FIELD_NUMBER: _ClassVar[int]
    CONSEQUENCES_CLASS_FIELD_NUMBER: _ClassVar[int]
    GENERATION_FIELD_NUMBER: _ClassVar[int]
    NATIONAL_ANNEX_FIELD_NUMBER: _ClassVar[int]
    combination_of_actions: _loadcombination_pb2_1.CoaType
    consequences_class: _structure_pb2_1.ConsequenceClass
    generation: _eurocode_pb2_1.Generation
    national_annex: _eurocode_pb2_1.Annex
    def __init__(self, national_annex: _Optional[_Union[_eurocode_pb2_1.Annex, str]] = ..., consequences_class: _Optional[_Union[_structure_pb2_1.ConsequenceClass, str]] = ..., combination_of_actions: _Optional[_Union[_loadcombination_pb2_1.CoaType, str]] = ..., generation: _Optional[_Union[_eurocode_pb2_1.Generation, str]] = ...) -> None: ...

class EN1990Gamma0ArgsOut(_message.Message):
    __slots__ = ["gamma0", "log"]
    GAMMA0_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    gamma0: float
    log: _log_pb2.Log
    def __init__(self, gamma0: _Optional[float] = ..., log: _Optional[_Union[_log_pb2.Log, _Mapping]] = ...) -> None: ...

class EN1992GammaArgsIn(_message.Message):
    __slots__ = ["combination_of_actions", "consequences_class", "element", "generation", "light_concrete", "national_annex"]
    COMBINATION_OF_ACTIONS_FIELD_NUMBER: _ClassVar[int]
    CONSEQUENCES_CLASS_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_FIELD_NUMBER: _ClassVar[int]
    GENERATION_FIELD_NUMBER: _ClassVar[int]
    LIGHT_CONCRETE_FIELD_NUMBER: _ClassVar[int]
    NATIONAL_ANNEX_FIELD_NUMBER: _ClassVar[int]
    combination_of_actions: _loadcombination_pb2_1.CoaType
    consequences_class: _structure_pb2_1.ConsequenceClass
    element: _element_pb2_1.Data
    generation: _eurocode_pb2_1.Generation
    light_concrete: bool
    national_annex: _eurocode_pb2_1.Annex
    def __init__(self, national_annex: _Optional[_Union[_eurocode_pb2_1.Annex, str]] = ..., element: _Optional[_Union[_element_pb2_1.Data, _Mapping]] = ..., light_concrete: bool = ..., consequences_class: _Optional[_Union[_structure_pb2_1.ConsequenceClass, str]] = ..., combination_of_actions: _Optional[_Union[_loadcombination_pb2_1.CoaType, str]] = ..., generation: _Optional[_Union[_eurocode_pb2_1.Generation, str]] = ...) -> None: ...

class EN1992GammaArgsOut(_message.Message):
    __slots__ = ["coeff", "log"]
    COEFF_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    coeff: _concrete_pb2.PartialCoefficient
    log: _log_pb2.Log
    def __init__(self, coeff: _Optional[_Union[_concrete_pb2.PartialCoefficient, _Mapping]] = ..., log: _Optional[_Union[_log_pb2.Log, _Mapping]] = ...) -> None: ...

class Geotechnical(_message.Message):
    __slots__ = ["designApproach"]
    DESIGNAPPROACH_FIELD_NUMBER: _ClassVar[int]
    designApproach: _soil_pb2.DesignApproach
    def __init__(self, designApproach: _Optional[_Union[_soil_pb2.DesignApproach, str]] = ...) -> None: ...

class LoadCombGenArgsIn(_message.Message):
    __slots__ = ["project_data", "settings"]
    PROJECT_DATA_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    project_data: _input_pb2.Data
    settings: LoadCombGenSettings
    def __init__(self, project_data: _Optional[_Union[_input_pb2.Data, _Mapping]] = ..., settings: _Optional[_Union[LoadCombGenSettings, _Mapping]] = ...) -> None: ...

class LoadCombGenArgsOut(_message.Message):
    __slots__ = ["loadcombinations", "log"]
    LOADCOMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    loadcombinations: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2_1.Data]
    log: _log_pb2.Log
    def __init__(self, loadcombinations: _Optional[_Iterable[_Union[_loadcombination_pb2_1.Data, _Mapping]]] = ..., log: _Optional[_Union[_log_pb2.Log, _Mapping]] = ...) -> None: ...

class LoadCombGenSettings(_message.Message):
    __slots__ = ["advanced", "all_loadcases", "geotechnical", "lc_types", "loadcases", "remove_duplex", "simple", "structureguid"]
    ADVANCED_FIELD_NUMBER: _ClassVar[int]
    ALL_LOADCASES_FIELD_NUMBER: _ClassVar[int]
    GEOTECHNICAL_FIELD_NUMBER: _ClassVar[int]
    LC_TYPES_FIELD_NUMBER: _ClassVar[int]
    LOADCASES_FIELD_NUMBER: _ClassVar[int]
    REMOVE_DUPLEX_FIELD_NUMBER: _ClassVar[int]
    SIMPLE_FIELD_NUMBER: _ClassVar[int]
    STRUCTUREGUID_FIELD_NUMBER: _ClassVar[int]
    advanced: Advanced
    all_loadcases: bool
    geotechnical: Geotechnical
    lc_types: _containers.RepeatedScalarFieldContainer[_loadcombination_pb2_1.Type]
    loadcases: _containers.RepeatedScalarFieldContainer[str]
    remove_duplex: bool
    simple: Simple
    structureguid: str
    def __init__(self, lc_types: _Optional[_Iterable[_Union[_loadcombination_pb2_1.Type, str]]] = ..., structureguid: _Optional[str] = ..., all_loadcases: bool = ..., loadcases: _Optional[_Iterable[str]] = ..., simple: _Optional[_Union[Simple, _Mapping]] = ..., advanced: _Optional[_Union[Advanced, _Mapping]] = ..., remove_duplex: bool = ..., geotechnical: _Optional[_Union[Geotechnical, _Mapping]] = ...) -> None: ...

class Simple(_message.Message):
    __slots__ = ["include_permanent_load_favorable", "timber"]
    INCLUDE_PERMANENT_LOAD_FAVORABLE_FIELD_NUMBER: _ClassVar[int]
    TIMBER_FIELD_NUMBER: _ClassVar[int]
    include_permanent_load_favorable: bool
    timber: bool
    def __init__(self, timber: bool = ..., include_permanent_load_favorable: bool = ...) -> None: ...

class UpdateFactorsArgsIn(_message.Message):
    __slots__ = ["input"]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    input: _input_pb2.Data
    def __init__(self, input: _Optional[_Union[_input_pb2.Data, _Mapping]] = ...) -> None: ...

class UpdateFactorsArgsOut(_message.Message):
    __slots__ = ["log", "updated_input"]
    LOG_FIELD_NUMBER: _ClassVar[int]
    UPDATED_INPUT_FIELD_NUMBER: _ClassVar[int]
    log: _log_pb2.Log
    updated_input: _input_pb2.Data
    def __init__(self, updated_input: _Optional[_Union[_input_pb2.Data, _Mapping]] = ..., log: _Optional[_Union[_log_pb2.Log, _Mapping]] = ...) -> None: ...
