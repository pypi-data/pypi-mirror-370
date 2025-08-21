from FEMDesign import analysis_data_pb2 as _analysis_data_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
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
ALIGNMENT_BOTTOM: Alignment
ALIGNMENT_CENTER: Alignment
ALIGNMENT_TOP: Alignment
BAR_SECTION_TYPE_UNIFORM: BarSectionType
BAR_SECTION_TYPE_VARIABLE: BarSectionType
CURVE_A: Curve
CURVE_A0: Curve
CURVE_B: Curve
CURVE_C: Curve
CURVE_D: Curve
CURVE_L_T_A: CurveLT
CURVE_L_T_B: CurveLT
CURVE_L_T_C: CurveLT
CURVE_L_T_D: CurveLT
DESCRIPTOR: _descriptor.FileDescriptor
INTERACTION_METHOD_1: InteractionMethod
INTERACTION_METHOD_2: InteractionMethod
LIMIT_STATE_ACCIDENTAL: LimitState
LIMIT_STATE_CHARACTERISTIC: LimitState
LIMIT_STATE_FREQUENT: LimitState
LIMIT_STATE_QUASI_PERMANENT: LimitState
LIMIT_STATE_SEISMIC: LimitState
LIMIT_STATE_ULTIMATE: LimitState
SHEAR_RESISTANCE_HOLLOW: ShearResistanceEnum
SHEAR_RESISTANCE_I_LIKE: ShearResistanceEnum
SHEAR_RESISTANCE_UNSPECIFIED: ShearResistanceEnum
SHEAR_RESISTANCE_U_LIKE: ShearResistanceEnum
SHEAR_STRESS_CHECK_RELEVANT_NO: ShearStressCheckRelevant
SHEAR_STRESS_CHECK_RELEVANT_NO_BECAUSE_WEB_BUCKLING: ShearStressCheckRelevant
SHEAR_STRESS_CHECK_RELEVANT_YES: ShearStressCheckRelevant
STAT_SYS_CANTILEVER: StatSys
STAT_SYS_SIMPLE_SUPPORTED: StatSys
ST_BAR_WEB_RELEVANT_NO: StBarWebRelevant
ST_BAR_WEB_RELEVANT_NO_STIFF_LIMIT: StBarWebRelevant
ST_BAR_WEB_RELEVANT_NO_UNSTIFF_LIMIT: StBarWebRelevant
ST_BAR_WEB_RELEVANT_YES: StBarWebRelevant

class BarExtraDataRecord(_message.Message):
    __slots__ = ["cross_section_data_record", "fire_data_record", "material_data_record"]
    CROSS_SECTION_DATA_RECORD_FIELD_NUMBER: _ClassVar[int]
    FIRE_DATA_RECORD_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_DATA_RECORD_FIELD_NUMBER: _ClassVar[int]
    cross_section_data_record: CrossSectionDataRecord
    fire_data_record: FireDataRecord
    material_data_record: MaterialDataRecord
    def __init__(self, cross_section_data_record: _Optional[_Union[CrossSectionDataRecord, _Mapping]] = ..., material_data_record: _Optional[_Union[MaterialDataRecord, _Mapping]] = ..., fire_data_record: _Optional[_Union[FireDataRecord, _Mapping]] = ...) -> None: ...

class Boolean2D(_message.Message):
    __slots__ = ["one", "two"]
    ONE_FIELD_NUMBER: _ClassVar[int]
    TWO_FIELD_NUMBER: _ClassVar[int]
    one: bool
    two: bool
    def __init__(self, one: bool = ..., two: bool = ...) -> None: ...

class BooleanYZ(_message.Message):
    __slots__ = ["y", "z"]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    y: bool
    z: bool
    def __init__(self, y: bool = ..., z: bool = ...) -> None: ...

class BucklingShapes(_message.Message):
    __slots__ = ["flexural1", "flexural2", "flexural_torsional", "lateral_torsional_bottum", "lateral_torsional_top"]
    FLEXURAL1_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL2_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_TORSIONAL_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_BOTTUM_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_TOP_FIELD_NUMBER: _ClassVar[int]
    flexural1: Curve
    flexural2: Curve
    flexural_torsional: Curve
    lateral_torsional_bottum: CurveLT
    lateral_torsional_top: CurveLT
    def __init__(self, flexural1: _Optional[_Union[Curve, str]] = ..., flexural2: _Optional[_Union[Curve, str]] = ..., flexural_torsional: _Optional[_Union[Curve, str]] = ..., lateral_torsional_top: _Optional[_Union[CurveLT, str]] = ..., lateral_torsional_bottum: _Optional[_Union[CurveLT, str]] = ...) -> None: ...

class CombDesignCalcRecord(_message.Message):
    __slots__ = ["gamma_m0", "gamma_m1", "gamma_m2", "gamma_m_fi", "is_not_calculated", "limit_state", "number_of_sections", "order_number", "second_order", "section_class", "section_design_calc", "utilization"]
    GAMMA_M0_FIELD_NUMBER: _ClassVar[int]
    GAMMA_M1_FIELD_NUMBER: _ClassVar[int]
    GAMMA_M2_FIELD_NUMBER: _ClassVar[int]
    GAMMA_M_FI_FIELD_NUMBER: _ClassVar[int]
    IS_NOT_CALCULATED_FIELD_NUMBER: _ClassVar[int]
    LIMIT_STATE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    ORDER_NUMBER_FIELD_NUMBER: _ClassVar[int]
    SECOND_ORDER_FIELD_NUMBER: _ClassVar[int]
    SECTION_CLASS_FIELD_NUMBER: _ClassVar[int]
    SECTION_DESIGN_CALC_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    gamma_m0: float
    gamma_m1: float
    gamma_m2: float
    gamma_m_fi: float
    is_not_calculated: bool
    limit_state: LimitState
    number_of_sections: int
    order_number: int
    second_order: bool
    section_class: _containers.RepeatedCompositeFieldContainer[SectionClassRecord]
    section_design_calc: _containers.RepeatedCompositeFieldContainer[SectionDesignCalcRecord]
    utilization: float
    def __init__(self, is_not_calculated: bool = ..., order_number: _Optional[int] = ..., limit_state: _Optional[_Union[LimitState, str]] = ..., second_order: bool = ..., utilization: _Optional[float] = ..., gamma_m0: _Optional[float] = ..., gamma_m1: _Optional[float] = ..., gamma_m2: _Optional[float] = ..., gamma_m_fi: _Optional[float] = ..., number_of_sections: _Optional[int] = ..., section_class: _Optional[_Iterable[_Union[SectionClassRecord, _Mapping]]] = ..., section_design_calc: _Optional[_Iterable[_Union[SectionDesignCalcRecord, _Mapping]]] = ...) -> None: ...

class CrossSectionDataRecord(_message.Message):
    __slots__ = ["ay", "az", "hs", "hw", "lfc", "lft", "r_a", "r_beta", "r_i", "r_it", "r_iw", "r_iyz", "r_p", "r_w1_el", "r_w2_el", "r_w_pl", "ri12", "ry0", "rz0", "tw"]
    AY_FIELD_NUMBER: _ClassVar[int]
    AZ_FIELD_NUMBER: _ClassVar[int]
    HS_FIELD_NUMBER: _ClassVar[int]
    HW_FIELD_NUMBER: _ClassVar[int]
    LFC_FIELD_NUMBER: _ClassVar[int]
    LFT_FIELD_NUMBER: _ClassVar[int]
    RI12_FIELD_NUMBER: _ClassVar[int]
    RY0_FIELD_NUMBER: _ClassVar[int]
    RZ0_FIELD_NUMBER: _ClassVar[int]
    R_A_FIELD_NUMBER: _ClassVar[int]
    R_BETA_FIELD_NUMBER: _ClassVar[int]
    R_IT_FIELD_NUMBER: _ClassVar[int]
    R_IW_FIELD_NUMBER: _ClassVar[int]
    R_IYZ_FIELD_NUMBER: _ClassVar[int]
    R_I_FIELD_NUMBER: _ClassVar[int]
    R_P_FIELD_NUMBER: _ClassVar[int]
    R_W1_EL_FIELD_NUMBER: _ClassVar[int]
    R_W2_EL_FIELD_NUMBER: _ClassVar[int]
    R_W_PL_FIELD_NUMBER: _ClassVar[int]
    TW_FIELD_NUMBER: _ClassVar[int]
    ay: float
    az: float
    hs: float
    hw: float
    lfc: float
    lft: float
    r_a: float
    r_beta: float
    r_i: Vector2D
    r_it: float
    r_iw: float
    r_iyz: Vector2D
    r_p: float
    r_w1_el: Vector2D
    r_w2_el: Vector2D
    r_w_pl: Vector2D
    ri12: Vector2D
    ry0: float
    rz0: float
    tw: float
    def __init__(self, r_beta: _Optional[float] = ..., r_p: _Optional[float] = ..., r_a: _Optional[float] = ..., r_iyz: _Optional[_Union[Vector2D, _Mapping]] = ..., ri12: _Optional[_Union[Vector2D, _Mapping]] = ..., r_it: _Optional[float] = ..., r_iw: _Optional[float] = ..., r_i: _Optional[_Union[Vector2D, _Mapping]] = ..., ry0: _Optional[float] = ..., rz0: _Optional[float] = ..., r_w_pl: _Optional[_Union[Vector2D, _Mapping]] = ..., r_w1_el: _Optional[_Union[Vector2D, _Mapping]] = ..., r_w2_el: _Optional[_Union[Vector2D, _Mapping]] = ..., lfc: _Optional[float] = ..., lft: _Optional[float] = ..., hs: _Optional[float] = ..., ay: _Optional[float] = ..., az: _Optional[float] = ..., hw: _Optional[float] = ..., tw: _Optional[float] = ...) -> None: ...

class FireDataRecord(_message.Message):
    __slots__ = ["adaption_factors", "gas_temperature", "member_temp_protechted", "member_temp_unprotechted"]
    ADAPTION_FACTORS_FIELD_NUMBER: _ClassVar[int]
    GAS_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TEMP_PROTECHTED_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TEMP_UNPROTECHTED_FIELD_NUMBER: _ClassVar[int]
    adaption_factors: Vector2D
    gas_temperature: GasTemperature
    member_temp_protechted: MemberTemperatureProtechted
    member_temp_unprotechted: MemberTemperatureUnprotechted
    def __init__(self, gas_temperature: _Optional[_Union[GasTemperature, _Mapping]] = ..., member_temp_unprotechted: _Optional[_Union[MemberTemperatureUnprotechted, _Mapping]] = ..., member_temp_protechted: _Optional[_Union[MemberTemperatureProtechted, _Mapping]] = ..., adaption_factors: _Optional[_Union[Vector2D, _Mapping]] = ...) -> None: ...

class GasTemperature(_message.Message):
    __slots__ = ["parametric", "section_exposion", "temp_gas", "temperature_curve", "treq", "v_graph_gas_temp"]
    PARAMETRIC_FIELD_NUMBER: _ClassVar[int]
    SECTION_EXPOSION_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_CURVE_FIELD_NUMBER: _ClassVar[int]
    TEMP_GAS_FIELD_NUMBER: _ClassVar[int]
    TREQ_FIELD_NUMBER: _ClassVar[int]
    V_GRAPH_GAS_TEMP_FIELD_NUMBER: _ClassVar[int]
    parametric: Parametric
    section_exposion: int
    temp_gas: float
    temperature_curve: int
    treq: float
    v_graph_gas_temp: TVPointW
    def __init__(self, temperature_curve: _Optional[int] = ..., parametric: _Optional[_Union[Parametric, _Mapping]] = ..., v_graph_gas_temp: _Optional[_Union[TVPointW, _Mapping]] = ..., treq: _Optional[float] = ..., temp_gas: _Optional[float] = ..., section_exposion: _Optional[int] = ...) -> None: ...

class Information(_message.Message):
    __slots__ = ["bar_extra_data_record", "bar_name", "barid", "beta", "buckling_shapes", "comb_design_calc_record", "etawb", "interaction_method", "kfl", "lambda_l_t0", "material_name", "max_loadcombination_index", "max_utilization", "ncomb", "nsec", "section_name", "torsional_sharpe", "varying_bar", "virtual_stiffeners"]
    BARID_FIELD_NUMBER: _ClassVar[int]
    BAR_EXTRA_DATA_RECORD_FIELD_NUMBER: _ClassVar[int]
    BAR_NAME_FIELD_NUMBER: _ClassVar[int]
    BETA_FIELD_NUMBER: _ClassVar[int]
    BUCKLING_SHAPES_FIELD_NUMBER: _ClassVar[int]
    COMB_DESIGN_CALC_RECORD_FIELD_NUMBER: _ClassVar[int]
    ETAWB_FIELD_NUMBER: _ClassVar[int]
    INTERACTION_METHOD_FIELD_NUMBER: _ClassVar[int]
    KFL_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_L_T0_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_NAME_FIELD_NUMBER: _ClassVar[int]
    MAX_LOADCOMBINATION_INDEX_FIELD_NUMBER: _ClassVar[int]
    MAX_UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    NCOMB_FIELD_NUMBER: _ClassVar[int]
    NSEC_FIELD_NUMBER: _ClassVar[int]
    SECTION_NAME_FIELD_NUMBER: _ClassVar[int]
    TORSIONAL_SHARPE_FIELD_NUMBER: _ClassVar[int]
    VARYING_BAR_FIELD_NUMBER: _ClassVar[int]
    VIRTUAL_STIFFENERS_FIELD_NUMBER: _ClassVar[int]
    bar_extra_data_record: _containers.RepeatedCompositeFieldContainer[BarExtraDataRecord]
    bar_name: str
    barid: int
    beta: float
    buckling_shapes: BucklingShapes
    comb_design_calc_record: _containers.RepeatedCompositeFieldContainer[CombDesignCalcRecord]
    etawb: float
    interaction_method: InteractionMethod
    kfl: float
    lambda_l_t0: float
    material_name: str
    max_loadcombination_index: int
    max_utilization: float
    ncomb: int
    nsec: int
    section_name: str
    torsional_sharpe: ShearResistanceEnum
    varying_bar: BarSectionType
    virtual_stiffeners: VirtualStiffeners
    def __init__(self, barid: _Optional[int] = ..., max_utilization: _Optional[float] = ..., max_loadcombination_index: _Optional[int] = ..., ncomb: _Optional[int] = ..., comb_design_calc_record: _Optional[_Iterable[_Union[CombDesignCalcRecord, _Mapping]]] = ..., varying_bar: _Optional[_Union[BarSectionType, str]] = ..., bar_name: _Optional[str] = ..., section_name: _Optional[str] = ..., material_name: _Optional[str] = ..., virtual_stiffeners: _Optional[_Union[VirtualStiffeners, _Mapping]] = ..., buckling_shapes: _Optional[_Union[BucklingShapes, _Mapping]] = ..., torsional_sharpe: _Optional[_Union[ShearResistanceEnum, str]] = ..., kfl: _Optional[float] = ..., etawb: _Optional[float] = ..., interaction_method: _Optional[_Union[InteractionMethod, str]] = ..., lambda_l_t0: _Optional[float] = ..., beta: _Optional[float] = ..., nsec: _Optional[int] = ..., bar_extra_data_record: _Optional[_Iterable[_Union[BarExtraDataRecord, _Mapping]]] = ...) -> None: ...

class MaterialDataRecord(_message.Message):
    __slots__ = ["k_e_theta", "kp02_theta", "kp_theta", "ky_theta", "r_e", "r_g", "r_gamma_fi", "r_gamma_m0", "r_gamma_m1", "r_gamma_m2", "r_lambda1", "repsilon", "rf_y"]
    KP02_THETA_FIELD_NUMBER: _ClassVar[int]
    KP_THETA_FIELD_NUMBER: _ClassVar[int]
    KY_THETA_FIELD_NUMBER: _ClassVar[int]
    K_E_THETA_FIELD_NUMBER: _ClassVar[int]
    REPSILON_FIELD_NUMBER: _ClassVar[int]
    RF_Y_FIELD_NUMBER: _ClassVar[int]
    R_E_FIELD_NUMBER: _ClassVar[int]
    R_GAMMA_FI_FIELD_NUMBER: _ClassVar[int]
    R_GAMMA_M0_FIELD_NUMBER: _ClassVar[int]
    R_GAMMA_M1_FIELD_NUMBER: _ClassVar[int]
    R_GAMMA_M2_FIELD_NUMBER: _ClassVar[int]
    R_G_FIELD_NUMBER: _ClassVar[int]
    R_LAMBDA1_FIELD_NUMBER: _ClassVar[int]
    k_e_theta: float
    kp02_theta: float
    kp_theta: float
    ky_theta: float
    r_e: float
    r_g: float
    r_gamma_fi: float
    r_gamma_m0: float
    r_gamma_m1: float
    r_gamma_m2: float
    r_lambda1: float
    repsilon: float
    rf_y: float
    def __init__(self, rf_y: _Optional[float] = ..., repsilon: _Optional[float] = ..., r_lambda1: _Optional[float] = ..., r_e: _Optional[float] = ..., r_g: _Optional[float] = ..., r_gamma_m0: _Optional[float] = ..., r_gamma_m1: _Optional[float] = ..., r_gamma_m2: _Optional[float] = ..., r_gamma_fi: _Optional[float] = ..., ky_theta: _Optional[float] = ..., kp02_theta: _Optional[float] = ..., kp_theta: _Optional[float] = ..., k_e_theta: _Optional[float] = ...) -> None: ...

class MemberTemperatureProtechted(_message.Message):
    __slots__ = ["ap", "ap_v", "cp", "dp", "encasement", "lambdap", "rhop", "temp_member", "v_graph_member_temperature"]
    AP_FIELD_NUMBER: _ClassVar[int]
    AP_V_FIELD_NUMBER: _ClassVar[int]
    CP_FIELD_NUMBER: _ClassVar[int]
    DP_FIELD_NUMBER: _ClassVar[int]
    ENCASEMENT_FIELD_NUMBER: _ClassVar[int]
    LAMBDAP_FIELD_NUMBER: _ClassVar[int]
    RHOP_FIELD_NUMBER: _ClassVar[int]
    TEMP_MEMBER_FIELD_NUMBER: _ClassVar[int]
    V_GRAPH_MEMBER_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    ap: float
    ap_v: float
    cp: float
    dp: float
    encasement: int
    lambdap: float
    rhop: float
    temp_member: float
    v_graph_member_temperature: TVPointW
    def __init__(self, dp: _Optional[float] = ..., encasement: _Optional[int] = ..., cp: _Optional[float] = ..., rhop: _Optional[float] = ..., lambdap: _Optional[float] = ..., ap: _Optional[float] = ..., ap_v: _Optional[float] = ..., v_graph_member_temperature: _Optional[_Union[TVPointW, _Mapping]] = ..., temp_member: _Optional[float] = ...) -> None: ...

class MemberTemperatureUnprotechted(_message.Message):
    __slots__ = ["alphac", "am", "am_b", "am_v", "am_v_b", "dt", "epsf", "epsm", "f_deflection_crit_essential", "f_section_convex", "f_section_i", "ksh", "phi", "rhoa", "v"]
    ALPHAC_FIELD_NUMBER: _ClassVar[int]
    AM_B_FIELD_NUMBER: _ClassVar[int]
    AM_FIELD_NUMBER: _ClassVar[int]
    AM_V_B_FIELD_NUMBER: _ClassVar[int]
    AM_V_FIELD_NUMBER: _ClassVar[int]
    DT_FIELD_NUMBER: _ClassVar[int]
    EPSF_FIELD_NUMBER: _ClassVar[int]
    EPSM_FIELD_NUMBER: _ClassVar[int]
    F_DEFLECTION_CRIT_ESSENTIAL_FIELD_NUMBER: _ClassVar[int]
    F_SECTION_CONVEX_FIELD_NUMBER: _ClassVar[int]
    F_SECTION_I_FIELD_NUMBER: _ClassVar[int]
    KSH_FIELD_NUMBER: _ClassVar[int]
    PHI_FIELD_NUMBER: _ClassVar[int]
    RHOA_FIELD_NUMBER: _ClassVar[int]
    V_FIELD_NUMBER: _ClassVar[int]
    alphac: float
    am: float
    am_b: float
    am_v: float
    am_v_b: float
    dt: float
    epsf: float
    epsm: float
    f_deflection_crit_essential: bool
    f_section_convex: bool
    f_section_i: bool
    ksh: float
    phi: float
    rhoa: float
    v: float
    def __init__(self, ksh: _Optional[float] = ..., am: _Optional[float] = ..., v: _Optional[float] = ..., am_v: _Optional[float] = ..., am_b: _Optional[float] = ..., am_v_b: _Optional[float] = ..., dt: _Optional[float] = ..., rhoa: _Optional[float] = ..., f_section_i: bool = ..., f_section_convex: bool = ..., epsm: _Optional[float] = ..., epsf: _Optional[float] = ..., alphac: _Optional[float] = ..., phi: _Optional[float] = ..., f_deflection_crit_essential: bool = ...) -> None: ...

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

class PointStress(_message.Message):
    __slots__ = ["s_zigma_yx", "s_zigma_zx", "tau_xy", "tau_xz", "tau_yy", "tau_yz", "tau_zy", "tau_zz"]
    S_ZIGMA_YX_FIELD_NUMBER: _ClassVar[int]
    S_ZIGMA_ZX_FIELD_NUMBER: _ClassVar[int]
    TAU_XY_FIELD_NUMBER: _ClassVar[int]
    TAU_XZ_FIELD_NUMBER: _ClassVar[int]
    TAU_YY_FIELD_NUMBER: _ClassVar[int]
    TAU_YZ_FIELD_NUMBER: _ClassVar[int]
    TAU_ZY_FIELD_NUMBER: _ClassVar[int]
    TAU_ZZ_FIELD_NUMBER: _ClassVar[int]
    s_zigma_yx: float
    s_zigma_zx: float
    tau_xy: float
    tau_xz: float
    tau_yy: float
    tau_yz: float
    tau_zy: float
    tau_zz: float
    def __init__(self, tau_yy: _Optional[float] = ..., tau_yz: _Optional[float] = ..., tau_zy: _Optional[float] = ..., tau_zz: _Optional[float] = ..., tau_xy: _Optional[float] = ..., tau_xz: _Optional[float] = ..., s_zigma_yx: _Optional[float] = ..., s_zigma_zx: _Optional[float] = ...) -> None: ...

class SectionClassRecord(_message.Message):
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

class SectionDesignCalcRecord(_message.Message):
    __slots__ = ["ar_int_forces", "id_gmax_comb", "r_util", "r_util_f_b", "r_util_f_t_b", "r_util_i_a", "r_util_i_a2nd", "r_util_l_b_t_bottom", "r_util_l_t_b_top", "r_util_n", "r_util_norm", "r_util_shear", "r_util_sigma", "r_util_t", "r_util_tau", "r_util_v", "st_bar_interaction", "st_bar_interaction2nd", "st_bar_torsional_bottom", "st_bar_torsional_top", "st_bar_web", "st_c_s_resist", "st_effective_c_s", "st_flexural", "st_flexural_torsional", "x"]
    AR_INT_FORCES_FIELD_NUMBER: _ClassVar[int]
    ID_GMAX_COMB_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_F_B_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_F_T_B_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_I_A2ND_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_I_A_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_L_B_T_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_L_T_B_TOP_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_NORM_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_N_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_SHEAR_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_SIGMA_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_TAU_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_T_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_V_FIELD_NUMBER: _ClassVar[int]
    ST_BAR_INTERACTION2ND_FIELD_NUMBER: _ClassVar[int]
    ST_BAR_INTERACTION_FIELD_NUMBER: _ClassVar[int]
    ST_BAR_TORSIONAL_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    ST_BAR_TORSIONAL_TOP_FIELD_NUMBER: _ClassVar[int]
    ST_BAR_WEB_FIELD_NUMBER: _ClassVar[int]
    ST_C_S_RESIST_FIELD_NUMBER: _ClassVar[int]
    ST_EFFECTIVE_C_S_FIELD_NUMBER: _ClassVar[int]
    ST_FLEXURAL_FIELD_NUMBER: _ClassVar[int]
    ST_FLEXURAL_TORSIONAL_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    ar_int_forces: _analysis_data_pb2.Force
    id_gmax_comb: int
    r_util: float
    r_util_f_b: Vector2D
    r_util_f_t_b: float
    r_util_i_a: Vector2D
    r_util_i_a2nd: float
    r_util_l_b_t_bottom: float
    r_util_l_t_b_top: float
    r_util_n: float
    r_util_norm: float
    r_util_shear: float
    r_util_sigma: float
    r_util_t: float
    r_util_tau: float
    r_util_v: Vector2D
    st_bar_interaction: StBarInteraction
    st_bar_interaction2nd: StBarInteraction2nd
    st_bar_torsional_bottom: StBarTorsional
    st_bar_torsional_top: StBarTorsional
    st_bar_web: StBarWeb
    st_c_s_resist: StBarCSResist
    st_effective_c_s: StBarEffectiveCS
    st_flexural: StBarFlexural
    st_flexural_torsional: StBarFlexuralTorsional
    x: float
    def __init__(self, x: _Optional[float] = ..., r_util: _Optional[float] = ..., id_gmax_comb: _Optional[int] = ..., r_util_v: _Optional[_Union[Vector2D, _Mapping]] = ..., r_util_tau: _Optional[float] = ..., r_util_t: _Optional[float] = ..., r_util_n: _Optional[float] = ..., r_util_norm: _Optional[float] = ..., r_util_sigma: _Optional[float] = ..., r_util_f_b: _Optional[_Union[Vector2D, _Mapping]] = ..., r_util_f_t_b: _Optional[float] = ..., r_util_l_t_b_top: _Optional[float] = ..., r_util_l_b_t_bottom: _Optional[float] = ..., r_util_shear: _Optional[float] = ..., r_util_i_a: _Optional[_Union[Vector2D, _Mapping]] = ..., r_util_i_a2nd: _Optional[float] = ..., ar_int_forces: _Optional[_Union[_analysis_data_pb2.Force, _Mapping]] = ..., st_effective_c_s: _Optional[_Union[StBarEffectiveCS, _Mapping]] = ..., st_c_s_resist: _Optional[_Union[StBarCSResist, _Mapping]] = ..., st_flexural: _Optional[_Union[StBarFlexural, _Mapping]] = ..., st_flexural_torsional: _Optional[_Union[StBarFlexuralTorsional, _Mapping]] = ..., st_bar_torsional_top: _Optional[_Union[StBarTorsional, _Mapping]] = ..., st_bar_torsional_bottom: _Optional[_Union[StBarTorsional, _Mapping]] = ..., st_bar_interaction: _Optional[_Union[StBarInteraction, _Mapping]] = ..., st_bar_interaction2nd: _Optional[_Union[StBarInteraction2nd, _Mapping]] = ..., st_bar_web: _Optional[_Union[StBarWeb, _Mapping]] = ...) -> None: ...

class StBarCSResist(_message.Message):
    __slots__ = ["alpha", "beta", "f_calculated", "f_m_n_rd_reduced", "f_sigma", "f_use641", "f_v", "m_n_rd", "n_pl_rd", "n_pl_v_rd", "n_w_pl_rd", "r_a_v", "r_m_ed", "r_m_pl_rd", "r_m_rd", "r_m_rd_fi", "r_n_ed", "r_n_rd", "r_n_rd_fi", "r_rho", "r_sigma_x_ed", "r_t_ed", "r_t_rd", "r_t_rd_fi", "r_tau_ed", "r_tau_rd", "r_tau_s_ed", "r_util_n", "r_util_norm", "r_util_t", "r_util_tau", "r_util_v", "r_v_ed", "r_v_pl_rd", "r_v_pl_rd_fi", "r_v_pl_t_rd", "r_v_pl_t_rd_fi", "rtau_rd_fi", "rtau_t_ed", "rtau_w_ed", "shape", "tau"]
    ALPHA_FIELD_NUMBER: _ClassVar[int]
    BETA_FIELD_NUMBER: _ClassVar[int]
    F_CALCULATED_FIELD_NUMBER: _ClassVar[int]
    F_M_N_RD_REDUCED_FIELD_NUMBER: _ClassVar[int]
    F_SIGMA_FIELD_NUMBER: _ClassVar[int]
    F_USE641_FIELD_NUMBER: _ClassVar[int]
    F_V_FIELD_NUMBER: _ClassVar[int]
    M_N_RD_FIELD_NUMBER: _ClassVar[int]
    N_PL_RD_FIELD_NUMBER: _ClassVar[int]
    N_PL_V_RD_FIELD_NUMBER: _ClassVar[int]
    N_W_PL_RD_FIELD_NUMBER: _ClassVar[int]
    RTAU_RD_FI_FIELD_NUMBER: _ClassVar[int]
    RTAU_T_ED_FIELD_NUMBER: _ClassVar[int]
    RTAU_W_ED_FIELD_NUMBER: _ClassVar[int]
    R_A_V_FIELD_NUMBER: _ClassVar[int]
    R_M_ED_FIELD_NUMBER: _ClassVar[int]
    R_M_PL_RD_FIELD_NUMBER: _ClassVar[int]
    R_M_RD_FIELD_NUMBER: _ClassVar[int]
    R_M_RD_FI_FIELD_NUMBER: _ClassVar[int]
    R_N_ED_FIELD_NUMBER: _ClassVar[int]
    R_N_RD_FIELD_NUMBER: _ClassVar[int]
    R_N_RD_FI_FIELD_NUMBER: _ClassVar[int]
    R_RHO_FIELD_NUMBER: _ClassVar[int]
    R_SIGMA_X_ED_FIELD_NUMBER: _ClassVar[int]
    R_TAU_ED_FIELD_NUMBER: _ClassVar[int]
    R_TAU_RD_FIELD_NUMBER: _ClassVar[int]
    R_TAU_S_ED_FIELD_NUMBER: _ClassVar[int]
    R_T_ED_FIELD_NUMBER: _ClassVar[int]
    R_T_RD_FIELD_NUMBER: _ClassVar[int]
    R_T_RD_FI_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_NORM_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_N_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_TAU_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_T_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_V_FIELD_NUMBER: _ClassVar[int]
    R_V_ED_FIELD_NUMBER: _ClassVar[int]
    R_V_PL_RD_FIELD_NUMBER: _ClassVar[int]
    R_V_PL_RD_FI_FIELD_NUMBER: _ClassVar[int]
    R_V_PL_T_RD_FIELD_NUMBER: _ClassVar[int]
    R_V_PL_T_RD_FI_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    TAU_FIELD_NUMBER: _ClassVar[int]
    alpha: float
    beta: float
    f_calculated: bool
    f_m_n_rd_reduced: BooleanYZ
    f_sigma: bool
    f_use641: bool
    f_v: Boolean2D
    m_n_rd: Vector2D
    n_pl_rd: float
    n_pl_v_rd: float
    n_w_pl_rd: float
    r_a_v: Vector2D
    r_m_ed: Vector2D
    r_m_pl_rd: Vector2D
    r_m_rd: Vector2D
    r_m_rd_fi: Vector2D
    r_n_ed: float
    r_n_rd: float
    r_n_rd_fi: float
    r_rho: Vector2D
    r_sigma_x_ed: float
    r_t_ed: float
    r_t_rd: float
    r_t_rd_fi: float
    r_tau_ed: float
    r_tau_rd: float
    r_tau_s_ed: float
    r_util_n: float
    r_util_norm: float
    r_util_t: float
    r_util_tau: float
    r_util_v: Vector2D
    r_v_ed: Vector2D
    r_v_pl_rd: Vector2D
    r_v_pl_rd_fi: Vector2D
    r_v_pl_t_rd: Vector2D
    r_v_pl_t_rd_fi: Vector2D
    rtau_rd_fi: float
    rtau_t_ed: float
    rtau_w_ed: float
    shape: ShearResistanceEnum
    tau: ShearStressCheckRelevant
    def __init__(self, f_calculated: bool = ..., r_util_v: _Optional[_Union[Vector2D, _Mapping]] = ..., r_util_tau: _Optional[float] = ..., r_util_t: _Optional[float] = ..., r_util_n: _Optional[float] = ..., r_util_norm: _Optional[float] = ..., tau: _Optional[_Union[ShearStressCheckRelevant, str]] = ..., f_v: _Optional[_Union[Boolean2D, _Mapping]] = ..., f_sigma: bool = ..., r_v_ed: _Optional[_Union[Vector2D, _Mapping]] = ..., r_t_ed: _Optional[float] = ..., r_v_pl_t_rd: _Optional[_Union[Vector2D, _Mapping]] = ..., r_v_pl_rd: _Optional[_Union[Vector2D, _Mapping]] = ..., r_t_rd: _Optional[float] = ..., rtau_t_ed: _Optional[float] = ..., rtau_w_ed: _Optional[float] = ..., r_a_v: _Optional[_Union[Vector2D, _Mapping]] = ..., shape: _Optional[_Union[ShearResistanceEnum, str]] = ..., r_tau_ed: _Optional[float] = ..., r_tau_rd: _Optional[float] = ..., r_n_ed: _Optional[float] = ..., r_m_ed: _Optional[_Union[Vector2D, _Mapping]] = ..., r_m_pl_rd: _Optional[_Union[Vector2D, _Mapping]] = ..., r_n_rd: _Optional[float] = ..., r_m_rd: _Optional[_Union[Vector2D, _Mapping]] = ..., r_rho: _Optional[_Union[Vector2D, _Mapping]] = ..., r_sigma_x_ed: _Optional[float] = ..., r_tau_s_ed: _Optional[float] = ..., f_use641: bool = ..., n_pl_rd: _Optional[float] = ..., n_pl_v_rd: _Optional[float] = ..., n_w_pl_rd: _Optional[float] = ..., f_m_n_rd_reduced: _Optional[_Union[BooleanYZ, _Mapping]] = ..., m_n_rd: _Optional[_Union[Vector2D, _Mapping]] = ..., alpha: _Optional[float] = ..., beta: _Optional[float] = ..., r_v_pl_t_rd_fi: _Optional[_Union[Vector2D, _Mapping]] = ..., r_v_pl_rd_fi: _Optional[_Union[Vector2D, _Mapping]] = ..., r_t_rd_fi: _Optional[float] = ..., rtau_rd_fi: _Optional[float] = ..., r_n_rd_fi: _Optional[float] = ..., r_m_rd_fi: _Optional[_Union[Vector2D, _Mapping]] = ...) -> None: ...

class StBarEffectiveCS(_message.Message):
    __slots__ = ["f_calculated", "r_a_eff", "r_w_eff_c", "r_w_eff_t", "re_n", "rl_eff"]
    F_CALCULATED_FIELD_NUMBER: _ClassVar[int]
    RE_N_FIELD_NUMBER: _ClassVar[int]
    RL_EFF_FIELD_NUMBER: _ClassVar[int]
    R_A_EFF_FIELD_NUMBER: _ClassVar[int]
    R_W_EFF_C_FIELD_NUMBER: _ClassVar[int]
    R_W_EFF_T_FIELD_NUMBER: _ClassVar[int]
    f_calculated: bool
    r_a_eff: float
    r_w_eff_c: Vector2D
    r_w_eff_t: Vector2D
    re_n: Vector2D
    rl_eff: Vector2D
    def __init__(self, f_calculated: bool = ..., r_a_eff: _Optional[float] = ..., rl_eff: _Optional[_Union[Vector2D, _Mapping]] = ..., re_n: _Optional[_Union[Vector2D, _Mapping]] = ..., r_w_eff_c: _Optional[_Union[Vector2D, _Mapping]] = ..., r_w_eff_t: _Optional[_Union[Vector2D, _Mapping]] = ...) -> None: ...

class StBarFlexural(_message.Message):
    __slots__ = ["f_calculated", "lambda_theta", "lambda_theta_interaction", "r_alfa", "r_chi", "r_lambda", "r_lambda_over", "r_lcr", "r_nb_rd", "r_ncr", "r_phi", "r_util"]
    F_CALCULATED_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_THETA_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_THETA_INTERACTION_FIELD_NUMBER: _ClassVar[int]
    R_ALFA_FIELD_NUMBER: _ClassVar[int]
    R_CHI_FIELD_NUMBER: _ClassVar[int]
    R_LAMBDA_FIELD_NUMBER: _ClassVar[int]
    R_LAMBDA_OVER_FIELD_NUMBER: _ClassVar[int]
    R_LCR_FIELD_NUMBER: _ClassVar[int]
    R_NB_RD_FIELD_NUMBER: _ClassVar[int]
    R_NCR_FIELD_NUMBER: _ClassVar[int]
    R_PHI_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_FIELD_NUMBER: _ClassVar[int]
    f_calculated: bool
    lambda_theta: Vector2D
    lambda_theta_interaction: float
    r_alfa: Vector2D
    r_chi: Vector2D
    r_lambda: Vector2D
    r_lambda_over: Vector2D
    r_lcr: Vector2D
    r_nb_rd: Vector2D
    r_ncr: Vector2D
    r_phi: Vector2D
    r_util: Vector2D
    def __init__(self, f_calculated: bool = ..., r_util: _Optional[_Union[Vector2D, _Mapping]] = ..., r_nb_rd: _Optional[_Union[Vector2D, _Mapping]] = ..., r_chi: _Optional[_Union[Vector2D, _Mapping]] = ..., r_phi: _Optional[_Union[Vector2D, _Mapping]] = ..., r_alfa: _Optional[_Union[Vector2D, _Mapping]] = ..., r_lambda_over: _Optional[_Union[Vector2D, _Mapping]] = ..., r_lambda: _Optional[_Union[Vector2D, _Mapping]] = ..., r_lcr: _Optional[_Union[Vector2D, _Mapping]] = ..., r_ncr: _Optional[_Union[Vector2D, _Mapping]] = ..., lambda_theta: _Optional[_Union[Vector2D, _Mapping]] = ..., lambda_theta_interaction: _Optional[float] = ...) -> None: ...

class StBarFlexuralTorsional(_message.Message):
    __slots__ = ["f_calculated", "lambda_over", "lambda_theta", "r_alfa", "r_chi", "r_lcr", "r_nb_rd", "r_ncr_t", "r_ncr_t_f", "r_phi", "r_util", "ri02"]
    F_CALCULATED_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_OVER_FIELD_NUMBER: _ClassVar[int]
    LAMBDA_THETA_FIELD_NUMBER: _ClassVar[int]
    RI02_FIELD_NUMBER: _ClassVar[int]
    R_ALFA_FIELD_NUMBER: _ClassVar[int]
    R_CHI_FIELD_NUMBER: _ClassVar[int]
    R_LCR_FIELD_NUMBER: _ClassVar[int]
    R_NB_RD_FIELD_NUMBER: _ClassVar[int]
    R_NCR_T_FIELD_NUMBER: _ClassVar[int]
    R_NCR_T_F_FIELD_NUMBER: _ClassVar[int]
    R_PHI_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_FIELD_NUMBER: _ClassVar[int]
    f_calculated: bool
    lambda_over: float
    lambda_theta: float
    r_alfa: float
    r_chi: float
    r_lcr: float
    r_nb_rd: float
    r_ncr_t: float
    r_ncr_t_f: float
    r_phi: float
    r_util: float
    ri02: float
    def __init__(self, f_calculated: bool = ..., r_util: _Optional[float] = ..., r_nb_rd: _Optional[float] = ..., r_chi: _Optional[float] = ..., r_phi: _Optional[float] = ..., r_alfa: _Optional[float] = ..., lambda_theta: _Optional[float] = ..., lambda_over: _Optional[float] = ..., r_lcr: _Optional[float] = ..., ri02: _Optional[float] = ..., r_ncr_t: _Optional[float] = ..., r_ncr_t_f: _Optional[float] = ...) -> None: ...

class StBarInteraction(_message.Message):
    __slots__ = ["beta_m", "c11", "c12", "c21", "c22", "cm10", "cm20", "f_calculated", "psi", "r_alpha", "r_c_m", "r_c_m_l_t", "r_delta_m_ed", "r_delta_x", "r_m_ed", "r_m_ed_max", "r_m_rk", "r_n_rk", "r_psi", "r_util", "rk11", "rk12", "rk21", "rk22"]
    BETA_M_FIELD_NUMBER: _ClassVar[int]
    C11_FIELD_NUMBER: _ClassVar[int]
    C12_FIELD_NUMBER: _ClassVar[int]
    C21_FIELD_NUMBER: _ClassVar[int]
    C22_FIELD_NUMBER: _ClassVar[int]
    CM10_FIELD_NUMBER: _ClassVar[int]
    CM20_FIELD_NUMBER: _ClassVar[int]
    F_CALCULATED_FIELD_NUMBER: _ClassVar[int]
    PSI_FIELD_NUMBER: _ClassVar[int]
    RK11_FIELD_NUMBER: _ClassVar[int]
    RK12_FIELD_NUMBER: _ClassVar[int]
    RK21_FIELD_NUMBER: _ClassVar[int]
    RK22_FIELD_NUMBER: _ClassVar[int]
    R_ALPHA_FIELD_NUMBER: _ClassVar[int]
    R_C_M_FIELD_NUMBER: _ClassVar[int]
    R_C_M_L_T_FIELD_NUMBER: _ClassVar[int]
    R_DELTA_M_ED_FIELD_NUMBER: _ClassVar[int]
    R_DELTA_X_FIELD_NUMBER: _ClassVar[int]
    R_M_ED_FIELD_NUMBER: _ClassVar[int]
    R_M_ED_MAX_FIELD_NUMBER: _ClassVar[int]
    R_M_RK_FIELD_NUMBER: _ClassVar[int]
    R_N_RK_FIELD_NUMBER: _ClassVar[int]
    R_PSI_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_FIELD_NUMBER: _ClassVar[int]
    beta_m: Vector4D
    c11: float
    c12: float
    c21: float
    c22: float
    cm10: float
    cm20: float
    f_calculated: bool
    psi: Vector2D
    r_alpha: Vector4D
    r_c_m: Vector2D
    r_c_m_l_t: Vector2D
    r_delta_m_ed: Vector2D
    r_delta_x: Vector2D
    r_m_ed: Vector2D
    r_m_ed_max: Vector2D
    r_m_rk: Vector2D
    r_n_rk: float
    r_psi: Vector4D
    r_util: Vector2D
    rk11: float
    rk12: float
    rk21: float
    rk22: float
    def __init__(self, f_calculated: bool = ..., r_util: _Optional[_Union[Vector2D, _Mapping]] = ..., r_n_rk: _Optional[float] = ..., r_m_rk: _Optional[_Union[Vector2D, _Mapping]] = ..., r_m_ed: _Optional[_Union[Vector2D, _Mapping]] = ..., r_m_ed_max: _Optional[_Union[Vector2D, _Mapping]] = ..., r_delta_x: _Optional[_Union[Vector2D, _Mapping]] = ..., psi: _Optional[_Union[Vector2D, _Mapping]] = ..., r_delta_m_ed: _Optional[_Union[Vector2D, _Mapping]] = ..., r_alpha: _Optional[_Union[Vector4D, _Mapping]] = ..., r_psi: _Optional[_Union[Vector4D, _Mapping]] = ..., r_c_m: _Optional[_Union[Vector2D, _Mapping]] = ..., r_c_m_l_t: _Optional[_Union[Vector2D, _Mapping]] = ..., c11: _Optional[float] = ..., c12: _Optional[float] = ..., c21: _Optional[float] = ..., c22: _Optional[float] = ..., rk11: _Optional[float] = ..., rk12: _Optional[float] = ..., rk21: _Optional[float] = ..., rk22: _Optional[float] = ..., cm10: _Optional[float] = ..., cm20: _Optional[float] = ..., beta_m: _Optional[_Union[Vector4D, _Mapping]] = ...) -> None: ...

class StBarInteraction2nd(_message.Message):
    __slots__ = ["f_calculated", "r_util"]
    F_CALCULATED_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_FIELD_NUMBER: _ClassVar[int]
    f_calculated: bool
    r_util: float
    def __init__(self, f_calculated: bool = ..., r_util: _Optional[float] = ...) -> None: ...

class StBarTorsional(_message.Message):
    __slots__ = ["c1", "c2", "c2zg_c3zj", "c3", "curve", "curve_l_t", "f_calc_general_method", "f_calc_general_method_spec_forl", "f_calculated", "f_calculated_not_implemented", "f_top_comp", "factorf", "kw", "kz", "load_pos", "mcr", "ncr_l_t", "psi", "psi_f", "r_alfa", "r_alpha_l_t", "r_chi", "r_chi_l_t", "r_chi_l_t_basic", "r_lambda0", "r_lambda_f", "r_lambda_l_t", "r_lambda_l_t_fi", "r_lcr", "r_m_ed_max", "r_mb_rd", "r_mc_rd", "r_phi", "r_phi_l_t", "r_util", "rifz", "rkc", "zg", "zj"]
    C1_FIELD_NUMBER: _ClassVar[int]
    C2ZG_C3ZJ_FIELD_NUMBER: _ClassVar[int]
    C2_FIELD_NUMBER: _ClassVar[int]
    C3_FIELD_NUMBER: _ClassVar[int]
    CURVE_FIELD_NUMBER: _ClassVar[int]
    CURVE_L_T_FIELD_NUMBER: _ClassVar[int]
    FACTORF_FIELD_NUMBER: _ClassVar[int]
    F_CALCULATED_FIELD_NUMBER: _ClassVar[int]
    F_CALCULATED_NOT_IMPLEMENTED_FIELD_NUMBER: _ClassVar[int]
    F_CALC_GENERAL_METHOD_FIELD_NUMBER: _ClassVar[int]
    F_CALC_GENERAL_METHOD_SPEC_FORL_FIELD_NUMBER: _ClassVar[int]
    F_TOP_COMP_FIELD_NUMBER: _ClassVar[int]
    KW_FIELD_NUMBER: _ClassVar[int]
    KZ_FIELD_NUMBER: _ClassVar[int]
    LOAD_POS_FIELD_NUMBER: _ClassVar[int]
    MCR_FIELD_NUMBER: _ClassVar[int]
    NCR_L_T_FIELD_NUMBER: _ClassVar[int]
    PSI_FIELD_NUMBER: _ClassVar[int]
    PSI_F_FIELD_NUMBER: _ClassVar[int]
    RIFZ_FIELD_NUMBER: _ClassVar[int]
    RKC_FIELD_NUMBER: _ClassVar[int]
    R_ALFA_FIELD_NUMBER: _ClassVar[int]
    R_ALPHA_L_T_FIELD_NUMBER: _ClassVar[int]
    R_CHI_FIELD_NUMBER: _ClassVar[int]
    R_CHI_L_T_BASIC_FIELD_NUMBER: _ClassVar[int]
    R_CHI_L_T_FIELD_NUMBER: _ClassVar[int]
    R_LAMBDA0_FIELD_NUMBER: _ClassVar[int]
    R_LAMBDA_F_FIELD_NUMBER: _ClassVar[int]
    R_LAMBDA_L_T_FIELD_NUMBER: _ClassVar[int]
    R_LAMBDA_L_T_FI_FIELD_NUMBER: _ClassVar[int]
    R_LCR_FIELD_NUMBER: _ClassVar[int]
    R_MB_RD_FIELD_NUMBER: _ClassVar[int]
    R_MC_RD_FIELD_NUMBER: _ClassVar[int]
    R_M_ED_MAX_FIELD_NUMBER: _ClassVar[int]
    R_PHI_FIELD_NUMBER: _ClassVar[int]
    R_PHI_L_T_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_FIELD_NUMBER: _ClassVar[int]
    ZG_FIELD_NUMBER: _ClassVar[int]
    ZJ_FIELD_NUMBER: _ClassVar[int]
    c1: float
    c2: float
    c2zg_c3zj: float
    c3: float
    curve: Curve
    curve_l_t: CurveLT
    f_calc_general_method: bool
    f_calc_general_method_spec_forl: bool
    f_calculated: bool
    f_calculated_not_implemented: bool
    f_top_comp: bool
    factorf: float
    kw: float
    kz: float
    load_pos: Alignment
    mcr: float
    ncr_l_t: float
    psi: float
    psi_f: float
    r_alfa: float
    r_alpha_l_t: float
    r_chi: float
    r_chi_l_t: float
    r_chi_l_t_basic: float
    r_lambda0: float
    r_lambda_f: float
    r_lambda_l_t: float
    r_lambda_l_t_fi: float
    r_lcr: float
    r_m_ed_max: Vector2D
    r_mb_rd: float
    r_mc_rd: float
    r_phi: float
    r_phi_l_t: float
    r_util: float
    rifz: float
    rkc: float
    zg: float
    zj: float
    def __init__(self, f_calculated: bool = ..., f_calculated_not_implemented: bool = ..., r_util: _Optional[float] = ..., f_top_comp: bool = ..., rkc: _Optional[float] = ..., r_lcr: _Optional[float] = ..., rifz: _Optional[float] = ..., r_lambda_f: _Optional[float] = ..., r_m_ed_max: _Optional[_Union[Vector2D, _Mapping]] = ..., r_mc_rd: _Optional[float] = ..., r_mb_rd: _Optional[float] = ..., r_chi: _Optional[float] = ..., r_phi: _Optional[float] = ..., r_alfa: _Optional[float] = ..., curve: _Optional[_Union[Curve, str]] = ..., f_calc_general_method: bool = ..., f_calc_general_method_spec_forl: bool = ..., psi: _Optional[float] = ..., psi_f: _Optional[float] = ..., c1: _Optional[float] = ..., c2: _Optional[float] = ..., c3: _Optional[float] = ..., kz: _Optional[float] = ..., kw: _Optional[float] = ..., load_pos: _Optional[_Union[Alignment, str]] = ..., zg: _Optional[float] = ..., zj: _Optional[float] = ..., c2zg_c3zj: _Optional[float] = ..., ncr_l_t: _Optional[float] = ..., mcr: _Optional[float] = ..., r_lambda_l_t: _Optional[float] = ..., curve_l_t: _Optional[_Union[CurveLT, str]] = ..., r_alpha_l_t: _Optional[float] = ..., r_phi_l_t: _Optional[float] = ..., r_chi_l_t: _Optional[float] = ..., r_chi_l_t_basic: _Optional[float] = ..., factorf: _Optional[float] = ..., r_lambda0: _Optional[float] = ..., r_lambda_l_t_fi: _Optional[float] = ...) -> None: ...

class StBarWeb(_message.Message):
    __slots__ = ["f_calculated", "r_a_f", "r_chi", "r_lambda_w", "r_m_f_rd", "r_m_fk", "r_my_ed_max", "r_sigma_e", "r_tau_cr", "r_util", "r_v_b_rd", "r_v_bf_rd", "r_v_bw_rd", "r_v_bw_rd_fi", "ra", "rbf", "rc", "relevant", "rhw", "rk_tau", "rt", "rtf", "vz_ed"]
    F_CALCULATED_FIELD_NUMBER: _ClassVar[int]
    RA_FIELD_NUMBER: _ClassVar[int]
    RBF_FIELD_NUMBER: _ClassVar[int]
    RC_FIELD_NUMBER: _ClassVar[int]
    RELEVANT_FIELD_NUMBER: _ClassVar[int]
    RHW_FIELD_NUMBER: _ClassVar[int]
    RK_TAU_FIELD_NUMBER: _ClassVar[int]
    RTF_FIELD_NUMBER: _ClassVar[int]
    RT_FIELD_NUMBER: _ClassVar[int]
    R_A_F_FIELD_NUMBER: _ClassVar[int]
    R_CHI_FIELD_NUMBER: _ClassVar[int]
    R_LAMBDA_W_FIELD_NUMBER: _ClassVar[int]
    R_MY_ED_MAX_FIELD_NUMBER: _ClassVar[int]
    R_M_FK_FIELD_NUMBER: _ClassVar[int]
    R_M_F_RD_FIELD_NUMBER: _ClassVar[int]
    R_SIGMA_E_FIELD_NUMBER: _ClassVar[int]
    R_TAU_CR_FIELD_NUMBER: _ClassVar[int]
    R_UTIL_FIELD_NUMBER: _ClassVar[int]
    R_V_BF_RD_FIELD_NUMBER: _ClassVar[int]
    R_V_BW_RD_FIELD_NUMBER: _ClassVar[int]
    R_V_BW_RD_FI_FIELD_NUMBER: _ClassVar[int]
    R_V_B_RD_FIELD_NUMBER: _ClassVar[int]
    VZ_ED_FIELD_NUMBER: _ClassVar[int]
    f_calculated: bool
    r_a_f: Vector2D
    r_chi: float
    r_lambda_w: float
    r_m_f_rd: float
    r_m_fk: float
    r_my_ed_max: float
    r_sigma_e: float
    r_tau_cr: float
    r_util: float
    r_v_b_rd: float
    r_v_bf_rd: float
    r_v_bw_rd: float
    r_v_bw_rd_fi: float
    ra: float
    rbf: float
    rc: float
    relevant: StBarWebRelevant
    rhw: float
    rk_tau: float
    rt: float
    rtf: float
    vz_ed: float
    def __init__(self, f_calculated: bool = ..., r_util: _Optional[float] = ..., ra: _Optional[float] = ..., rk_tau: _Optional[float] = ..., r_v_bw_rd: _Optional[float] = ..., r_v_bf_rd: _Optional[float] = ..., r_v_b_rd: _Optional[float] = ..., r_v_bw_rd_fi: _Optional[float] = ..., r_my_ed_max: _Optional[float] = ..., r_m_f_rd: _Optional[float] = ..., r_m_fk: _Optional[float] = ..., r_sigma_e: _Optional[float] = ..., r_tau_cr: _Optional[float] = ..., r_lambda_w: _Optional[float] = ..., r_chi: _Optional[float] = ..., rhw: _Optional[float] = ..., rt: _Optional[float] = ..., r_a_f: _Optional[_Union[Vector2D, _Mapping]] = ..., rtf: _Optional[float] = ..., rbf: _Optional[float] = ..., rc: _Optional[float] = ..., vz_ed: _Optional[float] = ..., relevant: _Optional[_Union[StBarWebRelevant, str]] = ...) -> None: ...

class TVPointW(_message.Message):
    __slots__ = ["coordinates", "number_of_points"]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_POINTS_FIELD_NUMBER: _ClassVar[int]
    coordinates: _containers.RepeatedCompositeFieldContainer[Vector2D]
    number_of_points: int
    def __init__(self, number_of_points: _Optional[int] = ..., coordinates: _Optional[_Iterable[_Union[Vector2D, _Mapping]]] = ...) -> None: ...

class Vector2D(_message.Message):
    __slots__ = ["one", "two"]
    ONE_FIELD_NUMBER: _ClassVar[int]
    TWO_FIELD_NUMBER: _ClassVar[int]
    one: float
    two: float
    def __init__(self, one: _Optional[float] = ..., two: _Optional[float] = ...) -> None: ...

class Vector4D(_message.Message):
    __slots__ = ["four", "one", "three", "two"]
    FOUR_FIELD_NUMBER: _ClassVar[int]
    ONE_FIELD_NUMBER: _ClassVar[int]
    THREE_FIELD_NUMBER: _ClassVar[int]
    TWO_FIELD_NUMBER: _ClassVar[int]
    four: float
    one: float
    three: float
    two: float
    def __init__(self, one: _Optional[float] = ..., two: _Optional[float] = ..., three: _Optional[float] = ..., four: _Optional[float] = ...) -> None: ...

class VirtualStiffeners(_message.Message):
    __slots__ = ["end", "start"]
    END_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    end: bool
    start: bool
    def __init__(self, start: bool = ..., end: bool = ...) -> None: ...

class BarSectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class StatSys(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Alignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class LimitState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
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

class InteractionMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
