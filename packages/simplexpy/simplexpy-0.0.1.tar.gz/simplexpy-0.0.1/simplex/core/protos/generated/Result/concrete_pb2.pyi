from Utils import utils_pb2 as _utils_pb2
from Geometry import link_pb2 as _link_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Geometry import geometry_pb2 as _geometry_pb2
from Geometry import reinf_pb2 as _reinf_pb2
from Geometry import geometry_pb2 as _geometry_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1
from Result import control_pb2 as _control_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
from Geometry.link_pb2 import Group
from Geometry.link_pb2 import Data
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
from Result.control_pb2 import ControlTypeFoundation
from Result.control_pb2 import ControlData
from Result.control_pb2 import ControlTypeConcrete
from Result.control_pb2 import ControlTypeSteel
from Result.control_pb2 import ControlTypeTimber
from Result.control_pb2 import CtrlTypeFoundation
from Result.control_pb2 import AnalysisTypeFoundation
from Result.control_pb2 import DesignTypeFoundation
from Result.control_pb2 import EccentricityTypeFoundation
ANALYSIS_TYPE_NORMAL: _control_pb2.AnalysisTypeFoundation
ANALYSIS_TYPE_SOIL_PUNCHING: _control_pb2.AnalysisTypeFoundation
ANALYSIS_TYPE_UNSPECIFIED: _control_pb2.AnalysisTypeFoundation
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
DESCRIPTOR: _descriptor.FileDescriptor
DESIGN_TYPE_ALLOWEDSOILPRESSURE: _control_pb2.DesignTypeFoundation
DESIGN_TYPE_DRAINED: _control_pb2.DesignTypeFoundation
DESIGN_TYPE_DRAINED_PUNCHNING_ALT: _control_pb2.DesignTypeFoundation
DESIGN_TYPE_DRAINED_PUNCHNING_B6: _control_pb2.DesignTypeFoundation
DESIGN_TYPE_ROCK: _control_pb2.DesignTypeFoundation
DESIGN_TYPE_UNDRAINED: _control_pb2.DesignTypeFoundation
DESIGN_TYPE_UNDRAINED_PUNCHING: _control_pb2.DesignTypeFoundation
DESIGN_TYPE_UNSPECIFIED: _control_pb2.DesignTypeFoundation
ECCENTRICITY_TYPE_HIGH: _control_pb2.EccentricityTypeFoundation
ECCENTRICITY_TYPE_NORMAL: _control_pb2.EccentricityTypeFoundation
ECCENTRICITY_TYPE_UNSPECIFIED: _control_pb2.EccentricityTypeFoundation
OWNER_COMPANY: _utils_pb2_1_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1_1.Owner
OWNER_USER: _utils_pb2_1_1_1.Owner

class BendingDataSLS(_message.Message):
    __slots__ = ["avg_crk_dist", "compression_strength", "compression_stress", "compression_stress_factor", "controls", "coord", "crack_width", "crack_width_limit", "crk_moment", "crk_stage_btm", "crk_stage_top", "cur_reinf_area", "deflection", "eff_area", "eff_moment_of_inertia_y", "eigenfreq_uncrk", "ext_moment", "ext_normal_force", "int_moment", "int_normal_force", "min_req_reinf_area", "min_req_reinf_area_ec", "sigma_c_btm", "sigma_c_top", "sigma_s_btm", "sigma_s_top", "zeta"]
    AVG_CRK_DIST_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_STRESS_FACTOR_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_STRESS_FIELD_NUMBER: _ClassVar[int]
    CONTROLS_FIELD_NUMBER: _ClassVar[int]
    COORD_FIELD_NUMBER: _ClassVar[int]
    CRACK_WIDTH_FIELD_NUMBER: _ClassVar[int]
    CRACK_WIDTH_LIMIT_FIELD_NUMBER: _ClassVar[int]
    CRK_MOMENT_FIELD_NUMBER: _ClassVar[int]
    CRK_STAGE_BTM_FIELD_NUMBER: _ClassVar[int]
    CRK_STAGE_TOP_FIELD_NUMBER: _ClassVar[int]
    CUR_REINF_AREA_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_FIELD_NUMBER: _ClassVar[int]
    EFF_AREA_FIELD_NUMBER: _ClassVar[int]
    EFF_MOMENT_OF_INERTIA_Y_FIELD_NUMBER: _ClassVar[int]
    EIGENFREQ_UNCRK_FIELD_NUMBER: _ClassVar[int]
    EXT_MOMENT_FIELD_NUMBER: _ClassVar[int]
    EXT_NORMAL_FORCE_FIELD_NUMBER: _ClassVar[int]
    INT_MOMENT_FIELD_NUMBER: _ClassVar[int]
    INT_NORMAL_FORCE_FIELD_NUMBER: _ClassVar[int]
    MIN_REQ_REINF_AREA_EC_FIELD_NUMBER: _ClassVar[int]
    MIN_REQ_REINF_AREA_FIELD_NUMBER: _ClassVar[int]
    SIGMA_C_BTM_FIELD_NUMBER: _ClassVar[int]
    SIGMA_C_TOP_FIELD_NUMBER: _ClassVar[int]
    SIGMA_S_BTM_FIELD_NUMBER: _ClassVar[int]
    SIGMA_S_TOP_FIELD_NUMBER: _ClassVar[int]
    ZETA_FIELD_NUMBER: _ClassVar[int]
    avg_crk_dist: float
    compression_strength: float
    compression_stress: float
    compression_stress_factor: float
    controls: _containers.RepeatedCompositeFieldContainer[_control_pb2.ControlData]
    coord: _geometry_pb2_1.Point3D
    crack_width: float
    crack_width_limit: float
    crk_moment: float
    crk_stage_btm: int
    crk_stage_top: int
    cur_reinf_area: float
    deflection: float
    eff_area: float
    eff_moment_of_inertia_y: float
    eigenfreq_uncrk: float
    ext_moment: float
    ext_normal_force: float
    int_moment: float
    int_normal_force: float
    min_req_reinf_area: float
    min_req_reinf_area_ec: float
    sigma_c_btm: float
    sigma_c_top: float
    sigma_s_btm: float
    sigma_s_top: float
    zeta: float
    def __init__(self, coord: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., ext_normal_force: _Optional[float] = ..., int_normal_force: _Optional[float] = ..., ext_moment: _Optional[float] = ..., int_moment: _Optional[float] = ..., crk_moment: _Optional[float] = ..., deflection: _Optional[float] = ..., crack_width: _Optional[float] = ..., sigma_c_top: _Optional[float] = ..., sigma_c_btm: _Optional[float] = ..., sigma_s_top: _Optional[float] = ..., sigma_s_btm: _Optional[float] = ..., crk_stage_top: _Optional[int] = ..., crk_stage_btm: _Optional[int] = ..., eigenfreq_uncrk: _Optional[float] = ..., eff_area: _Optional[float] = ..., eff_moment_of_inertia_y: _Optional[float] = ..., avg_crk_dist: _Optional[float] = ..., min_req_reinf_area: _Optional[float] = ..., cur_reinf_area: _Optional[float] = ..., zeta: _Optional[float] = ..., crack_width_limit: _Optional[float] = ..., compression_stress: _Optional[float] = ..., compression_stress_factor: _Optional[float] = ..., compression_strength: _Optional[float] = ..., min_req_reinf_area_ec: _Optional[float] = ..., controls: _Optional[_Iterable[_Union[_control_pb2.ControlData, _Mapping]]] = ...) -> None: ...

class BendingDataULS(_message.Message):
    __slots__ = ["adj_factor_moment", "biax", "comp_zone_height", "controls", "coord", "crk_moment", "crk_stage_btm", "crk_stage_top", "cur_reinf_area", "eigenfreq_uncrk", "eps_c", "eps_s", "has_adj_factor_moment", "int_lever", "moment", "moment2", "moment2_capacity", "moment_capa", "normal_force", "normal_force_capacity", "req_min_reinf_area", "req_reinf_area", "sigma_sc", "sigma_st", "utilization"]
    ADJ_FACTOR_MOMENT_FIELD_NUMBER: _ClassVar[int]
    BIAX_FIELD_NUMBER: _ClassVar[int]
    COMP_ZONE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    CONTROLS_FIELD_NUMBER: _ClassVar[int]
    COORD_FIELD_NUMBER: _ClassVar[int]
    CRK_MOMENT_FIELD_NUMBER: _ClassVar[int]
    CRK_STAGE_BTM_FIELD_NUMBER: _ClassVar[int]
    CRK_STAGE_TOP_FIELD_NUMBER: _ClassVar[int]
    CUR_REINF_AREA_FIELD_NUMBER: _ClassVar[int]
    EIGENFREQ_UNCRK_FIELD_NUMBER: _ClassVar[int]
    EPS_C_FIELD_NUMBER: _ClassVar[int]
    EPS_S_FIELD_NUMBER: _ClassVar[int]
    HAS_ADJ_FACTOR_MOMENT_FIELD_NUMBER: _ClassVar[int]
    INT_LEVER_FIELD_NUMBER: _ClassVar[int]
    MOMENT2_CAPACITY_FIELD_NUMBER: _ClassVar[int]
    MOMENT2_FIELD_NUMBER: _ClassVar[int]
    MOMENT_CAPA_FIELD_NUMBER: _ClassVar[int]
    MOMENT_FIELD_NUMBER: _ClassVar[int]
    NORMAL_FORCE_CAPACITY_FIELD_NUMBER: _ClassVar[int]
    NORMAL_FORCE_FIELD_NUMBER: _ClassVar[int]
    REQ_MIN_REINF_AREA_FIELD_NUMBER: _ClassVar[int]
    REQ_REINF_AREA_FIELD_NUMBER: _ClassVar[int]
    SIGMA_SC_FIELD_NUMBER: _ClassVar[int]
    SIGMA_ST_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    adj_factor_moment: float
    biax: float
    comp_zone_height: float
    controls: _containers.RepeatedCompositeFieldContainer[_control_pb2.ControlData]
    coord: _geometry_pb2_1.Point3D
    crk_moment: float
    crk_stage_btm: int
    crk_stage_top: int
    cur_reinf_area: float
    eigenfreq_uncrk: float
    eps_c: float
    eps_s: float
    has_adj_factor_moment: bool
    int_lever: float
    moment: float
    moment2: float
    moment2_capacity: float
    moment_capa: float
    normal_force: float
    normal_force_capacity: float
    req_min_reinf_area: float
    req_reinf_area: float
    sigma_sc: float
    sigma_st: float
    utilization: float
    def __init__(self, coord: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., moment: _Optional[float] = ..., moment_capa: _Optional[float] = ..., utilization: _Optional[float] = ..., normal_force: _Optional[float] = ..., int_lever: _Optional[float] = ..., comp_zone_height: _Optional[float] = ..., eps_c: _Optional[float] = ..., eps_s: _Optional[float] = ..., sigma_sc: _Optional[float] = ..., sigma_st: _Optional[float] = ..., eigenfreq_uncrk: _Optional[float] = ..., has_adj_factor_moment: bool = ..., adj_factor_moment: _Optional[float] = ..., normal_force_capacity: _Optional[float] = ..., moment2: _Optional[float] = ..., moment2_capacity: _Optional[float] = ..., biax: _Optional[float] = ..., crk_moment: _Optional[float] = ..., crk_stage_top: _Optional[int] = ..., crk_stage_btm: _Optional[int] = ..., req_min_reinf_area: _Optional[float] = ..., req_reinf_area: _Optional[float] = ..., cur_reinf_area: _Optional[float] = ..., controls: _Optional[_Iterable[_Union[_control_pb2.ControlData, _Mapping]]] = ...) -> None: ...

class BurstingReinf(_message.Message):
    __slots__ = ["area", "controls", "end_coord", "start_coord", "stirrup"]
    AREA_FIELD_NUMBER: _ClassVar[int]
    CONTROLS_FIELD_NUMBER: _ClassVar[int]
    END_COORD_FIELD_NUMBER: _ClassVar[int]
    START_COORD_FIELD_NUMBER: _ClassVar[int]
    STIRRUP_FIELD_NUMBER: _ClassVar[int]
    area: float
    controls: _containers.RepeatedCompositeFieldContainer[_control_pb2.ControlData]
    end_coord: _geometry_pb2_1.Point3D
    start_coord: _geometry_pb2_1.Point3D
    stirrup: _link_pb2.Data
    def __init__(self, stirrup: _Optional[_Union[_link_pb2.Data, _Mapping]] = ..., start_coord: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., end_coord: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., area: _Optional[float] = ..., controls: _Optional[_Iterable[_Union[_control_pb2.ControlData, _Mapping]]] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["bend_sls", "bend_uls", "shear", "stirrup", "topping", "torsion"]
    BEND_SLS_FIELD_NUMBER: _ClassVar[int]
    BEND_ULS_FIELD_NUMBER: _ClassVar[int]
    SHEAR_FIELD_NUMBER: _ClassVar[int]
    STIRRUP_FIELD_NUMBER: _ClassVar[int]
    TOPPING_FIELD_NUMBER: _ClassVar[int]
    TORSION_FIELD_NUMBER: _ClassVar[int]
    bend_sls: BendingDataSLS
    bend_uls: BendingDataULS
    shear: ShearData
    stirrup: StirrupData
    topping: ToppingData
    torsion: TorsionData
    def __init__(self, bend_sls: _Optional[_Union[BendingDataSLS, _Mapping]] = ..., bend_uls: _Optional[_Union[BendingDataULS, _Mapping]] = ..., shear: _Optional[_Union[ShearData, _Mapping]] = ..., stirrup: _Optional[_Union[StirrupData, _Mapping]] = ..., torsion: _Optional[_Union[TorsionData, _Mapping]] = ..., topping: _Optional[_Union[ToppingData, _Mapping]] = ...) -> None: ...

class DesignSummary(_message.Message):
    __slots__ = ["controls", "elem_guid"]
    CONTROLS_FIELD_NUMBER: _ClassVar[int]
    ELEM_GUID_FIELD_NUMBER: _ClassVar[int]
    controls: _containers.RepeatedCompositeFieldContainer[_control_pb2.ControlData]
    elem_guid: str
    def __init__(self, elem_guid: _Optional[str] = ..., controls: _Optional[_Iterable[_Union[_control_pb2.ControlData, _Mapping]]] = ...) -> None: ...

class Element(_message.Message):
    __slots__ = ["anchorages", "end_reinf", "flange_reinf", "max_of_controls"]
    class Anchorage(_message.Message):
        __slots__ = ["end", "group_id", "start"]
        END_FIELD_NUMBER: _ClassVar[int]
        GROUP_ID_FIELD_NUMBER: _ClassVar[int]
        START_FIELD_NUMBER: _ClassVar[int]
        end: float
        group_id: str
        start: float
        def __init__(self, group_id: _Optional[str] = ..., start: _Optional[float] = ..., end: _Optional[float] = ...) -> None: ...
    ANCHORAGES_FIELD_NUMBER: _ClassVar[int]
    END_REINF_FIELD_NUMBER: _ClassVar[int]
    FLANGE_REINF_FIELD_NUMBER: _ClassVar[int]
    MAX_OF_CONTROLS_FIELD_NUMBER: _ClassVar[int]
    anchorages: _containers.RepeatedCompositeFieldContainer[Element.Anchorage]
    end_reinf: EndReinf
    flange_reinf: FlangeReinf
    max_of_controls: _containers.RepeatedCompositeFieldContainer[_control_pb2.ControlData]
    def __init__(self, anchorages: _Optional[_Iterable[_Union[Element.Anchorage, _Mapping]]] = ..., flange_reinf: _Optional[_Union[FlangeReinf, _Mapping]] = ..., end_reinf: _Optional[_Union[EndReinf, _Mapping]] = ..., max_of_controls: _Optional[_Iterable[_Union[_control_pb2.ControlData, _Mapping]]] = ...) -> None: ...

class EndReinf(_message.Message):
    __slots__ = ["bursting", "spalling", "splitting_reinf"]
    BURSTING_FIELD_NUMBER: _ClassVar[int]
    SPALLING_FIELD_NUMBER: _ClassVar[int]
    SPLITTING_REINF_FIELD_NUMBER: _ClassVar[int]
    bursting: BurstingReinf
    spalling: SpallingReinf
    splitting_reinf: SplittingReinf
    def __init__(self, spalling: _Optional[_Union[SpallingReinf, _Mapping]] = ..., bursting: _Optional[_Union[BurstingReinf, _Mapping]] = ..., splitting_reinf: _Optional[_Union[SplittingReinf, _Mapping]] = ...) -> None: ...

class FlangeReinf(_message.Message):
    __slots__ = ["area", "controls", "end_coord", "start_coord", "stirrup"]
    AREA_FIELD_NUMBER: _ClassVar[int]
    CONTROLS_FIELD_NUMBER: _ClassVar[int]
    END_COORD_FIELD_NUMBER: _ClassVar[int]
    START_COORD_FIELD_NUMBER: _ClassVar[int]
    STIRRUP_FIELD_NUMBER: _ClassVar[int]
    area: float
    controls: _containers.RepeatedCompositeFieldContainer[_control_pb2.ControlData]
    end_coord: _geometry_pb2_1.Point3D
    start_coord: _geometry_pb2_1.Point3D
    stirrup: _link_pb2.Data
    def __init__(self, stirrup: _Optional[_Union[_link_pb2.Data, _Mapping]] = ..., start_coord: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., end_coord: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., area: _Optional[float] = ..., controls: _Optional[_Iterable[_Union[_control_pb2.ControlData, _Mapping]]] = ...) -> None: ...

class ShearData(_message.Message):
    __slots__ = ["A_sl", "C_Rd_c", "I", "S", "adj_factor_shear", "close_to_supp_factor", "controls", "coord", "eff_depth", "f_cd", "f_ck", "f_ctd", "has_adj_factor_shear", "has_core_filling", "has_torsion", "k", "k_1", "rho_l", "shear_capa_bend", "shear_capa_core_filling", "shear_capa_force", "shear_capa_max", "shear_capa_normal_force", "shear_capa_section_depth", "shear_capa_stress", "shear_capa_torsion", "shear_capa_web", "shear_field_end", "shear_field_start", "shear_force", "shear_resist_req", "shear_stress", "sigma_cp", "sigma_cp_alpha_l", "torque", "use_shear_capa_web", "use_shear_stress_ctrl", "utilization_force", "utilization_stress", "v", "v_min", "vrd_eq_str", "web_width"]
    ADJ_FACTOR_SHEAR_FIELD_NUMBER: _ClassVar[int]
    A_SL_FIELD_NUMBER: _ClassVar[int]
    A_sl: float
    CLOSE_TO_SUPP_FACTOR_FIELD_NUMBER: _ClassVar[int]
    CONTROLS_FIELD_NUMBER: _ClassVar[int]
    COORD_FIELD_NUMBER: _ClassVar[int]
    C_RD_C_FIELD_NUMBER: _ClassVar[int]
    C_Rd_c: float
    EFF_DEPTH_FIELD_NUMBER: _ClassVar[int]
    F_CD_FIELD_NUMBER: _ClassVar[int]
    F_CK_FIELD_NUMBER: _ClassVar[int]
    F_CTD_FIELD_NUMBER: _ClassVar[int]
    HAS_ADJ_FACTOR_SHEAR_FIELD_NUMBER: _ClassVar[int]
    HAS_CORE_FILLING_FIELD_NUMBER: _ClassVar[int]
    HAS_TORSION_FIELD_NUMBER: _ClassVar[int]
    I: float
    I_FIELD_NUMBER: _ClassVar[int]
    K_1_FIELD_NUMBER: _ClassVar[int]
    K_FIELD_NUMBER: _ClassVar[int]
    RHO_L_FIELD_NUMBER: _ClassVar[int]
    S: float
    SHEAR_CAPA_BEND_FIELD_NUMBER: _ClassVar[int]
    SHEAR_CAPA_CORE_FILLING_FIELD_NUMBER: _ClassVar[int]
    SHEAR_CAPA_FORCE_FIELD_NUMBER: _ClassVar[int]
    SHEAR_CAPA_MAX_FIELD_NUMBER: _ClassVar[int]
    SHEAR_CAPA_NORMAL_FORCE_FIELD_NUMBER: _ClassVar[int]
    SHEAR_CAPA_SECTION_DEPTH_FIELD_NUMBER: _ClassVar[int]
    SHEAR_CAPA_STRESS_FIELD_NUMBER: _ClassVar[int]
    SHEAR_CAPA_TORSION_FIELD_NUMBER: _ClassVar[int]
    SHEAR_CAPA_WEB_FIELD_NUMBER: _ClassVar[int]
    SHEAR_FIELD_END_FIELD_NUMBER: _ClassVar[int]
    SHEAR_FIELD_START_FIELD_NUMBER: _ClassVar[int]
    SHEAR_FORCE_FIELD_NUMBER: _ClassVar[int]
    SHEAR_RESIST_REQ_FIELD_NUMBER: _ClassVar[int]
    SHEAR_STRESS_FIELD_NUMBER: _ClassVar[int]
    SIGMA_CP_ALPHA_L_FIELD_NUMBER: _ClassVar[int]
    SIGMA_CP_FIELD_NUMBER: _ClassVar[int]
    S_FIELD_NUMBER: _ClassVar[int]
    TORQUE_FIELD_NUMBER: _ClassVar[int]
    USE_SHEAR_CAPA_WEB_FIELD_NUMBER: _ClassVar[int]
    USE_SHEAR_STRESS_CTRL_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FORCE_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_STRESS_FIELD_NUMBER: _ClassVar[int]
    VRD_EQ_STR_FIELD_NUMBER: _ClassVar[int]
    V_FIELD_NUMBER: _ClassVar[int]
    V_MIN_FIELD_NUMBER: _ClassVar[int]
    WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    adj_factor_shear: float
    close_to_supp_factor: float
    controls: _containers.RepeatedCompositeFieldContainer[_control_pb2.ControlData]
    coord: _geometry_pb2_1.Point3D
    eff_depth: float
    f_cd: float
    f_ck: float
    f_ctd: float
    has_adj_factor_shear: bool
    has_core_filling: bool
    has_torsion: bool
    k: float
    k_1: float
    rho_l: float
    shear_capa_bend: float
    shear_capa_core_filling: float
    shear_capa_force: float
    shear_capa_max: float
    shear_capa_normal_force: float
    shear_capa_section_depth: float
    shear_capa_stress: float
    shear_capa_torsion: float
    shear_capa_web: float
    shear_field_end: float
    shear_field_start: float
    shear_force: float
    shear_resist_req: bool
    shear_stress: float
    sigma_cp: float
    sigma_cp_alpha_l: float
    torque: float
    use_shear_capa_web: bool
    use_shear_stress_ctrl: bool
    utilization_force: float
    utilization_stress: float
    v: float
    v_min: float
    vrd_eq_str: str
    web_width: float
    def __init__(self, coord: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., shear_force: _Optional[float] = ..., shear_capa_force: _Optional[float] = ..., utilization_force: _Optional[float] = ..., torque: _Optional[float] = ..., shear_capa_max: _Optional[float] = ..., shear_capa_web: _Optional[float] = ..., shear_capa_bend: _Optional[float] = ..., shear_capa_normal_force: _Optional[float] = ..., shear_capa_section_depth: _Optional[float] = ..., shear_capa_core_filling: _Optional[float] = ..., shear_capa_torsion: _Optional[float] = ..., web_width: _Optional[float] = ..., eff_depth: _Optional[float] = ..., shear_stress: _Optional[float] = ..., shear_capa_stress: _Optional[float] = ..., utilization_stress: _Optional[float] = ..., shear_resist_req: bool = ..., has_core_filling: bool = ..., has_torsion: bool = ..., use_shear_stress_ctrl: bool = ..., use_shear_capa_web: bool = ..., vrd_eq_str: _Optional[str] = ..., adj_factor_shear: _Optional[float] = ..., has_adj_factor_shear: bool = ..., shear_field_start: _Optional[float] = ..., shear_field_end: _Optional[float] = ..., C_Rd_c: _Optional[float] = ..., k: _Optional[float] = ..., A_sl: _Optional[float] = ..., rho_l: _Optional[float] = ..., f_ck: _Optional[float] = ..., k_1: _Optional[float] = ..., sigma_cp: _Optional[float] = ..., v_min: _Optional[float] = ..., I: _Optional[float] = ..., S: _Optional[float] = ..., sigma_cp_alpha_l: _Optional[float] = ..., f_ctd: _Optional[float] = ..., v: _Optional[float] = ..., f_cd: _Optional[float] = ..., close_to_supp_factor: _Optional[float] = ..., controls: _Optional[_Iterable[_Union[_control_pb2.ControlData, _Mapping]]] = ...) -> None: ...

class SpallingReinf(_message.Message):
    __slots__ = ["area", "controls", "end_coord", "start_coord", "stirrup"]
    AREA_FIELD_NUMBER: _ClassVar[int]
    CONTROLS_FIELD_NUMBER: _ClassVar[int]
    END_COORD_FIELD_NUMBER: _ClassVar[int]
    START_COORD_FIELD_NUMBER: _ClassVar[int]
    STIRRUP_FIELD_NUMBER: _ClassVar[int]
    area: float
    controls: _containers.RepeatedCompositeFieldContainer[_control_pb2.ControlData]
    end_coord: _geometry_pb2_1.Point3D
    start_coord: _geometry_pb2_1.Point3D
    stirrup: _link_pb2.Data
    def __init__(self, stirrup: _Optional[_Union[_link_pb2.Data, _Mapping]] = ..., start_coord: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., end_coord: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., area: _Optional[float] = ..., controls: _Optional[_Iterable[_Union[_control_pb2.ControlData, _Mapping]]] = ...) -> None: ...

class SplittingReinf(_message.Message):
    __slots__ = ["area", "controls", "end_coord", "start_coord", "stirrup"]
    AREA_FIELD_NUMBER: _ClassVar[int]
    CONTROLS_FIELD_NUMBER: _ClassVar[int]
    END_COORD_FIELD_NUMBER: _ClassVar[int]
    START_COORD_FIELD_NUMBER: _ClassVar[int]
    STIRRUP_FIELD_NUMBER: _ClassVar[int]
    area: float
    controls: _containers.RepeatedCompositeFieldContainer[_control_pb2.ControlData]
    end_coord: _geometry_pb2_1.Point3D
    start_coord: _geometry_pb2_1.Point3D
    stirrup: _link_pb2.Data
    def __init__(self, stirrup: _Optional[_Union[_link_pb2.Data, _Mapping]] = ..., start_coord: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., end_coord: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., area: _Optional[float] = ..., controls: _Optional[_Iterable[_Union[_control_pb2.ControlData, _Mapping]]] = ...) -> None: ...

class StirrupData(_message.Message):
    __slots__ = ["A_sw", "S", "adj_factor_shear", "alpha_cw", "controls", "coord", "cot_alpha", "cot_theta", "cur_reinf_area", "f_cd", "f_ywd", "has_adj_factor_shear", "has_torsion", "int_lever", "min_req_reinf_area", "nu_1", "req_reinf_area", "shear_capa_force", "shear_capa_max", "shear_capa_stirrups", "shear_field_end", "shear_field_force", "shear_field_start", "shear_force_stirrups", "shear_result_req", "sin_alpha", "utilization_force", "vrd_eq_str", "web_width"]
    ADJ_FACTOR_SHEAR_FIELD_NUMBER: _ClassVar[int]
    ALPHA_CW_FIELD_NUMBER: _ClassVar[int]
    A_SW_FIELD_NUMBER: _ClassVar[int]
    A_sw: float
    CONTROLS_FIELD_NUMBER: _ClassVar[int]
    COORD_FIELD_NUMBER: _ClassVar[int]
    COT_ALPHA_FIELD_NUMBER: _ClassVar[int]
    COT_THETA_FIELD_NUMBER: _ClassVar[int]
    CUR_REINF_AREA_FIELD_NUMBER: _ClassVar[int]
    F_CD_FIELD_NUMBER: _ClassVar[int]
    F_YWD_FIELD_NUMBER: _ClassVar[int]
    HAS_ADJ_FACTOR_SHEAR_FIELD_NUMBER: _ClassVar[int]
    HAS_TORSION_FIELD_NUMBER: _ClassVar[int]
    INT_LEVER_FIELD_NUMBER: _ClassVar[int]
    MIN_REQ_REINF_AREA_FIELD_NUMBER: _ClassVar[int]
    NU_1_FIELD_NUMBER: _ClassVar[int]
    REQ_REINF_AREA_FIELD_NUMBER: _ClassVar[int]
    S: float
    SHEAR_CAPA_FORCE_FIELD_NUMBER: _ClassVar[int]
    SHEAR_CAPA_MAX_FIELD_NUMBER: _ClassVar[int]
    SHEAR_CAPA_STIRRUPS_FIELD_NUMBER: _ClassVar[int]
    SHEAR_FIELD_END_FIELD_NUMBER: _ClassVar[int]
    SHEAR_FIELD_FORCE_FIELD_NUMBER: _ClassVar[int]
    SHEAR_FIELD_START_FIELD_NUMBER: _ClassVar[int]
    SHEAR_FORCE_STIRRUPS_FIELD_NUMBER: _ClassVar[int]
    SHEAR_RESULT_REQ_FIELD_NUMBER: _ClassVar[int]
    SIN_ALPHA_FIELD_NUMBER: _ClassVar[int]
    S_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FORCE_FIELD_NUMBER: _ClassVar[int]
    VRD_EQ_STR_FIELD_NUMBER: _ClassVar[int]
    WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    adj_factor_shear: float
    alpha_cw: float
    controls: _containers.RepeatedCompositeFieldContainer[_control_pb2.ControlData]
    coord: _geometry_pb2_1.Point3D
    cot_alpha: float
    cot_theta: float
    cur_reinf_area: float
    f_cd: float
    f_ywd: float
    has_adj_factor_shear: bool
    has_torsion: bool
    int_lever: float
    min_req_reinf_area: float
    nu_1: float
    req_reinf_area: float
    shear_capa_force: float
    shear_capa_max: float
    shear_capa_stirrups: float
    shear_field_end: float
    shear_field_force: float
    shear_field_start: float
    shear_force_stirrups: float
    shear_result_req: bool
    sin_alpha: float
    utilization_force: float
    vrd_eq_str: str
    web_width: float
    def __init__(self, coord: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., shear_force_stirrups: _Optional[float] = ..., shear_capa_force: _Optional[float] = ..., utilization_force: _Optional[float] = ..., shear_field_force: _Optional[float] = ..., shear_capa_stirrups: _Optional[float] = ..., shear_capa_max: _Optional[float] = ..., cur_reinf_area: _Optional[float] = ..., req_reinf_area: _Optional[float] = ..., min_req_reinf_area: _Optional[float] = ..., web_width: _Optional[float] = ..., int_lever: _Optional[float] = ..., shear_result_req: bool = ..., has_torsion: bool = ..., vrd_eq_str: _Optional[str] = ..., adj_factor_shear: _Optional[float] = ..., has_adj_factor_shear: bool = ..., shear_field_start: _Optional[float] = ..., shear_field_end: _Optional[float] = ..., A_sw: _Optional[float] = ..., S: _Optional[float] = ..., f_ywd: _Optional[float] = ..., cot_theta: _Optional[float] = ..., cot_alpha: _Optional[float] = ..., sin_alpha: _Optional[float] = ..., alpha_cw: _Optional[float] = ..., nu_1: _Optional[float] = ..., f_cd: _Optional[float] = ..., controls: _Optional[_Iterable[_Union[_control_pb2.ControlData, _Mapping]]] = ...) -> None: ...

class ToppingData(_message.Message):
    __slots__ = ["controls", "coord", "cur_shear_reinf_area", "joint_capa_force", "joint_force", "joint_stress", "joint_width", "req_shear_reinf_area", "shear_force"]
    CONTROLS_FIELD_NUMBER: _ClassVar[int]
    COORD_FIELD_NUMBER: _ClassVar[int]
    CUR_SHEAR_REINF_AREA_FIELD_NUMBER: _ClassVar[int]
    JOINT_CAPA_FORCE_FIELD_NUMBER: _ClassVar[int]
    JOINT_FORCE_FIELD_NUMBER: _ClassVar[int]
    JOINT_STRESS_FIELD_NUMBER: _ClassVar[int]
    JOINT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    REQ_SHEAR_REINF_AREA_FIELD_NUMBER: _ClassVar[int]
    SHEAR_FORCE_FIELD_NUMBER: _ClassVar[int]
    controls: _containers.RepeatedCompositeFieldContainer[_control_pb2.ControlData]
    coord: _geometry_pb2_1.Point3D
    cur_shear_reinf_area: float
    joint_capa_force: float
    joint_force: float
    joint_stress: float
    joint_width: float
    req_shear_reinf_area: float
    shear_force: float
    def __init__(self, coord: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., shear_force: _Optional[float] = ..., joint_force: _Optional[float] = ..., joint_stress: _Optional[float] = ..., joint_width: _Optional[float] = ..., joint_capa_force: _Optional[float] = ..., cur_shear_reinf_area: _Optional[float] = ..., req_shear_reinf_area: _Optional[float] = ..., controls: _Optional[_Iterable[_Union[_control_pb2.ControlData, _Mapping]]] = ...) -> None: ...

class TorsionData(_message.Message):
    __slots__ = ["controls", "coord", "cur_reinf_area", "enclosed_area", "enclosed_perimeter", "req_reinf_area_shear", "req_reinf_area_torsion", "shear_capa_stirrups", "shear_field_force", "shear_force", "shear_ratio", "torque", "torque_capa", "utilization", "utilization_shear_force"]
    CONTROLS_FIELD_NUMBER: _ClassVar[int]
    COORD_FIELD_NUMBER: _ClassVar[int]
    CUR_REINF_AREA_FIELD_NUMBER: _ClassVar[int]
    ENCLOSED_AREA_FIELD_NUMBER: _ClassVar[int]
    ENCLOSED_PERIMETER_FIELD_NUMBER: _ClassVar[int]
    REQ_REINF_AREA_SHEAR_FIELD_NUMBER: _ClassVar[int]
    REQ_REINF_AREA_TORSION_FIELD_NUMBER: _ClassVar[int]
    SHEAR_CAPA_STIRRUPS_FIELD_NUMBER: _ClassVar[int]
    SHEAR_FIELD_FORCE_FIELD_NUMBER: _ClassVar[int]
    SHEAR_FORCE_FIELD_NUMBER: _ClassVar[int]
    SHEAR_RATIO_FIELD_NUMBER: _ClassVar[int]
    TORQUE_CAPA_FIELD_NUMBER: _ClassVar[int]
    TORQUE_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_SHEAR_FORCE_FIELD_NUMBER: _ClassVar[int]
    controls: _containers.RepeatedCompositeFieldContainer[_control_pb2.ControlData]
    coord: _geometry_pb2_1.Point3D
    cur_reinf_area: float
    enclosed_area: float
    enclosed_perimeter: float
    req_reinf_area_shear: float
    req_reinf_area_torsion: float
    shear_capa_stirrups: float
    shear_field_force: float
    shear_force: float
    shear_ratio: float
    torque: float
    torque_capa: float
    utilization: float
    utilization_shear_force: float
    def __init__(self, coord: _Optional[_Union[_geometry_pb2_1.Point3D, _Mapping]] = ..., torque: _Optional[float] = ..., torque_capa: _Optional[float] = ..., utilization: _Optional[float] = ..., shear_force: _Optional[float] = ..., shear_field_force: _Optional[float] = ..., shear_capa_stirrups: _Optional[float] = ..., utilization_shear_force: _Optional[float] = ..., req_reinf_area_shear: _Optional[float] = ..., cur_reinf_area: _Optional[float] = ..., req_reinf_area_torsion: _Optional[float] = ..., enclosed_area: _Optional[float] = ..., enclosed_perimeter: _Optional[float] = ..., shear_ratio: _Optional[float] = ..., controls: _Optional[_Iterable[_Union[_control_pb2.ControlData, _Mapping]]] = ...) -> None: ...
