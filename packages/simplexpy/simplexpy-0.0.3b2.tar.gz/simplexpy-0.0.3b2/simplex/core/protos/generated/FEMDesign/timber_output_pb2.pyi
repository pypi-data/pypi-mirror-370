from FEMDesign import analysis_data_pb2 as _analysis_data_pb2
from FEMDesign import steel_output_pb2 as _steel_output_pb2
from FEMDesign import analysis_data_pb2 as _analysis_data_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from FEMDesign.analysis_data_pb2 import Displacement
from FEMDesign.analysis_data_pb2 import Force
from FEMDesign.analysis_data_pb2 import SectionResultRecord
from FEMDesign.analysis_data_pb2 import CombResultRecord
from FEMDesign.analysis_data_pb2 import BarResultRecord
from FEMDesign.analysis_data_pb2 import LoadCombRecord
from FEMDesign.analysis_data_pb2 import LoadCombTimberRecord
from FEMDesign.analysis_data_pb2 import BarSteelFireProtRecord
from FEMDesign.analysis_data_pb2 import BarTimberFireProtRecord
from FEMDesign.analysis_data_pb2 import InformationSteel
from FEMDesign.analysis_data_pb2 import InformationTimber
from FEMDesign.steel_output_pb2 import BucklingShapes
from FEMDesign.steel_output_pb2 import VirtualStiffeners
from FEMDesign.steel_output_pb2 import Boolean2D
from FEMDesign.steel_output_pb2 import TVPointW
from FEMDesign.steel_output_pb2 import Vector2D
from FEMDesign.steel_output_pb2 import BooleanYZ
from FEMDesign.steel_output_pb2 import Vector4D
from FEMDesign.steel_output_pb2 import CrossSectionDataRecord
from FEMDesign.steel_output_pb2 import MaterialDataRecord
from FEMDesign.steel_output_pb2 import GasTemperature
from FEMDesign.steel_output_pb2 import Parametric
from FEMDesign.steel_output_pb2 import MemberTemperatureUnprotechted
from FEMDesign.steel_output_pb2 import MemberTemperatureProtechted
from FEMDesign.steel_output_pb2 import FireDataRecord
from FEMDesign.steel_output_pb2 import BarExtraDataRecord
from FEMDesign.steel_output_pb2 import SectionClassRecord
from FEMDesign.steel_output_pb2 import SectionDesignCalcRecord
from FEMDesign.steel_output_pb2 import PointStress
from FEMDesign.steel_output_pb2 import StBarEffectiveCS
from FEMDesign.steel_output_pb2 import StBarCSResist
from FEMDesign.steel_output_pb2 import StBarFlexural
from FEMDesign.steel_output_pb2 import StBarFlexuralTorsional
from FEMDesign.steel_output_pb2 import StBarTorsional
from FEMDesign.steel_output_pb2 import StBarWeb
from FEMDesign.steel_output_pb2 import StBarInteraction
from FEMDesign.steel_output_pb2 import StBarInteraction2nd
from FEMDesign.steel_output_pb2 import CombDesignCalcRecord
from FEMDesign.steel_output_pb2 import Information
from FEMDesign.steel_output_pb2 import BarSectionType
from FEMDesign.steel_output_pb2 import StatSys
from FEMDesign.steel_output_pb2 import Alignment
from FEMDesign.steel_output_pb2 import LimitState
from FEMDesign.steel_output_pb2 import Curve
from FEMDesign.steel_output_pb2 import CurveLT
from FEMDesign.steel_output_pb2 import ShearResistanceEnum
from FEMDesign.steel_output_pb2 import StBarWebRelevant
from FEMDesign.steel_output_pb2 import ShearStressCheckRelevant
from FEMDesign.steel_output_pb2 import InteractionMethod
ALIGNMENT_BOTTOM: _steel_output_pb2.Alignment
ALIGNMENT_CENTER: _steel_output_pb2.Alignment
ALIGNMENT_TOP: _steel_output_pb2.Alignment
BAR_SECTION_TYPE_UNIFORM: _steel_output_pb2.BarSectionType
BAR_SECTION_TYPE_VARIABLE: _steel_output_pb2.BarSectionType
CURVE_A: _steel_output_pb2.Curve
CURVE_A0: _steel_output_pb2.Curve
CURVE_B: _steel_output_pb2.Curve
CURVE_C: _steel_output_pb2.Curve
CURVE_D: _steel_output_pb2.Curve
CURVE_L_T_A: _steel_output_pb2.CurveLT
CURVE_L_T_B: _steel_output_pb2.CurveLT
CURVE_L_T_C: _steel_output_pb2.CurveLT
CURVE_L_T_D: _steel_output_pb2.CurveLT
DESCRIPTOR: _descriptor.FileDescriptor
INTERACTION_METHOD_1: _steel_output_pb2.InteractionMethod
INTERACTION_METHOD_2: _steel_output_pb2.InteractionMethod
LIMIT_STATE_ACCIDENTAL: _steel_output_pb2.LimitState
LIMIT_STATE_CHARACTERISTIC: _steel_output_pb2.LimitState
LIMIT_STATE_FREQUENT: _steel_output_pb2.LimitState
LIMIT_STATE_QUASI_PERMANENT: _steel_output_pb2.LimitState
LIMIT_STATE_SEISMIC: _steel_output_pb2.LimitState
LIMIT_STATE_ULTIMATE: _steel_output_pb2.LimitState
SHEAR_RESISTANCE_HOLLOW: _steel_output_pb2.ShearResistanceEnum
SHEAR_RESISTANCE_I_LIKE: _steel_output_pb2.ShearResistanceEnum
SHEAR_RESISTANCE_UNSPECIFIED: _steel_output_pb2.ShearResistanceEnum
SHEAR_RESISTANCE_U_LIKE: _steel_output_pb2.ShearResistanceEnum
SHEAR_STRESS_CHECK_RELEVANT_NO: _steel_output_pb2.ShearStressCheckRelevant
SHEAR_STRESS_CHECK_RELEVANT_NO_BECAUSE_WEB_BUCKLING: _steel_output_pb2.ShearStressCheckRelevant
SHEAR_STRESS_CHECK_RELEVANT_YES: _steel_output_pb2.ShearStressCheckRelevant
STAT_SYS_CANTILEVER: _steel_output_pb2.StatSys
STAT_SYS_SIMPLE_SUPPORTED: _steel_output_pb2.StatSys
ST_BAR_WEB_RELEVANT_NO: _steel_output_pb2.StBarWebRelevant
ST_BAR_WEB_RELEVANT_NO_STIFF_LIMIT: _steel_output_pb2.StBarWebRelevant
ST_BAR_WEB_RELEVANT_NO_UNSTIFF_LIMIT: _steel_output_pb2.StBarWebRelevant
ST_BAR_WEB_RELEVANT_YES: _steel_output_pb2.StBarWebRelevant

class ApexRecord(_message.Message):
    __slots__ = ["f_positive_moment_causes_tension", "r", "r_alpha_ap", "r_b", "r_h_ap", "r_in", "r_k", "r_kdis", "r_kl", "r_kp", "r_kr", "r_kvol", "r_volume_ap"]
    F_POSITIVE_MOMENT_CAUSES_TENSION_FIELD_NUMBER: _ClassVar[int]
    R_ALPHA_AP_FIELD_NUMBER: _ClassVar[int]
    R_B_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    R_H_AP_FIELD_NUMBER: _ClassVar[int]
    R_IN_FIELD_NUMBER: _ClassVar[int]
    R_KDIS_FIELD_NUMBER: _ClassVar[int]
    R_KL_FIELD_NUMBER: _ClassVar[int]
    R_KP_FIELD_NUMBER: _ClassVar[int]
    R_KR_FIELD_NUMBER: _ClassVar[int]
    R_KVOL_FIELD_NUMBER: _ClassVar[int]
    R_K_FIELD_NUMBER: _ClassVar[int]
    R_VOLUME_AP_FIELD_NUMBER: _ClassVar[int]
    f_positive_moment_causes_tension: bool
    r: float
    r_alpha_ap: float
    r_b: float
    r_h_ap: float
    r_in: float
    r_k: _containers.RepeatedScalarFieldContainer[float]
    r_kdis: float
    r_kl: float
    r_kp: float
    r_kr: float
    r_kvol: float
    r_volume_ap: float
    def __init__(self, f_positive_moment_causes_tension: bool = ..., r_alpha_ap: _Optional[float] = ..., r_h_ap: _Optional[float] = ..., r_b: _Optional[float] = ..., r_kr: _Optional[float] = ..., r_kl: _Optional[float] = ..., r_kdis: _Optional[float] = ..., r_kvol: _Optional[float] = ..., r_kp: _Optional[float] = ..., r_k: _Optional[_Iterable[float]] = ..., r_volume_ap: _Optional[float] = ..., r_in: _Optional[float] = ..., r: _Optional[float] = ...) -> None: ...

class BarExtraDataRecord(_message.Message):
    __slots__ = ["apex_data", "flexural_buckling_data1", "flexural_buckling_data2", "fm1k", "fm2k", "ft0k", "km", "section_distance_start", "section_geometrical_data", "taper_data", "torsional_buckling_data"]
    APEX_DATA_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_DATA1_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_DATA2_FIELD_NUMBER: _ClassVar[int]
    FM1K_FIELD_NUMBER: _ClassVar[int]
    FM2K_FIELD_NUMBER: _ClassVar[int]
    FT0K_FIELD_NUMBER: _ClassVar[int]
    KM_FIELD_NUMBER: _ClassVar[int]
    SECTION_DISTANCE_START_FIELD_NUMBER: _ClassVar[int]
    SECTION_GEOMETRICAL_DATA_FIELD_NUMBER: _ClassVar[int]
    TAPER_DATA_FIELD_NUMBER: _ClassVar[int]
    TORSIONAL_BUCKLING_DATA_FIELD_NUMBER: _ClassVar[int]
    apex_data: ApexRecord
    flexural_buckling_data1: FlexBucklingRecord
    flexural_buckling_data2: FlexBucklingRecord
    fm1k: float
    fm2k: float
    ft0k: float
    km: float
    section_distance_start: float
    section_geometrical_data: SectionGeomData
    taper_data: TaperRecord
    torsional_buckling_data: TorsBucklingRecord
    def __init__(self, section_distance_start: _Optional[float] = ..., section_geometrical_data: _Optional[_Union[SectionGeomData, _Mapping]] = ..., km: _Optional[float] = ..., ft0k: _Optional[float] = ..., fm1k: _Optional[float] = ..., fm2k: _Optional[float] = ..., flexural_buckling_data1: _Optional[_Union[FlexBucklingRecord, _Mapping]] = ..., flexural_buckling_data2: _Optional[_Union[FlexBucklingRecord, _Mapping]] = ..., torsional_buckling_data: _Optional[_Union[TorsBucklingRecord, _Mapping]] = ..., taper_data: _Optional[_Union[TaperRecord, _Mapping]] = ..., apex_data: _Optional[_Union[ApexRecord, _Mapping]] = ...) -> None: ...

class CombDesignCalcUniformRecord(_message.Message):
    __slots__ = ["bar_type", "design_strength_data", "is_combination2nd_order", "is_the_combination_not_calculated", "kmod", "limit_state_of_combination", "maximum_utilization_of_load_combination", "number_of_sections", "number_of_torsional_buckling_lengths", "order_number_of_the_calculation", "results_of_calculated_sections", "torsional_buckling_calculation_results"]
    BAR_TYPE_FIELD_NUMBER: _ClassVar[int]
    DESIGN_STRENGTH_DATA_FIELD_NUMBER: _ClassVar[int]
    IS_COMBINATION2ND_ORDER_FIELD_NUMBER: _ClassVar[int]
    IS_THE_COMBINATION_NOT_CALCULATED_FIELD_NUMBER: _ClassVar[int]
    KMOD_FIELD_NUMBER: _ClassVar[int]
    LIMIT_STATE_OF_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_UTILIZATION_OF_LOAD_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_TORSIONAL_BUCKLING_LENGTHS_FIELD_NUMBER: _ClassVar[int]
    ORDER_NUMBER_OF_THE_CALCULATION_FIELD_NUMBER: _ClassVar[int]
    RESULTS_OF_CALCULATED_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    TORSIONAL_BUCKLING_CALCULATION_RESULTS_FIELD_NUMBER: _ClassVar[int]
    bar_type: _steel_output_pb2.BarSectionType
    design_strength_data: CombDesignStrengthRecord
    is_combination2nd_order: bool
    is_the_combination_not_calculated: bool
    kmod: float
    limit_state_of_combination: _steel_output_pb2.LimitState
    maximum_utilization_of_load_combination: float
    number_of_sections: int
    number_of_torsional_buckling_lengths: int
    order_number_of_the_calculation: int
    results_of_calculated_sections: _containers.RepeatedCompositeFieldContainer[SectionDesignCalcRecord]
    torsional_buckling_calculation_results: _containers.RepeatedCompositeFieldContainer[CombTorsBucklingRecord]
    def __init__(self, is_the_combination_not_calculated: bool = ..., order_number_of_the_calculation: _Optional[int] = ..., limit_state_of_combination: _Optional[_Union[_steel_output_pb2.LimitState, str]] = ..., is_combination2nd_order: bool = ..., maximum_utilization_of_load_combination: _Optional[float] = ..., bar_type: _Optional[_Union[_steel_output_pb2.BarSectionType, str]] = ..., kmod: _Optional[float] = ..., design_strength_data: _Optional[_Union[CombDesignStrengthRecord, _Mapping]] = ..., number_of_torsional_buckling_lengths: _Optional[int] = ..., torsional_buckling_calculation_results: _Optional[_Iterable[_Union[CombTorsBucklingRecord, _Mapping]]] = ..., number_of_sections: _Optional[int] = ..., results_of_calculated_sections: _Optional[_Iterable[_Union[SectionDesignCalcRecord, _Mapping]]] = ...) -> None: ...

class CombDesignCalcVaryingRecord(_message.Message):
    __slots__ = ["bar_type", "design_section_data", "is_combination2nd_order", "is_the_combination_not_calculated", "kmod", "limit_state_of_combination", "maximum_utilization_of_load_combination", "number_of_sections", "number_of_sections_strength", "order_number_of_the_calculation", "results_of_calculated_sections"]
    BAR_TYPE_FIELD_NUMBER: _ClassVar[int]
    DESIGN_SECTION_DATA_FIELD_NUMBER: _ClassVar[int]
    IS_COMBINATION2ND_ORDER_FIELD_NUMBER: _ClassVar[int]
    IS_THE_COMBINATION_NOT_CALCULATED_FIELD_NUMBER: _ClassVar[int]
    KMOD_FIELD_NUMBER: _ClassVar[int]
    LIMIT_STATE_OF_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_UTILIZATION_OF_LOAD_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_SECTIONS_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    ORDER_NUMBER_OF_THE_CALCULATION_FIELD_NUMBER: _ClassVar[int]
    RESULTS_OF_CALCULATED_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    bar_type: _steel_output_pb2.BarSectionType
    design_section_data: _containers.RepeatedCompositeFieldContainer[CombDesignSectionRecord]
    is_combination2nd_order: bool
    is_the_combination_not_calculated: bool
    kmod: float
    limit_state_of_combination: _steel_output_pb2.LimitState
    maximum_utilization_of_load_combination: float
    number_of_sections: int
    number_of_sections_strength: int
    order_number_of_the_calculation: int
    results_of_calculated_sections: _containers.RepeatedCompositeFieldContainer[SectionDesignCalcRecord]
    def __init__(self, is_the_combination_not_calculated: bool = ..., order_number_of_the_calculation: _Optional[int] = ..., limit_state_of_combination: _Optional[_Union[_steel_output_pb2.LimitState, str]] = ..., is_combination2nd_order: bool = ..., maximum_utilization_of_load_combination: _Optional[float] = ..., bar_type: _Optional[_Union[_steel_output_pb2.BarSectionType, str]] = ..., kmod: _Optional[float] = ..., number_of_sections_strength: _Optional[int] = ..., design_section_data: _Optional[_Iterable[_Union[CombDesignSectionRecord, _Mapping]]] = ..., number_of_sections: _Optional[int] = ..., results_of_calculated_sections: _Optional[_Iterable[_Union[SectionDesignCalcRecord, _Mapping]]] = ...) -> None: ...

class CombDesignSectionRecord(_message.Message):
    __slots__ = ["design_stregth_data", "torsional_buckling_calculation_results"]
    DESIGN_STREGTH_DATA_FIELD_NUMBER: _ClassVar[int]
    TORSIONAL_BUCKLING_CALCULATION_RESULTS_FIELD_NUMBER: _ClassVar[int]
    design_stregth_data: CombDesignStrengthRecord
    torsional_buckling_calculation_results: CombTorsBucklingRecord
    def __init__(self, design_stregth_data: _Optional[_Union[CombDesignStrengthRecord, _Mapping]] = ..., torsional_buckling_calculation_results: _Optional[_Union[CombTorsBucklingRecord, _Mapping]] = ...) -> None: ...

class CombDesignStrengthRecord(_message.Message):
    __slots__ = ["r_fc0d", "r_fc90d", "r_fm1d", "r_fm2d", "r_ft0d", "r_ft90d", "r_fvd"]
    R_FC0D_FIELD_NUMBER: _ClassVar[int]
    R_FC90D_FIELD_NUMBER: _ClassVar[int]
    R_FM1D_FIELD_NUMBER: _ClassVar[int]
    R_FM2D_FIELD_NUMBER: _ClassVar[int]
    R_FT0D_FIELD_NUMBER: _ClassVar[int]
    R_FT90D_FIELD_NUMBER: _ClassVar[int]
    R_FVD_FIELD_NUMBER: _ClassVar[int]
    r_fc0d: float
    r_fc90d: float
    r_fm1d: float
    r_fm2d: float
    r_ft0d: float
    r_ft90d: float
    r_fvd: float
    def __init__(self, r_ft0d: _Optional[float] = ..., r_ft90d: _Optional[float] = ..., r_fc0d: _Optional[float] = ..., r_fc90d: _Optional[float] = ..., r_fm1d: _Optional[float] = ..., r_fm2d: _Optional[float] = ..., r_fvd: _Optional[float] = ...) -> None: ...

class CombTorsBucklingRecord(_message.Message):
    __slots__ = ["f_relevant", "load_pos", "r_beta", "r_h", "r_kcrit", "r_lambdarelm", "r_lef", "r_m", "r_m_max", "r_sigmamcrit", "stat_sys"]
    F_RELEVANT_FIELD_NUMBER: _ClassVar[int]
    LOAD_POS_FIELD_NUMBER: _ClassVar[int]
    R_BETA_FIELD_NUMBER: _ClassVar[int]
    R_H_FIELD_NUMBER: _ClassVar[int]
    R_KCRIT_FIELD_NUMBER: _ClassVar[int]
    R_LAMBDARELM_FIELD_NUMBER: _ClassVar[int]
    R_LEF_FIELD_NUMBER: _ClassVar[int]
    R_M_FIELD_NUMBER: _ClassVar[int]
    R_M_MAX_FIELD_NUMBER: _ClassVar[int]
    R_SIGMAMCRIT_FIELD_NUMBER: _ClassVar[int]
    STAT_SYS_FIELD_NUMBER: _ClassVar[int]
    f_relevant: bool
    load_pos: _steel_output_pb2.Alignment
    r_beta: float
    r_h: float
    r_kcrit: float
    r_lambdarelm: float
    r_lef: float
    r_m: _containers.RepeatedScalarFieldContainer[float]
    r_m_max: float
    r_sigmamcrit: float
    stat_sys: _steel_output_pb2.StatSys
    def __init__(self, f_relevant: bool = ..., stat_sys: _Optional[_Union[_steel_output_pb2.StatSys, str]] = ..., load_pos: _Optional[_Union[_steel_output_pb2.Alignment, str]] = ..., r_m_max: _Optional[float] = ..., r_m: _Optional[_Iterable[float]] = ..., r_beta: _Optional[float] = ..., r_h: _Optional[float] = ..., r_lef: _Optional[float] = ..., r_sigmamcrit: _Optional[float] = ..., r_lambdarelm: _Optional[float] = ..., r_kcrit: _Optional[float] = ...) -> None: ...

class FlexBucklingRecord(_message.Message):
    __slots__ = ["r_betac", "r_i0", "r_k", "r_kc", "r_l0", "r_lambda", "r_lambda_rel", "xe", "xs"]
    R_BETAC_FIELD_NUMBER: _ClassVar[int]
    R_I0_FIELD_NUMBER: _ClassVar[int]
    R_KC_FIELD_NUMBER: _ClassVar[int]
    R_K_FIELD_NUMBER: _ClassVar[int]
    R_L0_FIELD_NUMBER: _ClassVar[int]
    R_LAMBDA_FIELD_NUMBER: _ClassVar[int]
    R_LAMBDA_REL_FIELD_NUMBER: _ClassVar[int]
    XE_FIELD_NUMBER: _ClassVar[int]
    XS_FIELD_NUMBER: _ClassVar[int]
    r_betac: float
    r_i0: float
    r_k: float
    r_kc: float
    r_l0: float
    r_lambda: float
    r_lambda_rel: float
    xe: float
    xs: float
    def __init__(self, xs: _Optional[float] = ..., xe: _Optional[float] = ..., r_l0: _Optional[float] = ..., r_i0: _Optional[float] = ..., r_lambda: _Optional[float] = ..., r_lambda_rel: _Optional[float] = ..., r_betac: _Optional[float] = ..., r_k: _Optional[float] = ..., r_kc: _Optional[float] = ...) -> None: ...

class SectionApexResultRecord(_message.Message):
    __slots__ = ["f_relevant_bending", "f_relevant_tension", "r_m_ap", "r_sigmamd", "r_sigmat90d", "r_util"]
    F_RELEVANT_BENDING_FIELD_NUMBER: _ClassVar[int]
    F_RELEVANT_TENSION_FIELD_NUMBER: _ClassVar[int]
    R_M_AP_FIELD_NUMBER: _ClassVar[int]
    R_SIGMAMD_FIELD_NUMBER: _ClassVar[int]
    R_SIGMAT90D_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_FIELD_NUMBER: _ClassVar[int]
    f_relevant_bending: bool
    f_relevant_tension: bool
    r_m_ap: float
    r_sigmamd: float
    r_sigmat90d: float
    r_util: _steel_output_pb2.Vector2D
    def __init__(self, f_relevant_bending: bool = ..., f_relevant_tension: bool = ..., r_m_ap: _Optional[float] = ..., r_sigmamd: _Optional[float] = ..., r_sigmat90d: _Optional[float] = ..., r_util: _Optional[_Union[_steel_output_pb2.Vector2D, _Mapping]] = ...) -> None: ...

class SectionCompressionResultRecord(_message.Message):
    __slots__ = ["f_relevant", "r_util_my", "r_util_mz", "r_util_n"]
    F_RELEVANT_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_MY_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_MZ_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_N_FIELD_NUMBER: _ClassVar[int]
    f_relevant: bool
    r_util_my: float
    r_util_mz: float
    r_util_n: float
    def __init__(self, f_relevant: bool = ..., r_util_n: _Optional[float] = ..., r_util_my: _Optional[float] = ..., r_util_mz: _Optional[float] = ...) -> None: ...

class SectionDesignCalcRecord(_message.Message):
    __slots__ = ["apex_results", "compression_results", "flexural_buckling_results1", "flexural_buckling_results2", "id_gmax_comb", "section_alignment", "section_distance_from_bar_start_point", "shear_results", "sigmad0", "sigmayd", "sigmaz0", "taper_results", "tension_results", "torsional_buckling_results", "ulilization"]
    APEX_RESULTS_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_RESULTS_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_RESULTS1_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_RESULTS2_FIELD_NUMBER: _ClassVar[int]
    ID_GMAX_COMB_FIELD_NUMBER: _ClassVar[int]
    SECTION_ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    SECTION_DISTANCE_FROM_BAR_START_POINT_FIELD_NUMBER: _ClassVar[int]
    SHEAR_RESULTS_FIELD_NUMBER: _ClassVar[int]
    SIGMAD0_FIELD_NUMBER: _ClassVar[int]
    SIGMAYD_FIELD_NUMBER: _ClassVar[int]
    SIGMAZ0_FIELD_NUMBER: _ClassVar[int]
    TAPER_RESULTS_FIELD_NUMBER: _ClassVar[int]
    TENSION_RESULTS_FIELD_NUMBER: _ClassVar[int]
    TORSIONAL_BUCKLING_RESULTS_FIELD_NUMBER: _ClassVar[int]
    ULILIZATION_FIELD_NUMBER: _ClassVar[int]
    apex_results: SectionApexResultRecord
    compression_results: SectionCompressionResultRecord
    flexural_buckling_results1: SectionFlexBucklingResultRecord
    flexural_buckling_results2: SectionFlexBucklingResultRecord
    id_gmax_comb: int
    section_alignment: _steel_output_pb2.Alignment
    section_distance_from_bar_start_point: float
    shear_results: SectionShearResultRecord
    sigmad0: float
    sigmayd: float
    sigmaz0: float
    taper_results: SectionTaperResultRecord
    tension_results: SectionTensionResultRecord
    torsional_buckling_results: SectionTorsBucklingResultRecord
    ulilization: float
    def __init__(self, section_distance_from_bar_start_point: _Optional[float] = ..., ulilization: _Optional[float] = ..., id_gmax_comb: _Optional[int] = ..., section_alignment: _Optional[_Union[_steel_output_pb2.Alignment, str]] = ..., sigmad0: _Optional[float] = ..., sigmayd: _Optional[float] = ..., sigmaz0: _Optional[float] = ..., tension_results: _Optional[_Union[SectionTensionResultRecord, _Mapping]] = ..., compression_results: _Optional[_Union[SectionCompressionResultRecord, _Mapping]] = ..., shear_results: _Optional[_Union[SectionShearResultRecord, _Mapping]] = ..., flexural_buckling_results1: _Optional[_Union[SectionFlexBucklingResultRecord, _Mapping]] = ..., flexural_buckling_results2: _Optional[_Union[SectionFlexBucklingResultRecord, _Mapping]] = ..., torsional_buckling_results: _Optional[_Union[SectionTorsBucklingResultRecord, _Mapping]] = ..., taper_results: _Optional[_Union[SectionTaperResultRecord, _Mapping]] = ..., apex_results: _Optional[_Union[SectionApexResultRecord, _Mapping]] = ...) -> None: ...

class SectionFlexBucklingResultRecord(_message.Message):
    __slots__ = ["f_relevant", "r_kc", "r_util"]
    F_RELEVANT_FIELD_NUMBER: _ClassVar[int]
    R_KC_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_FIELD_NUMBER: _ClassVar[int]
    f_relevant: bool
    r_kc: float
    r_util: float
    def __init__(self, f_relevant: bool = ..., r_kc: _Optional[float] = ..., r_util: _Optional[float] = ...) -> None: ...

class SectionGeomData(_message.Message):
    __slots__ = ["r_a", "r_beta", "r_h", "r_i1", "r_i2", "r_ir1", "r_ir2", "r_it", "r_w", "r_w1", "r_w2"]
    R_A_FIELD_NUMBER: _ClassVar[int]
    R_BETA_FIELD_NUMBER: _ClassVar[int]
    R_H_FIELD_NUMBER: _ClassVar[int]
    R_I1_FIELD_NUMBER: _ClassVar[int]
    R_I2_FIELD_NUMBER: _ClassVar[int]
    R_IR1_FIELD_NUMBER: _ClassVar[int]
    R_IR2_FIELD_NUMBER: _ClassVar[int]
    R_IT_FIELD_NUMBER: _ClassVar[int]
    R_W1_FIELD_NUMBER: _ClassVar[int]
    R_W2_FIELD_NUMBER: _ClassVar[int]
    R_W_FIELD_NUMBER: _ClassVar[int]
    r_a: float
    r_beta: float
    r_h: float
    r_i1: float
    r_i2: float
    r_ir1: float
    r_ir2: float
    r_it: float
    r_w: float
    r_w1: float
    r_w2: float
    def __init__(self, r_w: _Optional[float] = ..., r_h: _Optional[float] = ..., r_a: _Optional[float] = ..., r_w1: _Optional[float] = ..., r_w2: _Optional[float] = ..., r_beta: _Optional[float] = ..., r_ir1: _Optional[float] = ..., r_ir2: _Optional[float] = ..., r_i1: _Optional[float] = ..., r_i2: _Optional[float] = ..., r_it: _Optional[float] = ...) -> None: ...

class SectionShearResultRecord(_message.Message):
    __slots__ = ["f_relevant", "r_tau_vd", "r_util"]
    F_RELEVANT_FIELD_NUMBER: _ClassVar[int]
    R_TAU_VD_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_FIELD_NUMBER: _ClassVar[int]
    f_relevant: bool
    r_tau_vd: float
    r_util: float
    def __init__(self, f_relevant: bool = ..., r_util: _Optional[float] = ..., r_tau_vd: _Optional[float] = ...) -> None: ...

class SectionTaperResultRecord(_message.Message):
    __slots__ = ["f_relevant", "r_kmalpha"]
    F_RELEVANT_FIELD_NUMBER: _ClassVar[int]
    R_KMALPHA_FIELD_NUMBER: _ClassVar[int]
    f_relevant: bool
    r_kmalpha: float
    def __init__(self, f_relevant: bool = ..., r_kmalpha: _Optional[float] = ...) -> None: ...

class SectionTensionResultRecord(_message.Message):
    __slots__ = ["f_relevant", "r_util_my", "r_util_mz"]
    F_RELEVANT_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_MY_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_MZ_FIELD_NUMBER: _ClassVar[int]
    f_relevant: bool
    r_util_my: float
    r_util_mz: float
    def __init__(self, f_relevant: bool = ..., r_util_my: _Optional[float] = ..., r_util_mz: _Optional[float] = ...) -> None: ...

class SectionTorsBucklingResultRecord(_message.Message):
    __slots__ = ["f_relevant", "r_kcrit", "r_util"]
    F_RELEVANT_FIELD_NUMBER: _ClassVar[int]
    R_KCRIT_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_FIELD_NUMBER: _ClassVar[int]
    f_relevant: bool
    r_kcrit: float
    r_util: _steel_output_pb2.Vector2D
    def __init__(self, f_relevant: bool = ..., r_kcrit: _Optional[float] = ..., r_util: _Optional[_Union[_steel_output_pb2.Vector2D, _Mapping]] = ...) -> None: ...

class TaperRecord(_message.Message):
    __slots__ = ["r_alpha_tap", "r_b", "r_h"]
    R_ALPHA_TAP_FIELD_NUMBER: _ClassVar[int]
    R_B_FIELD_NUMBER: _ClassVar[int]
    R_H_FIELD_NUMBER: _ClassVar[int]
    r_alpha_tap: float
    r_b: float
    r_h: float
    def __init__(self, r_alpha_tap: _Optional[float] = ..., r_h: _Optional[float] = ..., r_b: _Optional[float] = ...) -> None: ...

class TorsBucklingRecord(_message.Message):
    __slots__ = ["f_relevant", "load_pos", "stat_sys", "xe", "xs"]
    F_RELEVANT_FIELD_NUMBER: _ClassVar[int]
    LOAD_POS_FIELD_NUMBER: _ClassVar[int]
    STAT_SYS_FIELD_NUMBER: _ClassVar[int]
    XE_FIELD_NUMBER: _ClassVar[int]
    XS_FIELD_NUMBER: _ClassVar[int]
    f_relevant: bool
    load_pos: _steel_output_pb2.Alignment
    stat_sys: _steel_output_pb2.StatSys
    xe: float
    xs: float
    def __init__(self, xs: _Optional[float] = ..., xe: _Optional[float] = ..., f_relevant: bool = ..., stat_sys: _Optional[_Union[_steel_output_pb2.StatSys, str]] = ..., load_pos: _Optional[_Union[_steel_output_pb2.Alignment, str]] = ...) -> None: ...

class UniformBar(_message.Message):
    __slots__ = ["apex_data_for_curved_bars", "bar_type", "data_for_flexural_buckling1", "data_for_flexural_buckling2", "data_for_torsional_buckling", "fm1k", "fm2k", "ft0k", "index_of_combination_of_the_maximal_utilization_of_the_bar", "is_charred_section_too_small", "km_factor", "load_combination_design_calculation_results", "number_of_flexural_buckling_length1", "number_of_flexural_buckling_length2", "number_of_load_combination", "number_of_torsional_buckling_length", "object_unique_id", "overall_utilization_of_the_bar", "section_geometrical_data"]
    APEX_DATA_FOR_CURVED_BARS_FIELD_NUMBER: _ClassVar[int]
    BAR_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_FOR_FLEXURAL_BUCKLING1_FIELD_NUMBER: _ClassVar[int]
    DATA_FOR_FLEXURAL_BUCKLING2_FIELD_NUMBER: _ClassVar[int]
    DATA_FOR_TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
    FM1K_FIELD_NUMBER: _ClassVar[int]
    FM2K_FIELD_NUMBER: _ClassVar[int]
    FT0K_FIELD_NUMBER: _ClassVar[int]
    INDEX_OF_COMBINATION_OF_THE_MAXIMAL_UTILIZATION_OF_THE_BAR_FIELD_NUMBER: _ClassVar[int]
    IS_CHARRED_SECTION_TOO_SMALL_FIELD_NUMBER: _ClassVar[int]
    KM_FACTOR_FIELD_NUMBER: _ClassVar[int]
    LOAD_COMBINATION_DESIGN_CALCULATION_RESULTS_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_FLEXURAL_BUCKLING_LENGTH1_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_FLEXURAL_BUCKLING_LENGTH2_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_LOAD_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_TORSIONAL_BUCKLING_LENGTH_FIELD_NUMBER: _ClassVar[int]
    OBJECT_UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    OVERALL_UTILIZATION_OF_THE_BAR_FIELD_NUMBER: _ClassVar[int]
    SECTION_GEOMETRICAL_DATA_FIELD_NUMBER: _ClassVar[int]
    apex_data_for_curved_bars: ApexRecord
    bar_type: _steel_output_pb2.BarSectionType
    data_for_flexural_buckling1: _containers.RepeatedCompositeFieldContainer[FlexBucklingRecord]
    data_for_flexural_buckling2: _containers.RepeatedCompositeFieldContainer[FlexBucklingRecord]
    data_for_torsional_buckling: _containers.RepeatedCompositeFieldContainer[TorsBucklingRecord]
    fm1k: float
    fm2k: float
    ft0k: float
    index_of_combination_of_the_maximal_utilization_of_the_bar: int
    is_charred_section_too_small: bool
    km_factor: float
    load_combination_design_calculation_results: _containers.RepeatedCompositeFieldContainer[CombDesignCalcUniformRecord]
    number_of_flexural_buckling_length1: int
    number_of_flexural_buckling_length2: int
    number_of_load_combination: int
    number_of_torsional_buckling_length: int
    object_unique_id: int
    overall_utilization_of_the_bar: float
    section_geometrical_data: SectionGeomData
    def __init__(self, object_unique_id: _Optional[int] = ..., overall_utilization_of_the_bar: _Optional[float] = ..., index_of_combination_of_the_maximal_utilization_of_the_bar: _Optional[int] = ..., number_of_load_combination: _Optional[int] = ..., load_combination_design_calculation_results: _Optional[_Iterable[_Union[CombDesignCalcUniformRecord, _Mapping]]] = ..., bar_type: _Optional[_Union[_steel_output_pb2.BarSectionType, str]] = ..., is_charred_section_too_small: bool = ..., section_geometrical_data: _Optional[_Union[SectionGeomData, _Mapping]] = ..., km_factor: _Optional[float] = ..., ft0k: _Optional[float] = ..., fm1k: _Optional[float] = ..., fm2k: _Optional[float] = ..., apex_data_for_curved_bars: _Optional[_Union[ApexRecord, _Mapping]] = ..., number_of_flexural_buckling_length1: _Optional[int] = ..., data_for_flexural_buckling1: _Optional[_Iterable[_Union[FlexBucklingRecord, _Mapping]]] = ..., number_of_flexural_buckling_length2: _Optional[int] = ..., data_for_flexural_buckling2: _Optional[_Iterable[_Union[FlexBucklingRecord, _Mapping]]] = ..., number_of_torsional_buckling_length: _Optional[int] = ..., data_for_torsional_buckling: _Optional[_Iterable[_Union[TorsBucklingRecord, _Mapping]]] = ...) -> None: ...

class VaryingBar(_message.Message):
    __slots__ = ["bar_specific_data", "bar_type", "index_of_combination_of_the_maximal_utilization_of_the_bar", "is_charred_section_too_small", "load_combination_design_calculation_results", "number_of_load_combination", "number_of_sections", "object_unique_id", "overall_utilization_of_the_bar"]
    BAR_SPECIFIC_DATA_FIELD_NUMBER: _ClassVar[int]
    BAR_TYPE_FIELD_NUMBER: _ClassVar[int]
    INDEX_OF_COMBINATION_OF_THE_MAXIMAL_UTILIZATION_OF_THE_BAR_FIELD_NUMBER: _ClassVar[int]
    IS_CHARRED_SECTION_TOO_SMALL_FIELD_NUMBER: _ClassVar[int]
    LOAD_COMBINATION_DESIGN_CALCULATION_RESULTS_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_LOAD_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    OBJECT_UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    OVERALL_UTILIZATION_OF_THE_BAR_FIELD_NUMBER: _ClassVar[int]
    bar_specific_data: _containers.RepeatedCompositeFieldContainer[BarExtraDataRecord]
    bar_type: _steel_output_pb2.BarSectionType
    index_of_combination_of_the_maximal_utilization_of_the_bar: int
    is_charred_section_too_small: bool
    load_combination_design_calculation_results: _containers.RepeatedCompositeFieldContainer[CombDesignCalcVaryingRecord]
    number_of_load_combination: int
    number_of_sections: int
    object_unique_id: int
    overall_utilization_of_the_bar: float
    def __init__(self, object_unique_id: _Optional[int] = ..., overall_utilization_of_the_bar: _Optional[float] = ..., index_of_combination_of_the_maximal_utilization_of_the_bar: _Optional[int] = ..., number_of_load_combination: _Optional[int] = ..., load_combination_design_calculation_results: _Optional[_Iterable[_Union[CombDesignCalcVaryingRecord, _Mapping]]] = ..., bar_type: _Optional[_Union[_steel_output_pb2.BarSectionType, str]] = ..., is_charred_section_too_small: bool = ..., number_of_sections: _Optional[int] = ..., bar_specific_data: _Optional[_Iterable[_Union[BarExtraDataRecord, _Mapping]]] = ...) -> None: ...
