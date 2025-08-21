import element_pb2 as _element_pb2
from Utils import utils_pb2 as _utils_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Geometry import beam_pb2 as _beam_pb2
from Geometry import foundation_pb2 as _foundation_pb2
from Geometry import retainingwall_pb2 as _retainingwall_pb2
from Geometry import pile_pb2 as _pile_pb2
from Design import design_pb2 as _design_pb2
from Design import steel_pb2 as _steel_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Geometry import geometry_pb2 as _geometry_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1
from Result import steel_pb2 as _steel_pb2_1
from Geometry import beam_pb2 as _beam_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1_1
from Design import steel_pb2 as _steel_pb2_1_1
from Design import general_pb2 as _general_pb2
import sections_pb2 as _sections_pb2
from Geometry import geometry_pb2 as _geometry_pb2_1_1
from Material import steel_pb2 as _steel_pb2_1_1_1
from Result import control_pb2 as _control_pb2
from Result import control_pb2 as _control_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from element_pb2 import Data
from element_pb2 import InspectionLevel
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
from Result.control_pb2 import ControlTypeFoundation
from Result.control_pb2 import ControlData
from Result.control_pb2 import ControlTypeConcrete
from Result.control_pb2 import ControlTypeSteel
from Result.control_pb2 import ControlTypeTimber
from Result.control_pb2 import CtrlTypeFoundation
from Result.control_pb2 import AnalysisTypeFoundation
from Result.control_pb2 import DesignTypeFoundation
from Result.control_pb2 import EccentricityTypeFoundation
ANALYSIS_TYPE_NORMAL: _control_pb2_1.AnalysisTypeFoundation
ANALYSIS_TYPE_SOIL_PUNCHING: _control_pb2_1.AnalysisTypeFoundation
ANALYSIS_TYPE_UNSPECIFIED: _control_pb2_1.AnalysisTypeFoundation
BAR_SECTION_TYPE_UNIFORM: _steel_pb2_1.BarSectionType
BAR_SECTION_TYPE_UNSPECIFIED: _steel_pb2_1.BarSectionType
BAR_SECTION_TYPE_VARIABLE: _steel_pb2_1.BarSectionType
BUCKLING_CURVE_FLEXURAL_A: _steel_pb2_1_1.BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_A0: _steel_pb2_1_1.BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_AUTO: _steel_pb2_1_1.BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_B: _steel_pb2_1_1.BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_C: _steel_pb2_1_1.BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_D: _steel_pb2_1_1.BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_UNSPECIFIED: _steel_pb2_1_1.BucklingCurveFlexural
BUCKLING_CURVE_LATERAL_A: _steel_pb2_1_1.BucklingCurveLateral
BUCKLING_CURVE_LATERAL_AUTO: _steel_pb2_1_1.BucklingCurveLateral
BUCKLING_CURVE_LATERAL_B: _steel_pb2_1_1.BucklingCurveLateral
BUCKLING_CURVE_LATERAL_C: _steel_pb2_1_1.BucklingCurveLateral
BUCKLING_CURVE_LATERAL_D: _steel_pb2_1_1.BucklingCurveLateral
BUCKLING_CURVE_LATERAL_UNSPECIFIED: _steel_pb2_1_1.BucklingCurveLateral
CONTROL_TYPE_CONCRETE_ANCHORAGE_BTM: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_ANCHORAGE_TOP: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_AXIAL_FORCE: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_BIAXIAL_MOMENT: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_COMPRESSION_COVER_CHECK: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_COMPRESSION_STRESS: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_DEFLECTION: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_HOLLOWCORE_SPALLING: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_INITIAL_PRESTRESS: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_MOMENT_M2: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_NEGATIVE_CRACK_WIDTH: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_NEGATIVE_MOMENT_M1: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_POSITIVE_CRACK_WIDTH: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_POSITIVE_MOMENT_M1: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_PUNCHING_COLUMN: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_PUNCHING_PERIMETER: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_FORCE: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_FORCE_TOPPING: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_STIRRUPS: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_STIRRUPS_TOPPING: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_STRESS_AFTER_RELEASE: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TOPPING_JOINT: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_COMPRESSION_LONGITUDINAL: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_COMPRESSION_TRANSVERSE: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_LONGITUDINAL: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_TENSION_TRANSVERSE: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_TRANSVERSE: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_CONCRETE_UNSPECIFIED: _control_pb2_1.ControlTypeConcrete
CONTROL_TYPE_FOUNDATION_BEARING: _control_pb2_1.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_OVERALL: _control_pb2_1.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_OVERTURNING: _control_pb2_1.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_SETTLEMENT: _control_pb2_1.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_SLIDING: _control_pb2_1.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_UNREINFORCED: _control_pb2_1.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_UNSPECIFIED: _control_pb2_1.CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_UPLIFT: _control_pb2_1.CtrlTypeFoundation
CONTROL_TYPE_STEEL_DEFLECTION: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_FB1: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_FB2: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_FTB: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_IA1: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_IA2: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_IA2ND: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_LTB_BOTTOM: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_LTB_TOP: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_M1: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_M1_FIRE: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_M2: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_M2_FIRE: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_N: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_NORMAL: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_N_FIRE: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_OVERALL: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_PURE_NORMAL: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_SIGMA: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_T: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_TAU: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_UNSPECIFIED: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_V1: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_V2: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_STEEL_WEB: _control_pb2_1.ControlTypeSteel
CONTROL_TYPE_TIMBER_APEX: _control_pb2_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_COMPRESSION: _control_pb2_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_DEFLECTION: _control_pb2_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_FLEXURAL_BUCKLING1: _control_pb2_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_FLEXURAL_BUCKLING2: _control_pb2_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_OVERALL: _control_pb2_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_SHEAR: _control_pb2_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_TENSION: _control_pb2_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_TORSIONAL_BUCKLING: _control_pb2_1.ControlTypeTimber
CONTROL_TYPE_TIMBER_UNSPECIFIED: _control_pb2_1.ControlTypeTimber
CURVE_A: _steel_pb2_1.Curve
CURVE_A0: _steel_pb2_1.Curve
CURVE_B: _steel_pb2_1.Curve
CURVE_C: _steel_pb2_1.Curve
CURVE_D: _steel_pb2_1.Curve
CURVE_LT_UNSPECIFIED: _steel_pb2_1.CurveLT
CURVE_L_T_A: _steel_pb2_1.CurveLT
CURVE_L_T_B: _steel_pb2_1.CurveLT
CURVE_L_T_C: _steel_pb2_1.CurveLT
CURVE_L_T_D: _steel_pb2_1.CurveLT
CURVE_UNSPECIFIED: _steel_pb2_1.Curve
DESCRIPTOR: _descriptor.FileDescriptor
DESIGN_TYPE_ALLOWEDSOILPRESSURE: _control_pb2_1.DesignTypeFoundation
DESIGN_TYPE_DRAINED: _control_pb2_1.DesignTypeFoundation
DESIGN_TYPE_DRAINED_PUNCHNING_ALT: _control_pb2_1.DesignTypeFoundation
DESIGN_TYPE_DRAINED_PUNCHNING_B6: _control_pb2_1.DesignTypeFoundation
DESIGN_TYPE_ROCK: _control_pb2_1.DesignTypeFoundation
DESIGN_TYPE_UNDRAINED: _control_pb2_1.DesignTypeFoundation
DESIGN_TYPE_UNDRAINED_PUNCHING: _control_pb2_1.DesignTypeFoundation
DESIGN_TYPE_UNSPECIFIED: _control_pb2_1.DesignTypeFoundation
ECCENTRICITY_TYPE_HIGH: _control_pb2_1.EccentricityTypeFoundation
ECCENTRICITY_TYPE_NORMAL: _control_pb2_1.EccentricityTypeFoundation
ECCENTRICITY_TYPE_UNSPECIFIED: _control_pb2_1.EccentricityTypeFoundation
INSPECTION_LEVEL_NORMAL: _element_pb2.InspectionLevel
INSPECTION_LEVEL_RELAXED: _element_pb2.InspectionLevel
INSPECTION_LEVEL_TIGHTENED: _element_pb2.InspectionLevel
INSPECTION_LEVEL_UNSPECIFIED: _element_pb2.InspectionLevel
INTERACTION_METHOD_METHOD1: _steel_pb2_1_1.InteractionMethod
INTERACTION_METHOD_METHOD2: _steel_pb2_1_1.InteractionMethod
INTERACTION_METHOD_UNSPECIFIED: _steel_pb2_1_1.InteractionMethod
LATERAL_TORSIONAL_METHOD_GENERAL: _steel_pb2_1_1.LateralTorsionalMethod
LATERAL_TORSIONAL_METHOD_GENERAL_SPEC_FOR_I: _steel_pb2_1_1.LateralTorsionalMethod
LATERAL_TORSIONAL_METHOD_SIMPLIFIED: _steel_pb2_1_1.LateralTorsionalMethod
LATERAL_TORSIONAL_METHOD_UNSPECIFIED: _steel_pb2_1_1.LateralTorsionalMethod
SECOND_ORDER_ANALYSIS_CONSIDER: _steel_pb2_1_1.SecondOrderAnalysis
SECOND_ORDER_ANALYSIS_FIRST_ORDER_DESIGN: _steel_pb2_1_1.SecondOrderAnalysis
SECOND_ORDER_ANALYSIS_IGNORE: _steel_pb2_1_1.SecondOrderAnalysis
SECOND_ORDER_ANALYSIS_UNSPECIFIED: _steel_pb2_1_1.SecondOrderAnalysis
SECTION_EXPOSURE_ALL_SIDES: _steel_pb2_1_1.SectionExposure
SECTION_EXPOSURE_FLANGE_ONLY: _steel_pb2_1_1.SectionExposure
SECTION_EXPOSURE_THREE_SIDES: _steel_pb2_1_1.SectionExposure
SECTION_EXPOSURE_UNSPECIFIED: _steel_pb2_1_1.SectionExposure
SHEAR_RESISTANCE_HOLLOW: _steel_pb2_1.ShearResistanceEnum
SHEAR_RESISTANCE_I_LIKE: _steel_pb2_1.ShearResistanceEnum
SHEAR_RESISTANCE_NONE: _steel_pb2_1.ShearResistanceEnum
SHEAR_RESISTANCE_UNSPECIFIED: _steel_pb2_1.ShearResistanceEnum
SHEAR_RESISTANCE_U_LIKE: _steel_pb2_1.ShearResistanceEnum
SHEAR_STRESS_CHECK_RELEVANT_NO: _steel_pb2_1.ShearStressCheckRelevant
SHEAR_STRESS_CHECK_RELEVANT_NO_BECAUSE_WEB_BUCKLING: _steel_pb2_1.ShearStressCheckRelevant
SHEAR_STRESS_CHECK_RELEVANT_UNSPECIFIED: _steel_pb2_1.ShearStressCheckRelevant
SHEAR_STRESS_CHECK_RELEVANT_YES: _steel_pb2_1.ShearStressCheckRelevant
STAT_SYS_CANTILEVER: StatSys
STAT_SYS_SIMPLE_SUPPORTED: StatSys
STAT_SYS_UNSPECIFIED: StatSys
ST_BAR_WEB_RELEVANT_NO: _steel_pb2_1.StBarWebRelevant
ST_BAR_WEB_RELEVANT_NO_STIFF_LIMIT: _steel_pb2_1.StBarWebRelevant
ST_BAR_WEB_RELEVANT_NO_UNSTIFF_LIMIT: _steel_pb2_1.StBarWebRelevant
ST_BAR_WEB_RELEVANT_UNSPECIFIED: _steel_pb2_1.StBarWebRelevant
ST_BAR_WEB_RELEVANT_YES: _steel_pb2_1.StBarWebRelevant

class Apex(_message.Message):
    __slots__ = ["f_relevant_bending", "f_relevant_tension", "m_ap", "sigmamd", "sigmat90d", "utilization"]
    F_RELEVANT_BENDING_FIELD_NUMBER: _ClassVar[int]
    F_RELEVANT_TENSION_FIELD_NUMBER: _ClassVar[int]
    M_AP_FIELD_NUMBER: _ClassVar[int]
    SIGMAMD_FIELD_NUMBER: _ClassVar[int]
    SIGMAT90D_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    f_relevant_bending: bool
    f_relevant_tension: bool
    m_ap: float
    sigmamd: float
    sigmat90d: float
    utilization: _geometry_pb2_1_1.Vector2D
    def __init__(self, f_relevant_bending: bool = ..., f_relevant_tension: bool = ..., m_ap: _Optional[float] = ..., sigmamd: _Optional[float] = ..., sigmat90d: _Optional[float] = ..., utilization: _Optional[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]] = ...) -> None: ...

class ApexParameters(_message.Message):
    __slots__ = ["alpha_ap", "b", "h_ap", "k", "kdis", "kl", "kp", "kr", "kvol", "positive_moment_causes_tension", "r", "r_in", "volume_ap"]
    ALPHA_AP_FIELD_NUMBER: _ClassVar[int]
    B_FIELD_NUMBER: _ClassVar[int]
    H_AP_FIELD_NUMBER: _ClassVar[int]
    KDIS_FIELD_NUMBER: _ClassVar[int]
    KL_FIELD_NUMBER: _ClassVar[int]
    KP_FIELD_NUMBER: _ClassVar[int]
    KR_FIELD_NUMBER: _ClassVar[int]
    KVOL_FIELD_NUMBER: _ClassVar[int]
    K_FIELD_NUMBER: _ClassVar[int]
    POSITIVE_MOMENT_CAUSES_TENSION_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    R_IN_FIELD_NUMBER: _ClassVar[int]
    VOLUME_AP_FIELD_NUMBER: _ClassVar[int]
    alpha_ap: float
    b: float
    h_ap: float
    k: _containers.RepeatedScalarFieldContainer[float]
    kdis: float
    kl: float
    kp: float
    kr: float
    kvol: float
    positive_moment_causes_tension: bool
    r: float
    r_in: float
    volume_ap: float
    def __init__(self, positive_moment_causes_tension: bool = ..., alpha_ap: _Optional[float] = ..., h_ap: _Optional[float] = ..., b: _Optional[float] = ..., kr: _Optional[float] = ..., kl: _Optional[float] = ..., kdis: _Optional[float] = ..., kvol: _Optional[float] = ..., kp: _Optional[float] = ..., k: _Optional[_Iterable[float]] = ..., volume_ap: _Optional[float] = ..., r_in: _Optional[float] = ..., r: _Optional[float] = ...) -> None: ...

class Compression(_message.Message):
    __slots__ = ["utilization_my", "utilization_mz", "utilization_n"]
    UTILIZATION_MY_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_MZ_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_N_FIELD_NUMBER: _ClassVar[int]
    utilization_my: float
    utilization_mz: float
    utilization_n: float
    def __init__(self, utilization_n: _Optional[float] = ..., utilization_my: _Optional[float] = ..., utilization_mz: _Optional[float] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["section_result"]
    SECTION_RESULT_FIELD_NUMBER: _ClassVar[int]
    section_result: SectionResult
    def __init__(self, section_result: _Optional[_Union[SectionResult, _Mapping]] = ...) -> None: ...

class DesignStrength(_message.Message):
    __slots__ = ["fc0d", "fc90d", "fm1d", "fm2d", "ft0d", "ft90d", "fvd"]
    FC0D_FIELD_NUMBER: _ClassVar[int]
    FC90D_FIELD_NUMBER: _ClassVar[int]
    FM1D_FIELD_NUMBER: _ClassVar[int]
    FM2D_FIELD_NUMBER: _ClassVar[int]
    FT0D_FIELD_NUMBER: _ClassVar[int]
    FT90D_FIELD_NUMBER: _ClassVar[int]
    FVD_FIELD_NUMBER: _ClassVar[int]
    fc0d: float
    fc90d: float
    fm1d: float
    fm2d: float
    ft0d: float
    ft90d: float
    fvd: float
    def __init__(self, ft0d: _Optional[float] = ..., ft90d: _Optional[float] = ..., fc0d: _Optional[float] = ..., fc90d: _Optional[float] = ..., fm1d: _Optional[float] = ..., fm2d: _Optional[float] = ..., fvd: _Optional[float] = ...) -> None: ...

class DesignSummary(_message.Message):
    __slots__ = ["controls", "elem_guid", "extra_parameters", "extra_parameters_fire", "is_charred_section_too_small", "varying_bar"]
    CONTROLS_FIELD_NUMBER: _ClassVar[int]
    ELEM_GUID_FIELD_NUMBER: _ClassVar[int]
    EXTRA_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    EXTRA_PARAMETERS_FIRE_FIELD_NUMBER: _ClassVar[int]
    IS_CHARRED_SECTION_TOO_SMALL_FIELD_NUMBER: _ClassVar[int]
    VARYING_BAR_FIELD_NUMBER: _ClassVar[int]
    controls: _containers.RepeatedCompositeFieldContainer[_control_pb2_1.ControlData]
    elem_guid: str
    extra_parameters: _containers.RepeatedCompositeFieldContainer[ExtraParameters]
    extra_parameters_fire: _containers.RepeatedCompositeFieldContainer[ExtraParameters]
    is_charred_section_too_small: bool
    varying_bar: _steel_pb2_1.BarSectionType
    def __init__(self, elem_guid: _Optional[str] = ..., varying_bar: _Optional[_Union[_steel_pb2_1.BarSectionType, str]] = ..., is_charred_section_too_small: bool = ..., extra_parameters: _Optional[_Iterable[_Union[ExtraParameters, _Mapping]]] = ..., extra_parameters_fire: _Optional[_Iterable[_Union[ExtraParameters, _Mapping]]] = ..., controls: _Optional[_Iterable[_Union[_control_pb2_1.ControlData, _Mapping]]] = ...) -> None: ...

class Element(_message.Message):
    __slots__ = ["max_of_controls"]
    MAX_OF_CONTROLS_FIELD_NUMBER: _ClassVar[int]
    max_of_controls: _containers.RepeatedCompositeFieldContainer[_control_pb2_1.ControlData]
    def __init__(self, max_of_controls: _Optional[_Iterable[_Union[_control_pb2_1.ControlData, _Mapping]]] = ...) -> None: ...

class ExtraParameters(_message.Message):
    __slots__ = ["apex_data", "extra_materials", "extra_sections", "taper_data"]
    APEX_DATA_FIELD_NUMBER: _ClassVar[int]
    EXTRA_MATERIALS_FIELD_NUMBER: _ClassVar[int]
    EXTRA_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    TAPER_DATA_FIELD_NUMBER: _ClassVar[int]
    apex_data: ApexParameters
    extra_materials: MaterialParameters
    extra_sections: SectionParameters
    taper_data: TaperParameters
    def __init__(self, extra_sections: _Optional[_Union[SectionParameters, _Mapping]] = ..., extra_materials: _Optional[_Union[MaterialParameters, _Mapping]] = ..., taper_data: _Optional[_Union[TaperParameters, _Mapping]] = ..., apex_data: _Optional[_Union[ApexParameters, _Mapping]] = ...) -> None: ...

class FlexBucklingParameters(_message.Message):
    __slots__ = ["betac", "i0", "k", "kc", "l0", "lambda_rel", "xe", "xs"]
    BETAC_FIELD_NUMBER: _ClassVar[int]
    I0_FIELD_NUMBER: _ClassVar[int]
    KC_FIELD_NUMBER: _ClassVar[int]
    K_FIELD_NUMBER: _ClassVar[int]
    L0_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_REL_FIELD_NUMBER: _ClassVar[int]
    XE_FIELD_NUMBER: _ClassVar[int]
    XS_FIELD_NUMBER: _ClassVar[int]
    betac: float
    i0: float
    k: float
    kc: float
    l0: float
    lambda_rel: float
    xe: float
    xs: float
    def __init__(self, xs: _Optional[float] = ..., xe: _Optional[float] = ..., l0: _Optional[float] = ..., i0: _Optional[float] = ..., lambda_rel: _Optional[float] = ..., betac: _Optional[float] = ..., k: _Optional[float] = ..., kc: _Optional[float] = ..., **kwargs) -> None: ...

class FlexuralBuckling(_message.Message):
    __slots__ = ["flexural_buckling_parameters", "kc", "utilization"]
    FLEXURAL_BUCKLING_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    KC_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    flexural_buckling_parameters: FlexBucklingParameters
    kc: float
    utilization: float
    def __init__(self, kc: _Optional[float] = ..., utilization: _Optional[float] = ..., flexural_buckling_parameters: _Optional[_Union[FlexBucklingParameters, _Mapping]] = ...) -> None: ...

class MaterialParameters(_message.Message):
    __slots__ = ["fm1k", "fm2k", "ft0k", "km"]
    FM1K_FIELD_NUMBER: _ClassVar[int]
    FM2K_FIELD_NUMBER: _ClassVar[int]
    FT0K_FIELD_NUMBER: _ClassVar[int]
    KM_FIELD_NUMBER: _ClassVar[int]
    fm1k: float
    fm2k: float
    ft0k: float
    km: float
    def __init__(self, km: _Optional[float] = ..., ft0k: _Optional[float] = ..., fm1k: _Optional[float] = ..., fm2k: _Optional[float] = ...) -> None: ...

class SectionParameters(_message.Message):
    __slots__ = ["I1", "I2", "It", "a", "beta", "h", "ir1", "ir2", "w", "w1", "w2"]
    A_FIELD_NUMBER: _ClassVar[int]
    BETA_FIELD_NUMBER: _ClassVar[int]
    H_FIELD_NUMBER: _ClassVar[int]
    I1: float
    I1_FIELD_NUMBER: _ClassVar[int]
    I2: float
    I2_FIELD_NUMBER: _ClassVar[int]
    IR1_FIELD_NUMBER: _ClassVar[int]
    IR2_FIELD_NUMBER: _ClassVar[int]
    IT_FIELD_NUMBER: _ClassVar[int]
    It: float
    W1_FIELD_NUMBER: _ClassVar[int]
    W2_FIELD_NUMBER: _ClassVar[int]
    W_FIELD_NUMBER: _ClassVar[int]
    a: float
    beta: float
    h: float
    ir1: float
    ir2: float
    w: float
    w1: float
    w2: float
    def __init__(self, w: _Optional[float] = ..., h: _Optional[float] = ..., a: _Optional[float] = ..., w1: _Optional[float] = ..., w2: _Optional[float] = ..., beta: _Optional[float] = ..., ir1: _Optional[float] = ..., ir2: _Optional[float] = ..., I1: _Optional[float] = ..., I2: _Optional[float] = ..., It: _Optional[float] = ...) -> None: ...

class SectionResult(_message.Message):
    __slots__ = ["apex", "compression", "control_data", "design_strength", "flexural_buckling1", "flexural_buckling2", "kmod", "shear", "sigmad0", "sigmayd", "sigmaz0", "taper", "tension", "torsional_buckling"]
    APEX_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_FIELD_NUMBER: _ClassVar[int]
    CONTROL_DATA_FIELD_NUMBER: _ClassVar[int]
    DESIGN_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING1_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING2_FIELD_NUMBER: _ClassVar[int]
    KMOD_FIELD_NUMBER: _ClassVar[int]
    SHEAR_FIELD_NUMBER: _ClassVar[int]
    SIGMAD0_FIELD_NUMBER: _ClassVar[int]
    SIGMAYD_FIELD_NUMBER: _ClassVar[int]
    SIGMAZ0_FIELD_NUMBER: _ClassVar[int]
    TAPER_FIELD_NUMBER: _ClassVar[int]
    TENSION_FIELD_NUMBER: _ClassVar[int]
    TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
    apex: Apex
    compression: Compression
    control_data: _containers.RepeatedCompositeFieldContainer[_control_pb2_1.ControlData]
    design_strength: DesignStrength
    flexural_buckling1: FlexuralBuckling
    flexural_buckling2: FlexuralBuckling
    kmod: float
    shear: Shear
    sigmad0: float
    sigmayd: float
    sigmaz0: float
    taper: Taper
    tension: Tension
    torsional_buckling: TorsionalBuckling
    def __init__(self, tension: _Optional[_Union[Tension, _Mapping]] = ..., compression: _Optional[_Union[Compression, _Mapping]] = ..., shear: _Optional[_Union[Shear, _Mapping]] = ..., flexural_buckling1: _Optional[_Union[FlexuralBuckling, _Mapping]] = ..., flexural_buckling2: _Optional[_Union[FlexuralBuckling, _Mapping]] = ..., torsional_buckling: _Optional[_Union[TorsionalBuckling, _Mapping]] = ..., apex: _Optional[_Union[Apex, _Mapping]] = ..., taper: _Optional[_Union[Taper, _Mapping]] = ..., sigmad0: _Optional[float] = ..., sigmayd: _Optional[float] = ..., sigmaz0: _Optional[float] = ..., kmod: _Optional[float] = ..., design_strength: _Optional[_Union[DesignStrength, _Mapping]] = ..., control_data: _Optional[_Iterable[_Union[_control_pb2_1.ControlData, _Mapping]]] = ...) -> None: ...

class Shear(_message.Message):
    __slots__ = ["tau_d", "utilization"]
    TAU_D_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    tau_d: float
    utilization: float
    def __init__(self, tau_d: _Optional[float] = ..., utilization: _Optional[float] = ...) -> None: ...

class Taper(_message.Message):
    __slots__ = ["kmalpha"]
    KMALPHA_FIELD_NUMBER: _ClassVar[int]
    kmalpha: float
    def __init__(self, kmalpha: _Optional[float] = ...) -> None: ...

class TaperParameters(_message.Message):
    __slots__ = ["alpha_tap", "b", "h"]
    ALPHA_TAP_FIELD_NUMBER: _ClassVar[int]
    B_FIELD_NUMBER: _ClassVar[int]
    H_FIELD_NUMBER: _ClassVar[int]
    alpha_tap: float
    b: float
    h: float
    def __init__(self, alpha_tap: _Optional[float] = ..., h: _Optional[float] = ..., b: _Optional[float] = ...) -> None: ...

class Tension(_message.Message):
    __slots__ = ["utilization_my", "utilization_mz"]
    UTILIZATION_MY_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_MZ_FIELD_NUMBER: _ClassVar[int]
    utilization_my: float
    utilization_mz: float
    def __init__(self, utilization_my: _Optional[float] = ..., utilization_mz: _Optional[float] = ...) -> None: ...

class TorsionalBuckling(_message.Message):
    __slots__ = ["kcrit", "torsional_buckling_parameters", "torsional_buckling_strength", "utilization"]
    KCRIT_FIELD_NUMBER: _ClassVar[int]
    TORSIONAL_BUCKLING_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    TORSIONAL_BUCKLING_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    kcrit: float
    torsional_buckling_parameters: TorsionalBucklingParameters
    torsional_buckling_strength: TorsionalBucklingStrength
    utilization: _geometry_pb2_1_1.Vector2D
    def __init__(self, kcrit: _Optional[float] = ..., utilization: _Optional[_Union[_geometry_pb2_1_1.Vector2D, _Mapping]] = ..., torsional_buckling_parameters: _Optional[_Union[TorsionalBucklingParameters, _Mapping]] = ..., torsional_buckling_strength: _Optional[_Union[TorsionalBucklingStrength, _Mapping]] = ...) -> None: ...

class TorsionalBucklingParameters(_message.Message):
    __slots__ = ["load_pos", "relevant", "stat_sys", "xe", "xs"]
    LOAD_POS_FIELD_NUMBER: _ClassVar[int]
    RELEVANT_FIELD_NUMBER: _ClassVar[int]
    STAT_SYS_FIELD_NUMBER: _ClassVar[int]
    XE_FIELD_NUMBER: _ClassVar[int]
    XS_FIELD_NUMBER: _ClassVar[int]
    load_pos: _beam_pb2_1.Alignment
    relevant: bool
    stat_sys: StatSys
    xe: float
    xs: float
    def __init__(self, relevant: bool = ..., xs: _Optional[float] = ..., xe: _Optional[float] = ..., stat_sys: _Optional[_Union[StatSys, str]] = ..., load_pos: _Optional[_Union[_beam_pb2_1.Alignment, str]] = ...) -> None: ...

class TorsionalBucklingStrength(_message.Message):
    __slots__ = ["beta", "h", "kcrit", "lambdarelm", "lef", "load_pos", "m", "m_max", "relevant", "sigmamcrit", "stat_sys"]
    BETA_FIELD_NUMBER: _ClassVar[int]
    H_FIELD_NUMBER: _ClassVar[int]
    KCRIT_FIELD_NUMBER: _ClassVar[int]
    LAMBDARELM_FIELD_NUMBER: _ClassVar[int]
    LEF_FIELD_NUMBER: _ClassVar[int]
    LOAD_POS_FIELD_NUMBER: _ClassVar[int]
    M_FIELD_NUMBER: _ClassVar[int]
    M_MAX_FIELD_NUMBER: _ClassVar[int]
    RELEVANT_FIELD_NUMBER: _ClassVar[int]
    SIGMAMCRIT_FIELD_NUMBER: _ClassVar[int]
    STAT_SYS_FIELD_NUMBER: _ClassVar[int]
    beta: float
    h: float
    kcrit: float
    lambdarelm: float
    lef: float
    load_pos: _beam_pb2_1.Alignment
    m: _containers.RepeatedScalarFieldContainer[float]
    m_max: float
    relevant: bool
    sigmamcrit: float
    stat_sys: StatSys
    def __init__(self, relevant: bool = ..., stat_sys: _Optional[_Union[StatSys, str]] = ..., load_pos: _Optional[_Union[_beam_pb2_1.Alignment, str]] = ..., m_max: _Optional[float] = ..., m: _Optional[_Iterable[float]] = ..., beta: _Optional[float] = ..., h: _Optional[float] = ..., lef: _Optional[float] = ..., sigmamcrit: _Optional[float] = ..., lambdarelm: _Optional[float] = ..., kcrit: _Optional[float] = ...) -> None: ...

class StatSys(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
