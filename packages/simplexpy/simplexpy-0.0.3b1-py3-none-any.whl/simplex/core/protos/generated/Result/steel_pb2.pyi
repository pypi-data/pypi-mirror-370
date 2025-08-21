from Geometry import beam_pb2 as _beam_pb2
from Utils import utils_pb2 as _utils_pb2
import stage_pb2 as _stage_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Geometry import foundation_pb2 as _foundation_pb2
from Design import design_pb2 as _design_pb2
from Geometry import rebar_pb2 as _rebar_pb2
from Geometry import strand_pb2 as _strand_pb2
from Geometry import link_pb2 as _link_pb2
from Design import concrete_pb2 as _concrete_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Design import steel_pb2 as _steel_pb2
from Utils import utils_pb2 as _utils_pb2_1_1
from Design import general_pb2 as _general_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1
import sections_pb2 as _sections_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1
from Geometry import geometry_pb2 as _geometry_pb2_1_1
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1
from Material import steel_pb2 as _steel_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1_1
from Result import control_pb2 as _control_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Geometry.beam_pb2 import ConcreteElement
from Geometry.beam_pb2 import Stiffener
from Geometry.beam_pb2 import BucklingSpan
from Geometry.beam_pb2 import BucklingData
from Geometry.beam_pb2 import FlexBuckling
from Geometry.beam_pb2 import LTBuckling
from Geometry.beam_pb2 import LTSBuckling
from Geometry.beam_pb2 import SteelElement
from Geometry.beam_pb2 import TimberElement
from Geometry.beam_pb2 import MultiLayerSegment
from Geometry.beam_pb2 import Segment
from Geometry.beam_pb2 import Layer
from Geometry.beam_pb2 import MultiLayer
from Geometry.beam_pb2 import SecInPlane
from Geometry.beam_pb2 import Data
from Geometry.beam_pb2 import ConcreteBeamType
from Geometry.beam_pb2 import BucklingType
from Geometry.beam_pb2 import ActionType
from Geometry.beam_pb2 import Alignment
from Geometry.beam_pb2 import SupportCondition
from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
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
from Design.general_pb2 import PartialCoefficient
from Design.general_pb2 import PartialCoefficients
from Design.general_pb2 import FireGeneral
from Design.general_pb2 import FireRadiativeHeatFlux
from Design.general_pb2 import ElementDesignSettings
from Design.general_pb2 import GeneralDesignSettings
from Design.general_pb2 import TemperatureCurve
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
from Geometry.geometry_pb2 import Vector2D
from Geometry.geometry_pb2 import VectorYZ
from Geometry.geometry_pb2 import VectorYZLT
from Geometry.geometry_pb2 import Point2D
from Geometry.geometry_pb2 import Line2D
from Geometry.geometry_pb2 import Arc2D
from Geometry.geometry_pb2 import Circle2D
from Geometry.geometry_pb2 import Curve2D
from Geometry.geometry_pb2 import PolyLine2D
from Geometry.geometry_pb2 import PolyCurve2D
from Geometry.geometry_pb2 import LineFace2D
from Geometry.geometry_pb2 import CurveFace2D
from Geometry.geometry_pb2 import Vector3D
from Geometry.geometry_pb2 import Point3D
from Geometry.geometry_pb2 import Orientation
from Geometry.geometry_pb2 import Line3D
from Geometry.geometry_pb2 import Arc3D
from Geometry.geometry_pb2 import Circle3D
from Geometry.geometry_pb2 import Curve3D
from Geometry.geometry_pb2 import PolyLine3D
from Geometry.geometry_pb2 import PolyCurve3D
from Geometry.geometry_pb2 import LineFace3D
from Geometry.geometry_pb2 import CurveFace3D
from Geometry.geometry_pb2 import Block
from Material.steel_pb2 import Type
from Material.steel_pb2 import CharacteristicData
from Material.steel_pb2 import StrengthValue
from Material.steel_pb2 import Data
from Material.steel_pb2 import ProductionType
from Material.steel_pb2 import Sort
from Material.steel_pb2 import Product
from Material.steel_pb2 import DuctilityClass
from Result.control_pb2 import ControlTypeFoundation
from Result.control_pb2 import ControlData
from Result.control_pb2 import ControlTypeConcrete
from Result.control_pb2 import ControlTypeSteel
from Result.control_pb2 import ControlTypeTimber
from Result.control_pb2 import CtrlTypeFoundation
from Result.control_pb2 import AnalysisTypeFoundation
from Result.control_pb2 import DesignTypeFoundation
from Result.control_pb2 import EccentricityTypeFoundation
ACTION_TYPE_BAR: _beam_pb2.ActionType
ACTION_TYPE_BEAM: _beam_pb2.ActionType
ACTION_TYPE_COLUMN: _beam_pb2.ActionType
ACTION_TYPE_UNSPECIFIED: _beam_pb2.ActionType
ALIGNMENT_BOTTOM: _beam_pb2.Alignment
ALIGNMENT_CENTER: _beam_pb2.Alignment
ALIGNMENT_TOP: _beam_pb2.Alignment
ALIGNMENT_UNSPECIFIED: _beam_pb2.Alignment
ANALYSIS_TYPE_NORMAL: _control_pb2.AnalysisTypeFoundation
ANALYSIS_TYPE_SOIL_PUNCHING: _control_pb2.AnalysisTypeFoundation
ANALYSIS_TYPE_UNSPECIFIED: _control_pb2.AnalysisTypeFoundation
BAR_SECTION_TYPE_UNIFORM: BarSectionType
BAR_SECTION_TYPE_UNSPECIFIED: BarSectionType
BAR_SECTION_TYPE_VARIABLE: BarSectionType
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
BUCKLING_TYPE_FLEXURAL_STIFF: _beam_pb2.BucklingType
BUCKLING_TYPE_FLEXURAL_WEAK: _beam_pb2.BucklingType
BUCKLING_TYPE_LATERAL_TORSIONAL: _beam_pb2.BucklingType
BUCKLING_TYPE_PRESSURED_BOTTOM_FLANGE: _beam_pb2.BucklingType
BUCKLING_TYPE_PRESSURED_TOP_FLANGE: _beam_pb2.BucklingType
BUCKLING_TYPE_UNSPECIFIED: _beam_pb2.BucklingType
CONCRETE_BEAM_TYPE_CONSTANT: _beam_pb2.ConcreteBeamType
CONCRETE_BEAM_TYPE_CUSTOM: _beam_pb2.ConcreteBeamType
CONCRETE_BEAM_TYPE_IB: _beam_pb2.ConcreteBeamType
CONCRETE_BEAM_TYPE_RBX: _beam_pb2.ConcreteBeamType
CONCRETE_BEAM_TYPE_SIB: _beam_pb2.ConcreteBeamType
CONCRETE_BEAM_TYPE_STT: _beam_pb2.ConcreteBeamType
CONCRETE_BEAM_TYPE_UNSPECIFIED: _beam_pb2.ConcreteBeamType
CONTROL_TYPE_CONCRETE_ANCHORAGE_BTM: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_ANCHORAGE_TOP: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_AXIAL_FORCE: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_BIAXIAL_MOMENT: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_COMPRESSION_COVER_CHECK: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_COMPRESSION_STRESS: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_DEFLECTION: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_HOLLOWCORE_SPALLING: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_INITIAL_PRESTRESS: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_MOMENT_M2: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_NEGATIVE_CRACK_WIDTH: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_NEGATIVE_MOMENT_M1: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_POSITIVE_CRACK_WIDTH: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_POSITIVE_MOMENT_M1: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_PUNCHING_COLUMN: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_PUNCHING_PERIMETER: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_FORCE: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_FORCE_TOPPING: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_STIRRUPS: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_STIRRUPS_TOPPING: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_STRESS_AFTER_RELEASE: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TOPPING_JOINT: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_COMPRESSION_LONGITUDINAL: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_COMPRESSION_TRANSVERSE: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_LONGITUDINAL: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_TENSION_TRANSVERSE: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_TRANSVERSE: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_UNSPECIFIED: _control_pb2.ControlTypeConcrete
CONTROL_TYPE_FOUNDATION_BEARING: _control_pb2.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_OVERALL: _control_pb2.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_OVERTURNING: _control_pb2.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_SETTLEMENT: _control_pb2.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_SLIDING: _control_pb2.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_UNREINFORCED: _control_pb2.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_UNSPECIFIED: _control_pb2.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_UPLIFT: _control_pb2.CtrlTypeFoundation
CONTROL_TYPE_STEEL_DEFLECTION: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_FB1: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_FB2: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_FTB: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_IA1: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_IA2: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_IA2ND: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_LTB_BOTTOM: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_LTB_TOP: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_M1: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_M1_FIRE: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_M2: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_M2_FIRE: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_N: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_NORMAL: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_N_FIRE: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_OVERALL: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_PURE_NORMAL: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_SIGMA: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_T: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_TAU: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_UNSPECIFIED: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_V1: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_V2: _control_pb2.ControlTypeSteel
CONTROL_TYPE_STEEL_WEB: _control_pb2.ControlTypeSteel
CONTROL_TYPE_TIMBER_APEX: _control_pb2.ControlTypeTimber
CONTROL_TYPE_TIMBER_COMPRESSION: _control_pb2.ControlTypeTimber
CONTROL_TYPE_TIMBER_DEFLECTION: _control_pb2.ControlTypeTimber
CONTROL_TYPE_TIMBER_FLEXURAL_BUCKLING1: _control_pb2.ControlTypeTimber
CONTROL_TYPE_TIMBER_FLEXURAL_BUCKLING2: _control_pb2.ControlTypeTimber
CONTROL_TYPE_TIMBER_OVERALL: _control_pb2.ControlTypeTimber
CONTROL_TYPE_TIMBER_SHEAR: _control_pb2.ControlTypeTimber
CONTROL_TYPE_TIMBER_TENSION: _control_pb2.ControlTypeTimber
CONTROL_TYPE_TIMBER_TORSIONAL_BUCKLING: _control_pb2.ControlTypeTimber
CONTROL_TYPE_TIMBER_UNSPECIFIED: _control_pb2.ControlTypeTimber
CURVE_A: Curve
CURVE_A0: Curve
CURVE_B: Curve
CURVE_C: Curve
CURVE_D: Curve
CURVE_LT_UNSPECIFIED: CurveLT
CURVE_L_T_A: CurveLT
CURVE_L_T_B: CurveLT
CURVE_L_T_C: CurveLT
CURVE_L_T_D: CurveLT
CURVE_UNSPECIFIED: Curve
DESCRIPTOR: _descriptor.FileDescriptor
DESIGN_TYPE_ALLOWEDSOILPRESSURE: _control_pb2.DesignTypeFoundation
DESIGN_TYPE_DRAINED: _control_pb2.DesignTypeFoundation
DESIGN_TYPE_DRAINED_PUNCHNING_ALT: _control_pb2.DesignTypeFoundation
DESIGN_TYPE_DRAINED_PUNCHNING_B6: _control_pb2.DesignTypeFoundation
DESIGN_TYPE_ROCK: _control_pb2.DesignTypeFoundation
DESIGN_TYPE_UNDRAINED: _control_pb2.DesignTypeFoundation
DESIGN_TYPE_UNDRAINED_PUNCHING: _control_pb2.DesignTypeFoundation
DESIGN_TYPE_UNSPECIFIED: _control_pb2.DesignTypeFoundation
DUCTILITY_CLASS_A: _steel_pb2_1.DuctilityClass
DUCTILITY_CLASS_B: _steel_pb2_1.DuctilityClass
DUCTILITY_CLASS_C: _steel_pb2_1.DuctilityClass
DUCTILITY_CLASS_UNSPECIFIED: _steel_pb2_1.DuctilityClass
ECCENTRICITY_TYPE_HIGH: _control_pb2.EccentricityTypeFoundation
ECCENTRICITY_TYPE_NORMAL: _control_pb2.EccentricityTypeFoundation
ECCENTRICITY_TYPE_UNSPECIFIED: _control_pb2.EccentricityTypeFoundation
INTERACTION_METHOD_METHOD1: _steel_pb2.InteractionMethod
INTERACTION_METHOD_METHOD2: _steel_pb2.InteractionMethod
INTERACTION_METHOD_UNSPECIFIED: _steel_pb2.InteractionMethod
LATERAL_TORSIONAL_METHOD_GENERAL: _steel_pb2.LateralTorsionalMethod
LATERAL_TORSIONAL_METHOD_GENERAL_SPEC_FOR_I: _steel_pb2.LateralTorsionalMethod
LATERAL_TORSIONAL_METHOD_SIMPLIFIED: _steel_pb2.LateralTorsionalMethod
LATERAL_TORSIONAL_METHOD_UNSPECIFIED: _steel_pb2.LateralTorsionalMethod
MATERIAL_CATEGORY_CONCRETE: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_STEEL: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_TIMBER: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_UNSPECIFIED: _sections_pb2.MaterialCategory
OWNER_COMPANY: _utils_pb2_1_1_1_1_1_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1_1_1_1_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1_1_1_1_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1_1_1_1_1_1.Owner
OWNER_USER: _utils_pb2_1_1_1_1_1_1_1.Owner
PRODUCTION_TYPE_COLD_WORKED: _steel_pb2_1.ProductionType
PRODUCTION_TYPE_ROLLED: _steel_pb2_1.ProductionType
PRODUCTION_TYPE_UNSPECIFIED: _steel_pb2_1.ProductionType
PRODUCTION_TYPE_WELDED: _steel_pb2_1.ProductionType
PRODUCT_PLAIN: _steel_pb2_1.Product
PRODUCT_REINFORCEMENT: _steel_pb2_1.Product
PRODUCT_UNSPECIFIED: _steel_pb2_1.Product
SECOND_ORDER_ANALYSIS_CONSIDER: _steel_pb2.SecondOrderAnalysis
SECOND_ORDER_ANALYSIS_FIRST_ORDER_DESIGN: _steel_pb2.SecondOrderAnalysis
SECOND_ORDER_ANALYSIS_IGNORE: _steel_pb2.SecondOrderAnalysis
SECOND_ORDER_ANALYSIS_UNSPECIFIED: _steel_pb2.SecondOrderAnalysis
SECTION_EXPOSURE_ALL_SIDES: _steel_pb2.SectionExposure
SECTION_EXPOSURE_FLANGE_ONLY: _steel_pb2.SectionExposure
SECTION_EXPOSURE_THREE_SIDES: _steel_pb2.SectionExposure
SECTION_EXPOSURE_UNSPECIFIED: _steel_pb2.SectionExposure
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
SHEAR_RESISTANCE_HOLLOW: ShearResistanceEnum
SHEAR_RESISTANCE_I_LIKE: ShearResistanceEnum
SHEAR_RESISTANCE_NONE: ShearResistanceEnum
SHEAR_RESISTANCE_UNSPECIFIED: ShearResistanceEnum
SHEAR_RESISTANCE_U_LIKE: ShearResistanceEnum
SHEAR_STRESS_CHECK_RELEVANT_NO: ShearStressCheckRelevant
SHEAR_STRESS_CHECK_RELEVANT_NO_BECAUSE_WEB_BUCKLING: ShearStressCheckRelevant
SHEAR_STRESS_CHECK_RELEVANT_UNSPECIFIED: ShearStressCheckRelevant
SHEAR_STRESS_CHECK_RELEVANT_YES: ShearStressCheckRelevant
SORT_REGULAR: _steel_pb2_1.Sort
SORT_STAINLESS: _steel_pb2_1.Sort
SORT_UNSPECIFIED: _steel_pb2_1.Sort
ST_BAR_WEB_RELEVANT_NO: StBarWebRelevant
ST_BAR_WEB_RELEVANT_NO_STIFF_LIMIT: StBarWebRelevant
ST_BAR_WEB_RELEVANT_NO_UNSTIFF_LIMIT: StBarWebRelevant
ST_BAR_WEB_RELEVANT_UNSPECIFIED: StBarWebRelevant
ST_BAR_WEB_RELEVANT_YES: StBarWebRelevant
SUPPORT_CONDITION_CANTILEVER: _beam_pb2.SupportCondition
SUPPORT_CONDITION_SIMPLY: _beam_pb2.SupportCondition
SUPPORT_CONDITION_UNSPECIFIED: _beam_pb2.SupportCondition
TEMPERATURE_CURVE_EXTERNAL: _general_pb2.TemperatureCurve
TEMPERATURE_CURVE_HYDROCARBON: _general_pb2.TemperatureCurve
TEMPERATURE_CURVE_PARAMETRIC: _general_pb2.TemperatureCurve
TEMPERATURE_CURVE_STANDARD: _general_pb2.TemperatureCurve
TEMPERATURE_CURVE_UNSPECIFIED: _general_pb2.TemperatureCurve

class Boolean2D(_message.Message):
    __slots__ = ["one", "two"]
    ONE_FIELD_NUMBER: _ClassVar[int]
    TWO_FIELD_NUMBER: _ClassVar[int]
    one: bool
    two: bool
    def __init__(self, one: bool = ..., two: bool = ...) -> None: ...

class BucklingFactors(_message.Message):
    __slots__ = ["alfa", "chi", "lambda_over", "lambda_theta", "lcr", "ncr", "phi"]
    ALFA_FIELD_NUMBER: _ClassVar[int]
    CHI_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_OVER_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_THETA_FIELD_NUMBER: _ClassVar[int]
    LCR_FIELD_NUMBER: _ClassVar[int]
    NCR_FIELD_NUMBER: _ClassVar[int]
    PHI_FIELD_NUMBER: _ClassVar[int]
    alfa: float
    chi: float
    lambda_over: float
    lambda_theta: float
    lcr: float
    ncr: float
    phi: float
    def __init__(self, chi: _Optional[float] = ..., phi: _Optional[float] = ..., alfa: _Optional[float] = ..., lambda_over: _Optional[float] = ..., lcr: _Optional[float] = ..., ncr: _Optional[float] = ..., lambda_theta: _Optional[float] = ...) -> None: ...

class BucklingShapes(_message.Message):
    __slots__ = ["flexural1", "flexural2", "flexural_torsional", "lateral_torsional_bottom", "lateral_torsional_top"]
    FLEXURAL1_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL2_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_TORSIONAL_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_TOP_FIELD_NUMBER: _ClassVar[int]
    flexural1: Curve
    flexural2: Curve
    flexural_torsional: Curve
    lateral_torsional_bottom: CurveLT
    lateral_torsional_top: CurveLT
    def __init__(self, flexural1: _Optional[_Union[Curve, str]] = ..., flexural2: _Optional[_Union[Curve, str]] = ..., flexural_torsional: _Optional[_Union[Curve, str]] = ..., lateral_torsional_top: _Optional[_Union[CurveLT, str]] = ..., lateral_torsional_bottom: _Optional[_Union[CurveLT, str]] = ...) -> None: ...

class BucklingTorsionalFactors(_message.Message):
    __slots__ = ["ncr_t", "ncr_t_f"]
    NCR_T_FIELD_NUMBER: _ClassVar[int]
    NCR_T_F_FIELD_NUMBER: _ClassVar[int]
    ncr_t: float
    ncr_t_f: float
    def __init__(self, ncr_t: _Optional[float] = ..., ncr_t_f: _Optional[float] = ...) -> None: ...

class CharacteristicValues(_message.Message):
    __slots__ = ["elasticity_modulus", "shear_modulus", "ultimate_strength", "yield_strength"]
    ELASTICITY_MODULUS_FIELD_NUMBER: _ClassVar[int]
    SHEAR_MODULUS_FIELD_NUMBER: _ClassVar[int]
    ULTIMATE_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    YIELD_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    elasticity_modulus: float
    shear_modulus: float
    ultimate_strength: float
    yield_strength: float
    def __init__(self, elasticity_modulus: _Optional[float] = ..., yield_strength: _Optional[float] = ..., ultimate_strength: _Optional[float] = ..., shear_modulus: _Optional[float] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["section_class", "section_result"]
    SECTION_CLASS_FIELD_NUMBER: _ClassVar[int]
    SECTION_RESULT_FIELD_NUMBER: _ClassVar[int]
    section_class: SectionClass
    section_result: SectionResult
    def __init__(self, section_class: _Optional[_Union[SectionClass, _Mapping]] = ..., section_result: _Optional[_Union[SectionResult, _Mapping]] = ...) -> None: ...

class DesignSummary(_message.Message):
    __slots__ = ["buckling_shapes", "controls", "elem_guid", "extra_parameters", "gas_temperature", "interaction_method", "kappa", "n_a_values", "torsional_sharpe", "varying_bar", "virtual_stiffeners"]
    BUCKLING_SHAPES_FIELD_NUMBER: _ClassVar[int]
    CONTROLS_FIELD_NUMBER: _ClassVar[int]
    ELEM_GUID_FIELD_NUMBER: _ClassVar[int]
    EXTRA_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    GAS_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    INTERACTION_METHOD_FIELD_NUMBER: _ClassVar[int]
    KAPPA_FIELD_NUMBER: _ClassVar[int]
    N_A_VALUES_FIELD_NUMBER: _ClassVar[int]
    TORSIONAL_SHARPE_FIELD_NUMBER: _ClassVar[int]
    VARYING_BAR_FIELD_NUMBER: _ClassVar[int]
    VIRTUAL_STIFFENERS_FIELD_NUMBER: _ClassVar[int]
    buckling_shapes: BucklingShapes
    controls: _containers.RepeatedCompositeFieldContainer[_control_pb2.ControlData]
    elem_guid: str
    extra_parameters: _containers.RepeatedCompositeFieldContainer[ExtraParameters]
    gas_temperature: GasTemperature
    interaction_method: _steel_pb2.InteractionMethod
    kappa: _geometry_pb2_1_1.Vector2D
    n_a_values: SteelDesignNationalAnnexValues
    torsional_sharpe: ShearResistanceEnum
    varying_bar: BarSectionType
    virtual_stiffeners: VirtualStiffeners
    def __init__(self, elem_guid: _Optional[str] = ..., varying_bar: _Optional[_Union[BarSectionType, str]] = ..., virtual_stiffeners: _Optional[_Union[VirtualStiffeners, _Mapping]] = ..., buckling_shapes: _Optional[_Union[BucklingShapes, _Mapping]] = ..., torsional_sharpe: _Optional[_Union[ShearResistanceEnum, str]] = ..., n_a_values: _Optional[_Union[SteelDesignNationalAnnexValues, _Mapping]] = ..., interaction_method: _Optional[_Union[_steel_pb2.InteractionMethod, str]] = ..., gas_temperature: _Optional[_Union[GasTemperature, _Mapping]] = ..., kappa: _Optional[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]] = ..., extra_parameters: _Optional[_Iterable[_Union[ExtraParameters, _Mapping]]] = ..., controls: _Optional[_Iterable[_Union[_control_pb2.ControlData, _Mapping]]] = ...) -> None: ...

class EffectiveClassFour(_message.Message):
    __slots__ = ["a_eff", "e_n_eff", "i_eff", "wc_eff", "wt_eff"]
    A_EFF_FIELD_NUMBER: _ClassVar[int]
    E_N_EFF_FIELD_NUMBER: _ClassVar[int]
    I_EFF_FIELD_NUMBER: _ClassVar[int]
    WC_EFF_FIELD_NUMBER: _ClassVar[int]
    WT_EFF_FIELD_NUMBER: _ClassVar[int]
    a_eff: float
    e_n_eff: _geometry_pb2_1_1.Vector2D
    i_eff: _geometry_pb2_1_1.Vector2D
    wc_eff: _geometry_pb2_1_1.Vector2D
    wt_eff: _geometry_pb2_1_1.Vector2D
    def __init__(self, a_eff: _Optional[float] = ..., i_eff: _Optional[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]] = ..., e_n_eff: _Optional[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]] = ..., wc_eff: _Optional[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]] = ..., wt_eff: _Optional[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]] = ...) -> None: ...

class Element(_message.Message):
    __slots__ = ["max_of_controls"]
    MAX_OF_CONTROLS_FIELD_NUMBER: _ClassVar[int]
    max_of_controls: _containers.RepeatedCompositeFieldContainer[_control_pb2.ControlData]
    def __init__(self, max_of_controls: _Optional[_Iterable[_Union[_control_pb2.ControlData, _Mapping]]] = ...) -> None: ...

class ExtraParameters(_message.Message):
    __slots__ = ["extra_fire", "extra_materials", "extra_materials_fire", "extra_sections"]
    EXTRA_FIRE_FIELD_NUMBER: _ClassVar[int]
    EXTRA_MATERIALS_FIELD_NUMBER: _ClassVar[int]
    EXTRA_MATERIALS_FIRE_FIELD_NUMBER: _ClassVar[int]
    EXTRA_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    extra_fire: FireParameters
    extra_materials: MaterialParameters
    extra_materials_fire: MaterialFireParameters
    extra_sections: SectionParameters
    def __init__(self, extra_sections: _Optional[_Union[SectionParameters, _Mapping]] = ..., extra_materials: _Optional[_Union[MaterialParameters, _Mapping]] = ..., extra_fire: _Optional[_Union[FireParameters, _Mapping]] = ..., extra_materials_fire: _Optional[_Union[MaterialFireParameters, _Mapping]] = ...) -> None: ...

class FireParameters(_message.Message):
    __slots__ = ["protected", "unprotected"]
    PROTECTED_FIELD_NUMBER: _ClassVar[int]
    UNPROTECTED_FIELD_NUMBER: _ClassVar[int]
    protected: MemberTemperatureProtected
    unprotected: MemberTemperatureUnprotected
    def __init__(self, unprotected: _Optional[_Union[MemberTemperatureUnprotected, _Mapping]] = ..., protected: _Optional[_Union[MemberTemperatureProtected, _Mapping]] = ...) -> None: ...

class Flexural(_message.Message):
    __slots__ = ["buckling_factors", "curve", "nb_rd", "utilization"]
    BUCKLING_FACTORS_FIELD_NUMBER: _ClassVar[int]
    CURVE_FIELD_NUMBER: _ClassVar[int]
    NB_RD_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    buckling_factors: BucklingFactors
    curve: Curve
    nb_rd: float
    utilization: float
    def __init__(self, buckling_factors: _Optional[_Union[BucklingFactors, _Mapping]] = ..., nb_rd: _Optional[float] = ..., curve: _Optional[_Union[Curve, str]] = ..., utilization: _Optional[float] = ...) -> None: ...

class FlexuralTorsional(_message.Message):
    __slots__ = ["buckling_factors", "buckling_torsional_factors", "curve", "nb_rd_t", "utilization"]
    BUCKLING_FACTORS_FIELD_NUMBER: _ClassVar[int]
    BUCKLING_TORSIONAL_FACTORS_FIELD_NUMBER: _ClassVar[int]
    CURVE_FIELD_NUMBER: _ClassVar[int]
    NB_RD_T_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    buckling_factors: BucklingFactors
    buckling_torsional_factors: BucklingTorsionalFactors
    curve: Curve
    nb_rd_t: float
    utilization: float
    def __init__(self, buckling_factors: _Optional[_Union[BucklingFactors, _Mapping]] = ..., nb_rd_t: _Optional[float] = ..., buckling_torsional_factors: _Optional[_Union[BucklingTorsionalFactors, _Mapping]] = ..., curve: _Optional[_Union[Curve, str]] = ..., utilization: _Optional[float] = ...) -> None: ...

class Force(_message.Message):
    __slots__ = ["m1_ed", "m2_ed", "ned", "ned_comp", "ted", "v1_ed", "v2_ed"]
    M1_ED_FIELD_NUMBER: _ClassVar[int]
    M2_ED_FIELD_NUMBER: _ClassVar[int]
    NED_COMP_FIELD_NUMBER: _ClassVar[int]
    NED_FIELD_NUMBER: _ClassVar[int]
    TED_FIELD_NUMBER: _ClassVar[int]
    V1_ED_FIELD_NUMBER: _ClassVar[int]
    V2_ED_FIELD_NUMBER: _ClassVar[int]
    m1_ed: float
    m2_ed: float
    ned: float
    ned_comp: float
    ted: float
    v1_ed: float
    v2_ed: float
    def __init__(self, ned: _Optional[float] = ..., ned_comp: _Optional[float] = ..., ted: _Optional[float] = ..., m1_ed: _Optional[float] = ..., m2_ed: _Optional[float] = ..., v1_ed: _Optional[float] = ..., v2_ed: _Optional[float] = ...) -> None: ...

class GasTemperature(_message.Message):
    __slots__ = ["graph_gas_temp", "parametric", "section_exposion", "temp_curve", "temp_gas", "treq"]
    GRAPH_GAS_TEMP_FIELD_NUMBER: _ClassVar[int]
    PARAMETRIC_FIELD_NUMBER: _ClassVar[int]
    SECTION_EXPOSION_FIELD_NUMBER: _ClassVar[int]
    TEMP_CURVE_FIELD_NUMBER: _ClassVar[int]
    TEMP_GAS_FIELD_NUMBER: _ClassVar[int]
    TREQ_FIELD_NUMBER: _ClassVar[int]
    graph_gas_temp: TVPointW
    parametric: Parametric
    section_exposion: _steel_pb2.SectionExposure
    temp_curve: _general_pb2.TemperatureCurve
    temp_gas: float
    treq: float
    def __init__(self, temp_curve: _Optional[_Union[_general_pb2.TemperatureCurve, str]] = ..., parametric: _Optional[_Union[Parametric, _Mapping]] = ..., graph_gas_temp: _Optional[_Union[TVPointW, _Mapping]] = ..., treq: _Optional[float] = ..., temp_gas: _Optional[float] = ..., section_exposion: _Optional[_Union[_steel_pb2.SectionExposure, str]] = ...) -> None: ...

class Interaction(_message.Message):
    __slots__ = ["alfam", "beta_m", "cm", "cy", "cz", "delta_m_ed", "delta_x", "k", "k_fire", "m_rk", "psim", "utilization"]
    ALFAM_FIELD_NUMBER: _ClassVar[int]
    BETA_M_FIELD_NUMBER: _ClassVar[int]
    CM_FIELD_NUMBER: _ClassVar[int]
    CY_FIELD_NUMBER: _ClassVar[int]
    CZ_FIELD_NUMBER: _ClassVar[int]
    DELTA_M_ED_FIELD_NUMBER: _ClassVar[int]
    DELTA_X_FIELD_NUMBER: _ClassVar[int]
    K_FIELD_NUMBER: _ClassVar[int]
    K_FIRE_FIELD_NUMBER: _ClassVar[int]
    M_RK_FIELD_NUMBER: _ClassVar[int]
    PSIM_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    alfam: _geometry_pb2_1_1.VectorYZLT
    beta_m: _geometry_pb2_1_1.VectorYZLT
    cm: _geometry_pb2_1_1.VectorYZLT
    cy: _geometry_pb2_1_1.VectorYZ
    cz: _geometry_pb2_1_1.VectorYZ
    delta_m_ed: _geometry_pb2_1_1.Vector2D
    delta_x: _geometry_pb2_1_1.Vector2D
    k: _geometry_pb2_1_1.Vector2D
    k_fire: _geometry_pb2_1_1.VectorYZLT
    m_rk: _geometry_pb2_1_1.Vector2D
    psim: _geometry_pb2_1_1.VectorYZLT
    utilization: float
    def __init__(self, delta_x: _Optional[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]] = ..., delta_m_ed: _Optional[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]] = ..., cm: _Optional[_Union[_geometry_pb2_1_1.VectorYZLT, _Mapping]] = ..., alfam: _Optional[_Union[_geometry_pb2_1_1.VectorYZLT, _Mapping]] = ..., psim: _Optional[_Union[_geometry_pb2_1_1.VectorYZLT, _Mapping]] = ..., cy: _Optional[_Union[_geometry_pb2_1_1.VectorYZ, _Mapping]] = ..., cz: _Optional[_Union[_geometry_pb2_1_1.VectorYZ, _Mapping]] = ..., k: _Optional[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]] = ..., m_rk: _Optional[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]] = ..., utilization: _Optional[float] = ..., beta_m: _Optional[_Union[_geometry_pb2_1_1.VectorYZLT, _Mapping]] = ..., k_fire: _Optional[_Union[_geometry_pb2_1_1.VectorYZLT, _Mapping]] = ...) -> None: ...

class Interaction2nd(_message.Message):
    __slots__ = ["utilization"]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    utilization: float
    def __init__(self, utilization: _Optional[float] = ...) -> None: ...

class LateralTorsional(_message.Message):
    __slots__ = ["buckling_factors", "curve_l_t", "lateral_torsional_i_factors", "lateral_torsional_method", "lateral_torsional_sim_factors", "mb_rd", "mcr", "utilization"]
    BUCKLING_FACTORS_FIELD_NUMBER: _ClassVar[int]
    CURVE_L_T_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_I_FACTORS_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_METHOD_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_SIM_FACTORS_FIELD_NUMBER: _ClassVar[int]
    MB_RD_FIELD_NUMBER: _ClassVar[int]
    MCR_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    buckling_factors: BucklingFactors
    curve_l_t: CurveLT
    lateral_torsional_i_factors: LateralTorsionalIFactors
    lateral_torsional_method: _steel_pb2.LateralTorsionalMethod
    lateral_torsional_sim_factors: LateralTorsionalSimplyfied
    mb_rd: float
    mcr: Mcr
    utilization: float
    def __init__(self, lateral_torsional_method: _Optional[_Union[_steel_pb2.LateralTorsionalMethod, str]] = ..., buckling_factors: _Optional[_Union[BucklingFactors, _Mapping]] = ..., mb_rd: _Optional[float] = ..., mcr: _Optional[_Union[Mcr, _Mapping]] = ..., lateral_torsional_i_factors: _Optional[_Union[LateralTorsionalIFactors, _Mapping]] = ..., lateral_torsional_sim_factors: _Optional[_Union[LateralTorsionalSimplyfied, _Mapping]] = ..., curve_l_t: _Optional[_Union[CurveLT, str]] = ..., utilization: _Optional[float] = ...) -> None: ...

class LateralTorsionalIFactors(_message.Message):
    __slots__ = ["chi_l_t_mod", "factorf", "kc"]
    CHI_L_T_MOD_FIELD_NUMBER: _ClassVar[int]
    FACTORF_FIELD_NUMBER: _ClassVar[int]
    KC_FIELD_NUMBER: _ClassVar[int]
    chi_l_t_mod: float
    factorf: float
    kc: float
    def __init__(self, chi_l_t_mod: _Optional[float] = ..., kc: _Optional[float] = ..., factorf: _Optional[float] = ...) -> None: ...

class LateralTorsionalSimplyfied(_message.Message):
    __slots__ = ["ifz", "kc", "lambda_f", "mycrd"]
    IFZ_FIELD_NUMBER: _ClassVar[int]
    KC_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_F_FIELD_NUMBER: _ClassVar[int]
    MYCRD_FIELD_NUMBER: _ClassVar[int]
    ifz: float
    kc: float
    lambda_f: float
    mycrd: float
    def __init__(self, kc: _Optional[float] = ..., ifz: _Optional[float] = ..., lambda_f: _Optional[float] = ..., mycrd: _Optional[float] = ...) -> None: ...

class MaterialFireParameters(_message.Message):
    __slots__ = ["k_e", "kp02_theta", "kp_theta", "ky_theta"]
    KP02_THETA_FIELD_NUMBER: _ClassVar[int]
    KP_THETA_FIELD_NUMBER: _ClassVar[int]
    KY_THETA_FIELD_NUMBER: _ClassVar[int]
    K_E_FIELD_NUMBER: _ClassVar[int]
    k_e: float
    kp02_theta: float
    kp_theta: float
    ky_theta: float
    def __init__(self, ky_theta: _Optional[float] = ..., kp_theta: _Optional[float] = ..., kp02_theta: _Optional[float] = ..., k_e: _Optional[float] = ...) -> None: ...

class MaterialParameters(_message.Message):
    __slots__ = ["epsilon", "epsilon_fi", "lambda1", "material_steel"]
    EPSILON_FIELD_NUMBER: _ClassVar[int]
    EPSILON_FI_FIELD_NUMBER: _ClassVar[int]
    LAMBDA1_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_STEEL_FIELD_NUMBER: _ClassVar[int]
    epsilon: float
    epsilon_fi: float
    lambda1: float
    material_steel: CharacteristicValues
    def __init__(self, material_steel: _Optional[_Union[CharacteristicValues, _Mapping]] = ..., lambda1: _Optional[float] = ..., epsilon: _Optional[float] = ..., epsilon_fi: _Optional[float] = ...) -> None: ...

class Mcr(_message.Message):
    __slots__ = ["c1", "c2", "c2zg_c3zj", "c3", "kw", "kz", "load_pos", "mcr", "psi", "psi_f", "zg", "zj"]
    C1_FIELD_NUMBER: _ClassVar[int]
    C2ZG_C3ZJ_FIELD_NUMBER: _ClassVar[int]
    C2_FIELD_NUMBER: _ClassVar[int]
    C3_FIELD_NUMBER: _ClassVar[int]
    KW_FIELD_NUMBER: _ClassVar[int]
    KZ_FIELD_NUMBER: _ClassVar[int]
    LOAD_POS_FIELD_NUMBER: _ClassVar[int]
    MCR_FIELD_NUMBER: _ClassVar[int]
    PSI_FIELD_NUMBER: _ClassVar[int]
    PSI_F_FIELD_NUMBER: _ClassVar[int]
    ZG_FIELD_NUMBER: _ClassVar[int]
    ZJ_FIELD_NUMBER: _ClassVar[int]
    c1: float
    c2: float
    c2zg_c3zj: float
    c3: float
    kw: float
    kz: float
    load_pos: _beam_pb2.Alignment
    mcr: float
    psi: float
    psi_f: float
    zg: float
    zj: float
    def __init__(self, psi: _Optional[float] = ..., psi_f: _Optional[float] = ..., c1: _Optional[float] = ..., c2: _Optional[float] = ..., c3: _Optional[float] = ..., kz: _Optional[float] = ..., kw: _Optional[float] = ..., load_pos: _Optional[_Union[_beam_pb2.Alignment, str]] = ..., zg: _Optional[float] = ..., zj: _Optional[float] = ..., c2zg_c3zj: _Optional[float] = ..., mcr: _Optional[float] = ...) -> None: ...

class MemberTemperatureProtected(_message.Message):
    __slots__ = ["ap", "ap_v", "deltap", "fire_protection_guid", "graph_member_temp", "temp_member"]
    AP_FIELD_NUMBER: _ClassVar[int]
    AP_V_FIELD_NUMBER: _ClassVar[int]
    DELTAP_FIELD_NUMBER: _ClassVar[int]
    FIRE_PROTECTION_GUID_FIELD_NUMBER: _ClassVar[int]
    GRAPH_MEMBER_TEMP_FIELD_NUMBER: _ClassVar[int]
    TEMP_MEMBER_FIELD_NUMBER: _ClassVar[int]
    ap: float
    ap_v: float
    deltap: float
    fire_protection_guid: str
    graph_member_temp: TVPointW
    temp_member: float
    def __init__(self, deltap: _Optional[float] = ..., fire_protection_guid: _Optional[str] = ..., ap: _Optional[float] = ..., ap_v: _Optional[float] = ..., graph_member_temp: _Optional[_Union[TVPointW, _Mapping]] = ..., temp_member: _Optional[float] = ...) -> None: ...

class MemberTemperatureUnprotected(_message.Message):
    __slots__ = ["alphac", "am", "am_v", "am_vb", "amb", "deflection_crit_essential", "deltat", "epsf", "epsm", "ksh", "phi", "rhoa", "section_convex", "section_i", "v"]
    ALPHAC_FIELD_NUMBER: _ClassVar[int]
    AMB_FIELD_NUMBER: _ClassVar[int]
    AM_FIELD_NUMBER: _ClassVar[int]
    AM_VB_FIELD_NUMBER: _ClassVar[int]
    AM_V_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CRIT_ESSENTIAL_FIELD_NUMBER: _ClassVar[int]
    DELTAT_FIELD_NUMBER: _ClassVar[int]
    EPSF_FIELD_NUMBER: _ClassVar[int]
    EPSM_FIELD_NUMBER: _ClassVar[int]
    KSH_FIELD_NUMBER: _ClassVar[int]
    PHI_FIELD_NUMBER: _ClassVar[int]
    RHOA_FIELD_NUMBER: _ClassVar[int]
    SECTION_CONVEX_FIELD_NUMBER: _ClassVar[int]
    SECTION_I_FIELD_NUMBER: _ClassVar[int]
    V_FIELD_NUMBER: _ClassVar[int]
    alphac: float
    am: float
    am_v: float
    am_vb: float
    amb: float
    deflection_crit_essential: bool
    deltat: float
    epsf: float
    epsm: float
    ksh: float
    phi: float
    rhoa: float
    section_convex: bool
    section_i: bool
    v: float
    def __init__(self, ksh: _Optional[float] = ..., am: _Optional[float] = ..., v: _Optional[float] = ..., am_v: _Optional[float] = ..., amb: _Optional[float] = ..., am_vb: _Optional[float] = ..., deltat: _Optional[float] = ..., rhoa: _Optional[float] = ..., section_i: bool = ..., section_convex: bool = ..., epsm: _Optional[float] = ..., epsf: _Optional[float] = ..., alphac: _Optional[float] = ..., phi: _Optional[float] = ..., deflection_crit_essential: bool = ...) -> None: ...

class NormalCapacity(_message.Message):
    __slots__ = ["alfa", "beta", "m_n_rd_reduced", "mn_v_rd", "n", "n_ed_lim", "npl_v_rd", "nwpl_v_rd", "utilization", "with641"]
    ALFA_FIELD_NUMBER: _ClassVar[int]
    BETA_FIELD_NUMBER: _ClassVar[int]
    MN_V_RD_FIELD_NUMBER: _ClassVar[int]
    M_N_RD_REDUCED_FIELD_NUMBER: _ClassVar[int]
    NPL_V_RD_FIELD_NUMBER: _ClassVar[int]
    NWPL_V_RD_FIELD_NUMBER: _ClassVar[int]
    N_ED_LIM_FIELD_NUMBER: _ClassVar[int]
    N_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    WITH641_FIELD_NUMBER: _ClassVar[int]
    alfa: float
    beta: float
    m_n_rd_reduced: Boolean2D
    mn_v_rd: _geometry_pb2_1_1.Vector2D
    n: float
    n_ed_lim: _geometry_pb2_1_1.Vector2D
    npl_v_rd: float
    nwpl_v_rd: float
    utilization: float
    with641: bool
    def __init__(self, with641: bool = ..., npl_v_rd: _Optional[float] = ..., nwpl_v_rd: _Optional[float] = ..., n: _Optional[float] = ..., n_ed_lim: _Optional[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]] = ..., mn_v_rd: _Optional[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]] = ..., alfa: _Optional[float] = ..., beta: _Optional[float] = ..., m_n_rd_reduced: _Optional[_Union[Boolean2D, _Mapping]] = ..., utilization: _Optional[float] = ...) -> None: ...

class NormalStress(_message.Message):
    __slots__ = ["sigma_ed", "utilization"]
    SIGMA_ED_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    sigma_ed: float
    utilization: float
    def __init__(self, sigma_ed: _Optional[float] = ..., utilization: _Optional[float] = ...) -> None: ...

class Parametric(_message.Message):
    __slots__ = ["parametric_b", "parametric_fuel_controlled", "parametric_gamma", "parametric_gamma_lim", "parametric_k", "parametric_o", "parametric_olim", "parametric_qtd", "parametric_theta_max", "parametric_tlim", "parametric_tmax_a7", "parametric_tmax_asterisk", "parametric_txmax_a12", "parametric_x"]
    PARAMETRIC_B_FIELD_NUMBER: _ClassVar[int]
    PARAMETRIC_FUEL_CONTROLLED_FIELD_NUMBER: _ClassVar[int]
    PARAMETRIC_GAMMA_FIELD_NUMBER: _ClassVar[int]
    PARAMETRIC_GAMMA_LIM_FIELD_NUMBER: _ClassVar[int]
    PARAMETRIC_K_FIELD_NUMBER: _ClassVar[int]
    PARAMETRIC_OLIM_FIELD_NUMBER: _ClassVar[int]
    PARAMETRIC_O_FIELD_NUMBER: _ClassVar[int]
    PARAMETRIC_QTD_FIELD_NUMBER: _ClassVar[int]
    PARAMETRIC_THETA_MAX_FIELD_NUMBER: _ClassVar[int]
    PARAMETRIC_TLIM_FIELD_NUMBER: _ClassVar[int]
    PARAMETRIC_TMAX_A7_FIELD_NUMBER: _ClassVar[int]
    PARAMETRIC_TMAX_ASTERISK_FIELD_NUMBER: _ClassVar[int]
    PARAMETRIC_TXMAX_A12_FIELD_NUMBER: _ClassVar[int]
    PARAMETRIC_X_FIELD_NUMBER: _ClassVar[int]
    parametric_b: float
    parametric_fuel_controlled: bool
    parametric_gamma: float
    parametric_gamma_lim: float
    parametric_k: float
    parametric_o: float
    parametric_olim: float
    parametric_qtd: float
    parametric_theta_max: float
    parametric_tlim: float
    parametric_tmax_a7: float
    parametric_tmax_asterisk: float
    parametric_txmax_a12: float
    parametric_x: float
    def __init__(self, parametric_o: _Optional[float] = ..., parametric_b: _Optional[float] = ..., parametric_qtd: _Optional[float] = ..., parametric_tlim: _Optional[float] = ..., parametric_gamma: _Optional[float] = ..., parametric_tmax_a7: _Optional[float] = ..., parametric_fuel_controlled: bool = ..., parametric_tmax_asterisk: _Optional[float] = ..., parametric_theta_max: _Optional[float] = ..., parametric_olim: _Optional[float] = ..., parametric_gamma_lim: _Optional[float] = ..., parametric_k: _Optional[float] = ..., parametric_txmax_a12: _Optional[float] = ..., parametric_x: _Optional[float] = ...) -> None: ...

class PureNormalResistance(_message.Message):
    __slots__ = ["n_pl_v_rd", "utilization"]
    N_PL_V_RD_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    n_pl_v_rd: float
    utilization: float
    def __init__(self, n_pl_v_rd: _Optional[float] = ..., utilization: _Optional[float] = ...) -> None: ...

class SectionClass(_message.Message):
    __slots__ = ["s_class_gen_m1", "s_class_gen_m2", "s_class_gen_max", "s_class_gen_n"]
    S_CLASS_GEN_M1_FIELD_NUMBER: _ClassVar[int]
    S_CLASS_GEN_M2_FIELD_NUMBER: _ClassVar[int]
    S_CLASS_GEN_MAX_FIELD_NUMBER: _ClassVar[int]
    S_CLASS_GEN_N_FIELD_NUMBER: _ClassVar[int]
    s_class_gen_m1: int
    s_class_gen_m2: int
    s_class_gen_max: int
    s_class_gen_n: int
    def __init__(self, s_class_gen_n: _Optional[int] = ..., s_class_gen_m1: _Optional[int] = ..., s_class_gen_m2: _Optional[int] = ..., s_class_gen_max: _Optional[int] = ...) -> None: ...

class SectionGeometry(_message.Message):
    __slots__ = ["a_f", "bf", "c", "hw", "t", "tf"]
    A_F_FIELD_NUMBER: _ClassVar[int]
    BF_FIELD_NUMBER: _ClassVar[int]
    C_FIELD_NUMBER: _ClassVar[int]
    HW_FIELD_NUMBER: _ClassVar[int]
    TF_FIELD_NUMBER: _ClassVar[int]
    T_FIELD_NUMBER: _ClassVar[int]
    a_f: _geometry_pb2_1_1.Vector2D
    bf: float
    c: float
    hw: float
    t: float
    tf: float
    def __init__(self, hw: _Optional[float] = ..., t: _Optional[float] = ..., a_f: _Optional[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]] = ..., tf: _Optional[float] = ..., bf: _Optional[float] = ..., c: _Optional[float] = ...) -> None: ...

class SectionParameters(_message.Message):
    __slots__ = ["a", "i0", "iy", "iz", "section_units", "y0", "z0"]
    A_FIELD_NUMBER: _ClassVar[int]
    I0_FIELD_NUMBER: _ClassVar[int]
    IY_FIELD_NUMBER: _ClassVar[int]
    IZ_FIELD_NUMBER: _ClassVar[int]
    SECTION_UNITS_FIELD_NUMBER: _ClassVar[int]
    Y0_FIELD_NUMBER: _ClassVar[int]
    Z0_FIELD_NUMBER: _ClassVar[int]
    a: _geometry_pb2_1_1.Vector2D
    i0: float
    iy: float
    iz: float
    section_units: _sections_pb2.SectionUnits
    y0: float
    z0: float
    def __init__(self, section_units: _Optional[_Union[_sections_pb2.SectionUnits, _Mapping]] = ..., iy: _Optional[float] = ..., iz: _Optional[float] = ..., y0: _Optional[float] = ..., z0: _Optional[float] = ..., i0: _Optional[float] = ..., a: _Optional[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]] = ...) -> None: ...

class SectionResult(_message.Message):
    __slots__ = ["control_data", "effective_class_four", "flexural1", "flexural2", "flexural_torsional", "interaction1", "interaction2", "interaction2nd", "lateral_torsional_bottom", "lateral_torsional_top", "normal", "normal_stress", "pure_normal_resistance", "shear1", "shear2", "shear_stress", "torsional", "web"]
    CONTROL_DATA_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_CLASS_FOUR_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL1_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL2_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_TORSIONAL_FIELD_NUMBER: _ClassVar[int]
    INTERACTION1_FIELD_NUMBER: _ClassVar[int]
    INTERACTION2ND_FIELD_NUMBER: _ClassVar[int]
    INTERACTION2_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_TOP_FIELD_NUMBER: _ClassVar[int]
    NORMAL_FIELD_NUMBER: _ClassVar[int]
    NORMAL_STRESS_FIELD_NUMBER: _ClassVar[int]
    PURE_NORMAL_RESISTANCE_FIELD_NUMBER: _ClassVar[int]
    SHEAR1_FIELD_NUMBER: _ClassVar[int]
    SHEAR2_FIELD_NUMBER: _ClassVar[int]
    SHEAR_STRESS_FIELD_NUMBER: _ClassVar[int]
    TORSIONAL_FIELD_NUMBER: _ClassVar[int]
    WEB_FIELD_NUMBER: _ClassVar[int]
    control_data: _containers.RepeatedCompositeFieldContainer[_control_pb2.ControlData]
    effective_class_four: EffectiveClassFour
    flexural1: Flexural
    flexural2: Flexural
    flexural_torsional: FlexuralTorsional
    interaction1: Interaction
    interaction2: Interaction
    interaction2nd: Interaction2nd
    lateral_torsional_bottom: LateralTorsional
    lateral_torsional_top: LateralTorsional
    normal: NormalCapacity
    normal_stress: NormalStress
    pure_normal_resistance: PureNormalResistance
    shear1: ShearResistance
    shear2: ShearResistance
    shear_stress: ShearStress
    torsional: TorsionalResistance
    web: Web
    def __init__(self, effective_class_four: _Optional[_Union[EffectiveClassFour, _Mapping]] = ..., shear1: _Optional[_Union[ShearResistance, _Mapping]] = ..., shear2: _Optional[_Union[ShearResistance, _Mapping]] = ..., torsional: _Optional[_Union[TorsionalResistance, _Mapping]] = ..., shear_stress: _Optional[_Union[ShearStress, _Mapping]] = ..., normal_stress: _Optional[_Union[NormalStress, _Mapping]] = ..., pure_normal_resistance: _Optional[_Union[PureNormalResistance, _Mapping]] = ..., normal: _Optional[_Union[NormalCapacity, _Mapping]] = ..., flexural1: _Optional[_Union[Flexural, _Mapping]] = ..., flexural2: _Optional[_Union[Flexural, _Mapping]] = ..., flexural_torsional: _Optional[_Union[FlexuralTorsional, _Mapping]] = ..., lateral_torsional_top: _Optional[_Union[LateralTorsional, _Mapping]] = ..., lateral_torsional_bottom: _Optional[_Union[LateralTorsional, _Mapping]] = ..., interaction1: _Optional[_Union[Interaction, _Mapping]] = ..., interaction2: _Optional[_Union[Interaction, _Mapping]] = ..., interaction2nd: _Optional[_Union[Interaction2nd, _Mapping]] = ..., web: _Optional[_Union[Web, _Mapping]] = ..., control_data: _Optional[_Iterable[_Union[_control_pb2.ControlData, _Mapping]]] = ...) -> None: ...

class ShearResistance(_message.Message):
    __slots__ = ["a_v", "rho", "utilization", "v_pl_rd", "v_pl_rd_fi", "v_pl_t_rd", "v_pl_t_rd_fi"]
    A_V_FIELD_NUMBER: _ClassVar[int]
    RHO_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    V_PL_RD_FIELD_NUMBER: _ClassVar[int]
    V_PL_RD_FI_FIELD_NUMBER: _ClassVar[int]
    V_PL_T_RD_FIELD_NUMBER: _ClassVar[int]
    V_PL_T_RD_FI_FIELD_NUMBER: _ClassVar[int]
    a_v: float
    rho: float
    utilization: float
    v_pl_rd: float
    v_pl_rd_fi: float
    v_pl_t_rd: float
    v_pl_t_rd_fi: float
    def __init__(self, v_pl_t_rd: _Optional[float] = ..., v_pl_t_rd_fi: _Optional[float] = ..., v_pl_rd: _Optional[float] = ..., v_pl_rd_fi: _Optional[float] = ..., a_v: _Optional[float] = ..., rho: _Optional[float] = ..., utilization: _Optional[float] = ...) -> None: ...

class ShearStress(_message.Message):
    __slots__ = ["tau_ed", "tau_rd", "tau_rd_fi", "utilization"]
    TAU_ED_FIELD_NUMBER: _ClassVar[int]
    TAU_RD_FIELD_NUMBER: _ClassVar[int]
    TAU_RD_FI_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    tau_ed: float
    tau_rd: float
    tau_rd_fi: float
    utilization: float
    def __init__(self, tau_ed: _Optional[float] = ..., tau_rd: _Optional[float] = ..., tau_rd_fi: _Optional[float] = ..., utilization: _Optional[float] = ...) -> None: ...

class SteelDesignNationalAnnexValues(_message.Message):
    __slots__ = ["beta", "etawb", "kfl", "lambda_l_t0"]
    BETA_FIELD_NUMBER: _ClassVar[int]
    ETAWB_FIELD_NUMBER: _ClassVar[int]
    KFL_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_L_T0_FIELD_NUMBER: _ClassVar[int]
    beta: float
    etawb: float
    kfl: float
    lambda_l_t0: float
    def __init__(self, kfl: _Optional[float] = ..., etawb: _Optional[float] = ..., lambda_l_t0: _Optional[float] = ..., beta: _Optional[float] = ...) -> None: ...

class TVPointW(_message.Message):
    __slots__ = ["coordinates", "number_of_points"]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_POINTS_FIELD_NUMBER: _ClassVar[int]
    coordinates: _containers.RepeatedCompositeFieldContainer[_geometry_pb2_1_1.Vector2D]
    number_of_points: int
    def __init__(self, number_of_points: _Optional[int] = ..., coordinates: _Optional[_Iterable[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]]] = ...) -> None: ...

class TorsionalResistance(_message.Message):
    __slots__ = ["t_rd", "t_rd_fi", "tau_t_ed", "utilization"]
    TAU_T_ED_FIELD_NUMBER: _ClassVar[int]
    T_RD_FIELD_NUMBER: _ClassVar[int]
    T_RD_FI_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    t_rd: float
    t_rd_fi: float
    tau_t_ed: float
    utilization: float
    def __init__(self, t_rd: _Optional[float] = ..., t_rd_fi: _Optional[float] = ..., tau_t_ed: _Optional[float] = ..., utilization: _Optional[float] = ...) -> None: ...

class VirtualStiffeners(_message.Message):
    __slots__ = ["end", "start"]
    END_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    end: bool
    start: bool
    def __init__(self, start: bool = ..., end: bool = ...) -> None: ...

class Web(_message.Message):
    __slots__ = ["a", "capacity", "factors", "geometry", "relevant", "utilization"]
    A_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    FACTORS_FIELD_NUMBER: _ClassVar[int]
    GEOMETRY_FIELD_NUMBER: _ClassVar[int]
    RELEVANT_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    a: float
    capacity: WebCapacities
    factors: WebFactors
    geometry: SectionGeometry
    relevant: StBarWebRelevant
    utilization: float
    def __init__(self, capacity: _Optional[_Union[WebCapacities, _Mapping]] = ..., factors: _Optional[_Union[WebFactors, _Mapping]] = ..., geometry: _Optional[_Union[SectionGeometry, _Mapping]] = ..., relevant: _Optional[_Union[StBarWebRelevant, str]] = ..., a: _Optional[float] = ..., utilization: _Optional[float] = ...) -> None: ...

class WebCapacities(_message.Message):
    __slots__ = ["mf_rd", "mfk", "v_b_rd", "v_bf_rd", "v_bw_rd", "v_bw_rd_fi"]
    MFK_FIELD_NUMBER: _ClassVar[int]
    MF_RD_FIELD_NUMBER: _ClassVar[int]
    V_BF_RD_FIELD_NUMBER: _ClassVar[int]
    V_BW_RD_FIELD_NUMBER: _ClassVar[int]
    V_BW_RD_FI_FIELD_NUMBER: _ClassVar[int]
    V_B_RD_FIELD_NUMBER: _ClassVar[int]
    mf_rd: float
    mfk: float
    v_b_rd: float
    v_bf_rd: float
    v_bw_rd: float
    v_bw_rd_fi: float
    def __init__(self, v_bw_rd: _Optional[float] = ..., v_bw_rd_fi: _Optional[float] = ..., v_bf_rd: _Optional[float] = ..., v_b_rd: _Optional[float] = ..., mf_rd: _Optional[float] = ..., mfk: _Optional[float] = ...) -> None: ...

class WebFactors(_message.Message):
    __slots__ = ["chi", "k_tau", "lambda_w", "sigma_e"]
    CHI_FIELD_NUMBER: _ClassVar[int]
    K_TAU_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_W_FIELD_NUMBER: _ClassVar[int]
    SIGMA_E_FIELD_NUMBER: _ClassVar[int]
    chi: float
    k_tau: float
    lambda_w: float
    sigma_e: float
    def __init__(self, k_tau: _Optional[float] = ..., sigma_e: _Optional[float] = ..., lambda_w: _Optional[float] = ..., chi: _Optional[float] = ...) -> None: ...

class BarSectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Curve(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class CurveLT(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ShearResistanceEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class StBarWebRelevant(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ShearStressCheckRelevant(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
