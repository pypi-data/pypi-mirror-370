from Utils import utils_pb2 as _utils_pb2
from Result import concrete_pb2 as _concrete_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Geometry import link_pb2 as _link_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Result import control_pb2 as _control_pb2
from Result import foundation_pb2 as _foundation_pb2
from Utils import utils_pb2 as _utils_pb2_1_1
import element_pb2 as _element_pb2
import sections_pb2 as _sections_pb2
from Loading import load_pb2 as _load_pb2
from Loading import loadcase_pb2 as _loadcase_pb2
from Geometry import geometry_pb2 as _geometry_pb2_1
from Result import concrete_pb2 as _concrete_pb2_1
from Result import control_pb2 as _control_pb2_1
from Result import pile_pb2 as _pile_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1
import element_pb2 as _element_pb2_1
import sections_pb2 as _sections_pb2_1
from Result import foundation_pb2 as _foundation_pb2_1
from Result import retainingwall_pb2 as _retainingwall_pb2
from Result import foundation_pb2 as _foundation_pb2_1_1
from Result import steel_pb2 as _steel_pb2
from Geometry import beam_pb2 as _beam_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1
from Design import steel_pb2 as _steel_pb2_1
from Design import general_pb2 as _general_pb2
import sections_pb2 as _sections_pb2_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1_1
from Material import steel_pb2 as _steel_pb2_1_1
from Result import control_pb2 as _control_pb2_1_1
from Result import timber_pb2 as _timber_pb2
import element_pb2 as _element_pb2_1_1
from Design import steel_pb2 as _steel_pb2_1_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1_1_1
from Result import steel_pb2 as _steel_pb2_1_1_1_1
from Result import control_pb2 as _control_pb2_1_1_1
from Result import control_pb2 as _control_pb2_1_1_1_1
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
from Result.concrete_pb2 import BendingDataSLS
from Result.concrete_pb2 import BendingDataULS
from Result.concrete_pb2 import ShearData
from Result.concrete_pb2 import StirrupData
from Result.concrete_pb2 import TorsionData
from Result.concrete_pb2 import ToppingData
from Result.concrete_pb2 import FlangeReinf
from Result.concrete_pb2 import SpallingReinf
from Result.concrete_pb2 import BurstingReinf
from Result.concrete_pb2 import SplittingReinf
from Result.concrete_pb2 import EndReinf
from Result.concrete_pb2 import Data
from Result.concrete_pb2 import Element
from Result.concrete_pb2 import DesignSummary
from Result.foundation_pb2 import ConcreteInput
from Result.foundation_pb2 import EffectiveGeometry
from Result.foundation_pb2 import Stress
from Result.foundation_pb2 import FoundationForce
from Result.foundation_pb2 import SoilWaterLoads
from Result.foundation_pb2 import DetailedFoundationAnalysis
from Result.foundation_pb2 import BearingRes
from Result.foundation_pb2 import BearingResFormula
from Result.foundation_pb2 import DesignStrength
from Result.foundation_pb2 import SlidingRes
from Result.foundation_pb2 import SlidingResFormula
from Result.foundation_pb2 import DetailedFoundationDesign
from Result.foundation_pb2 import RCPunchingCheckConcreteCompression
from Result.foundation_pb2 import RCPunchingCheckConcreteShear
from Result.foundation_pb2 import RCUnreinforced
from Result.foundation_pb2 import Data
from Result.foundation_pb2 import Element
from Result.foundation_pb2 import DesignSummary
from Result.pile_pb2 import ControlData
from Result.pile_pb2 import ControlCapacities
from Result.pile_pb2 import ControlUtilization
from Result.pile_pb2 import ControlDistribution
from Result.pile_pb2 import DesignSummary
from Result.pile_pb2 import FoundationForce
from Result.pile_pb2 import DetailedPileAnalysis
from Result.pile_pb2 import DesignStrength
from Result.pile_pb2 import PileResDetailed
from Result.pile_pb2 import PileRes
from Result.pile_pb2 import DetailedPileDesign
from Result.pile_pb2 import Data
from Result.pile_pb2 import Element
from Result.pile_pb2 import ControlType
from Result.pile_pb2 import AnalysisType
from Result.pile_pb2 import DesignType
from Result.retainingwall_pb2 import DesignSummary
from Result.retainingwall_pb2 import ConcreteInput
from Result.retainingwall_pb2 import Data
from Result.retainingwall_pb2 import Element
from Result.steel_pb2 import TVPointW
from Result.steel_pb2 import BucklingShapes
from Result.steel_pb2 import SteelDesignNationalAnnexValues
from Result.steel_pb2 import Boolean2D
from Result.steel_pb2 import VirtualStiffeners
from Result.steel_pb2 import SectionClass
from Result.steel_pb2 import EffectiveClassFour
from Result.steel_pb2 import BucklingFactors
from Result.steel_pb2 import BucklingTorsionalFactors
from Result.steel_pb2 import LateralTorsionalIFactors
from Result.steel_pb2 import LateralTorsionalSimplyfied
from Result.steel_pb2 import Mcr
from Result.steel_pb2 import SectionGeometry
from Result.steel_pb2 import WebFactors
from Result.steel_pb2 import WebCapacities
from Result.steel_pb2 import Flexural
from Result.steel_pb2 import FlexuralTorsional
from Result.steel_pb2 import LateralTorsional
from Result.steel_pb2 import Web
from Result.steel_pb2 import ShearResistance
from Result.steel_pb2 import TorsionalResistance
from Result.steel_pb2 import ShearStress
from Result.steel_pb2 import NormalStress
from Result.steel_pb2 import PureNormalResistance
from Result.steel_pb2 import NormalCapacity
from Result.steel_pb2 import Force
from Result.steel_pb2 import Interaction
from Result.steel_pb2 import Interaction2nd
from Result.steel_pb2 import SectionResult
from Result.steel_pb2 import SectionParameters
from Result.steel_pb2 import CharacteristicValues
from Result.steel_pb2 import MaterialParameters
from Result.steel_pb2 import MaterialFireParameters
from Result.steel_pb2 import GasTemperature
from Result.steel_pb2 import Parametric
from Result.steel_pb2 import MemberTemperatureUnprotected
from Result.steel_pb2 import MemberTemperatureProtected
from Result.steel_pb2 import FireParameters
from Result.steel_pb2 import ExtraParameters
from Result.steel_pb2 import Data
from Result.steel_pb2 import Element
from Result.steel_pb2 import DesignSummary
from Result.steel_pb2 import BarSectionType
from Result.steel_pb2 import Curve
from Result.steel_pb2 import CurveLT
from Result.steel_pb2 import ShearResistanceEnum
from Result.steel_pb2 import StBarWebRelevant
from Result.steel_pb2 import ShearStressCheckRelevant
from Result.timber_pb2 import Tension
from Result.timber_pb2 import Compression
from Result.timber_pb2 import Shear
from Result.timber_pb2 import FlexuralBuckling
from Result.timber_pb2 import TorsionalBuckling
from Result.timber_pb2 import Apex
from Result.timber_pb2 import Taper
from Result.timber_pb2 import SectionResult
from Result.timber_pb2 import MaterialParameters
from Result.timber_pb2 import SectionParameters
from Result.timber_pb2 import TorsionalBucklingParameters
from Result.timber_pb2 import FlexBucklingParameters
from Result.timber_pb2 import TaperParameters
from Result.timber_pb2 import ApexParameters
from Result.timber_pb2 import ExtraParameters
from Result.timber_pb2 import DesignStrength
from Result.timber_pb2 import TorsionalBucklingStrength
from Result.timber_pb2 import Data
from Result.timber_pb2 import Element
from Result.timber_pb2 import DesignSummary
from Result.timber_pb2 import StatSys
from Result.control_pb2 import ControlTypeFoundation
from Result.control_pb2 import ControlData
from Result.control_pb2 import ControlTypeConcrete
from Result.control_pb2 import ControlTypeSteel
from Result.control_pb2 import ControlTypeTimber
from Result.control_pb2 import CtrlTypeFoundation
from Result.control_pb2 import AnalysisTypeFoundation
from Result.control_pb2 import DesignTypeFoundation
from Result.control_pb2 import EccentricityTypeFoundation
ANALYSIS_TYPE_NORMAL: _control_pb2_1_1_1_1.AnalysisTypeFoundation
ANALYSIS_TYPE_SOIL_PUNCHING: _control_pb2_1_1_1_1.AnalysisTypeFoundation
ANALYSIS_TYPE_UNSPECIFIED: _control_pb2_1_1_1_1.AnalysisTypeFoundation
BAR_SECTION_TYPE_UNIFORM: _steel_pb2_1_1_1_1.BarSectionType
BAR_SECTION_TYPE_UNSPECIFIED: _steel_pb2_1_1_1_1.BarSectionType
BAR_SECTION_TYPE_VARIABLE: _steel_pb2_1_1_1_1.BarSectionType
CONTROL_TYPE_COMPRESSION: _pile_pb2.ControlType
CONTROL_TYPE_CONCRETE_ANCHORAGE_BTM: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_ANCHORAGE_TOP: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_AXIAL_FORCE: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_BIAXIAL_MOMENT: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_COMPRESSION_COVER_CHECK: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_COMPRESSION_STRESS: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_DEFLECTION: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_HOLLOWCORE_SPALLING: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_INITIAL_PRESTRESS: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_MOMENT_M2: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_NEGATIVE_CRACK_WIDTH: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_NEGATIVE_MOMENT_M1: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_POSITIVE_CRACK_WIDTH: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_POSITIVE_MOMENT_M1: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_PUNCHING_COLUMN: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_PUNCHING_PERIMETER: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_FORCE: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_FORCE_TOPPING: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_STIRRUPS: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_STIRRUPS_TOPPING: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_STRESS_AFTER_RELEASE: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TOPPING_JOINT: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_COMPRESSION_LONGITUDINAL: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_COMPRESSION_TRANSVERSE: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_LONGITUDINAL: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_TENSION_TRANSVERSE: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_TRANSVERSE: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_UNSPECIFIED: _control_pb2_1_1_1_1.ControlTypeConcrete
CONTROL_TYPE_FOUNDATION_BEARING: _control_pb2_1_1_1_1.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_OVERALL: _control_pb2_1_1_1_1.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_OVERTURNING: _control_pb2_1_1_1_1.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_SETTLEMENT: _control_pb2_1_1_1_1.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_SLIDING: _control_pb2_1_1_1_1.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_UNREINFORCED: _control_pb2_1_1_1_1.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_UNSPECIFIED: _control_pb2_1_1_1_1.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_UPLIFT: _control_pb2_1_1_1_1.CtrlTypeFoundation
CONTROL_TYPE_OVERALL: _pile_pb2.ControlType
CONTROL_TYPE_STEEL_DEFLECTION: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_FB1: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_FB2: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_FTB: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_IA1: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_IA2: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_IA2ND: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_LTB_BOTTOM: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_LTB_TOP: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_M1: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_M1_FIRE: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_M2: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_M2_FIRE: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_N: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_NORMAL: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_N_FIRE: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_OVERALL: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_PURE_NORMAL: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_SIGMA: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_T: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_TAU: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_UNSPECIFIED: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_V1: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_V2: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_STEEL_WEB: _control_pb2_1_1_1_1.ControlTypeSteel
CONTROL_TYPE_TENSION: _pile_pb2.ControlType
CONTROL_TYPE_TIMBER_APEX: _control_pb2_1_1_1_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_COMPRESSION: _control_pb2_1_1_1_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_DEFLECTION: _control_pb2_1_1_1_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_FLEXURAL_BUCKLING1: _control_pb2_1_1_1_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_FLEXURAL_BUCKLING2: _control_pb2_1_1_1_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_OVERALL: _control_pb2_1_1_1_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_SHEAR: _control_pb2_1_1_1_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_TENSION: _control_pb2_1_1_1_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_TORSIONAL_BUCKLING: _control_pb2_1_1_1_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_UNSPECIFIED: _control_pb2_1_1_1_1.ControlTypeTimber
CONTROL_TYPE_UNSPECIFIED: _pile_pb2.ControlType
CURVE_A: _steel_pb2_1_1_1_1.Curve
CURVE_A0: _steel_pb2_1_1_1_1.Curve
CURVE_B: _steel_pb2_1_1_1_1.Curve
CURVE_C: _steel_pb2_1_1_1_1.Curve
CURVE_D: _steel_pb2_1_1_1_1.Curve
CURVE_LT_UNSPECIFIED: _steel_pb2_1_1_1_1.CurveLT
CURVE_L_T_A: _steel_pb2_1_1_1_1.CurveLT
CURVE_L_T_B: _steel_pb2_1_1_1_1.CurveLT
CURVE_L_T_C: _steel_pb2_1_1_1_1.CurveLT
CURVE_L_T_D: _steel_pb2_1_1_1_1.CurveLT
CURVE_UNSPECIFIED: _steel_pb2_1_1_1_1.Curve
DESCRIPTOR: _descriptor.FileDescriptor
DESIGN_TYPE_ALLOWEDSOILPRESSURE: _control_pb2_1_1_1_1.DesignTypeFoundation
DESIGN_TYPE_DRAINED: _control_pb2_1_1_1_1.DesignTypeFoundation
DESIGN_TYPE_DRAINED_PUNCHNING_ALT: _control_pb2_1_1_1_1.DesignTypeFoundation
DESIGN_TYPE_DRAINED_PUNCHNING_B6: _control_pb2_1_1_1_1.DesignTypeFoundation
DESIGN_TYPE_ROCK: _control_pb2_1_1_1_1.DesignTypeFoundation
DESIGN_TYPE_UNDRAINED: _control_pb2_1_1_1_1.DesignTypeFoundation
DESIGN_TYPE_UNDRAINED_PUNCHING: _control_pb2_1_1_1_1.DesignTypeFoundation
DESIGN_TYPE_UNSPECIFIED: _control_pb2_1_1_1_1.DesignTypeFoundation
DISPLACEMENT_RU: Displacement
DISPLACEMENT_RV: Displacement
DISPLACEMENT_RW: Displacement
DISPLACEMENT_RX: Displacement
DISPLACEMENT_RY: Displacement
DISPLACEMENT_RZ: Displacement
DISPLACEMENT_U: Displacement
DISPLACEMENT_UNSPECIFIED: Displacement
DISPLACEMENT_V: Displacement
DISPLACEMENT_W: Displacement
DISPLACEMENT_X: Displacement
DISPLACEMENT_Y: Displacement
DISPLACEMENT_Z: Displacement
ECCENTRICITY_TYPE_HIGH: _control_pb2_1_1_1_1.EccentricityTypeFoundation
ECCENTRICITY_TYPE_NORMAL: _control_pb2_1_1_1_1.EccentricityTypeFoundation
ECCENTRICITY_TYPE_UNSPECIFIED: _control_pb2_1_1_1_1.EccentricityTypeFoundation
FORCE_M1: Force
FORCE_M2: Force
FORCE_MX: Force
FORCE_MY: Force
FORCE_MZ: Force
FORCE_N: Force
FORCE_RX: Force
FORCE_RY: Force
FORCE_RZ: Force
FORCE_T: Force
FORCE_UNSPECIFIED: Force
FORCE_V1: Force
FORCE_V2: Force
OWNER_COMPANY: _utils_pb2_1_1_1_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1_1_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1_1_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1_1_1_1.Owner
OWNER_USER: _utils_pb2_1_1_1_1_1.Owner
SHEAR_RESISTANCE_HOLLOW: _steel_pb2_1_1_1_1.ShearResistanceEnum
SHEAR_RESISTANCE_I_LIKE: _steel_pb2_1_1_1_1.ShearResistanceEnum
SHEAR_RESISTANCE_NONE: _steel_pb2_1_1_1_1.ShearResistanceEnum
SHEAR_RESISTANCE_UNSPECIFIED: _steel_pb2_1_1_1_1.ShearResistanceEnum
SHEAR_RESISTANCE_U_LIKE: _steel_pb2_1_1_1_1.ShearResistanceEnum
SHEAR_STRESS_CHECK_RELEVANT_NO: _steel_pb2_1_1_1_1.ShearStressCheckRelevant
SHEAR_STRESS_CHECK_RELEVANT_NO_BECAUSE_WEB_BUCKLING: _steel_pb2_1_1_1_1.ShearStressCheckRelevant
SHEAR_STRESS_CHECK_RELEVANT_UNSPECIFIED: _steel_pb2_1_1_1_1.ShearStressCheckRelevant
SHEAR_STRESS_CHECK_RELEVANT_YES: _steel_pb2_1_1_1_1.ShearStressCheckRelevant
STAT_SYS_CANTILEVER: _timber_pb2.StatSys
STAT_SYS_SIMPLE_SUPPORTED: _timber_pb2.StatSys
STAT_SYS_UNSPECIFIED: _timber_pb2.StatSys
STRESS_MISES: Stress
STRESS_S11: Stress
STRESS_S12: Stress
STRESS_S22: Stress
STRESS_SP1: Stress
STRESS_SP2: Stress
STRESS_UNSPECIFIED: Stress
ST_BAR_WEB_RELEVANT_NO: _steel_pb2_1_1_1_1.StBarWebRelevant
ST_BAR_WEB_RELEVANT_NO_STIFF_LIMIT: _steel_pb2_1_1_1_1.StBarWebRelevant
ST_BAR_WEB_RELEVANT_NO_UNSTIFF_LIMIT: _steel_pb2_1_1_1_1.StBarWebRelevant
ST_BAR_WEB_RELEVANT_UNSPECIFIED: _steel_pb2_1_1_1_1.StBarWebRelevant
ST_BAR_WEB_RELEVANT_YES: _steel_pb2_1_1_1_1.StBarWebRelevant

class Data(_message.Message):
    __slots__ = ["displacement", "force", "stress", "temperature"]
    DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    STRESS_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    displacement: DisplacementData
    force: ForceData
    stress: StressData
    temperature: TemperatureData
    def __init__(self, displacement: _Optional[_Union[DisplacementData, _Mapping]] = ..., force: _Optional[_Union[ForceData, _Mapping]] = ..., stress: _Optional[_Union[StressData, _Mapping]] = ..., temperature: _Optional[_Union[TemperatureData, _Mapping]] = ...) -> None: ...

class DisplacementData(_message.Message):
    __slots__ = ["global_coordsys", "type", "value"]
    GLOBAL_COORDSYS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    global_coordsys: bool
    type: _containers.RepeatedScalarFieldContainer[Displacement]
    value: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, global_coordsys: bool = ..., type: _Optional[_Iterable[_Union[Displacement, str]]] = ..., value: _Optional[_Iterable[float]] = ...) -> None: ...

class Element(_message.Message):
    __slots__ = ["id", "introduced_positions", "positions", "result"]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTRODUCED_POSITIONS_FIELD_NUMBER: _ClassVar[int]
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2_1_1_1_1_1.ID
    introduced_positions: _containers.RepeatedCompositeFieldContainer[PositionResult]
    positions: _containers.RepeatedCompositeFieldContainer[PositionResult]
    result: ElementResult
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1_1_1_1.ID, _Mapping]] = ..., positions: _Optional[_Iterable[_Union[PositionResult, _Mapping]]] = ..., introduced_positions: _Optional[_Iterable[_Union[PositionResult, _Mapping]]] = ..., result: _Optional[_Union[ElementResult, _Mapping]] = ...) -> None: ...

class ElementResult(_message.Message):
    __slots__ = ["foundation", "pile", "rc", "retaining_wall", "steel", "timber"]
    FOUNDATION_FIELD_NUMBER: _ClassVar[int]
    PILE_FIELD_NUMBER: _ClassVar[int]
    RC_FIELD_NUMBER: _ClassVar[int]
    RETAINING_WALL_FIELD_NUMBER: _ClassVar[int]
    STEEL_FIELD_NUMBER: _ClassVar[int]
    TIMBER_FIELD_NUMBER: _ClassVar[int]
    foundation: _foundation_pb2_1_1.Element
    pile: _pile_pb2.Element
    rc: _concrete_pb2_1.Element
    retaining_wall: _retainingwall_pb2.Element
    steel: _steel_pb2_1_1_1_1.Element
    timber: _timber_pb2.Element
    def __init__(self, rc: _Optional[_Union[_concrete_pb2_1.Element, _Mapping]] = ..., steel: _Optional[_Union[_steel_pb2_1_1_1_1.Element, _Mapping]] = ..., timber: _Optional[_Union[_timber_pb2.Element, _Mapping]] = ..., foundation: _Optional[_Union[_foundation_pb2_1_1.Element, _Mapping]] = ..., pile: _Optional[_Union[_pile_pb2.Element, _Mapping]] = ..., retaining_wall: _Optional[_Union[_retainingwall_pb2.Element, _Mapping]] = ...) -> None: ...

class ForceData(_message.Message):
    __slots__ = ["global_coordsys", "type", "value"]
    GLOBAL_COORDSYS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    global_coordsys: bool
    type: _containers.RepeatedScalarFieldContainer[Force]
    value: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, global_coordsys: bool = ..., type: _Optional[_Iterable[_Union[Force, str]]] = ..., value: _Optional[_Iterable[float]] = ...) -> None: ...

class Node(_message.Message):
    __slots__ = ["results"]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: Data
    def __init__(self, results: _Optional[_Union[Data, _Mapping]] = ...) -> None: ...

class PositionResult(_message.Message):
    __slots__ = ["distance", "foundation", "group_name", "id", "pile", "position2d", "position3d", "rc", "results", "retaining_wall", "steel", "timber"]
    DISTANCE_FIELD_NUMBER: _ClassVar[int]
    FOUNDATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PILE_FIELD_NUMBER: _ClassVar[int]
    POSITION2D_FIELD_NUMBER: _ClassVar[int]
    POSITION3D_FIELD_NUMBER: _ClassVar[int]
    RC_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    RETAINING_WALL_FIELD_NUMBER: _ClassVar[int]
    STEEL_FIELD_NUMBER: _ClassVar[int]
    TIMBER_FIELD_NUMBER: _ClassVar[int]
    distance: float
    foundation: _foundation_pb2_1_1.Data
    group_name: str
    id: _utils_pb2_1_1_1_1_1.ID
    pile: _pile_pb2.Data
    position2d: _geometry_pb2_1_1_1.Point2D
    position3d: _geometry_pb2_1_1_1.Point3D
    rc: _concrete_pb2_1.Data
    results: Data
    retaining_wall: _retainingwall_pb2.Data
    steel: _steel_pb2_1_1_1_1.Data
    timber: _timber_pb2.Data
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1_1_1_1.ID, _Mapping]] = ..., distance: _Optional[float] = ..., position2d: _Optional[_Union[_geometry_pb2_1_1_1.Point2D, _Mapping]] = ..., position3d: _Optional[_Union[_geometry_pb2_1_1_1.Point3D, _Mapping]] = ..., results: _Optional[_Union[Data, _Mapping]] = ..., rc: _Optional[_Union[_concrete_pb2_1.Data, _Mapping]] = ..., steel: _Optional[_Union[_steel_pb2_1_1_1_1.Data, _Mapping]] = ..., timber: _Optional[_Union[_timber_pb2.Data, _Mapping]] = ..., foundation: _Optional[_Union[_foundation_pb2_1_1.Data, _Mapping]] = ..., pile: _Optional[_Union[_pile_pb2.Data, _Mapping]] = ..., retaining_wall: _Optional[_Union[_retainingwall_pb2.Data, _Mapping]] = ..., group_name: _Optional[str] = ...) -> None: ...

class StressData(_message.Message):
    __slots__ = ["type", "value"]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    type: _containers.RepeatedScalarFieldContainer[Stress]
    value: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, type: _Optional[_Iterable[_Union[Stress, str]]] = ..., value: _Optional[_Iterable[float]] = ...) -> None: ...

class TemperatureData(_message.Message):
    __slots__ = ["t"]
    T_FIELD_NUMBER: _ClassVar[int]
    t: float
    def __init__(self, t: _Optional[float] = ...) -> None: ...

class Force(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Displacement(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Stress(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
