from Utils import utils_pb2 as _utils_pb2
import stage_pb2 as _stage_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Utils import topology_pb2 as _topology_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Geometry import geometry_pb2 as _geometry_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1
from Geometry import foundation_pb2 as _foundation_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1_1
from Geometry import rebar_pb2 as _rebar_pb2
from Design import concrete_pb2 as _concrete_pb2
from Design import design_pb2 as _design_pb2
from Design import load_pb2 as _load_pb2
from Design import concrete_pb2 as _concrete_pb2_1
from Design import steel_pb2 as _steel_pb2
from Design import timber_pb2 as _timber_pb2
from Design import soil_pb2 as _soil_pb2
from Design import general_pb2 as _general_pb2
from Geometry import rebar_pb2 as _rebar_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1_1_1
from Geometry import reinf_pb2 as _reinf_pb2
from Geometry import strand_pb2 as _strand_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1_1_1_1
from Geometry import reinf_pb2 as _reinf_pb2_1
from Geometry import link_pb2 as _link_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1_1_1_1_1
from Geometry import reinf_pb2 as _reinf_pb2_1_1
from Design import concrete_pb2 as _concrete_pb2_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
from stage_pb2 import Data
from stage_pb2 import Beam
from stage_pb2 import Foundation
from stage_pb2 import RetainingWall
from stage_pb2 import Pile
from stage_pb2 import Element
from stage_pb2 import RCSpecific
from stage_pb2 import RC
from stage_pb2 import SteelSpecific
from stage_pb2 import TimberSpecific
from stage_pb2 import SoilSpecific
from stage_pb2 import SupportElementConnection
from stage_pb2 import Support
from stage_pb2 import ExposureClass
from stage_pb2 import LifeCategory
from stage_pb2 import EnvironmentalClass
from stage_pb2 import SupportLevel
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
from Geometry.foundation_pb2 import PointFoundation
from Geometry.foundation_pb2 import LineFoundation
from Geometry.foundation_pb2 import Circle
from Geometry.foundation_pb2 import Rectangle
from Geometry.foundation_pb2 import Elements
from Geometry.foundation_pb2 import FoundationGeometry
from Geometry.foundation_pb2 import ConcreteParameters
from Geometry.foundation_pb2 import SimpleFoundation
from Geometry.foundation_pb2 import AdvancedFoundation
from Geometry.foundation_pb2 import Data
from Design.design_pb2 import ElementDesignSettings
from Design.design_pb2 import GeneralDesignSettings
from Geometry.rebar_pb2 import Data
from Geometry.strand_pb2 import Data
from Geometry.link_pb2 import Group
from Geometry.link_pb2 import Data
from Design.concrete_pb2 import PartialCoefficient
from Design.concrete_pb2 import PartialCoefficients
from Design.concrete_pb2 import CoverAndSpace
from Design.concrete_pb2 import FireBeam
from Design.concrete_pb2 import Beam
from Design.concrete_pb2 import Column
from Design.concrete_pb2 import Wall
from Design.concrete_pb2 import PrestressedBeam
from Design.concrete_pb2 import HC
from Design.concrete_pb2 import Slab
from Design.concrete_pb2 import GeneralDesignSettings
from Design.concrete_pb2 import ElementDesignSettings
from Design.concrete_pb2 import Fabrication
from Design.concrete_pb2 import ColumnPlacement
from Design.concrete_pb2 import BeamSide
from Design.concrete_pb2 import ConstructionClass
from Design.concrete_pb2 import ShearDesignType
from Design.concrete_pb2 import WebShearCapacityMethod
from Design.concrete_pb2 import SurfaceType
from Design.concrete_pb2 import FctmType
from Design.concrete_pb2 import Commands
from Design.concrete_pb2 import Aggregates
ACTION_TYPE_BAR: ActionType
ACTION_TYPE_BEAM: ActionType
ACTION_TYPE_COLUMN: ActionType
ACTION_TYPE_UNSPECIFIED: ActionType
AGGREGATE_CALCAREOUS: _concrete_pb2_1_1.Aggregates
AGGREGATE_DK_CALCAREOUS: _concrete_pb2_1_1.Aggregates
AGGREGATE_DK_SILICEOUS: _concrete_pb2_1_1.Aggregates
AGGREGATE_SILICEOUS: _concrete_pb2_1_1.Aggregates
AGGREGATE_UNSPECIFIED: _concrete_pb2_1_1.Aggregates
ALIGNMENT_BOTTOM: Alignment
ALIGNMENT_CENTER: Alignment
ALIGNMENT_TOP: Alignment
ALIGNMENT_UNSPECIFIED: Alignment
BEAM_SIDE_BOTTOM: _concrete_pb2_1_1.BeamSide
BEAM_SIDE_END: _concrete_pb2_1_1.BeamSide
BEAM_SIDE_LEFT: _concrete_pb2_1_1.BeamSide
BEAM_SIDE_RIGHT: _concrete_pb2_1_1.BeamSide
BEAM_SIDE_START: _concrete_pb2_1_1.BeamSide
BEAM_SIDE_TOP: _concrete_pb2_1_1.BeamSide
BEAM_SIDE_UNSPECIFIED: _concrete_pb2_1_1.BeamSide
BUCKLING_TYPE_FLEXURAL_STIFF: BucklingType
BUCKLING_TYPE_FLEXURAL_WEAK: BucklingType
BUCKLING_TYPE_LATERAL_TORSIONAL: BucklingType
BUCKLING_TYPE_PRESSURED_BOTTOM_FLANGE: BucklingType
BUCKLING_TYPE_PRESSURED_TOP_FLANGE: BucklingType
BUCKLING_TYPE_UNSPECIFIED: BucklingType
COLUMN_PLACEMENT_CENTER: _concrete_pb2_1_1.ColumnPlacement
COLUMN_PLACEMENT_CORNER: _concrete_pb2_1_1.ColumnPlacement
COLUMN_PLACEMENT_EDGE: _concrete_pb2_1_1.ColumnPlacement
COLUMN_PLACEMENT_UNSPECIFIED: _concrete_pb2_1_1.ColumnPlacement
COMMANDS_PUNCHING_CHECK: _concrete_pb2_1_1.Commands
COMMANDS_SPALLING_CHECK: _concrete_pb2_1_1.Commands
COMMANDS_STIRRUP_DESIGN: _concrete_pb2_1_1.Commands
COMMANDS_UNSPECIFIED: _concrete_pb2_1_1.Commands
CONCRETE_BEAM_TYPE_CONSTANT: ConcreteBeamType
CONCRETE_BEAM_TYPE_CUSTOM: ConcreteBeamType
CONCRETE_BEAM_TYPE_IB: ConcreteBeamType
CONCRETE_BEAM_TYPE_RBX: ConcreteBeamType
CONCRETE_BEAM_TYPE_SIB: ConcreteBeamType
CONCRETE_BEAM_TYPE_STT: ConcreteBeamType
CONCRETE_BEAM_TYPE_UNSPECIFIED: ConcreteBeamType
CONSTRUCTION_CLASS_1: _concrete_pb2_1_1.ConstructionClass
CONSTRUCTION_CLASS_2: _concrete_pb2_1_1.ConstructionClass
CONSTRUCTION_CLASS_UNSPECIFIED: _concrete_pb2_1_1.ConstructionClass
DESCRIPTOR: _descriptor.FileDescriptor
ENVIROMENTAL_CLASS_AGGRESSIVE: _stage_pb2.EnvironmentalClass
ENVIROMENTAL_CLASS_EXTRA_AGGRESSIVE: _stage_pb2.EnvironmentalClass
ENVIROMENTAL_CLASS_MODERATE: _stage_pb2.EnvironmentalClass
ENVIROMENTAL_CLASS_PASSIVE: _stage_pb2.EnvironmentalClass
ENVIROMENTAL_CLASS_UNSPECIFIED: _stage_pb2.EnvironmentalClass
EXPOSURE_CLASS_UNSPECIFIED: _stage_pb2.ExposureClass
EXPOSURE_CLASS_X0: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XA1: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XA2: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XA3: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XC1: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XC2: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XC3: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XC4: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XD1: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XD2: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XD3: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XF1: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XF2: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XF3: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XF4: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XS1: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XS2: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XS3: _stage_pb2.ExposureClass
FABRICATION_IN_SITU: _concrete_pb2_1_1.Fabrication
FABRICATION_PREFAB: _concrete_pb2_1_1.Fabrication
FABRICATION_UNSPECIFIED: _concrete_pb2_1_1.Fabrication
FCTM_TYPE_FCTM: _concrete_pb2_1_1.FctmType
FCTM_TYPE_FCTM_FL: _concrete_pb2_1_1.FctmType
FCTM_TYPE_FCTM_XI: _concrete_pb2_1_1.FctmType
FCTM_TYPE_UNSPECIFIED: _concrete_pb2_1_1.FctmType
LIFE_CATEGORY_L100: _stage_pb2.LifeCategory
LIFE_CATEGORY_L20: _stage_pb2.LifeCategory
LIFE_CATEGORY_L50: _stage_pb2.LifeCategory
LIFE_CATEGORY_UNSPECIFIED: _stage_pb2.LifeCategory
OWNER_COMPANY: _utils_pb2_1_1_1_1_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1_1_1_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1_1_1_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1_1_1_1_1.Owner
OWNER_USER: _utils_pb2_1_1_1_1_1_1.Owner
SHEAR_DESIGN_TYPE_UNSPECIFIED: _concrete_pb2_1_1.ShearDesignType
SHEAR_DESIGN_TYPE_WITHOUT_SHEAR_REINFORCEMENT: _concrete_pb2_1_1.ShearDesignType
SHEAR_DESIGN_TYPE_WITH_SHEAR_REINFORCEMENT: _concrete_pb2_1_1.ShearDesignType
SUPPORT_CONDITION_CANTILEVER: SupportCondition
SUPPORT_CONDITION_SIMPLY: SupportCondition
SUPPORT_CONDITION_UNSPECIFIED: SupportCondition
SUPPORT_LEVEL_BOTTOM: _stage_pb2.SupportLevel
SUPPORT_LEVEL_CENTER: _stage_pb2.SupportLevel
SUPPORT_LEVEL_TOP: _stage_pb2.SupportLevel
SUPPORT_LEVEL_UNSPECIFIED: _stage_pb2.SupportLevel
SURFACE_TYPE_INDENTED: _concrete_pb2_1_1.SurfaceType
SURFACE_TYPE_ROUGH: _concrete_pb2_1_1.SurfaceType
SURFACE_TYPE_SMOOTH: _concrete_pb2_1_1.SurfaceType
SURFACE_TYPE_UNSPECIFIED: _concrete_pb2_1_1.SurfaceType
SURFACE_TYPE_VERY_SMOOTH: _concrete_pb2_1_1.SurfaceType
WEB_SHEAR_CAPACITY_METHOD_ADVANCED: _concrete_pb2_1_1.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_SIMPLIFIED: _concrete_pb2_1_1.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_STANDARD: _concrete_pb2_1_1.WebShearCapacityMethod
WEB_SHEAR_CAPACITY_METHOD_UNSPECIFIED: _concrete_pb2_1_1.WebShearCapacityMethod

class BucklingData(_message.Message):
    __slots__ = ["beta", "position", "support_condition"]
    BETA_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_CONDITION_FIELD_NUMBER: _ClassVar[int]
    beta: float
    position: BucklingSpan
    support_condition: SupportCondition
    def __init__(self, position: _Optional[_Union[BucklingSpan, _Mapping]] = ..., beta: _Optional[float] = ..., support_condition: _Optional[_Union[SupportCondition, str]] = ...) -> None: ...

class BucklingSpan(_message.Message):
    __slots__ = ["end", "start"]
    END_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    end: float
    start: float
    def __init__(self, start: _Optional[float] = ..., end: _Optional[float] = ...) -> None: ...

class ConcreteElement(_message.Message):
    __slots__ = ["distances", "fb_stiff", "fb_weak", "links", "rebars", "strands", "topping", "type"]
    class Topping(_message.Message):
        __slots__ = ["links", "mtrl_guid", "rebars", "segments", "strands"]
        class Segment(_message.Message):
            __slots__ = ["active", "layer", "length"]
            ACTIVE_FIELD_NUMBER: _ClassVar[int]
            LAYER_FIELD_NUMBER: _ClassVar[int]
            LENGTH_FIELD_NUMBER: _ClassVar[int]
            active: bool
            layer: Layer
            length: float
            def __init__(self, length: _Optional[float] = ..., layer: _Optional[_Union[Layer, _Mapping]] = ..., active: bool = ...) -> None: ...
        LINKS_FIELD_NUMBER: _ClassVar[int]
        MTRL_GUID_FIELD_NUMBER: _ClassVar[int]
        REBARS_FIELD_NUMBER: _ClassVar[int]
        SEGMENTS_FIELD_NUMBER: _ClassVar[int]
        STRANDS_FIELD_NUMBER: _ClassVar[int]
        links: _link_pb2.Data
        mtrl_guid: str
        rebars: _rebar_pb2_1.Data
        segments: _containers.RepeatedCompositeFieldContainer[ConcreteElement.Topping.Segment]
        strands: _strand_pb2.Data
        def __init__(self, segments: _Optional[_Iterable[_Union[ConcreteElement.Topping.Segment, _Mapping]]] = ..., mtrl_guid: _Optional[str] = ..., rebars: _Optional[_Union[_rebar_pb2_1.Data, _Mapping]] = ..., strands: _Optional[_Union[_strand_pb2.Data, _Mapping]] = ..., links: _Optional[_Union[_link_pb2.Data, _Mapping]] = ...) -> None: ...
    DISTANCES_FIELD_NUMBER: _ClassVar[int]
    FB_STIFF_FIELD_NUMBER: _ClassVar[int]
    FB_WEAK_FIELD_NUMBER: _ClassVar[int]
    LINKS_FIELD_NUMBER: _ClassVar[int]
    REBARS_FIELD_NUMBER: _ClassVar[int]
    STRANDS_FIELD_NUMBER: _ClassVar[int]
    TOPPING_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    distances: _containers.RepeatedCompositeFieldContainer[_concrete_pb2_1_1.CoverAndSpace]
    fb_stiff: FlexBuckling
    fb_weak: FlexBuckling
    links: _link_pb2.Data
    rebars: _rebar_pb2_1.Data
    strands: _strand_pb2.Data
    topping: ConcreteElement.Topping
    type: ConcreteBeamType
    def __init__(self, type: _Optional[_Union[ConcreteBeamType, str]] = ..., rebars: _Optional[_Union[_rebar_pb2_1.Data, _Mapping]] = ..., strands: _Optional[_Union[_strand_pb2.Data, _Mapping]] = ..., links: _Optional[_Union[_link_pb2.Data, _Mapping]] = ..., topping: _Optional[_Union[ConcreteElement.Topping, _Mapping]] = ..., fb_weak: _Optional[_Union[FlexBuckling, _Mapping]] = ..., fb_stiff: _Optional[_Union[FlexBuckling, _Mapping]] = ..., distances: _Optional[_Iterable[_Union[_concrete_pb2_1_1.CoverAndSpace, _Mapping]]] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["action_type", "active_borehole_guid", "concrete", "end_node_guid", "initial_bow_coef", "mtrl_guid", "n", "segments", "start_node_guid", "steel", "timber"]
    ACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_BOREHOLE_GUID_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_FIELD_NUMBER: _ClassVar[int]
    END_NODE_GUID_FIELD_NUMBER: _ClassVar[int]
    INITIAL_BOW_COEF_FIELD_NUMBER: _ClassVar[int]
    MTRL_GUID_FIELD_NUMBER: _ClassVar[int]
    N_FIELD_NUMBER: _ClassVar[int]
    SEGMENTS_FIELD_NUMBER: _ClassVar[int]
    START_NODE_GUID_FIELD_NUMBER: _ClassVar[int]
    STEEL_FIELD_NUMBER: _ClassVar[int]
    TIMBER_FIELD_NUMBER: _ClassVar[int]
    action_type: ActionType
    active_borehole_guid: str
    concrete: ConcreteElement
    end_node_guid: str
    initial_bow_coef: float
    mtrl_guid: str
    n: _geometry_pb2_1_1_1_1_1.Vector2D
    segments: _containers.RepeatedCompositeFieldContainer[Segment]
    start_node_guid: str
    steel: SteelElement
    timber: TimberElement
    def __init__(self, start_node_guid: _Optional[str] = ..., end_node_guid: _Optional[str] = ..., segments: _Optional[_Iterable[_Union[Segment, _Mapping]]] = ..., action_type: _Optional[_Union[ActionType, str]] = ..., n: _Optional[_Union[_geometry_pb2_1_1_1_1_1.Vector2D, _Mapping]] = ..., initial_bow_coef: _Optional[float] = ..., mtrl_guid: _Optional[str] = ..., concrete: _Optional[_Union[ConcreteElement, _Mapping]] = ..., steel: _Optional[_Union[SteelElement, _Mapping]] = ..., timber: _Optional[_Union[TimberElement, _Mapping]] = ..., active_borehole_guid: _Optional[str] = ...) -> None: ...

class FlexBuckling(_message.Message):
    __slots__ = ["betas", "data", "sway", "type"]
    BETAS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    SWAY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    betas: _containers.RepeatedScalarFieldContainer[float]
    data: _containers.RepeatedCompositeFieldContainer[BucklingData]
    sway: bool
    type: BucklingType
    def __init__(self, type: _Optional[_Union[BucklingType, str]] = ..., sway: bool = ..., betas: _Optional[_Iterable[float]] = ..., data: _Optional[_Iterable[_Union[BucklingData, _Mapping]]] = ...) -> None: ...

class LTBuckling(_message.Message):
    __slots__ = ["betas", "continously_restrained", "data", "type"]
    BETAS_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSLY_RESTRAINED_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    betas: _containers.RepeatedScalarFieldContainer[float]
    continously_restrained: bool
    data: _containers.RepeatedCompositeFieldContainer[BucklingData]
    type: BucklingType
    def __init__(self, type: _Optional[_Union[BucklingType, str]] = ..., continously_restrained: bool = ..., betas: _Optional[_Iterable[float]] = ..., data: _Optional[_Iterable[_Union[BucklingData, _Mapping]]] = ...) -> None: ...

class LTSBuckling(_message.Message):
    __slots__ = ["continously_restrained", "data", "support_conditions"]
    CONTINOUSLY_RESTRAINED_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    continously_restrained: bool
    data: _containers.RepeatedCompositeFieldContainer[BucklingData]
    support_conditions: _containers.RepeatedScalarFieldContainer[SupportCondition]
    def __init__(self, continously_restrained: bool = ..., support_conditions: _Optional[_Iterable[_Union[SupportCondition, str]]] = ..., data: _Optional[_Iterable[_Union[BucklingData, _Mapping]]] = ...) -> None: ...

class Layer(_message.Message):
    __slots__ = ["end", "start"]
    END_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    end: SecInPlane
    start: SecInPlane
    def __init__(self, start: _Optional[_Union[SecInPlane, _Mapping]] = ..., end: _Optional[_Union[SecInPlane, _Mapping]] = ...) -> None: ...

class MultiLayer(_message.Message):
    __slots__ = ["end", "mtrl_guid", "start"]
    END_FIELD_NUMBER: _ClassVar[int]
    MTRL_GUID_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    end: SecInPlane
    mtrl_guid: str
    start: SecInPlane
    def __init__(self, start: _Optional[_Union[SecInPlane, _Mapping]] = ..., end: _Optional[_Union[SecInPlane, _Mapping]] = ..., mtrl_guid: _Optional[str] = ...) -> None: ...

class MultiLayerSegment(_message.Message):
    __slots__ = ["id", "layer", "length"]
    ID_FIELD_NUMBER: _ClassVar[int]
    LAYER_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2_1_1_1_1_1_1.ID
    layer: _containers.RepeatedCompositeFieldContainer[MultiLayer]
    length: float
    def __init__(self, length: _Optional[float] = ..., layer: _Optional[_Iterable[_Union[MultiLayer, _Mapping]]] = ..., id: _Optional[_Union[_utils_pb2_1_1_1_1_1_1.ID, _Mapping]] = ...) -> None: ...

class SecInPlane(_message.Message):
    __slots__ = ["local_dx", "local_dy", "sec_guid"]
    LOCAL_DX_FIELD_NUMBER: _ClassVar[int]
    LOCAL_DY_FIELD_NUMBER: _ClassVar[int]
    SEC_GUID_FIELD_NUMBER: _ClassVar[int]
    local_dx: float
    local_dy: float
    sec_guid: str
    def __init__(self, sec_guid: _Optional[str] = ..., local_dx: _Optional[float] = ..., local_dy: _Optional[float] = ...) -> None: ...

class Segment(_message.Message):
    __slots__ = ["id", "layer", "length"]
    ID_FIELD_NUMBER: _ClassVar[int]
    LAYER_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2_1_1_1_1_1_1.ID
    layer: Layer
    length: float
    def __init__(self, length: _Optional[float] = ..., layer: _Optional[_Union[Layer, _Mapping]] = ..., id: _Optional[_Union[_utils_pb2_1_1_1_1_1_1.ID, _Mapping]] = ...) -> None: ...

class SteelElement(_message.Message):
    __slots__ = ["fb_stiff", "fb_weak", "load_position", "ltb_btm", "ltb_top", "stiffeners"]
    FB_STIFF_FIELD_NUMBER: _ClassVar[int]
    FB_WEAK_FIELD_NUMBER: _ClassVar[int]
    LOAD_POSITION_FIELD_NUMBER: _ClassVar[int]
    LTB_BTM_FIELD_NUMBER: _ClassVar[int]
    LTB_TOP_FIELD_NUMBER: _ClassVar[int]
    STIFFENERS_FIELD_NUMBER: _ClassVar[int]
    fb_stiff: FlexBuckling
    fb_weak: FlexBuckling
    load_position: Alignment
    ltb_btm: LTBuckling
    ltb_top: LTBuckling
    stiffeners: _containers.RepeatedCompositeFieldContainer[Stiffener]
    def __init__(self, stiffeners: _Optional[_Iterable[_Union[Stiffener, _Mapping]]] = ..., fb_weak: _Optional[_Union[FlexBuckling, _Mapping]] = ..., fb_stiff: _Optional[_Union[FlexBuckling, _Mapping]] = ..., ltb_top: _Optional[_Union[LTBuckling, _Mapping]] = ..., ltb_btm: _Optional[_Union[LTBuckling, _Mapping]] = ..., load_position: _Optional[_Union[Alignment, str]] = ...) -> None: ...

class Stiffener(_message.Message):
    __slots__ = ["lft", "pos", "rgt", "t"]
    LFT_FIELD_NUMBER: _ClassVar[int]
    POS_FIELD_NUMBER: _ClassVar[int]
    RGT_FIELD_NUMBER: _ClassVar[int]
    T_FIELD_NUMBER: _ClassVar[int]
    lft: bool
    pos: float
    rgt: bool
    t: float
    def __init__(self, pos: _Optional[float] = ..., lft: bool = ..., rgt: bool = ..., t: _Optional[float] = ...) -> None: ...

class TimberElement(_message.Message):
    __slots__ = ["fb_stiff", "fb_weak", "load_position", "ltsb"]
    FB_STIFF_FIELD_NUMBER: _ClassVar[int]
    FB_WEAK_FIELD_NUMBER: _ClassVar[int]
    LOAD_POSITION_FIELD_NUMBER: _ClassVar[int]
    LTSB_FIELD_NUMBER: _ClassVar[int]
    fb_stiff: FlexBuckling
    fb_weak: FlexBuckling
    load_position: Alignment
    ltsb: LTSBuckling
    def __init__(self, fb_weak: _Optional[_Union[FlexBuckling, _Mapping]] = ..., fb_stiff: _Optional[_Union[FlexBuckling, _Mapping]] = ..., ltsb: _Optional[_Union[LTSBuckling, _Mapping]] = ..., load_position: _Optional[_Union[Alignment, str]] = ...) -> None: ...

class ConcreteBeamType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class BucklingType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ActionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Alignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class SupportCondition(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
