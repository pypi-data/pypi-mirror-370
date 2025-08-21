from Utils import utils_pb2 as _utils_pb2
import element_pb2 as _element_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Geometry import geometry_pb2 as _geometry_pb2
from Geometry import beam_pb2 as _beam_pb2
from Geometry import foundation_pb2 as _foundation_pb2
from Geometry import retainingwall_pb2 as _retainingwall_pb2
from Geometry import pile_pb2 as _pile_pb2
from Design import design_pb2 as _design_pb2
import sections_pb2 as _sections_pb2
from Utils import utils_pb2 as _utils_pb2_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1
from Loading import load_pb2 as _load_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1_1
from Loading import loadcase_pb2 as _loadcase_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1_1_1
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1
from Result import concrete_pb2 as _concrete_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1_1
from Geometry import link_pb2 as _link_pb2
from Geometry import geometry_pb2 as _geometry_pb2_1_1_1_1
from Result import control_pb2 as _control_pb2
from Result import control_pb2 as _control_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
from element_pb2 import Data
from element_pb2 import InspectionLevel
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
from Loading.load_pb2 import Data
from Loading.load_pb2 import Type
from Loading.load_pb2 import DistributionType
from Loading.loadcase_pb2 import Data
from Loading.loadcase_pb2 import Type
from Loading.loadcase_pb2 import DurationClass
from Loading.loadcase_pb2 import Category
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
CATEGORY_A: _loadcase_pb2.Category
CATEGORY_B: _loadcase_pb2.Category
CATEGORY_C: _loadcase_pb2.Category
CATEGORY_D: _loadcase_pb2.Category
CATEGORY_E: _loadcase_pb2.Category
CATEGORY_F: _loadcase_pb2.Category
CATEGORY_G: _loadcase_pb2.Category
CATEGORY_G2: _loadcase_pb2.Category
CATEGORY_H: _loadcase_pb2.Category
CATEGORY_I1: _loadcase_pb2.Category
CATEGORY_I2: _loadcase_pb2.Category
CATEGORY_I3: _loadcase_pb2.Category
CATEGORY_K: _loadcase_pb2.Category
CATEGORY_S1: _loadcase_pb2.Category
CATEGORY_S2: _loadcase_pb2.Category
CATEGORY_S3_C_G: _loadcase_pb2.Category
CATEGORY_S3_H_K: _loadcase_pb2.Category
CATEGORY_T: _loadcase_pb2.Category
CATEGORY_UNSPECIFIED: _loadcase_pb2.Category
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
DESCRIPTOR: _descriptor.FileDescriptor
DESIGN_TYPE_ALLOWEDSOILPRESSURE: _control_pb2_1.DesignTypeFoundation
DESIGN_TYPE_DRAINED: _control_pb2_1.DesignTypeFoundation
DESIGN_TYPE_DRAINED_PUNCHNING_ALT: _control_pb2_1.DesignTypeFoundation
DESIGN_TYPE_DRAINED_PUNCHNING_B6: _control_pb2_1.DesignTypeFoundation
DESIGN_TYPE_ROCK: _control_pb2_1.DesignTypeFoundation
DESIGN_TYPE_UNDRAINED: _control_pb2_1.DesignTypeFoundation
DESIGN_TYPE_UNDRAINED_PUNCHING: _control_pb2_1.DesignTypeFoundation
DESIGN_TYPE_UNSPECIFIED: _control_pb2_1.DesignTypeFoundation
DISTRIBUTION_TYPE_LINE: _load_pb2.DistributionType
DISTRIBUTION_TYPE_NODE: _load_pb2.DistributionType
DISTRIBUTION_TYPE_POINT: _load_pb2.DistributionType
DISTRIBUTION_TYPE_SURFACE: _load_pb2.DistributionType
DISTRIBUTION_TYPE_UNSPECIFIED: _load_pb2.DistributionType
DISTRIBUTION_TYPE_VOLUME: _load_pb2.DistributionType
DURATION_CLASS_INSTANTANEOUS: _loadcase_pb2.DurationClass
DURATION_CLASS_LONG: _loadcase_pb2.DurationClass
DURATION_CLASS_MEDIUM: _loadcase_pb2.DurationClass
DURATION_CLASS_PERMANENT: _loadcase_pb2.DurationClass
DURATION_CLASS_SHORT: _loadcase_pb2.DurationClass
DURATION_CLASS_UNSPECIFIED: _loadcase_pb2.DurationClass
ECCENTRICITY_TYPE_HIGH: _control_pb2_1.EccentricityTypeFoundation
ECCENTRICITY_TYPE_NORMAL: _control_pb2_1.EccentricityTypeFoundation
ECCENTRICITY_TYPE_UNSPECIFIED: _control_pb2_1.EccentricityTypeFoundation
INSPECTION_LEVEL_NORMAL: _element_pb2.InspectionLevel
INSPECTION_LEVEL_RELAXED: _element_pb2.InspectionLevel
INSPECTION_LEVEL_TIGHTENED: _element_pb2.InspectionLevel
INSPECTION_LEVEL_UNSPECIFIED: _element_pb2.InspectionLevel
MATERIAL_CATEGORY_CONCRETE: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_STEEL: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_TIMBER: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_UNSPECIFIED: _sections_pb2.MaterialCategory
OWNER_COMPANY: _utils_pb2_1_1_1_1_1_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1_1_1_1_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1_1_1_1_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1_1_1_1_1_1.Owner
OWNER_USER: _utils_pb2_1_1_1_1_1_1_1.Owner
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
TYPE_ACCIDENT_LOAD: _loadcase_pb2.Type
TYPE_BODY_FORCE: _load_pb2.Type
TYPE_CONSTRUCTION_LOAD: _loadcase_pb2.Type
TYPE_FORCE: _load_pb2.Type
TYPE_ICE_LOAD: _loadcase_pb2.Type
TYPE_IMPOSED_LOAD: _loadcase_pb2.Type
TYPE_MOMENT: _load_pb2.Type
TYPE_PERMANENT_LOAD: _loadcase_pb2.Type
TYPE_PRESSURE: _load_pb2.Type
TYPE_SEISMIC_LOAD: _loadcase_pb2.Type
TYPE_SELF_WEIGHT: _loadcase_pb2.Type
TYPE_SNOW_LOAD: _loadcase_pb2.Type
TYPE_SOIL_FORCE: _load_pb2.Type
TYPE_SOIL_LOAD: _loadcase_pb2.Type
TYPE_SOIL_SELF_WEIGHT: _loadcase_pb2.Type
TYPE_TEMPERATURE: _load_pb2.Type
TYPE_TEMPERATURE_LOAD: _loadcase_pb2.Type
TYPE_UNSPECIFIED: _loadcase_pb2.Type
TYPE_WIND_LOAD: _loadcase_pb2.Type

class BearingRes(_message.Message):
    __slots__ = ["b", "b_gamma", "bc", "bq", "control", "d", "d_gamma", "dc", "dq", "eta_gamma", "etac", "etaq", "g_gamma", "gamma", "gc", "gq", "i_gamma", "ic", "iq", "k1", "kps", "l", "m", "m_b", "m_l", "n_gamma", "nc", "nq", "q", "r_d", "r_d_cat", "r_d_max", "s_gamma", "sc", "sq", "utilization", "vd"]
    BC_FIELD_NUMBER: _ClassVar[int]
    BQ_FIELD_NUMBER: _ClassVar[int]
    B_FIELD_NUMBER: _ClassVar[int]
    B_GAMMA_FIELD_NUMBER: _ClassVar[int]
    CONTROL_FIELD_NUMBER: _ClassVar[int]
    DC_FIELD_NUMBER: _ClassVar[int]
    DQ_FIELD_NUMBER: _ClassVar[int]
    D_FIELD_NUMBER: _ClassVar[int]
    D_GAMMA_FIELD_NUMBER: _ClassVar[int]
    ETAC_FIELD_NUMBER: _ClassVar[int]
    ETAQ_FIELD_NUMBER: _ClassVar[int]
    ETA_GAMMA_FIELD_NUMBER: _ClassVar[int]
    GAMMA_FIELD_NUMBER: _ClassVar[int]
    GC_FIELD_NUMBER: _ClassVar[int]
    GQ_FIELD_NUMBER: _ClassVar[int]
    G_GAMMA_FIELD_NUMBER: _ClassVar[int]
    IC_FIELD_NUMBER: _ClassVar[int]
    IQ_FIELD_NUMBER: _ClassVar[int]
    I_GAMMA_FIELD_NUMBER: _ClassVar[int]
    K1_FIELD_NUMBER: _ClassVar[int]
    KPS_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_FIELD_NUMBER: _ClassVar[int]
    L_FIELD_NUMBER: _ClassVar[int]
    M_B_FIELD_NUMBER: _ClassVar[int]
    M_FIELD_NUMBER: _ClassVar[int]
    M_L_FIELD_NUMBER: _ClassVar[int]
    NC_FIELD_NUMBER: _ClassVar[int]
    NQ_FIELD_NUMBER: _ClassVar[int]
    N_GAMMA_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    R_D_CAT_FIELD_NUMBER: _ClassVar[int]
    R_D_FIELD_NUMBER: _ClassVar[int]
    R_D_MAX_FIELD_NUMBER: _ClassVar[int]
    SC_FIELD_NUMBER: _ClassVar[int]
    SQ_FIELD_NUMBER: _ClassVar[int]
    S_GAMMA_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    VD_FIELD_NUMBER: _ClassVar[int]
    b: float
    b_gamma: float
    bc: float
    bq: float
    control: _control_pb2_1.ControlData
    d: float
    d_gamma: float
    dc: float
    dq: float
    eta_gamma: float
    etac: float
    etaq: float
    g_gamma: float
    gamma: float
    gc: float
    gq: float
    i_gamma: float
    ic: float
    iq: float
    k1: float
    kps: float
    l: float
    m: float
    m_b: float
    m_l: float
    n_gamma: float
    nc: float
    nq: float
    q: float
    r_d: float
    r_d_cat: float
    r_d_max: float
    s_gamma: float
    sc: float
    sq: float
    utilization: float
    vd: float
    def __init__(self, gamma: _Optional[float] = ..., q: _Optional[float] = ..., d: _Optional[float] = ..., b: _Optional[float] = ..., l: _Optional[float] = ..., sc: _Optional[float] = ..., ic: _Optional[float] = ..., gc: _Optional[float] = ..., bc: _Optional[float] = ..., dc: _Optional[float] = ..., etac: _Optional[float] = ..., sq: _Optional[float] = ..., iq: _Optional[float] = ..., gq: _Optional[float] = ..., bq: _Optional[float] = ..., dq: _Optional[float] = ..., etaq: _Optional[float] = ..., s_gamma: _Optional[float] = ..., i_gamma: _Optional[float] = ..., g_gamma: _Optional[float] = ..., b_gamma: _Optional[float] = ..., d_gamma: _Optional[float] = ..., eta_gamma: _Optional[float] = ..., k1: _Optional[float] = ..., kps: _Optional[float] = ..., m: _Optional[float] = ..., m_b: _Optional[float] = ..., m_l: _Optional[float] = ..., nc: _Optional[float] = ..., nq: _Optional[float] = ..., n_gamma: _Optional[float] = ..., r_d_cat: _Optional[float] = ..., r_d_max: _Optional[float] = ..., r_d: _Optional[float] = ..., vd: _Optional[float] = ..., utilization: _Optional[float] = ..., control: _Optional[_Union[_control_pb2_1.ControlData, _Mapping]] = ..., **kwargs) -> None: ...

class BearingResFormula(_message.Message):
    __slots__ = ["b_gamma", "bc", "bq", "d_gamma", "dc", "dq", "g_gamma", "gc", "gq", "i_gamma", "ic", "iq", "m", "m_b", "m_l", "n_gamma", "nc", "nq", "rdmax", "s_gamma", "sc", "sq"]
    BC_FIELD_NUMBER: _ClassVar[int]
    BQ_FIELD_NUMBER: _ClassVar[int]
    B_GAMMA_FIELD_NUMBER: _ClassVar[int]
    DC_FIELD_NUMBER: _ClassVar[int]
    DQ_FIELD_NUMBER: _ClassVar[int]
    D_GAMMA_FIELD_NUMBER: _ClassVar[int]
    GC_FIELD_NUMBER: _ClassVar[int]
    GQ_FIELD_NUMBER: _ClassVar[int]
    G_GAMMA_FIELD_NUMBER: _ClassVar[int]
    IC_FIELD_NUMBER: _ClassVar[int]
    IQ_FIELD_NUMBER: _ClassVar[int]
    I_GAMMA_FIELD_NUMBER: _ClassVar[int]
    M_B_FIELD_NUMBER: _ClassVar[int]
    M_FIELD_NUMBER: _ClassVar[int]
    M_L_FIELD_NUMBER: _ClassVar[int]
    NC_FIELD_NUMBER: _ClassVar[int]
    NQ_FIELD_NUMBER: _ClassVar[int]
    N_GAMMA_FIELD_NUMBER: _ClassVar[int]
    RDMAX_FIELD_NUMBER: _ClassVar[int]
    SC_FIELD_NUMBER: _ClassVar[int]
    SQ_FIELD_NUMBER: _ClassVar[int]
    S_GAMMA_FIELD_NUMBER: _ClassVar[int]
    b_gamma: str
    bc: str
    bq: str
    d_gamma: str
    dc: str
    dq: str
    g_gamma: str
    gc: str
    gq: str
    i_gamma: str
    ic: str
    iq: str
    m: str
    m_b: str
    m_l: str
    n_gamma: str
    nc: str
    nq: str
    rdmax: str
    s_gamma: str
    sc: str
    sq: str
    def __init__(self, sc: _Optional[str] = ..., ic: _Optional[str] = ..., gc: _Optional[str] = ..., bc: _Optional[str] = ..., dc: _Optional[str] = ..., sq: _Optional[str] = ..., iq: _Optional[str] = ..., gq: _Optional[str] = ..., bq: _Optional[str] = ..., dq: _Optional[str] = ..., s_gamma: _Optional[str] = ..., i_gamma: _Optional[str] = ..., g_gamma: _Optional[str] = ..., b_gamma: _Optional[str] = ..., d_gamma: _Optional[str] = ..., m: _Optional[str] = ..., m_b: _Optional[str] = ..., m_l: _Optional[str] = ..., nc: _Optional[str] = ..., nq: _Optional[str] = ..., n_gamma: _Optional[str] = ..., rdmax: _Optional[str] = ...) -> None: ...

class ConcreteInput(_message.Message):
    __slots__ = ["concrete_length", "concrete_width", "nodes", "sec_length", "sec_width"]
    CONCRETE_LENGTH_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    SEC_LENGTH_FIELD_NUMBER: _ClassVar[int]
    SEC_WIDTH_FIELD_NUMBER: _ClassVar[int]
    concrete_length: _element_pb2.Data
    concrete_width: _element_pb2.Data
    nodes: _containers.RepeatedCompositeFieldContainer[_topology_pb2.ElementNode]
    sec_length: _sections_pb2.Section
    sec_width: _sections_pb2.Section
    def __init__(self, concrete_width: _Optional[_Union[_element_pb2.Data, _Mapping]] = ..., concrete_length: _Optional[_Union[_element_pb2.Data, _Mapping]] = ..., nodes: _Optional[_Iterable[_Union[_topology_pb2.ElementNode, _Mapping]]] = ..., sec_width: _Optional[_Union[_sections_pb2.Section, _Mapping]] = ..., sec_length: _Optional[_Union[_sections_pb2.Section, _Mapping]] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["result_analysis", "result_design", "result_punching", "result_unreinforced", "utilization"]
    RESULT_ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    RESULT_DESIGN_FIELD_NUMBER: _ClassVar[int]
    RESULT_PUNCHING_FIELD_NUMBER: _ClassVar[int]
    RESULT_UNREINFORCED_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    result_analysis: _containers.RepeatedCompositeFieldContainer[DetailedFoundationAnalysis]
    result_design: _containers.RepeatedCompositeFieldContainer[DetailedFoundationDesign]
    result_punching: RCPunchingCheckConcreteCompression
    result_unreinforced: RCUnreinforced
    utilization: float
    def __init__(self, result_analysis: _Optional[_Iterable[_Union[DetailedFoundationAnalysis, _Mapping]]] = ..., result_design: _Optional[_Iterable[_Union[DetailedFoundationDesign, _Mapping]]] = ..., utilization: _Optional[float] = ..., result_punching: _Optional[_Union[RCPunchingCheckConcreteCompression, _Mapping]] = ..., result_unreinforced: _Optional[_Union[RCUnreinforced, _Mapping]] = ...) -> None: ...

class DesignStrength(_message.Message):
    __slots__ = ["ad", "cd", "cu2d", "cud", "deltad", "phid", "rk"]
    AD_FIELD_NUMBER: _ClassVar[int]
    CD_FIELD_NUMBER: _ClassVar[int]
    CU2D_FIELD_NUMBER: _ClassVar[int]
    CUD_FIELD_NUMBER: _ClassVar[int]
    DELTAD_FIELD_NUMBER: _ClassVar[int]
    PHID_FIELD_NUMBER: _ClassVar[int]
    RK_FIELD_NUMBER: _ClassVar[int]
    ad: float
    cd: float
    cu2d: float
    cud: float
    deltad: float
    phid: float
    rk: float
    def __init__(self, cud: _Optional[float] = ..., cd: _Optional[float] = ..., phid: _Optional[float] = ..., deltad: _Optional[float] = ..., ad: _Optional[float] = ..., rk: _Optional[float] = ..., cu2d: _Optional[float] = ...) -> None: ...

class DesignSummary(_message.Message):
    __slots__ = ["concrete_input", "controls", "elem_guid"]
    CONCRETE_INPUT_FIELD_NUMBER: _ClassVar[int]
    CONTROLS_FIELD_NUMBER: _ClassVar[int]
    ELEM_GUID_FIELD_NUMBER: _ClassVar[int]
    concrete_input: ConcreteInput
    controls: _containers.RepeatedCompositeFieldContainer[_control_pb2_1.ControlData]
    elem_guid: str
    def __init__(self, elem_guid: _Optional[str] = ..., concrete_input: _Optional[_Union[ConcreteInput, _Mapping]] = ..., controls: _Optional[_Iterable[_Union[_control_pb2_1.ControlData, _Mapping]]] = ...) -> None: ...

class DetailedFoundationAnalysis(_message.Message):
    __slots__ = ["active_overload", "active_soil_pressure", "active_soil_weight", "active_water_pressure", "analysis_type", "effective_geometry", "foundation_force", "id", "load", "passive_soil_pressure", "passive_soil_weight", "passive_water_pressure", "selfweight", "selfweight_effective", "selfweight_effective_concrete", "selfweight_effective_soil", "settlement", "soil_water_loads", "soil_water_loads_loadcase", "utilization_passive"]
    ACTIVE_OVERLOAD_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_SOIL_PRESSURE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_SOIL_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_WATER_PRESSURE_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_GEOMETRY_FIELD_NUMBER: _ClassVar[int]
    FOUNDATION_FORCE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LOAD_FIELD_NUMBER: _ClassVar[int]
    PASSIVE_SOIL_PRESSURE_FIELD_NUMBER: _ClassVar[int]
    PASSIVE_SOIL_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    PASSIVE_WATER_PRESSURE_FIELD_NUMBER: _ClassVar[int]
    SELFWEIGHT_EFFECTIVE_CONCRETE_FIELD_NUMBER: _ClassVar[int]
    SELFWEIGHT_EFFECTIVE_FIELD_NUMBER: _ClassVar[int]
    SELFWEIGHT_EFFECTIVE_SOIL_FIELD_NUMBER: _ClassVar[int]
    SELFWEIGHT_FIELD_NUMBER: _ClassVar[int]
    SETTLEMENT_FIELD_NUMBER: _ClassVar[int]
    SOIL_WATER_LOADS_FIELD_NUMBER: _ClassVar[int]
    SOIL_WATER_LOADS_LOADCASE_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_PASSIVE_FIELD_NUMBER: _ClassVar[int]
    active_overload: FoundationForce
    active_soil_pressure: FoundationForce
    active_soil_weight: FoundationForce
    active_water_pressure: FoundationForce
    analysis_type: _control_pb2_1.AnalysisTypeFoundation
    effective_geometry: EffectiveGeometry
    foundation_force: FoundationForce
    id: _utils_pb2_1_1_1_1_1_1_1.ID
    load: FoundationForce
    passive_soil_pressure: FoundationForce
    passive_soil_weight: FoundationForce
    passive_water_pressure: FoundationForce
    selfweight: FoundationForce
    selfweight_effective: FoundationForce
    selfweight_effective_concrete: FoundationForce
    selfweight_effective_soil: FoundationForce
    settlement: float
    soil_water_loads: SoilWaterLoads
    soil_water_loads_loadcase: _loadcase_pb2.Data
    utilization_passive: float
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1_1_1_1_1_1.ID, _Mapping]] = ..., analysis_type: _Optional[_Union[_control_pb2_1.AnalysisTypeFoundation, str]] = ..., load: _Optional[_Union[FoundationForce, _Mapping]] = ..., selfweight: _Optional[_Union[FoundationForce, _Mapping]] = ..., selfweight_effective: _Optional[_Union[FoundationForce, _Mapping]] = ..., foundation_force: _Optional[_Union[FoundationForce, _Mapping]] = ..., effective_geometry: _Optional[_Union[EffectiveGeometry, _Mapping]] = ..., settlement: _Optional[float] = ..., selfweight_effective_concrete: _Optional[_Union[FoundationForce, _Mapping]] = ..., selfweight_effective_soil: _Optional[_Union[FoundationForce, _Mapping]] = ..., utilization_passive: _Optional[float] = ..., passive_water_pressure: _Optional[_Union[FoundationForce, _Mapping]] = ..., active_water_pressure: _Optional[_Union[FoundationForce, _Mapping]] = ..., passive_soil_weight: _Optional[_Union[FoundationForce, _Mapping]] = ..., active_soil_weight: _Optional[_Union[FoundationForce, _Mapping]] = ..., passive_soil_pressure: _Optional[_Union[FoundationForce, _Mapping]] = ..., active_soil_pressure: _Optional[_Union[FoundationForce, _Mapping]] = ..., active_overload: _Optional[_Union[FoundationForce, _Mapping]] = ..., soil_water_loads_loadcase: _Optional[_Union[_loadcase_pb2.Data, _Mapping]] = ..., soil_water_loads: _Optional[_Union[SoilWaterLoads, _Mapping]] = ...) -> None: ...

class DetailedFoundationDesign(_message.Message):
    __slots__ = ["analysis_type", "bearing_result", "design_strength", "design_type", "eccentricity_type", "id", "material_name", "punching_level", "sliding_result"]
    ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    BEARING_RESULT_FIELD_NUMBER: _ClassVar[int]
    DESIGN_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    DESIGN_TYPE_FIELD_NUMBER: _ClassVar[int]
    ECCENTRICITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_NAME_FIELD_NUMBER: _ClassVar[int]
    PUNCHING_LEVEL_FIELD_NUMBER: _ClassVar[int]
    SLIDING_RESULT_FIELD_NUMBER: _ClassVar[int]
    analysis_type: _control_pb2_1.AnalysisTypeFoundation
    bearing_result: BearingRes
    design_strength: DesignStrength
    design_type: _control_pb2_1.DesignTypeFoundation
    eccentricity_type: _control_pb2_1.EccentricityTypeFoundation
    id: _utils_pb2_1_1_1_1_1_1_1.ID
    material_name: str
    punching_level: float
    sliding_result: SlidingRes
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1_1_1_1_1_1.ID, _Mapping]] = ..., analysis_type: _Optional[_Union[_control_pb2_1.AnalysisTypeFoundation, str]] = ..., design_type: _Optional[_Union[_control_pb2_1.DesignTypeFoundation, str]] = ..., eccentricity_type: _Optional[_Union[_control_pb2_1.EccentricityTypeFoundation, str]] = ..., bearing_result: _Optional[_Union[BearingRes, _Mapping]] = ..., sliding_result: _Optional[_Union[SlidingRes, _Mapping]] = ..., design_strength: _Optional[_Union[DesignStrength, _Mapping]] = ..., punching_level: _Optional[float] = ..., material_name: _Optional[str] = ...) -> None: ...

class EffectiveGeometry(_message.Message):
    __slots__ = ["e_length", "e_width", "eccentricity_factor", "effective_area", "effective_length", "effective_stress", "effective_width", "length", "navier_length", "navier_width", "plastic_length", "plastic_width", "width"]
    ECCENTRICITY_FACTOR_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_AREA_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_LENGTH_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_STRESS_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    E_LENGTH_FIELD_NUMBER: _ClassVar[int]
    E_WIDTH_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    NAVIER_LENGTH_FIELD_NUMBER: _ClassVar[int]
    NAVIER_WIDTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_WIDTH_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    e_length: float
    e_width: float
    eccentricity_factor: float
    effective_area: float
    effective_length: float
    effective_stress: float
    effective_width: float
    length: float
    navier_length: Stress
    navier_width: Stress
    plastic_length: Stress
    plastic_width: Stress
    width: float
    def __init__(self, width: _Optional[float] = ..., length: _Optional[float] = ..., effective_width: _Optional[float] = ..., effective_length: _Optional[float] = ..., effective_area: _Optional[float] = ..., e_width: _Optional[float] = ..., e_length: _Optional[float] = ..., eccentricity_factor: _Optional[float] = ..., effective_stress: _Optional[float] = ..., navier_width: _Optional[_Union[Stress, _Mapping]] = ..., navier_length: _Optional[_Union[Stress, _Mapping]] = ..., plastic_width: _Optional[_Union[Stress, _Mapping]] = ..., plastic_length: _Optional[_Union[Stress, _Mapping]] = ...) -> None: ...

class Element(_message.Message):
    __slots__ = ["max_of_controls"]
    MAX_OF_CONTROLS_FIELD_NUMBER: _ClassVar[int]
    max_of_controls: _containers.RepeatedCompositeFieldContainer[_control_pb2_1.ControlData]
    def __init__(self, max_of_controls: _Optional[_Iterable[_Union[_control_pb2_1.ControlData, _Mapping]]] = ...) -> None: ...

class FoundationForce(_message.Message):
    __slots__ = ["hx", "hy", "mx", "my", "t", "v"]
    HX_FIELD_NUMBER: _ClassVar[int]
    HY_FIELD_NUMBER: _ClassVar[int]
    MX_FIELD_NUMBER: _ClassVar[int]
    MY_FIELD_NUMBER: _ClassVar[int]
    T_FIELD_NUMBER: _ClassVar[int]
    V_FIELD_NUMBER: _ClassVar[int]
    hx: float
    hy: float
    mx: float
    my: float
    t: float
    v: float
    def __init__(self, hx: _Optional[float] = ..., hy: _Optional[float] = ..., v: _Optional[float] = ..., mx: _Optional[float] = ..., my: _Optional[float] = ..., t: _Optional[float] = ...) -> None: ...

class RCPunchingCheckConcreteCompression(_message.Message):
    __slots__ = ["M1", "M2", "V", "V_ed0", "V_ed1", "a", "beta", "crdc", "dBx", "dBy", "ddg", "deff", "densityclass", "dy", "dz", "eta", "gamma_shear", "k", "k1", "kpb", "nu", "ny_ed0", "ny_ed1", "ny_min", "ny_rdc", "ny_rdmax", "perimeter_no", "perimeter_points_u0", "perimeter_points_u1", "punch_zone", "rhol", "rholx", "rholy", "shape_no", "sigmacp", "u0", "u1", "utilization", "utilization0", "utilization1", "v_ed", "v_rdc", "v_rdmax"]
    A_FIELD_NUMBER: _ClassVar[int]
    BETA_FIELD_NUMBER: _ClassVar[int]
    CRDC_FIELD_NUMBER: _ClassVar[int]
    DBX_FIELD_NUMBER: _ClassVar[int]
    DBY_FIELD_NUMBER: _ClassVar[int]
    DDG_FIELD_NUMBER: _ClassVar[int]
    DEFF_FIELD_NUMBER: _ClassVar[int]
    DENSITYCLASS_FIELD_NUMBER: _ClassVar[int]
    DY_FIELD_NUMBER: _ClassVar[int]
    DZ_FIELD_NUMBER: _ClassVar[int]
    ETA_FIELD_NUMBER: _ClassVar[int]
    GAMMA_SHEAR_FIELD_NUMBER: _ClassVar[int]
    K1_FIELD_NUMBER: _ClassVar[int]
    KPB_FIELD_NUMBER: _ClassVar[int]
    K_FIELD_NUMBER: _ClassVar[int]
    M1: float
    M1_FIELD_NUMBER: _ClassVar[int]
    M2: float
    M2_FIELD_NUMBER: _ClassVar[int]
    NU_FIELD_NUMBER: _ClassVar[int]
    NY_ED0_FIELD_NUMBER: _ClassVar[int]
    NY_ED1_FIELD_NUMBER: _ClassVar[int]
    NY_MIN_FIELD_NUMBER: _ClassVar[int]
    NY_RDC_FIELD_NUMBER: _ClassVar[int]
    NY_RDMAX_FIELD_NUMBER: _ClassVar[int]
    PERIMETER_NO_FIELD_NUMBER: _ClassVar[int]
    PERIMETER_POINTS_U0_FIELD_NUMBER: _ClassVar[int]
    PERIMETER_POINTS_U1_FIELD_NUMBER: _ClassVar[int]
    PUNCH_ZONE_FIELD_NUMBER: _ClassVar[int]
    RHOLX_FIELD_NUMBER: _ClassVar[int]
    RHOLY_FIELD_NUMBER: _ClassVar[int]
    RHOL_FIELD_NUMBER: _ClassVar[int]
    SHAPE_NO_FIELD_NUMBER: _ClassVar[int]
    SIGMACP_FIELD_NUMBER: _ClassVar[int]
    U0_FIELD_NUMBER: _ClassVar[int]
    U1_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION0_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION1_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    V: float
    V_ED0_FIELD_NUMBER: _ClassVar[int]
    V_ED1_FIELD_NUMBER: _ClassVar[int]
    V_ED_FIELD_NUMBER: _ClassVar[int]
    V_FIELD_NUMBER: _ClassVar[int]
    V_RDC_FIELD_NUMBER: _ClassVar[int]
    V_RDMAX_FIELD_NUMBER: _ClassVar[int]
    V_ed0: float
    V_ed1: float
    a: float
    beta: float
    crdc: float
    dBx: float
    dBy: float
    ddg: float
    deff: float
    densityclass: int
    dy: float
    dz: float
    eta: float
    gamma_shear: float
    k: float
    k1: float
    kpb: float
    nu: float
    ny_ed0: float
    ny_ed1: float
    ny_min: float
    ny_rdc: float
    ny_rdmax: float
    perimeter_no: int
    perimeter_points_u0: _containers.RepeatedCompositeFieldContainer[_geometry_pb2_1_1_1_1.Point2D]
    perimeter_points_u1: _containers.RepeatedCompositeFieldContainer[_geometry_pb2_1_1_1_1.Point2D]
    punch_zone: float
    rhol: float
    rholx: float
    rholy: float
    shape_no: int
    sigmacp: float
    u0: float
    u1: float
    utilization: float
    utilization0: float
    utilization1: float
    v_ed: float
    v_rdc: float
    v_rdmax: float
    def __init__(self, beta: _Optional[float] = ..., dy: _Optional[float] = ..., dz: _Optional[float] = ..., deff: _Optional[float] = ..., rhol: _Optional[float] = ..., rholx: _Optional[float] = ..., rholy: _Optional[float] = ..., u0: _Optional[float] = ..., perimeter_points_u0: _Optional[_Iterable[_Union[_geometry_pb2_1_1_1_1.Point2D, _Mapping]]] = ..., a: _Optional[float] = ..., u1: _Optional[float] = ..., perimeter_points_u1: _Optional[_Iterable[_Union[_geometry_pb2_1_1_1_1.Point2D, _Mapping]]] = ..., nu: _Optional[float] = ..., V_ed0: _Optional[float] = ..., V_ed1: _Optional[float] = ..., v_ed: _Optional[float] = ..., v_rdmax: _Optional[float] = ..., v_rdc: _Optional[float] = ..., ny_rdmax: _Optional[float] = ..., ny_rdc: _Optional[float] = ..., ny_min: _Optional[float] = ..., ny_ed0: _Optional[float] = ..., ny_ed1: _Optional[float] = ..., k: _Optional[float] = ..., k1: _Optional[float] = ..., crdc: _Optional[float] = ..., eta: _Optional[float] = ..., densityclass: _Optional[int] = ..., utilization: _Optional[float] = ..., utilization0: _Optional[float] = ..., utilization1: _Optional[float] = ..., punch_zone: _Optional[float] = ..., perimeter_no: _Optional[int] = ..., shape_no: _Optional[int] = ..., V: _Optional[float] = ..., M1: _Optional[float] = ..., M2: _Optional[float] = ..., sigmacp: _Optional[float] = ..., dBx: _Optional[float] = ..., dBy: _Optional[float] = ..., ddg: _Optional[float] = ..., kpb: _Optional[float] = ..., gamma_shear: _Optional[float] = ...) -> None: ...

class RCPunchingCheckConcreteShear(_message.Message):
    __slots__ = ["C_rdc_sw", "capacity", "conc_shear", "sr", "v_rdcs", "v_rdcsw", "v_rdsw"]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    CONC_SHEAR_FIELD_NUMBER: _ClassVar[int]
    C_RDC_SW_FIELD_NUMBER: _ClassVar[int]
    C_rdc_sw: float
    SR_FIELD_NUMBER: _ClassVar[int]
    V_RDCSW_FIELD_NUMBER: _ClassVar[int]
    V_RDCS_FIELD_NUMBER: _ClassVar[int]
    V_RDSW_FIELD_NUMBER: _ClassVar[int]
    capacity: float
    conc_shear: RCPunchingCheckConcreteShear
    sr: float
    v_rdcs: float
    v_rdcsw: float
    v_rdsw: float
    def __init__(self, conc_shear: _Optional[_Union[RCPunchingCheckConcreteShear, _Mapping]] = ..., sr: _Optional[float] = ..., capacity: _Optional[float] = ..., v_rdsw: _Optional[float] = ..., v_rdcs: _Optional[float] = ..., v_rdcsw: _Optional[float] = ..., C_rdc_sw: _Optional[float] = ...) -> None: ...

class RCUnreinforced(_message.Message):
    __slots__ = ["unreinforced", "utilization"]
    UNREINFORCED_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    unreinforced: bool
    utilization: float
    def __init__(self, unreinforced: bool = ..., utilization: _Optional[float] = ...) -> None: ...

class SlidingRes(_message.Message):
    __slots__ = ["control", "hd", "hxd", "hyd", "r_d", "utilization"]
    CONTROL_FIELD_NUMBER: _ClassVar[int]
    HD_FIELD_NUMBER: _ClassVar[int]
    HXD_FIELD_NUMBER: _ClassVar[int]
    HYD_FIELD_NUMBER: _ClassVar[int]
    R_D_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    control: _control_pb2_1.ControlData
    hd: float
    hxd: float
    hyd: float
    r_d: float
    utilization: float
    def __init__(self, r_d: _Optional[float] = ..., utilization: _Optional[float] = ..., hd: _Optional[float] = ..., hxd: _Optional[float] = ..., hyd: _Optional[float] = ..., control: _Optional[_Union[_control_pb2_1.ControlData, _Mapping]] = ...) -> None: ...

class SlidingResFormula(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class SoilWaterLoads(_message.Message):
    __slots__ = ["active_earth_pressure", "active_water_pressure", "generated_point_line_loads", "passive_earth_pressure", "passive_water_pressure"]
    ACTIVE_EARTH_PRESSURE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_WATER_PRESSURE_FIELD_NUMBER: _ClassVar[int]
    GENERATED_POINT_LINE_LOADS_FIELD_NUMBER: _ClassVar[int]
    PASSIVE_EARTH_PRESSURE_FIELD_NUMBER: _ClassVar[int]
    PASSIVE_WATER_PRESSURE_FIELD_NUMBER: _ClassVar[int]
    active_earth_pressure: _containers.RepeatedCompositeFieldContainer[_load_pb2.Data]
    active_water_pressure: _load_pb2.Data
    generated_point_line_loads: _containers.RepeatedCompositeFieldContainer[_load_pb2.Data]
    passive_earth_pressure: _containers.RepeatedCompositeFieldContainer[_load_pb2.Data]
    passive_water_pressure: _load_pb2.Data
    def __init__(self, passive_water_pressure: _Optional[_Union[_load_pb2.Data, _Mapping]] = ..., active_water_pressure: _Optional[_Union[_load_pb2.Data, _Mapping]] = ..., passive_earth_pressure: _Optional[_Iterable[_Union[_load_pb2.Data, _Mapping]]] = ..., active_earth_pressure: _Optional[_Iterable[_Union[_load_pb2.Data, _Mapping]]] = ..., generated_point_line_loads: _Optional[_Iterable[_Union[_load_pb2.Data, _Mapping]]] = ...) -> None: ...

class Stress(_message.Message):
    __slots__ = ["stress_1", "stress_2", "x1", "x2"]
    STRESS_1_FIELD_NUMBER: _ClassVar[int]
    STRESS_2_FIELD_NUMBER: _ClassVar[int]
    X1_FIELD_NUMBER: _ClassVar[int]
    X2_FIELD_NUMBER: _ClassVar[int]
    stress_1: float
    stress_2: float
    x1: float
    x2: float
    def __init__(self, x1: _Optional[float] = ..., x2: _Optional[float] = ..., stress_1: _Optional[float] = ..., stress_2: _Optional[float] = ...) -> None: ...
