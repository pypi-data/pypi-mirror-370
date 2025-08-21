from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

AGGREGATE_CALCAREOUS: Aggregates
AGGREGATE_DK_CALCAREOUS: Aggregates
AGGREGATE_DK_SILICEOUS: Aggregates
AGGREGATE_SILICEOUS: Aggregates
AGGREGATE_UNSPECIFIED: Aggregates
BEAM_SIDE_BOTTOM: BeamSide
BEAM_SIDE_END: BeamSide
BEAM_SIDE_LEFT: BeamSide
BEAM_SIDE_RIGHT: BeamSide
BEAM_SIDE_START: BeamSide
BEAM_SIDE_TOP: BeamSide
BEAM_SIDE_UNSPECIFIED: BeamSide
COLUMN_PLACEMENT_CENTER: ColumnPlacement
COLUMN_PLACEMENT_CORNER: ColumnPlacement
COLUMN_PLACEMENT_EDGE: ColumnPlacement
COLUMN_PLACEMENT_UNSPECIFIED: ColumnPlacement
COMMANDS_PUNCHING_CHECK: Commands
COMMANDS_SPALLING_CHECK: Commands
COMMANDS_STIRRUP_DESIGN: Commands
COMMANDS_UNSPECIFIED: Commands
CONSTRUCTION_CLASS_1: ConstructionClass
CONSTRUCTION_CLASS_2: ConstructionClass
CONSTRUCTION_CLASS_UNSPECIFIED: ConstructionClass
DESCRIPTOR: _descriptor.FileDescriptor
FABRICATION_IN_SITU: Fabrication
FABRICATION_PREFAB: Fabrication
FABRICATION_UNSPECIFIED: Fabrication
FCTM_TYPE_FCTM: FctmType
FCTM_TYPE_FCTM_FL: FctmType
FCTM_TYPE_FCTM_XI: FctmType
FCTM_TYPE_UNSPECIFIED: FctmType
SHEAR_DESIGN_TYPE_UNSPECIFIED: ShearDesignType
SHEAR_DESIGN_TYPE_WITHOUT_SHEAR_REINFORCEMENT: ShearDesignType
SHEAR_DESIGN_TYPE_WITH_SHEAR_REINFORCEMENT: ShearDesignType
SURFACE_TYPE_INDENTED: SurfaceType
SURFACE_TYPE_ROUGH: SurfaceType
SURFACE_TYPE_SMOOTH: SurfaceType
SURFACE_TYPE_UNSPECIFIED: SurfaceType
SURFACE_TYPE_VERY_SMOOTH: SurfaceType
WEB_SHEAR_CAPACITY_METHOD_ADVANCED: WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_SIMPLIFIED: WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_STANDARD: WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_UNSPECIFIED: WebShearCapacityMethod

class Beam(_message.Message):
    __slots__ = ["consider_as_slab", "fire", "monolithic", "shear_design_type", "surface_type", "use_min_reinf"]
    CONSIDER_AS_SLAB_FIELD_NUMBER: _ClassVar[int]
    FIRE_FIELD_NUMBER: _ClassVar[int]
    MONOLITHIC_FIELD_NUMBER: _ClassVar[int]
    SHEAR_DESIGN_TYPE_FIELD_NUMBER: _ClassVar[int]
    SURFACE_TYPE_FIELD_NUMBER: _ClassVar[int]
    USE_MIN_REINF_FIELD_NUMBER: _ClassVar[int]
    consider_as_slab: bool
    fire: FireBeam
    monolithic: bool
    shear_design_type: ShearDesignType
    surface_type: SurfaceType
    use_min_reinf: bool
    def __init__(self, surface_type: _Optional[_Union[SurfaceType, str]] = ..., shear_design_type: _Optional[_Union[ShearDesignType, str]] = ..., use_min_reinf: bool = ..., monolithic: bool = ..., fire: _Optional[_Union[FireBeam, _Mapping]] = ..., consider_as_slab: bool = ...) -> None: ...

class Column(_message.Message):
    __slots__ = ["no_reinf", "shear_design_type", "use_min_reinf"]
    NO_REINF_FIELD_NUMBER: _ClassVar[int]
    SHEAR_DESIGN_TYPE_FIELD_NUMBER: _ClassVar[int]
    USE_MIN_REINF_FIELD_NUMBER: _ClassVar[int]
    no_reinf: bool
    shear_design_type: ShearDesignType
    use_min_reinf: bool
    def __init__(self, no_reinf: bool = ..., use_min_reinf: bool = ..., shear_design_type: _Optional[_Union[ShearDesignType, str]] = ...) -> None: ...

class CoverAndSpace(_message.Message):
    __slots__ = ["cover", "side", "space"]
    COVER_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    SPACE_FIELD_NUMBER: _ClassVar[int]
    cover: float
    side: BeamSide
    space: float
    def __init__(self, cover: _Optional[float] = ..., space: _Optional[float] = ..., side: _Optional[_Union[BeamSide, str]] = ...) -> None: ...

class ElementDesignSettings(_message.Message):
    __slots__ = ["additional_commands", "beam", "column", "construction_class", "cot", "cracked_in_shear", "enhanced_data", "enhanced_quality", "enhanced_shear", "fabrication", "fctm_type", "hc", "largest_aggregate_size", "low_strength_variation", "partial_coeffs", "ps", "slab", "smallest_aggregate_size", "use_comp_reinf", "wall"]
    ADDITIONAL_COMMANDS_FIELD_NUMBER: _ClassVar[int]
    BEAM_FIELD_NUMBER: _ClassVar[int]
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    CONSTRUCTION_CLASS_FIELD_NUMBER: _ClassVar[int]
    COT_FIELD_NUMBER: _ClassVar[int]
    CRACKED_IN_SHEAR_FIELD_NUMBER: _ClassVar[int]
    ENHANCED_DATA_FIELD_NUMBER: _ClassVar[int]
    ENHANCED_QUALITY_FIELD_NUMBER: _ClassVar[int]
    ENHANCED_SHEAR_FIELD_NUMBER: _ClassVar[int]
    FABRICATION_FIELD_NUMBER: _ClassVar[int]
    FCTM_TYPE_FIELD_NUMBER: _ClassVar[int]
    HC_FIELD_NUMBER: _ClassVar[int]
    LARGEST_AGGREGATE_SIZE_FIELD_NUMBER: _ClassVar[int]
    LOW_STRENGTH_VARIATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_COEFFS_FIELD_NUMBER: _ClassVar[int]
    PS_FIELD_NUMBER: _ClassVar[int]
    SLAB_FIELD_NUMBER: _ClassVar[int]
    SMALLEST_AGGREGATE_SIZE_FIELD_NUMBER: _ClassVar[int]
    USE_COMP_REINF_FIELD_NUMBER: _ClassVar[int]
    WALL_FIELD_NUMBER: _ClassVar[int]
    additional_commands: _containers.RepeatedScalarFieldContainer[Commands]
    beam: Beam
    column: Column
    construction_class: ConstructionClass
    cot: float
    cracked_in_shear: bool
    enhanced_data: bool
    enhanced_quality: bool
    enhanced_shear: bool
    fabrication: Fabrication
    fctm_type: FctmType
    hc: HC
    largest_aggregate_size: float
    low_strength_variation: bool
    partial_coeffs: PartialCoefficients
    ps: PrestressedBeam
    slab: Slab
    smallest_aggregate_size: float
    use_comp_reinf: bool
    wall: Wall
    def __init__(self, partial_coeffs: _Optional[_Union[PartialCoefficients, _Mapping]] = ..., fabrication: _Optional[_Union[Fabrication, str]] = ..., enhanced_shear: bool = ..., enhanced_quality: bool = ..., enhanced_data: bool = ..., cracked_in_shear: bool = ..., cot: _Optional[float] = ..., construction_class: _Optional[_Union[ConstructionClass, str]] = ..., fctm_type: _Optional[_Union[FctmType, str]] = ..., use_comp_reinf: bool = ..., low_strength_variation: bool = ..., largest_aggregate_size: _Optional[float] = ..., smallest_aggregate_size: _Optional[float] = ..., beam: _Optional[_Union[Beam, _Mapping]] = ..., column: _Optional[_Union[Column, _Mapping]] = ..., wall: _Optional[_Union[Wall, _Mapping]] = ..., ps: _Optional[_Union[PrestressedBeam, _Mapping]] = ..., hc: _Optional[_Union[HC, _Mapping]] = ..., slab: _Optional[_Union[Slab, _Mapping]] = ..., additional_commands: _Optional[_Iterable[_Union[Commands, str]]] = ...) -> None: ...

class FireBeam(_message.Message):
    __slots__ = ["aggregate", "bottom_side", "fire_time", "left_side", "right_side", "upper_side", "use_0_2_epsilon"]
    AGGREGATE_FIELD_NUMBER: _ClassVar[int]
    BOTTOM_SIDE_FIELD_NUMBER: _ClassVar[int]
    FIRE_TIME_FIELD_NUMBER: _ClassVar[int]
    LEFT_SIDE_FIELD_NUMBER: _ClassVar[int]
    RIGHT_SIDE_FIELD_NUMBER: _ClassVar[int]
    UPPER_SIDE_FIELD_NUMBER: _ClassVar[int]
    USE_0_2_EPSILON_FIELD_NUMBER: _ClassVar[int]
    aggregate: Aggregates
    bottom_side: bool
    fire_time: int
    left_side: bool
    right_side: bool
    upper_side: bool
    use_0_2_epsilon: bool
    def __init__(self, upper_side: bool = ..., bottom_side: bool = ..., left_side: bool = ..., right_side: bool = ..., fire_time: _Optional[int] = ..., aggregate: _Optional[_Union[Aggregates, str]] = ..., use_0_2_epsilon: bool = ...) -> None: ...

class GeneralDesignSettings(_message.Message):
    __slots__ = ["crack_check", "crk_conv", "max_num_iter", "member_surface_emissivity_rc"]
    CRACK_CHECK_FIELD_NUMBER: _ClassVar[int]
    CRK_CONV_FIELD_NUMBER: _ClassVar[int]
    MAX_NUM_ITER_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SURFACE_EMISSIVITY_RC_FIELD_NUMBER: _ClassVar[int]
    crack_check: bool
    crk_conv: float
    max_num_iter: int
    member_surface_emissivity_rc: float
    def __init__(self, member_surface_emissivity_rc: _Optional[float] = ..., max_num_iter: _Optional[int] = ..., crk_conv: _Optional[float] = ..., crack_check: bool = ...) -> None: ...

class HC(_message.Message):
    __slots__ = ["consider_punching_edge_reduction", "surface_type", "use_shear_topping_cap", "web_shear_method"]
    CONSIDER_PUNCHING_EDGE_REDUCTION_FIELD_NUMBER: _ClassVar[int]
    SURFACE_TYPE_FIELD_NUMBER: _ClassVar[int]
    USE_SHEAR_TOPPING_CAP_FIELD_NUMBER: _ClassVar[int]
    WEB_SHEAR_METHOD_FIELD_NUMBER: _ClassVar[int]
    consider_punching_edge_reduction: bool
    surface_type: SurfaceType
    use_shear_topping_cap: bool
    web_shear_method: WebShearCapacityMethod
    def __init__(self, consider_punching_edge_reduction: bool = ..., surface_type: _Optional[_Union[SurfaceType, str]] = ..., use_shear_topping_cap: bool = ..., web_shear_method: _Optional[_Union[WebShearCapacityMethod, str]] = ...) -> None: ...

class PartialCoefficient(_message.Message):
    __slots__ = ["alfa_cc", "alfa_ct", "gamma_ce", "gamma_compression", "gamma_reinforcement", "gamma_shear", "gamma_tension"]
    ALFA_CC_FIELD_NUMBER: _ClassVar[int]
    ALFA_CT_FIELD_NUMBER: _ClassVar[int]
    GAMMA_CE_FIELD_NUMBER: _ClassVar[int]
    GAMMA_COMPRESSION_FIELD_NUMBER: _ClassVar[int]
    GAMMA_REINFORCEMENT_FIELD_NUMBER: _ClassVar[int]
    GAMMA_SHEAR_FIELD_NUMBER: _ClassVar[int]
    GAMMA_TENSION_FIELD_NUMBER: _ClassVar[int]
    alfa_cc: float
    alfa_ct: float
    gamma_ce: float
    gamma_compression: float
    gamma_reinforcement: float
    gamma_shear: float
    gamma_tension: float
    def __init__(self, gamma_compression: _Optional[float] = ..., gamma_tension: _Optional[float] = ..., gamma_reinforcement: _Optional[float] = ..., gamma_ce: _Optional[float] = ..., alfa_cc: _Optional[float] = ..., alfa_ct: _Optional[float] = ..., gamma_shear: _Optional[float] = ...) -> None: ...

class PartialCoefficients(_message.Message):
    __slots__ = ["accidental", "fire", "seismic", "service", "ultimate"]
    ACCIDENTAL_FIELD_NUMBER: _ClassVar[int]
    FIRE_FIELD_NUMBER: _ClassVar[int]
    SEISMIC_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    ULTIMATE_FIELD_NUMBER: _ClassVar[int]
    accidental: PartialCoefficient
    fire: PartialCoefficient
    seismic: PartialCoefficient
    service: PartialCoefficient
    ultimate: PartialCoefficient
    def __init__(self, ultimate: _Optional[_Union[PartialCoefficient, _Mapping]] = ..., accidental: _Optional[_Union[PartialCoefficient, _Mapping]] = ..., seismic: _Optional[_Union[PartialCoefficient, _Mapping]] = ..., fire: _Optional[_Union[PartialCoefficient, _Mapping]] = ..., service: _Optional[_Union[PartialCoefficient, _Mapping]] = ...) -> None: ...

class PrestressedBeam(_message.Message):
    __slots__ = ["limit_fyd", "monolithic", "shear_design_type", "surface_type", "use_min_reinf"]
    LIMIT_FYD_FIELD_NUMBER: _ClassVar[int]
    MONOLITHIC_FIELD_NUMBER: _ClassVar[int]
    SHEAR_DESIGN_TYPE_FIELD_NUMBER: _ClassVar[int]
    SURFACE_TYPE_FIELD_NUMBER: _ClassVar[int]
    USE_MIN_REINF_FIELD_NUMBER: _ClassVar[int]
    limit_fyd: float
    monolithic: bool
    shear_design_type: ShearDesignType
    surface_type: SurfaceType
    use_min_reinf: bool
    def __init__(self, surface_type: _Optional[_Union[SurfaceType, str]] = ..., shear_design_type: _Optional[_Union[ShearDesignType, str]] = ..., use_min_reinf: bool = ..., monolithic: bool = ..., limit_fyd: _Optional[float] = ...) -> None: ...

class Slab(_message.Message):
    __slots__ = ["consider_punching_edge_reduction", "surface_type"]
    CONSIDER_PUNCHING_EDGE_REDUCTION_FIELD_NUMBER: _ClassVar[int]
    SURFACE_TYPE_FIELD_NUMBER: _ClassVar[int]
    consider_punching_edge_reduction: bool
    surface_type: SurfaceType
    def __init__(self, consider_punching_edge_reduction: bool = ..., surface_type: _Optional[_Union[SurfaceType, str]] = ...) -> None: ...

class Wall(_message.Message):
    __slots__ = ["no_reinf", "use_min_reinf"]
    NO_REINF_FIELD_NUMBER: _ClassVar[int]
    USE_MIN_REINF_FIELD_NUMBER: _ClassVar[int]
    no_reinf: bool
    use_min_reinf: bool
    def __init__(self, no_reinf: bool = ..., use_min_reinf: bool = ...) -> None: ...

class Fabrication(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ColumnPlacement(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class BeamSide(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ConstructionClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ShearDesignType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class WebShearCapacityMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class SurfaceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class FctmType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Commands(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Aggregates(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
