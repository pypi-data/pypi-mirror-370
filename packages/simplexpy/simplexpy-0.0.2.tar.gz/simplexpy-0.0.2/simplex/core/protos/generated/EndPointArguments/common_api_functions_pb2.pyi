import project_pb2 as _project_pb2
import input_pb2 as _input_pb2
import output_pb2 as _output_pb2
from Utils import log_pb2 as _log_pb2
from Utils import log_pb2 as _log_pb2_1
from Result import result_pb2 as _result_pb2
from Utils import utils_pb2 as _utils_pb2
from Result import concrete_pb2 as _concrete_pb2
from Result import foundation_pb2 as _foundation_pb2
from Result import pile_pb2 as _pile_pb2
from Result import retainingwall_pb2 as _retainingwall_pb2
from Result import steel_pb2 as _steel_pb2
from Result import timber_pb2 as _timber_pb2
from Result import control_pb2 as _control_pb2
import sections_pb2 as _sections_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Geometry import geometry_pb2 as _geometry_pb2
from FireProtection import steel_pb2 as _steel_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1
from FireProtection import timber_pb2 as _timber_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1_1
from Design import concrete_pb2 as _concrete_pb2_1
from Material import reinforcement_pb2 as _reinforcement_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1
from Geometry import reinf_pb2 as _reinf_pb2
from Material import concrete_pb2 as _concrete_pb2_1_1
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.log_pb2 import LogValue
from Utils.log_pb2 import LogEntry
from Utils.log_pb2 import Log
from Utils.log_pb2 import LogType
from Result.result_pb2 import ForceData
from Result.result_pb2 import DisplacementData
from Result.result_pb2 import StressData
from Result.result_pb2 import TemperatureData
from Result.result_pb2 import Data
from Result.result_pb2 import PositionResult
from Result.result_pb2 import ElementResult
from Result.result_pb2 import Element
from Result.result_pb2 import Node
from Result.result_pb2 import Force
from Result.result_pb2 import Displacement
from Result.result_pb2 import Stress
from sections_pb2 import CustomParams
from sections_pb2 import RParams
from sections_pb2 import VRParams
from sections_pb2 import TParams
from sections_pb2 import VTParams
from sections_pb2 import FParams
from sections_pb2 import KBParams
from sections_pb2 import KBEParams
from sections_pb2 import CParams
from sections_pb2 import IParams
from sections_pb2 import IVParams
from sections_pb2 import LParams
from sections_pb2 import COParams
from sections_pb2 import HDXParams
from sections_pb2 import UParams
from sections_pb2 import ZParams
from sections_pb2 import RHSParams
from sections_pb2 import ToppingParams
from sections_pb2 import HEParams
from sections_pb2 import HSQParams
from sections_pb2 import UXParams
from sections_pb2 import ZXParams
from sections_pb2 import SectionUnits
from sections_pb2 import Section
from sections_pb2 import SectionSide
from sections_pb2 import SectionType
from sections_pb2 import MaterialCategory
from FireProtection.steel_pb2 import CharacteristicData
from FireProtection.steel_pb2 import Data
from FireProtection.steel_pb2 import Encasement
from FireProtection.timber_pb2 import CharacteristicData
from FireProtection.timber_pb2 import Data
from FireProtection.timber_pb2 import MaterialType
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
from Material.reinforcement_pb2 import CharacteristicData
from Material.reinforcement_pb2 import DiameterItem
from Material.reinforcement_pb2 import Data
from Material.concrete_pb2 import CharacteristicData
from Material.concrete_pb2 import Data
from Material.concrete_pb2 import Type
from Material.concrete_pb2 import DensityClass
AGGREGATE_CALCAREOUS: _concrete_pb2_1.Aggregates
AGGREGATE_DK_CALCAREOUS: _concrete_pb2_1.Aggregates
AGGREGATE_DK_SILICEOUS: _concrete_pb2_1.Aggregates
AGGREGATE_SILICEOUS: _concrete_pb2_1.Aggregates
AGGREGATE_UNSPECIFIED: _concrete_pb2_1.Aggregates
BEAM_SIDE_BOTTOM: _concrete_pb2_1.BeamSide
BEAM_SIDE_END: _concrete_pb2_1.BeamSide
BEAM_SIDE_LEFT: _concrete_pb2_1.BeamSide
BEAM_SIDE_RIGHT: _concrete_pb2_1.BeamSide
BEAM_SIDE_START: _concrete_pb2_1.BeamSide
BEAM_SIDE_TOP: _concrete_pb2_1.BeamSide
BEAM_SIDE_UNSPECIFIED: _concrete_pb2_1.BeamSide
COLUMN_PLACEMENT_CENTER: _concrete_pb2_1.ColumnPlacement
COLUMN_PLACEMENT_CORNER: _concrete_pb2_1.ColumnPlacement
COLUMN_PLACEMENT_EDGE: _concrete_pb2_1.ColumnPlacement
COLUMN_PLACEMENT_UNSPECIFIED: _concrete_pb2_1.ColumnPlacement
COMMANDS_PUNCHING_CHECK: _concrete_pb2_1.Commands
COMMANDS_SPALLING_CHECK: _concrete_pb2_1.Commands
COMMANDS_STIRRUP_DESIGN: _concrete_pb2_1.Commands
COMMANDS_UNSPECIFIED: _concrete_pb2_1.Commands
CONSTRUCTION_CLASS_1: _concrete_pb2_1.ConstructionClass
CONSTRUCTION_CLASS_2: _concrete_pb2_1.ConstructionClass
CONSTRUCTION_CLASS_UNSPECIFIED: _concrete_pb2_1.ConstructionClass
DENSITY_CLASS_LIGHT10: _concrete_pb2_1_1.DensityClass
DENSITY_CLASS_LIGHT12: _concrete_pb2_1_1.DensityClass
DENSITY_CLASS_LIGHT14: _concrete_pb2_1_1.DensityClass
DENSITY_CLASS_LIGHT16: _concrete_pb2_1_1.DensityClass
DENSITY_CLASS_LIGHT18: _concrete_pb2_1_1.DensityClass
DENSITY_CLASS_LIGHT20: _concrete_pb2_1_1.DensityClass
DENSITY_CLASS_REGULAR: _concrete_pb2_1_1.DensityClass
DENSITY_CLASS_UNSPECIFIED: _concrete_pb2_1_1.DensityClass
DESCRIPTOR: _descriptor.FileDescriptor
DISPLACEMENT_RU: _result_pb2.Displacement
DISPLACEMENT_RV: _result_pb2.Displacement
DISPLACEMENT_RW: _result_pb2.Displacement
DISPLACEMENT_RX: _result_pb2.Displacement
DISPLACEMENT_RY: _result_pb2.Displacement
DISPLACEMENT_RZ: _result_pb2.Displacement
DISPLACEMENT_U: _result_pb2.Displacement
DISPLACEMENT_UNSPECIFIED: _result_pb2.Displacement
DISPLACEMENT_V: _result_pb2.Displacement
DISPLACEMENT_W: _result_pb2.Displacement
DISPLACEMENT_X: _result_pb2.Displacement
DISPLACEMENT_Y: _result_pb2.Displacement
DISPLACEMENT_Z: _result_pb2.Displacement
ENCASEMENT_CONTOUR: _steel_pb2_1.Encasement
ENCASEMENT_HOLLOW: _steel_pb2_1.Encasement
ENCASEMENT_UNSPECIFIED: _steel_pb2_1.Encasement
FABRICATION_IN_SITU: _concrete_pb2_1.Fabrication
FABRICATION_PREFAB: _concrete_pb2_1.Fabrication
FABRICATION_UNSPECIFIED: _concrete_pb2_1.Fabrication
FCTM_TYPE_FCTM: _concrete_pb2_1.FctmType
FCTM_TYPE_FCTM_FL: _concrete_pb2_1.FctmType
FCTM_TYPE_FCTM_XI: _concrete_pb2_1.FctmType
FCTM_TYPE_UNSPECIFIED: _concrete_pb2_1.FctmType
FORCE_M1: _result_pb2.Force
FORCE_M2: _result_pb2.Force
FORCE_MX: _result_pb2.Force
FORCE_MY: _result_pb2.Force
FORCE_MZ: _result_pb2.Force
FORCE_N: _result_pb2.Force
FORCE_RX: _result_pb2.Force
FORCE_RY: _result_pb2.Force
FORCE_RZ: _result_pb2.Force
FORCE_T: _result_pb2.Force
FORCE_UNSPECIFIED: _result_pb2.Force
FORCE_V1: _result_pb2.Force
FORCE_V2: _result_pb2.Force
HEALTH_CHECK_STATUS_DEGRADED: HealthCheckStatus
HEALTH_CHECK_STATUS_HEALTHY: HealthCheckStatus
HEALTH_CHECK_STATUS_UNHEALTHY: HealthCheckStatus
HEALTH_CHECK_STATUS_UNSPECIFIED: HealthCheckStatus
LOG_TYPE_ERROR: _log_pb2_1.LogType
LOG_TYPE_INFORMATION: _log_pb2_1.LogType
LOG_TYPE_UNSPECIFIED: _log_pb2_1.LogType
LOG_TYPE_WARNING: _log_pb2_1.LogType
MATERIAL_CATEGORY_CONCRETE: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_STEEL: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_TIMBER: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_UNSPECIFIED: _sections_pb2.MaterialCategory
MATERIAL_TYPE_GYPSUM_BOARD_AH1_INTERNAL: _timber_pb2_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_AH1_OTHER: _timber_pb2_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_AH2_INTERNAL: _timber_pb2_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_AH2_OTHER: _timber_pb2_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F1_INTERNAL: _timber_pb2_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F1_OTHER: _timber_pb2_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F2_INTERNAL: _timber_pb2_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F2_OTHER: _timber_pb2_1.MaterialType
MATERIAL_TYPE_NONE: _timber_pb2_1.MaterialType
MATERIAL_TYPE_ROCK_FIBER: _timber_pb2_1.MaterialType
MATERIAL_TYPE_UNSPECIFIED: _timber_pb2_1.MaterialType
MATERIAL_TYPE_USER_DEFINED: _timber_pb2_1.MaterialType
MATERIAL_TYPE_WOOD: _timber_pb2_1.MaterialType
SECTION_SIDE_LEFT: _sections_pb2.SectionSide
SECTION_SIDE_RIGHT: _sections_pb2.SectionSide
SECTION_SIDE_UNSPECIFIED: _sections_pb2.SectionSide
SECTION_TYPE_ASB: _sections_pb2.SectionType
SECTION_TYPE_C: _sections_pb2.SectionType
SECTION_TYPE_CHS: _sections_pb2.SectionType
SECTION_TYPE_CO: _sections_pb2.SectionType
SECTION_TYPE_CUSTOM: _sections_pb2.SectionType
SECTION_TYPE_DESSED_LUMBER: _sections_pb2.SectionType
SECTION_TYPE_EA: _sections_pb2.SectionType
SECTION_TYPE_F: _sections_pb2.SectionType
SECTION_TYPE_GLULAM: _sections_pb2.SectionType
SECTION_TYPE_HDX: _sections_pb2.SectionType
SECTION_TYPE_HEA: _sections_pb2.SectionType
SECTION_TYPE_HEB: _sections_pb2.SectionType
SECTION_TYPE_HEM: _sections_pb2.SectionType
SECTION_TYPE_HSQ: _sections_pb2.SectionType
SECTION_TYPE_I: _sections_pb2.SectionType
SECTION_TYPE_IPE: _sections_pb2.SectionType
SECTION_TYPE_IV: _sections_pb2.SectionType
SECTION_TYPE_KB: _sections_pb2.SectionType
SECTION_TYPE_KBE: _sections_pb2.SectionType
SECTION_TYPE_KCKR: _sections_pb2.SectionType
SECTION_TYPE_KERTO: _sections_pb2.SectionType
SECTION_TYPE_KKR: _sections_pb2.SectionType
SECTION_TYPE_L: _sections_pb2.SectionType
SECTION_TYPE_LE: _sections_pb2.SectionType
SECTION_TYPE_LU: _sections_pb2.SectionType
SECTION_TYPE_PFC: _sections_pb2.SectionType
SECTION_TYPE_PLATE: _sections_pb2.SectionType
SECTION_TYPE_R: _sections_pb2.SectionType
SECTION_TYPE_RHS: _sections_pb2.SectionType
SECTION_TYPE_SAWN_LUMBER: _sections_pb2.SectionType
SECTION_TYPE_T: _sections_pb2.SectionType
SECTION_TYPE_TOPPING: _sections_pb2.SectionType
SECTION_TYPE_TPS: _sections_pb2.SectionType
SECTION_TYPE_U: _sections_pb2.SectionType
SECTION_TYPE_UA: _sections_pb2.SectionType
SECTION_TYPE_UAP: _sections_pb2.SectionType
SECTION_TYPE_UB: _sections_pb2.SectionType
SECTION_TYPE_UBP: _sections_pb2.SectionType
SECTION_TYPE_UC: _sections_pb2.SectionType
SECTION_TYPE_UKB: _sections_pb2.SectionType
SECTION_TYPE_UKC: _sections_pb2.SectionType
SECTION_TYPE_UNSPECIFIED: _sections_pb2.SectionType
SECTION_TYPE_UPE_DIN: _sections_pb2.SectionType
SECTION_TYPE_UPE_NEN: _sections_pb2.SectionType
SECTION_TYPE_UPE_SWE: _sections_pb2.SectionType
SECTION_TYPE_UX: _sections_pb2.SectionType
SECTION_TYPE_VCKR: _sections_pb2.SectionType
SECTION_TYPE_VKR: _sections_pb2.SectionType
SECTION_TYPE_VR: _sections_pb2.SectionType
SECTION_TYPE_VT: _sections_pb2.SectionType
SECTION_TYPE_Z: _sections_pb2.SectionType
SECTION_TYPE_ZX: _sections_pb2.SectionType
SHEAR_DESIGN_TYPE_UNSPECIFIED: _concrete_pb2_1.ShearDesignType
SHEAR_DESIGN_TYPE_WITHOUT_SHEAR_REINFORCEMENT: _concrete_pb2_1.ShearDesignType
SHEAR_DESIGN_TYPE_WITH_SHEAR_REINFORCEMENT: _concrete_pb2_1.ShearDesignType
STRESS_MISES: _result_pb2.Stress
STRESS_S11: _result_pb2.Stress
STRESS_S12: _result_pb2.Stress
STRESS_S22: _result_pb2.Stress
STRESS_SP1: _result_pb2.Stress
STRESS_SP2: _result_pb2.Stress
STRESS_UNSPECIFIED: _result_pb2.Stress
SURFACE_TYPE_INDENTED: _concrete_pb2_1.SurfaceType
SURFACE_TYPE_ROUGH: _concrete_pb2_1.SurfaceType
SURFACE_TYPE_SMOOTH: _concrete_pb2_1.SurfaceType
SURFACE_TYPE_UNSPECIFIED: _concrete_pb2_1.SurfaceType
SURFACE_TYPE_VERY_SMOOTH: _concrete_pb2_1.SurfaceType
TYPE_LIGHT: _concrete_pb2_1_1.Type
TYPE_REGULAR: _concrete_pb2_1_1.Type
TYPE_UNSPECIFIED: _concrete_pb2_1_1.Type
WEB_SHEAR_CAPACITY_METHOD_ADVANCED: _concrete_pb2_1.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_SIMPLIFIED: _concrete_pb2_1.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_STANDARD: _concrete_pb2_1.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_UNSPECIFIED: _concrete_pb2_1.WebShearCapacityMethod

class AdminReport(_message.Message):
    __slots__ = ["calculation_time", "call_count", "error_entries", "name"]
    class CalculationTime(_message.Message):
        __slots__ = ["average", "max", "median", "min"]
        AVERAGE_FIELD_NUMBER: _ClassVar[int]
        MAX_FIELD_NUMBER: _ClassVar[int]
        MEDIAN_FIELD_NUMBER: _ClassVar[int]
        MIN_FIELD_NUMBER: _ClassVar[int]
        average: str
        max: str
        median: str
        min: str
        def __init__(self, average: _Optional[str] = ..., median: _Optional[str] = ..., max: _Optional[str] = ..., min: _Optional[str] = ...) -> None: ...
    class CallCountEntry(_message.Message):
        __slots__ = ["count", "material", "type"]
        COUNT_FIELD_NUMBER: _ClassVar[int]
        MATERIAL_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        count: int
        material: _material_pb2.Mtrl
        type: str
        def __init__(self, count: _Optional[int] = ..., type: _Optional[str] = ..., material: _Optional[_Union[_material_pb2.Mtrl, str]] = ...) -> None: ...
    class ErrorEntry(_message.Message):
        __slots__ = ["count", "message"]
        COUNT_FIELD_NUMBER: _ClassVar[int]
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        count: int
        message: str
        def __init__(self, message: _Optional[str] = ..., count: _Optional[int] = ...) -> None: ...
    CALCULATION_TIME_FIELD_NUMBER: _ClassVar[int]
    CALL_COUNT_FIELD_NUMBER: _ClassVar[int]
    ERROR_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    calculation_time: AdminReport.CalculationTime
    call_count: _containers.RepeatedCompositeFieldContainer[AdminReport.CallCountEntry]
    error_entries: _containers.RepeatedCompositeFieldContainer[AdminReport.ErrorEntry]
    name: str
    def __init__(self, name: _Optional[str] = ..., calculation_time: _Optional[_Union[AdminReport.CalculationTime, _Mapping]] = ..., error_entries: _Optional[_Iterable[_Union[AdminReport.ErrorEntry, _Mapping]]] = ..., call_count: _Optional[_Iterable[_Union[AdminReport.CallCountEntry, _Mapping]]] = ...) -> None: ...

class AutoDesign(_message.Message):
    __slots__ = ["active", "mtrl_db", "sec_db", "settings"]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    MTRL_DB_FIELD_NUMBER: _ClassVar[int]
    SEC_DB_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    active: bool
    mtrl_db: _containers.RepeatedCompositeFieldContainer[_material_pb2.Data]
    sec_db: _containers.RepeatedCompositeFieldContainer[_sections_pb2.Section]
    settings: _containers.RepeatedCompositeFieldContainer[AutoDesignSettings]
    def __init__(self, active: bool = ..., sec_db: _Optional[_Iterable[_Union[_sections_pb2.Section, _Mapping]]] = ..., mtrl_db: _Optional[_Iterable[_Union[_material_pb2.Data, _Mapping]]] = ..., settings: _Optional[_Iterable[_Union[AutoDesignSettings, _Mapping]]] = ...) -> None: ...

class AutoDesignBeam(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class AutoDesignColumn(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class AutoDesignConcrete(_message.Message):
    __slots__ = ["btm_dia", "btm_dia_mtrl_guid", "code_control", "conc_lst", "cover_deviation", "distances", "free_space_between_stirrups", "link_dia", "link_dia_mtrl_guid", "long_dia", "long_dia_mtrl_guid", "max_aggregate_size", "nbr_of_legs_for_end_stirrups", "regular_spacing", "spacing_limits", "stirrups_slope", "top_dia", "top_dia_mtrl_guid", "vib_space"]
    BTM_DIA_FIELD_NUMBER: _ClassVar[int]
    BTM_DIA_MTRL_GUID_FIELD_NUMBER: _ClassVar[int]
    CODE_CONTROL_FIELD_NUMBER: _ClassVar[int]
    CONC_LST_FIELD_NUMBER: _ClassVar[int]
    COVER_DEVIATION_FIELD_NUMBER: _ClassVar[int]
    DISTANCES_FIELD_NUMBER: _ClassVar[int]
    FREE_SPACE_BETWEEN_STIRRUPS_FIELD_NUMBER: _ClassVar[int]
    LINK_DIA_FIELD_NUMBER: _ClassVar[int]
    LINK_DIA_MTRL_GUID_FIELD_NUMBER: _ClassVar[int]
    LONG_DIA_FIELD_NUMBER: _ClassVar[int]
    LONG_DIA_MTRL_GUID_FIELD_NUMBER: _ClassVar[int]
    MAX_AGGREGATE_SIZE_FIELD_NUMBER: _ClassVar[int]
    NBR_OF_LEGS_FOR_END_STIRRUPS_FIELD_NUMBER: _ClassVar[int]
    REGULAR_SPACING_FIELD_NUMBER: _ClassVar[int]
    SPACING_LIMITS_FIELD_NUMBER: _ClassVar[int]
    STIRRUPS_SLOPE_FIELD_NUMBER: _ClassVar[int]
    TOP_DIA_FIELD_NUMBER: _ClassVar[int]
    TOP_DIA_MTRL_GUID_FIELD_NUMBER: _ClassVar[int]
    VIB_SPACE_FIELD_NUMBER: _ClassVar[int]
    btm_dia: _containers.RepeatedScalarFieldContainer[float]
    btm_dia_mtrl_guid: str
    code_control: bool
    conc_lst: _containers.RepeatedScalarFieldContainer[str]
    cover_deviation: float
    distances: _containers.RepeatedCompositeFieldContainer[_concrete_pb2_1.CoverAndSpace]
    free_space_between_stirrups: float
    link_dia: _containers.RepeatedScalarFieldContainer[float]
    link_dia_mtrl_guid: str
    long_dia: _containers.RepeatedScalarFieldContainer[float]
    long_dia_mtrl_guid: str
    max_aggregate_size: float
    nbr_of_legs_for_end_stirrups: int
    regular_spacing: bool
    spacing_limits: AutoDesignValue
    stirrups_slope: float
    top_dia: _containers.RepeatedScalarFieldContainer[float]
    top_dia_mtrl_guid: str
    vib_space: float
    def __init__(self, btm_dia: _Optional[_Iterable[float]] = ..., top_dia: _Optional[_Iterable[float]] = ..., link_dia: _Optional[_Iterable[float]] = ..., long_dia: _Optional[_Iterable[float]] = ..., btm_dia_mtrl_guid: _Optional[str] = ..., top_dia_mtrl_guid: _Optional[str] = ..., link_dia_mtrl_guid: _Optional[str] = ..., long_dia_mtrl_guid: _Optional[str] = ..., conc_lst: _Optional[_Iterable[str]] = ..., distances: _Optional[_Iterable[_Union[_concrete_pb2_1.CoverAndSpace, _Mapping]]] = ..., cover_deviation: _Optional[float] = ..., vib_space: _Optional[float] = ..., max_aggregate_size: _Optional[float] = ..., regular_spacing: bool = ..., free_space_between_stirrups: _Optional[float] = ..., nbr_of_legs_for_end_stirrups: _Optional[int] = ..., stirrups_slope: _Optional[float] = ..., spacing_limits: _Optional[_Union[AutoDesignValue, _Mapping]] = ..., code_control: bool = ...) -> None: ...

class AutoDesignFoundation(_message.Message):
    __slots__ = ["height", "length", "length_width_ratio", "width"]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    LENGTH_WIDTH_RATIO_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    height: AutoDesignValue
    length: AutoDesignValue
    length_width_ratio: float
    width: AutoDesignValue
    def __init__(self, length_width_ratio: _Optional[float] = ..., width: _Optional[_Union[AutoDesignValue, _Mapping]] = ..., length: _Optional[_Union[AutoDesignValue, _Mapping]] = ..., height: _Optional[_Union[AutoDesignValue, _Mapping]] = ...) -> None: ...

class AutoDesignSettings(_message.Message):
    __slots__ = ["beam", "column", "concrete", "element_guid", "foundation", "limit_utilization", "section_guids", "steel", "timber"]
    BEAM_FIELD_NUMBER: _ClassVar[int]
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_GUID_FIELD_NUMBER: _ClassVar[int]
    FOUNDATION_FIELD_NUMBER: _ClassVar[int]
    LIMIT_UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    SECTION_GUIDS_FIELD_NUMBER: _ClassVar[int]
    STEEL_FIELD_NUMBER: _ClassVar[int]
    TIMBER_FIELD_NUMBER: _ClassVar[int]
    beam: AutoDesignBeam
    column: AutoDesignColumn
    concrete: AutoDesignConcrete
    element_guid: str
    foundation: AutoDesignFoundation
    limit_utilization: float
    section_guids: _containers.RepeatedScalarFieldContainer[str]
    steel: AutoDesignSteel
    timber: AutoDesignTimber
    def __init__(self, element_guid: _Optional[str] = ..., section_guids: _Optional[_Iterable[str]] = ..., limit_utilization: _Optional[float] = ..., steel: _Optional[_Union[AutoDesignSteel, _Mapping]] = ..., timber: _Optional[_Union[AutoDesignTimber, _Mapping]] = ..., concrete: _Optional[_Union[AutoDesignConcrete, _Mapping]] = ..., beam: _Optional[_Union[AutoDesignBeam, _Mapping]] = ..., column: _Optional[_Union[AutoDesignColumn, _Mapping]] = ..., foundation: _Optional[_Union[AutoDesignFoundation, _Mapping]] = ...) -> None: ...

class AutoDesignSteel(_message.Message):
    __slots__ = ["fire_settings"]
    FIRE_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    fire_settings: AutoDesignSteelFire
    def __init__(self, fire_settings: _Optional[_Union[AutoDesignSteelFire, _Mapping]] = ...) -> None: ...

class AutoDesignSteelFire(_message.Message):
    __slots__ = ["protecting_material", "temperature_step"]
    PROTECTING_MATERIAL_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_STEP_FIELD_NUMBER: _ClassVar[int]
    protecting_material: ProtectingMaterial
    temperature_step: float
    def __init__(self, protecting_material: _Optional[_Union[ProtectingMaterial, _Mapping]] = ..., temperature_step: _Optional[float] = ...) -> None: ...

class AutoDesignTimber(_message.Message):
    __slots__ = ["fire_settings"]
    FIRE_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    fire_settings: AutoDesignTimberFire
    def __init__(self, fire_settings: _Optional[_Union[AutoDesignTimberFire, _Mapping]] = ...) -> None: ...

class AutoDesignTimberFire(_message.Message):
    __slots__ = ["protecting_material"]
    PROTECTING_MATERIAL_FIELD_NUMBER: _ClassVar[int]
    protecting_material: ProtectingMaterial
    def __init__(self, protecting_material: _Optional[_Union[ProtectingMaterial, _Mapping]] = ...) -> None: ...

class AutoDesignValue(_message.Message):
    __slots__ = ["max", "min", "step"]
    MAX_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    max: float
    min: float
    step: float
    def __init__(self, min: _Optional[float] = ..., max: _Optional[float] = ..., step: _Optional[float] = ...) -> None: ...

class CodeCheckInput(_message.Message):
    __slots__ = ["auto_design", "lcomb_guids", "mathml", "mathmlmax", "project"]
    AUTO_DESIGN_FIELD_NUMBER: _ClassVar[int]
    LCOMB_GUIDS_FIELD_NUMBER: _ClassVar[int]
    MATHMLMAX_FIELD_NUMBER: _ClassVar[int]
    MATHML_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    auto_design: AutoDesign
    lcomb_guids: _containers.RepeatedScalarFieldContainer[str]
    mathml: bool
    mathmlmax: bool
    project: _project_pb2.Data
    def __init__(self, project: _Optional[_Union[_project_pb2.Data, _Mapping]] = ..., lcomb_guids: _Optional[_Iterable[str]] = ..., mathml: bool = ..., mathmlmax: bool = ..., auto_design: _Optional[_Union[AutoDesign, _Mapping]] = ...) -> None: ...

class CodeCheckOutput(_message.Message):
    __slots__ = ["log", "project"]
    LOG_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    log: _log_pb2_1.Log
    project: _project_pb2.Data
    def __init__(self, project: _Optional[_Union[_project_pb2.Data, _Mapping]] = ..., log: _Optional[_Union[_log_pb2_1.Log, _Mapping]] = ...) -> None: ...

class HealthCheckData(_message.Message):
    __slots__ = ["key", "value"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class HealthCheckDuration(_message.Message):
    __slots__ = ["days", "hours", "milliseconds", "minutes", "seconds"]
    DAYS_FIELD_NUMBER: _ClassVar[int]
    HOURS_FIELD_NUMBER: _ClassVar[int]
    MILLISECONDS_FIELD_NUMBER: _ClassVar[int]
    MINUTES_FIELD_NUMBER: _ClassVar[int]
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    days: int
    hours: int
    milliseconds: int
    minutes: int
    seconds: int
    def __init__(self, days: _Optional[int] = ..., hours: _Optional[int] = ..., minutes: _Optional[int] = ..., seconds: _Optional[int] = ..., milliseconds: _Optional[int] = ...) -> None: ...

class HealthCheckEntry(_message.Message):
    __slots__ = ["data", "description", "duration", "name", "status"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[HealthCheckData]
    description: str
    duration: HealthCheckDuration
    name: str
    status: HealthCheckStatus
    def __init__(self, name: _Optional[str] = ..., status: _Optional[_Union[HealthCheckStatus, str]] = ..., description: _Optional[str] = ..., duration: _Optional[_Union[HealthCheckDuration, _Mapping]] = ..., data: _Optional[_Iterable[_Union[HealthCheckData, _Mapping]]] = ...) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ["entries", "status", "total_duration"]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_DURATION_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[HealthCheckEntry]
    status: HealthCheckStatus
    total_duration: HealthCheckDuration
    def __init__(self, status: _Optional[_Union[HealthCheckStatus, str]] = ..., total_duration: _Optional[_Union[HealthCheckDuration, _Mapping]] = ..., entries: _Optional[_Iterable[_Union[HealthCheckEntry, _Mapping]]] = ...) -> None: ...

class ProtectingMaterial(_message.Message):
    __slots__ = ["thickness_max", "thickness_min", "thickness_step"]
    THICKNESS_MAX_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_MIN_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_STEP_FIELD_NUMBER: _ClassVar[int]
    thickness_max: float
    thickness_min: float
    thickness_step: float
    def __init__(self, thickness_step: _Optional[float] = ..., thickness_min: _Optional[float] = ..., thickness_max: _Optional[float] = ...) -> None: ...

class HealthCheckStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
