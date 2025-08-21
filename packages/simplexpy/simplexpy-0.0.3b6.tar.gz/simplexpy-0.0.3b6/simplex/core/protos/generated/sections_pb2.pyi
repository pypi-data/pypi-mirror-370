from Utils import utils_pb2 as _utils_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Utils import utils_pb2 as _utils_pb2_1
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
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
DESCRIPTOR: _descriptor.FileDescriptor
MATERIAL_CATEGORY_CONCRETE: MaterialCategory
MATERIAL_CATEGORY_STEEL: MaterialCategory
MATERIAL_CATEGORY_TIMBER: MaterialCategory
MATERIAL_CATEGORY_UNSPECIFIED: MaterialCategory
OWNER_COMPANY: _utils_pb2_1.Owner
OWNER_OFFICE: _utils_pb2_1.Owner
OWNER_STRUSOFT: _utils_pb2_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1.Owner
OWNER_USER: _utils_pb2_1.Owner
SECTION_SIDE_LEFT: SectionSide
SECTION_SIDE_RIGHT: SectionSide
SECTION_SIDE_UNSPECIFIED: SectionSide
SECTION_TYPE_ASB: SectionType
SECTION_TYPE_C: SectionType
SECTION_TYPE_CHS: SectionType
SECTION_TYPE_CO: SectionType
SECTION_TYPE_CUSTOM: SectionType
SECTION_TYPE_DESSED_LUMBER: SectionType
SECTION_TYPE_EA: SectionType
SECTION_TYPE_F: SectionType
SECTION_TYPE_GLULAM: SectionType
SECTION_TYPE_HDX: SectionType
SECTION_TYPE_HEA: SectionType
SECTION_TYPE_HEB: SectionType
SECTION_TYPE_HEM: SectionType
SECTION_TYPE_HSQ: SectionType
SECTION_TYPE_I: SectionType
SECTION_TYPE_IPE: SectionType
SECTION_TYPE_IV: SectionType
SECTION_TYPE_KB: SectionType
SECTION_TYPE_KBE: SectionType
SECTION_TYPE_KCKR: SectionType
SECTION_TYPE_KERTO: SectionType
SECTION_TYPE_KKR: SectionType
SECTION_TYPE_L: SectionType
SECTION_TYPE_LE: SectionType
SECTION_TYPE_LU: SectionType
SECTION_TYPE_PFC: SectionType
SECTION_TYPE_PLATE: SectionType
SECTION_TYPE_R: SectionType
SECTION_TYPE_RHS: SectionType
SECTION_TYPE_SAWN_LUMBER: SectionType
SECTION_TYPE_T: SectionType
SECTION_TYPE_TOPPING: SectionType
SECTION_TYPE_TPS: SectionType
SECTION_TYPE_U: SectionType
SECTION_TYPE_UA: SectionType
SECTION_TYPE_UAP: SectionType
SECTION_TYPE_UB: SectionType
SECTION_TYPE_UBP: SectionType
SECTION_TYPE_UC: SectionType
SECTION_TYPE_UKB: SectionType
SECTION_TYPE_UKC: SectionType
SECTION_TYPE_UNSPECIFIED: SectionType
SECTION_TYPE_UPE_DIN: SectionType
SECTION_TYPE_UPE_NEN: SectionType
SECTION_TYPE_UPE_SWE: SectionType
SECTION_TYPE_UX: SectionType
SECTION_TYPE_VCKR: SectionType
SECTION_TYPE_VKR: SectionType
SECTION_TYPE_VR: SectionType
SECTION_TYPE_VT: SectionType
SECTION_TYPE_Z: SectionType
SECTION_TYPE_ZX: SectionType

class COParams(_message.Message):
    __slots__ = ["diameter", "thickness"]
    DIAMETER_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_FIELD_NUMBER: _ClassVar[int]
    diameter: float
    thickness: float
    def __init__(self, diameter: _Optional[float] = ..., thickness: _Optional[float] = ...) -> None: ...

class CParams(_message.Message):
    __slots__ = ["diameter"]
    DIAMETER_FIELD_NUMBER: _ClassVar[int]
    diameter: float
    def __init__(self, diameter: _Optional[float] = ...) -> None: ...

class CustomParams(_message.Message):
    __slots__ = ["btm_flange_btm_width", "btm_flange_height_lft", "btm_flange_height_rgt", "btm_flange_inclination_lft", "btm_flange_inclination_rgt", "btm_flange_width_lft", "btm_flange_width_rgt", "btm_inner_web_width", "btm_web_height", "btm_web_width", "height", "inner_radius", "radius", "thickness", "top_flange_height_lft", "top_flange_height_rgt", "top_flange_inclination_lft", "top_flange_inclination_rgt", "top_flange_top_width", "top_flange_width_lft", "top_flange_width_rgt", "top_inner_web_width", "top_web_height", "top_web_width", "width"]
    BTM_FLANGE_BTM_WIDTH_FIELD_NUMBER: _ClassVar[int]
    BTM_FLANGE_HEIGHT_LFT_FIELD_NUMBER: _ClassVar[int]
    BTM_FLANGE_HEIGHT_RGT_FIELD_NUMBER: _ClassVar[int]
    BTM_FLANGE_INCLINATION_LFT_FIELD_NUMBER: _ClassVar[int]
    BTM_FLANGE_INCLINATION_RGT_FIELD_NUMBER: _ClassVar[int]
    BTM_FLANGE_WIDTH_LFT_FIELD_NUMBER: _ClassVar[int]
    BTM_FLANGE_WIDTH_RGT_FIELD_NUMBER: _ClassVar[int]
    BTM_INNER_WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    BTM_WEB_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    BTM_WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    INNER_RADIUS_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_FIELD_NUMBER: _ClassVar[int]
    TOP_FLANGE_HEIGHT_LFT_FIELD_NUMBER: _ClassVar[int]
    TOP_FLANGE_HEIGHT_RGT_FIELD_NUMBER: _ClassVar[int]
    TOP_FLANGE_INCLINATION_LFT_FIELD_NUMBER: _ClassVar[int]
    TOP_FLANGE_INCLINATION_RGT_FIELD_NUMBER: _ClassVar[int]
    TOP_FLANGE_TOP_WIDTH_FIELD_NUMBER: _ClassVar[int]
    TOP_FLANGE_WIDTH_LFT_FIELD_NUMBER: _ClassVar[int]
    TOP_FLANGE_WIDTH_RGT_FIELD_NUMBER: _ClassVar[int]
    TOP_INNER_WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    TOP_WEB_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    TOP_WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    btm_flange_btm_width: float
    btm_flange_height_lft: float
    btm_flange_height_rgt: float
    btm_flange_inclination_lft: int
    btm_flange_inclination_rgt: int
    btm_flange_width_lft: float
    btm_flange_width_rgt: float
    btm_inner_web_width: float
    btm_web_height: float
    btm_web_width: float
    height: float
    inner_radius: float
    radius: float
    thickness: float
    top_flange_height_lft: float
    top_flange_height_rgt: float
    top_flange_inclination_lft: int
    top_flange_inclination_rgt: int
    top_flange_top_width: float
    top_flange_width_lft: float
    top_flange_width_rgt: float
    top_inner_web_width: float
    top_web_height: float
    top_web_width: float
    width: float
    def __init__(self, height: _Optional[float] = ..., width: _Optional[float] = ..., top_web_height: _Optional[float] = ..., top_web_width: _Optional[float] = ..., top_inner_web_width: _Optional[float] = ..., top_flange_height_lft: _Optional[float] = ..., top_flange_height_rgt: _Optional[float] = ..., top_flange_width_lft: _Optional[float] = ..., top_flange_width_rgt: _Optional[float] = ..., top_flange_top_width: _Optional[float] = ..., top_flange_inclination_lft: _Optional[int] = ..., top_flange_inclination_rgt: _Optional[int] = ..., btm_web_height: _Optional[float] = ..., btm_inner_web_width: _Optional[float] = ..., btm_web_width: _Optional[float] = ..., btm_flange_height_lft: _Optional[float] = ..., btm_flange_height_rgt: _Optional[float] = ..., btm_flange_width_lft: _Optional[float] = ..., btm_flange_width_rgt: _Optional[float] = ..., btm_flange_btm_width: _Optional[float] = ..., btm_flange_inclination_lft: _Optional[int] = ..., btm_flange_inclination_rgt: _Optional[int] = ..., radius: _Optional[float] = ..., thickness: _Optional[float] = ..., inner_radius: _Optional[float] = ...) -> None: ...

class FParams(_message.Message):
    __slots__ = ["flange_height", "flange_width", "height", "web_width"]
    FLANGE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FLANGE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    flange_height: float
    flange_width: float
    height: float
    web_width: float
    def __init__(self, height: _Optional[float] = ..., flange_height: _Optional[float] = ..., flange_width: _Optional[float] = ..., web_width: _Optional[float] = ...) -> None: ...

class HDXParams(_message.Message):
    __slots__ = ["flange_height1_down", "flange_height1_up", "flange_height2_down", "flange_height2_up", "flange_width_down", "flange_width_up", "hc_dist_up", "hc_height", "hc_radius_down", "hc_radius_up", "hc_spacing", "hc_width_down", "hc_width_up", "height", "max_width", "nbr_of_hcs", "nbr_of_hcs_sides_down", "nbr_of_hcs_sides_up", "radius_dist_down", "radius_dist_up", "width_up"]
    FLANGE_HEIGHT1_DOWN_FIELD_NUMBER: _ClassVar[int]
    FLANGE_HEIGHT1_UP_FIELD_NUMBER: _ClassVar[int]
    FLANGE_HEIGHT2_DOWN_FIELD_NUMBER: _ClassVar[int]
    FLANGE_HEIGHT2_UP_FIELD_NUMBER: _ClassVar[int]
    FLANGE_WIDTH_DOWN_FIELD_NUMBER: _ClassVar[int]
    FLANGE_WIDTH_UP_FIELD_NUMBER: _ClassVar[int]
    HC_DIST_UP_FIELD_NUMBER: _ClassVar[int]
    HC_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    HC_RADIUS_DOWN_FIELD_NUMBER: _ClassVar[int]
    HC_RADIUS_UP_FIELD_NUMBER: _ClassVar[int]
    HC_SPACING_FIELD_NUMBER: _ClassVar[int]
    HC_WIDTH_DOWN_FIELD_NUMBER: _ClassVar[int]
    HC_WIDTH_UP_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    MAX_WIDTH_FIELD_NUMBER: _ClassVar[int]
    NBR_OF_HCS_FIELD_NUMBER: _ClassVar[int]
    NBR_OF_HCS_SIDES_DOWN_FIELD_NUMBER: _ClassVar[int]
    NBR_OF_HCS_SIDES_UP_FIELD_NUMBER: _ClassVar[int]
    RADIUS_DIST_DOWN_FIELD_NUMBER: _ClassVar[int]
    RADIUS_DIST_UP_FIELD_NUMBER: _ClassVar[int]
    WIDTH_UP_FIELD_NUMBER: _ClassVar[int]
    flange_height1_down: float
    flange_height1_up: float
    flange_height2_down: float
    flange_height2_up: float
    flange_width_down: float
    flange_width_up: float
    hc_dist_up: float
    hc_height: float
    hc_radius_down: float
    hc_radius_up: float
    hc_spacing: float
    hc_width_down: float
    hc_width_up: float
    height: float
    max_width: float
    nbr_of_hcs: int
    nbr_of_hcs_sides_down: int
    nbr_of_hcs_sides_up: int
    radius_dist_down: float
    radius_dist_up: float
    width_up: float
    def __init__(self, max_width: _Optional[float] = ..., width_up: _Optional[float] = ..., height: _Optional[float] = ..., nbr_of_hcs: _Optional[int] = ..., nbr_of_hcs_sides_up: _Optional[int] = ..., nbr_of_hcs_sides_down: _Optional[int] = ..., hc_width_up: _Optional[float] = ..., hc_width_down: _Optional[float] = ..., hc_height: _Optional[float] = ..., hc_spacing: _Optional[float] = ..., hc_dist_up: _Optional[float] = ..., hc_radius_up: _Optional[float] = ..., radius_dist_up: _Optional[float] = ..., hc_radius_down: _Optional[float] = ..., radius_dist_down: _Optional[float] = ..., flange_width_up: _Optional[float] = ..., flange_height1_up: _Optional[float] = ..., flange_height2_up: _Optional[float] = ..., flange_width_down: _Optional[float] = ..., flange_height1_down: _Optional[float] = ..., flange_height2_down: _Optional[float] = ...) -> None: ...

class HEParams(_message.Message):
    __slots__ = ["flange_thickness", "height", "radius", "web_thickness", "width"]
    FLANGE_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    WEB_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    flange_thickness: float
    height: float
    radius: float
    web_thickness: float
    width: float
    def __init__(self, height: _Optional[float] = ..., width: _Optional[float] = ..., flange_thickness: _Optional[float] = ..., web_thickness: _Optional[float] = ..., radius: _Optional[float] = ...) -> None: ...

class HSQParams(_message.Message):
    __slots__ = ["bottom_flange_thickness", "cut_off", "height", "indent", "indent_cut", "top_flange_thickness", "top_width", "web_thickness", "width"]
    BOTTOM_FLANGE_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    CUT_OFF_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    INDENT_CUT_FIELD_NUMBER: _ClassVar[int]
    INDENT_FIELD_NUMBER: _ClassVar[int]
    TOP_FLANGE_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    TOP_WIDTH_FIELD_NUMBER: _ClassVar[int]
    WEB_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    bottom_flange_thickness: float
    cut_off: int
    height: float
    indent: float
    indent_cut: float
    top_flange_thickness: float
    top_width: float
    web_thickness: float
    width: float
    def __init__(self, cut_off: _Optional[int] = ..., height: _Optional[float] = ..., top_width: _Optional[float] = ..., width: _Optional[float] = ..., top_flange_thickness: _Optional[float] = ..., bottom_flange_thickness: _Optional[float] = ..., web_thickness: _Optional[float] = ..., indent: _Optional[float] = ..., indent_cut: _Optional[float] = ...) -> None: ...

class IParams(_message.Message):
    __slots__ = ["bottom_flange_height", "bottom_flange_width", "bottom_web_height", "height", "top_flange_height", "top_flange_width", "top_web_height", "web_width"]
    BOTTOM_FLANGE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    BOTTOM_FLANGE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    BOTTOM_WEB_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    TOP_FLANGE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    TOP_FLANGE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    TOP_WEB_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    bottom_flange_height: float
    bottom_flange_width: float
    bottom_web_height: float
    height: float
    top_flange_height: float
    top_flange_width: float
    top_web_height: float
    web_width: float
    def __init__(self, height: _Optional[float] = ..., top_flange_height: _Optional[float] = ..., top_web_height: _Optional[float] = ..., bottom_web_height: _Optional[float] = ..., bottom_flange_height: _Optional[float] = ..., top_flange_width: _Optional[float] = ..., web_width: _Optional[float] = ..., bottom_flange_width: _Optional[float] = ...) -> None: ...

class IVParams(_message.Message):
    __slots__ = ["bottom_flange_height", "bottom_flange_width", "bottom_inner_web_width", "bottom_web_height", "bottom_web_width", "height", "top_flange_height", "top_flange_width", "top_inner_web_width", "top_web_height", "top_web_width"]
    BOTTOM_FLANGE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    BOTTOM_FLANGE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    BOTTOM_INNER_WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    BOTTOM_WEB_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    BOTTOM_WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    TOP_FLANGE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    TOP_FLANGE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    TOP_INNER_WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    TOP_WEB_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    TOP_WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    bottom_flange_height: float
    bottom_flange_width: float
    bottom_inner_web_width: float
    bottom_web_height: float
    bottom_web_width: float
    height: float
    top_flange_height: float
    top_flange_width: float
    top_inner_web_width: float
    top_web_height: float
    top_web_width: float
    def __init__(self, height: _Optional[float] = ..., top_flange_height: _Optional[float] = ..., top_web_height: _Optional[float] = ..., bottom_web_height: _Optional[float] = ..., bottom_flange_height: _Optional[float] = ..., top_flange_width: _Optional[float] = ..., top_web_width: _Optional[float] = ..., top_inner_web_width: _Optional[float] = ..., bottom_inner_web_width: _Optional[float] = ..., bottom_web_width: _Optional[float] = ..., bottom_flange_width: _Optional[float] = ...) -> None: ...

class KBEParams(_message.Message):
    __slots__ = ["bottom_width", "flange_height", "height", "side", "support_width", "web_width"]
    BOTTOM_WIDTH_FIELD_NUMBER: _ClassVar[int]
    FLANGE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    bottom_width: float
    flange_height: float
    height: float
    side: SectionSide
    support_width: float
    web_width: float
    def __init__(self, height: _Optional[float] = ..., flange_height: _Optional[float] = ..., web_width: _Optional[float] = ..., bottom_width: _Optional[float] = ..., support_width: _Optional[float] = ..., side: _Optional[_Union[SectionSide, str]] = ...) -> None: ...

class KBParams(_message.Message):
    __slots__ = ["bottom_width", "height", "inclination_left_flange", "inclination_right_flange", "left_flange_height", "left_support_width", "right_flange_height", "right_support_width"]
    BOTTOM_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    INCLINATION_LEFT_FLANGE_FIELD_NUMBER: _ClassVar[int]
    INCLINATION_RIGHT_FLANGE_FIELD_NUMBER: _ClassVar[int]
    LEFT_FLANGE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    LEFT_SUPPORT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    RIGHT_FLANGE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    RIGHT_SUPPORT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    bottom_width: float
    height: float
    inclination_left_flange: float
    inclination_right_flange: float
    left_flange_height: float
    left_support_width: float
    right_flange_height: float
    right_support_width: float
    def __init__(self, height: _Optional[float] = ..., left_flange_height: _Optional[float] = ..., right_flange_height: _Optional[float] = ..., inclination_left_flange: _Optional[float] = ..., inclination_right_flange: _Optional[float] = ..., bottom_width: _Optional[float] = ..., left_support_width: _Optional[float] = ..., right_support_width: _Optional[float] = ...) -> None: ...

class LParams(_message.Message):
    __slots__ = ["flange_height", "flange_width", "height", "side", "web_width"]
    FLANGE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FLANGE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    flange_height: float
    flange_width: float
    height: float
    side: SectionSide
    web_width: float
    def __init__(self, height: _Optional[float] = ..., flange_height: _Optional[float] = ..., flange_width: _Optional[float] = ..., web_width: _Optional[float] = ..., side: _Optional[_Union[SectionSide, str]] = ...) -> None: ...

class RHSParams(_message.Message):
    __slots__ = ["height", "radius", "thickness", "width"]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    height: float
    radius: float
    thickness: float
    width: float
    def __init__(self, height: _Optional[float] = ..., width: _Optional[float] = ..., thickness: _Optional[float] = ..., radius: _Optional[float] = ...) -> None: ...

class RParams(_message.Message):
    __slots__ = ["height", "width"]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    height: float
    width: float
    def __init__(self, height: _Optional[float] = ..., width: _Optional[float] = ...) -> None: ...

class Section(_message.Message):
    __slots__ = ["c_params", "co_params", "custom_params", "f_params", "hdx_params", "he_params", "hsq_params", "i_params", "id", "iv_params", "kb_params", "kbe_params", "l_params", "material_category", "orientation", "owner_name", "owner_type", "polycurves", "polylines", "r_params", "rhs_params", "t_params", "topping_params", "type", "u_params", "units", "ux_params", "vr_params", "vt_params", "z_params", "zx_params"]
    CO_PARAMS_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_PARAMS_FIELD_NUMBER: _ClassVar[int]
    C_PARAMS_FIELD_NUMBER: _ClassVar[int]
    F_PARAMS_FIELD_NUMBER: _ClassVar[int]
    HDX_PARAMS_FIELD_NUMBER: _ClassVar[int]
    HE_PARAMS_FIELD_NUMBER: _ClassVar[int]
    HSQ_PARAMS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    IV_PARAMS_FIELD_NUMBER: _ClassVar[int]
    I_PARAMS_FIELD_NUMBER: _ClassVar[int]
    KBE_PARAMS_FIELD_NUMBER: _ClassVar[int]
    KB_PARAMS_FIELD_NUMBER: _ClassVar[int]
    L_PARAMS_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    OWNER_NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_TYPE_FIELD_NUMBER: _ClassVar[int]
    POLYCURVES_FIELD_NUMBER: _ClassVar[int]
    POLYLINES_FIELD_NUMBER: _ClassVar[int]
    RHS_PARAMS_FIELD_NUMBER: _ClassVar[int]
    R_PARAMS_FIELD_NUMBER: _ClassVar[int]
    TOPPING_PARAMS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    T_PARAMS_FIELD_NUMBER: _ClassVar[int]
    UNITS_FIELD_NUMBER: _ClassVar[int]
    UX_PARAMS_FIELD_NUMBER: _ClassVar[int]
    U_PARAMS_FIELD_NUMBER: _ClassVar[int]
    VR_PARAMS_FIELD_NUMBER: _ClassVar[int]
    VT_PARAMS_FIELD_NUMBER: _ClassVar[int]
    ZX_PARAMS_FIELD_NUMBER: _ClassVar[int]
    Z_PARAMS_FIELD_NUMBER: _ClassVar[int]
    c_params: CParams
    co_params: COParams
    custom_params: CustomParams
    f_params: FParams
    hdx_params: HDXParams
    he_params: HEParams
    hsq_params: HSQParams
    i_params: IParams
    id: _utils_pb2_1.ID
    iv_params: IVParams
    kb_params: KBParams
    kbe_params: KBEParams
    l_params: LParams
    material_category: MaterialCategory
    orientation: _geometry_pb2.Orientation
    owner_name: str
    owner_type: _utils_pb2_1.Owner
    polycurves: _geometry_pb2.CurveFace2D
    polylines: _geometry_pb2.LineFace2D
    r_params: RParams
    rhs_params: RHSParams
    t_params: TParams
    topping_params: ToppingParams
    type: SectionType
    u_params: UParams
    units: SectionUnits
    ux_params: UXParams
    vr_params: VRParams
    vt_params: VTParams
    z_params: ZParams
    zx_params: ZXParams
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ..., type: _Optional[_Union[SectionType, str]] = ..., units: _Optional[_Union[SectionUnits, _Mapping]] = ..., polylines: _Optional[_Union[_geometry_pb2.LineFace2D, _Mapping]] = ..., polycurves: _Optional[_Union[_geometry_pb2.CurveFace2D, _Mapping]] = ..., material_category: _Optional[_Union[MaterialCategory, str]] = ..., orientation: _Optional[_Union[_geometry_pb2.Orientation, _Mapping]] = ..., custom_params: _Optional[_Union[CustomParams, _Mapping]] = ..., r_params: _Optional[_Union[RParams, _Mapping]] = ..., vr_params: _Optional[_Union[VRParams, _Mapping]] = ..., t_params: _Optional[_Union[TParams, _Mapping]] = ..., vt_params: _Optional[_Union[VTParams, _Mapping]] = ..., f_params: _Optional[_Union[FParams, _Mapping]] = ..., kb_params: _Optional[_Union[KBParams, _Mapping]] = ..., kbe_params: _Optional[_Union[KBEParams, _Mapping]] = ..., c_params: _Optional[_Union[CParams, _Mapping]] = ..., i_params: _Optional[_Union[IParams, _Mapping]] = ..., iv_params: _Optional[_Union[IVParams, _Mapping]] = ..., l_params: _Optional[_Union[LParams, _Mapping]] = ..., co_params: _Optional[_Union[COParams, _Mapping]] = ..., hdx_params: _Optional[_Union[HDXParams, _Mapping]] = ..., topping_params: _Optional[_Union[ToppingParams, _Mapping]] = ..., u_params: _Optional[_Union[UParams, _Mapping]] = ..., z_params: _Optional[_Union[ZParams, _Mapping]] = ..., rhs_params: _Optional[_Union[RHSParams, _Mapping]] = ..., he_params: _Optional[_Union[HEParams, _Mapping]] = ..., hsq_params: _Optional[_Union[HSQParams, _Mapping]] = ..., ux_params: _Optional[_Union[UXParams, _Mapping]] = ..., zx_params: _Optional[_Union[ZXParams, _Mapping]] = ..., owner_type: _Optional[_Union[_utils_pb2_1.Owner, str]] = ..., owner_name: _Optional[str] = ...) -> None: ...

class SectionUnits(_message.Message):
    __slots__ = ["a", "ang1", "ang2", "beta1", "beta2", "beta_omega", "c1", "c2", "cog", "emax1", "emax2", "emax_x", "emax_y", "emin1", "emin2", "emin_x", "emin_y", "i1", "i2", "i_t", "i_w", "i_x", "i_xy", "i_y", "ir1", "ir2", "ir_x", "ir_y", "j", "p", "rho1", "rho2", "sh1", "sh2", "sm1", "sm2", "sm_x", "sm_y", "w1", "w2", "w_t", "w_x", "w_y", "xc", "xs", "yc", "ys", "z1", "z2", "z_x", "z_y"]
    ANG1_FIELD_NUMBER: _ClassVar[int]
    ANG2_FIELD_NUMBER: _ClassVar[int]
    A_FIELD_NUMBER: _ClassVar[int]
    BETA1_FIELD_NUMBER: _ClassVar[int]
    BETA2_FIELD_NUMBER: _ClassVar[int]
    BETA_OMEGA_FIELD_NUMBER: _ClassVar[int]
    C1_FIELD_NUMBER: _ClassVar[int]
    C2_FIELD_NUMBER: _ClassVar[int]
    COG_FIELD_NUMBER: _ClassVar[int]
    EMAX1_FIELD_NUMBER: _ClassVar[int]
    EMAX2_FIELD_NUMBER: _ClassVar[int]
    EMAX_X_FIELD_NUMBER: _ClassVar[int]
    EMAX_Y_FIELD_NUMBER: _ClassVar[int]
    EMIN1_FIELD_NUMBER: _ClassVar[int]
    EMIN2_FIELD_NUMBER: _ClassVar[int]
    EMIN_X_FIELD_NUMBER: _ClassVar[int]
    EMIN_Y_FIELD_NUMBER: _ClassVar[int]
    I1_FIELD_NUMBER: _ClassVar[int]
    I2_FIELD_NUMBER: _ClassVar[int]
    IR1_FIELD_NUMBER: _ClassVar[int]
    IR2_FIELD_NUMBER: _ClassVar[int]
    IR_X_FIELD_NUMBER: _ClassVar[int]
    IR_Y_FIELD_NUMBER: _ClassVar[int]
    I_T_FIELD_NUMBER: _ClassVar[int]
    I_W_FIELD_NUMBER: _ClassVar[int]
    I_XY_FIELD_NUMBER: _ClassVar[int]
    I_X_FIELD_NUMBER: _ClassVar[int]
    I_Y_FIELD_NUMBER: _ClassVar[int]
    J_FIELD_NUMBER: _ClassVar[int]
    P_FIELD_NUMBER: _ClassVar[int]
    RHO1_FIELD_NUMBER: _ClassVar[int]
    RHO2_FIELD_NUMBER: _ClassVar[int]
    SH1_FIELD_NUMBER: _ClassVar[int]
    SH2_FIELD_NUMBER: _ClassVar[int]
    SM1_FIELD_NUMBER: _ClassVar[int]
    SM2_FIELD_NUMBER: _ClassVar[int]
    SM_X_FIELD_NUMBER: _ClassVar[int]
    SM_Y_FIELD_NUMBER: _ClassVar[int]
    W1_FIELD_NUMBER: _ClassVar[int]
    W2_FIELD_NUMBER: _ClassVar[int]
    W_T_FIELD_NUMBER: _ClassVar[int]
    W_X_FIELD_NUMBER: _ClassVar[int]
    W_Y_FIELD_NUMBER: _ClassVar[int]
    XC_FIELD_NUMBER: _ClassVar[int]
    XS_FIELD_NUMBER: _ClassVar[int]
    YC_FIELD_NUMBER: _ClassVar[int]
    YS_FIELD_NUMBER: _ClassVar[int]
    Z1_FIELD_NUMBER: _ClassVar[int]
    Z2_FIELD_NUMBER: _ClassVar[int]
    Z_X_FIELD_NUMBER: _ClassVar[int]
    Z_Y_FIELD_NUMBER: _ClassVar[int]
    a: float
    ang1: float
    ang2: float
    beta1: float
    beta2: float
    beta_omega: float
    c1: float
    c2: float
    cog: _geometry_pb2.Point2D
    emax1: float
    emax2: float
    emax_x: float
    emax_y: float
    emin1: float
    emin2: float
    emin_x: float
    emin_y: float
    i1: float
    i2: float
    i_t: float
    i_w: float
    i_x: float
    i_xy: float
    i_y: float
    ir1: float
    ir2: float
    ir_x: float
    ir_y: float
    j: float
    p: float
    rho1: float
    rho2: float
    sh1: float
    sh2: float
    sm1: float
    sm2: float
    sm_x: float
    sm_y: float
    w1: float
    w2: float
    w_t: float
    w_x: float
    w_y: float
    xc: float
    xs: float
    yc: float
    ys: float
    z1: float
    z2: float
    z_x: float
    z_y: float
    def __init__(self, a: _Optional[float] = ..., p: _Optional[float] = ..., xc: _Optional[float] = ..., yc: _Optional[float] = ..., xs: _Optional[float] = ..., ys: _Optional[float] = ..., i_x: _Optional[float] = ..., w_x: _Optional[float] = ..., z_x: _Optional[float] = ..., sm_x: _Optional[float] = ..., ir_x: _Optional[float] = ..., emax_y: _Optional[float] = ..., emin_y: _Optional[float] = ..., i_y: _Optional[float] = ..., w_y: _Optional[float] = ..., z_y: _Optional[float] = ..., sm_y: _Optional[float] = ..., ir_y: _Optional[float] = ..., emax_x: _Optional[float] = ..., emin_x: _Optional[float] = ..., j: _Optional[float] = ..., i_t: _Optional[float] = ..., w_t: _Optional[float] = ..., i_w: _Optional[float] = ..., i_xy: _Optional[float] = ..., beta_omega: _Optional[float] = ..., i1: _Optional[float] = ..., w1: _Optional[float] = ..., z1: _Optional[float] = ..., sm1: _Optional[float] = ..., ir1: _Optional[float] = ..., emax2: _Optional[float] = ..., emin2: _Optional[float] = ..., rho1: _Optional[float] = ..., c1: _Optional[float] = ..., beta1: _Optional[float] = ..., sh1: _Optional[float] = ..., ang1: _Optional[float] = ..., i2: _Optional[float] = ..., w2: _Optional[float] = ..., z2: _Optional[float] = ..., sm2: _Optional[float] = ..., ir2: _Optional[float] = ..., emax1: _Optional[float] = ..., emin1: _Optional[float] = ..., rho2: _Optional[float] = ..., c2: _Optional[float] = ..., beta2: _Optional[float] = ..., sh2: _Optional[float] = ..., ang2: _Optional[float] = ..., cog: _Optional[_Union[_geometry_pb2.Point2D, _Mapping]] = ...) -> None: ...

class TParams(_message.Message):
    __slots__ = ["flange_height", "flange_width", "height", "web_width"]
    FLANGE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FLANGE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    flange_height: float
    flange_width: float
    height: float
    web_width: float
    def __init__(self, height: _Optional[float] = ..., flange_height: _Optional[float] = ..., flange_width: _Optional[float] = ..., web_width: _Optional[float] = ...) -> None: ...

class ToppingParams(_message.Message):
    __slots__ = ["max_width_lft", "max_width_rgt", "min_thickness_lft", "min_thickness_rgt", "slope_thickness_lft", "slope_thickness_rgt", "thickness_above_beam", "width_above_beam", "width_of_max_thickness_lft", "width_of_max_thickness_rgt", "width_of_slope_lft", "width_of_slope_rgt"]
    MAX_WIDTH_LFT_FIELD_NUMBER: _ClassVar[int]
    MAX_WIDTH_RGT_FIELD_NUMBER: _ClassVar[int]
    MIN_THICKNESS_LFT_FIELD_NUMBER: _ClassVar[int]
    MIN_THICKNESS_RGT_FIELD_NUMBER: _ClassVar[int]
    SLOPE_THICKNESS_LFT_FIELD_NUMBER: _ClassVar[int]
    SLOPE_THICKNESS_RGT_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_ABOVE_BEAM_FIELD_NUMBER: _ClassVar[int]
    WIDTH_ABOVE_BEAM_FIELD_NUMBER: _ClassVar[int]
    WIDTH_OF_MAX_THICKNESS_LFT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_OF_MAX_THICKNESS_RGT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_OF_SLOPE_LFT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_OF_SLOPE_RGT_FIELD_NUMBER: _ClassVar[int]
    max_width_lft: float
    max_width_rgt: float
    min_thickness_lft: float
    min_thickness_rgt: float
    slope_thickness_lft: float
    slope_thickness_rgt: float
    thickness_above_beam: float
    width_above_beam: float
    width_of_max_thickness_lft: float
    width_of_max_thickness_rgt: float
    width_of_slope_lft: float
    width_of_slope_rgt: float
    def __init__(self, max_width_lft: _Optional[float] = ..., width_of_max_thickness_lft: _Optional[float] = ..., width_of_slope_lft: _Optional[float] = ..., max_width_rgt: _Optional[float] = ..., width_of_max_thickness_rgt: _Optional[float] = ..., width_of_slope_rgt: _Optional[float] = ..., thickness_above_beam: _Optional[float] = ..., min_thickness_lft: _Optional[float] = ..., slope_thickness_lft: _Optional[float] = ..., min_thickness_rgt: _Optional[float] = ..., slope_thickness_rgt: _Optional[float] = ..., width_above_beam: _Optional[float] = ...) -> None: ...

class UParams(_message.Message):
    __slots__ = ["flange_thickness", "height", "radius", "web_thickness", "width"]
    FLANGE_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    WEB_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    flange_thickness: float
    height: float
    radius: float
    web_thickness: float
    width: float
    def __init__(self, height: _Optional[float] = ..., width: _Optional[float] = ..., web_thickness: _Optional[float] = ..., flange_thickness: _Optional[float] = ..., radius: _Optional[float] = ...) -> None: ...

class UXParams(_message.Message):
    __slots__ = ["flange_thickness", "height", "web_thickness", "width"]
    FLANGE_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WEB_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    flange_thickness: float
    height: float
    web_thickness: float
    width: float
    def __init__(self, height: _Optional[float] = ..., width: _Optional[float] = ..., web_thickness: _Optional[float] = ..., flange_thickness: _Optional[float] = ...) -> None: ...

class VRParams(_message.Message):
    __slots__ = ["bottom_width", "height", "top_width"]
    BOTTOM_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    TOP_WIDTH_FIELD_NUMBER: _ClassVar[int]
    bottom_width: float
    height: float
    top_width: float
    def __init__(self, height: _Optional[float] = ..., top_width: _Optional[float] = ..., bottom_width: _Optional[float] = ...) -> None: ...

class VTParams(_message.Message):
    __slots__ = ["bottom_web_width", "flange_height", "flange_width", "height", "top_web_width"]
    BOTTOM_WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    FLANGE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FLANGE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    TOP_WEB_WIDTH_FIELD_NUMBER: _ClassVar[int]
    bottom_web_width: float
    flange_height: float
    flange_width: float
    height: float
    top_web_width: float
    def __init__(self, height: _Optional[float] = ..., flange_height: _Optional[float] = ..., flange_width: _Optional[float] = ..., top_web_width: _Optional[float] = ..., bottom_web_width: _Optional[float] = ...) -> None: ...

class ZParams(_message.Message):
    __slots__ = ["flange_thickness", "height", "radius", "web_thickness", "width"]
    FLANGE_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    WEB_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    flange_thickness: float
    height: float
    radius: float
    web_thickness: float
    width: float
    def __init__(self, height: _Optional[float] = ..., width: _Optional[float] = ..., web_thickness: _Optional[float] = ..., flange_thickness: _Optional[float] = ..., radius: _Optional[float] = ...) -> None: ...

class ZXParams(_message.Message):
    __slots__ = ["flange_thickness", "height", "web_thickness", "width"]
    FLANGE_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WEB_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    flange_thickness: float
    height: float
    web_thickness: float
    width: float
    def __init__(self, height: _Optional[float] = ..., width: _Optional[float] = ..., web_thickness: _Optional[float] = ..., flange_thickness: _Optional[float] = ...) -> None: ...

class SectionSide(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class SectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class MaterialCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
