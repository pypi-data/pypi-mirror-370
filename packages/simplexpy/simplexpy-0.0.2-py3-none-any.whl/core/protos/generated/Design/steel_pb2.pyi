from Utils import utils_pb2 as _utils_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
BUCKLING_CURVE_FLEXURAL_A: BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_A0: BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_AUTO: BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_B: BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_C: BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_D: BucklingCurveFlexural
BUCKLING_CURVE_FLEXURAL_UNSPECIFIED: BucklingCurveFlexural
BUCKLING_CURVE_LATERAL_A: BucklingCurveLateral
BUCKLING_CURVE_LATERAL_AUTO: BucklingCurveLateral
BUCKLING_CURVE_LATERAL_B: BucklingCurveLateral
BUCKLING_CURVE_LATERAL_C: BucklingCurveLateral
BUCKLING_CURVE_LATERAL_D: BucklingCurveLateral
BUCKLING_CURVE_LATERAL_UNSPECIFIED: BucklingCurveLateral
DESCRIPTOR: _descriptor.FileDescriptor
INTERACTION_METHOD_METHOD1: InteractionMethod
INTERACTION_METHOD_METHOD2: InteractionMethod
INTERACTION_METHOD_UNSPECIFIED: InteractionMethod
LATERAL_TORSIONAL_METHOD_GENERAL: LateralTorsionalMethod
LATERAL_TORSIONAL_METHOD_GENERAL_SPEC_FOR_I: LateralTorsionalMethod
LATERAL_TORSIONAL_METHOD_SIMPLIFIED: LateralTorsionalMethod
LATERAL_TORSIONAL_METHOD_UNSPECIFIED: LateralTorsionalMethod
OWNER_COMPANY: _utils_pb2.Owner
OWNER_OFFICE: _utils_pb2.Owner
OWNER_STRUSOFT: _utils_pb2.Owner
OWNER_UNSPECIFIED: _utils_pb2.Owner
OWNER_USER: _utils_pb2.Owner
SECOND_ORDER_ANALYSIS_CONSIDER: SecondOrderAnalysis
SECOND_ORDER_ANALYSIS_FIRST_ORDER_DESIGN: SecondOrderAnalysis
SECOND_ORDER_ANALYSIS_IGNORE: SecondOrderAnalysis
SECOND_ORDER_ANALYSIS_UNSPECIFIED: SecondOrderAnalysis
SECTION_EXPOSURE_ALL_SIDES: SectionExposure
SECTION_EXPOSURE_FLANGE_ONLY: SectionExposure
SECTION_EXPOSURE_THREE_SIDES: SectionExposure
SECTION_EXPOSURE_UNSPECIFIED: SectionExposure

class BeamSettings(_message.Message):
    __slots__ = ["check_resistance_only", "class4_not_allowed", "fb_curve_stiff", "fb_curve_weak", "ft_curve", "lateral_torsional_method", "ltb_curve_btm", "ltb_curve_top", "plastic_calculation_not_allowed", "second_order_analysis", "use641"]
    CHECK_RESISTANCE_ONLY_FIELD_NUMBER: _ClassVar[int]
    CLASS4_NOT_ALLOWED_FIELD_NUMBER: _ClassVar[int]
    FB_CURVE_STIFF_FIELD_NUMBER: _ClassVar[int]
    FB_CURVE_WEAK_FIELD_NUMBER: _ClassVar[int]
    FT_CURVE_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_METHOD_FIELD_NUMBER: _ClassVar[int]
    LTB_CURVE_BTM_FIELD_NUMBER: _ClassVar[int]
    LTB_CURVE_TOP_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_CALCULATION_NOT_ALLOWED_FIELD_NUMBER: _ClassVar[int]
    SECOND_ORDER_ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    USE641_FIELD_NUMBER: _ClassVar[int]
    check_resistance_only: bool
    class4_not_allowed: bool
    fb_curve_stiff: BucklingCurveFlexural
    fb_curve_weak: BucklingCurveFlexural
    ft_curve: BucklingCurveFlexural
    lateral_torsional_method: LateralTorsionalMethod
    ltb_curve_btm: BucklingCurveLateral
    ltb_curve_top: BucklingCurveLateral
    plastic_calculation_not_allowed: bool
    second_order_analysis: SecondOrderAnalysis
    use641: bool
    def __init__(self, second_order_analysis: _Optional[_Union[SecondOrderAnalysis, str]] = ..., plastic_calculation_not_allowed: bool = ..., use641: bool = ..., class4_not_allowed: bool = ..., lateral_torsional_method: _Optional[_Union[LateralTorsionalMethod, str]] = ..., check_resistance_only: bool = ..., fb_curve_stiff: _Optional[_Union[BucklingCurveFlexural, str]] = ..., fb_curve_weak: _Optional[_Union[BucklingCurveFlexural, str]] = ..., ft_curve: _Optional[_Union[BucklingCurveFlexural, str]] = ..., ltb_curve_top: _Optional[_Union[BucklingCurveLateral, str]] = ..., ltb_curve_btm: _Optional[_Union[BucklingCurveLateral, str]] = ...) -> None: ...

class ElementDesignSettings(_message.Message):
    __slots__ = ["beam", "fire"]
    BEAM_FIELD_NUMBER: _ClassVar[int]
    FIRE_FIELD_NUMBER: _ClassVar[int]
    beam: BeamSettings
    fire: Fire
    def __init__(self, beam: _Optional[_Union[BeamSettings, _Mapping]] = ..., fire: _Optional[_Union[Fire, _Mapping]] = ...) -> None: ...

class Fire(_message.Message):
    __slots__ = ["crit_deflection", "protected", "protecting_material", "section_exposure", "temperature"]
    CRIT_DEFLECTION_FIELD_NUMBER: _ClassVar[int]
    PROTECTED_FIELD_NUMBER: _ClassVar[int]
    PROTECTING_MATERIAL_FIELD_NUMBER: _ClassVar[int]
    SECTION_EXPOSURE_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    crit_deflection: bool
    protected: bool
    protecting_material: ProtectingMaterial
    section_exposure: SectionExposure
    temperature: float
    def __init__(self, crit_deflection: bool = ..., protected: bool = ..., protecting_material: _Optional[_Union[ProtectingMaterial, _Mapping]] = ..., temperature: _Optional[float] = ..., section_exposure: _Optional[_Union[SectionExposure, str]] = ...) -> None: ...

class GeneralDesignSettings(_message.Message):
    __slots__ = ["interaction_method", "kappa2", "member_surface_emissivity_carbon_steel", "member_surface_emissivity_strainless_steel", "partial_coeffs"]
    INTERACTION_METHOD_FIELD_NUMBER: _ClassVar[int]
    KAPPA2_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SURFACE_EMISSIVITY_CARBON_STEEL_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SURFACE_EMISSIVITY_STRAINLESS_STEEL_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_COEFFS_FIELD_NUMBER: _ClassVar[int]
    interaction_method: InteractionMethod
    kappa2: float
    member_surface_emissivity_carbon_steel: float
    member_surface_emissivity_strainless_steel: float
    partial_coeffs: PartialCoefficients
    def __init__(self, partial_coeffs: _Optional[_Union[PartialCoefficients, _Mapping]] = ..., interaction_method: _Optional[_Union[InteractionMethod, str]] = ..., kappa2: _Optional[float] = ..., member_surface_emissivity_carbon_steel: _Optional[float] = ..., member_surface_emissivity_strainless_steel: _Optional[float] = ...) -> None: ...

class PartialCoefficient(_message.Message):
    __slots__ = ["gamma_m0", "gamma_m1", "gamma_m2", "gamma_m5"]
    GAMMA_M0_FIELD_NUMBER: _ClassVar[int]
    GAMMA_M1_FIELD_NUMBER: _ClassVar[int]
    GAMMA_M2_FIELD_NUMBER: _ClassVar[int]
    GAMMA_M5_FIELD_NUMBER: _ClassVar[int]
    gamma_m0: float
    gamma_m1: float
    gamma_m2: float
    gamma_m5: float
    def __init__(self, gamma_m0: _Optional[float] = ..., gamma_m1: _Optional[float] = ..., gamma_m2: _Optional[float] = ..., gamma_m5: _Optional[float] = ...) -> None: ...

class PartialCoefficients(_message.Message):
    __slots__ = ["accidental", "gamma_fire", "ultimate"]
    ACCIDENTAL_FIELD_NUMBER: _ClassVar[int]
    GAMMA_FIRE_FIELD_NUMBER: _ClassVar[int]
    ULTIMATE_FIELD_NUMBER: _ClassVar[int]
    accidental: PartialCoefficient
    gamma_fire: float
    ultimate: PartialCoefficient
    def __init__(self, ultimate: _Optional[_Union[PartialCoefficient, _Mapping]] = ..., accidental: _Optional[_Union[PartialCoefficient, _Mapping]] = ..., gamma_fire: _Optional[float] = ...) -> None: ...

class ProtectingMaterial(_message.Message):
    __slots__ = ["guid", "thickness"]
    GUID_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_FIELD_NUMBER: _ClassVar[int]
    guid: str
    thickness: float
    def __init__(self, guid: _Optional[str] = ..., thickness: _Optional[float] = ...) -> None: ...

class SecondOrderAnalysis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class InteractionMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class LateralTorsionalMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class BucklingCurveFlexural(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class BucklingCurveLateral(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class SectionExposure(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
