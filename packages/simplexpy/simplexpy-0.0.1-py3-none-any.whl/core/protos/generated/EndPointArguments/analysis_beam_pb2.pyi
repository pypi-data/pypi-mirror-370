from Utils import log_pb2 as _log_pb2
import sections_pb2 as _sections_pb2
from Utils import utils_pb2 as _utils_pb2
from Geometry import geometry_pb2 as _geometry_pb2
import project_pb2 as _project_pb2
import input_pb2 as _input_pb2
import output_pb2 as _output_pb2
from Utils import log_pb2 as _log_pb2_1
from Geometry import beam_pb2 as _beam_pb2
from Utils import utils_pb2 as _utils_pb2_1
import stage_pb2 as _stage_pb2
from Geometry import geometry_pb2 as _geometry_pb2_1
from Geometry import foundation_pb2 as _foundation_pb2
from Design import design_pb2 as _design_pb2
from Geometry import rebar_pb2 as _rebar_pb2
from Geometry import strand_pb2 as _strand_pb2
from Geometry import link_pb2 as _link_pb2
from Design import concrete_pb2 as _concrete_pb2
from Geometry import rebar_pb2 as _rebar_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1_1
from Geometry import reinf_pb2 as _reinf_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.log_pb2 import LogValue
from Utils.log_pb2 import LogEntry
from Utils.log_pb2 import Log
from Utils.log_pb2 import LogType
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
from project_pb2 import Data
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
from Geometry.rebar_pb2 import Data
ACTION_TYPE_BAR: _beam_pb2.ActionType
ACTION_TYPE_BEAM: _beam_pb2.ActionType
ACTION_TYPE_COLUMN: _beam_pb2.ActionType
ACTION_TYPE_UNSPECIFIED: _beam_pb2.ActionType
ALIGNMENT_BOTTOM: _beam_pb2.Alignment
ALIGNMENT_CENTER: _beam_pb2.Alignment
ALIGNMENT_TOP: _beam_pb2.Alignment
ALIGNMENT_UNSPECIFIED: _beam_pb2.Alignment
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
DESCRIPTOR: _descriptor.FileDescriptor
LOG_TYPE_ERROR: _log_pb2_1.LogType
LOG_TYPE_INFORMATION: _log_pb2_1.LogType
LOG_TYPE_UNSPECIFIED: _log_pb2_1.LogType
LOG_TYPE_WARNING: _log_pb2_1.LogType
MATERIAL_CATEGORY_CONCRETE: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_STEEL: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_TIMBER: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_UNSPECIFIED: _sections_pb2.MaterialCategory
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
SUPPORT_CONDITION_CANTILEVER: _beam_pb2.SupportCondition
SUPPORT_CONDITION_SIMPLY: _beam_pb2.SupportCondition
SUPPORT_CONDITION_UNSPECIFIED: _beam_pb2.SupportCondition

class AnalysisInput(_message.Message):
    __slots__ = ["lcomb_guids", "project"]
    LCOMB_GUIDS_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    lcomb_guids: _containers.RepeatedScalarFieldContainer[str]
    project: _project_pb2.Data
    def __init__(self, project: _Optional[_Union[_project_pb2.Data, _Mapping]] = ..., lcomb_guids: _Optional[_Iterable[str]] = ...) -> None: ...

class AnalysisOutput(_message.Message):
    __slots__ = ["log", "project"]
    LOG_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    log: _log_pb2_1.Log
    project: _project_pb2.Data
    def __init__(self, project: _Optional[_Union[_project_pb2.Data, _Mapping]] = ..., log: _Optional[_Union[_log_pb2_1.Log, _Mapping]] = ...) -> None: ...

class SelfWeightInput(_message.Message):
    __slots__ = ["grav", "reinfs", "rho1", "rho2", "sections", "segments"]
    GRAV_FIELD_NUMBER: _ClassVar[int]
    REINFS_FIELD_NUMBER: _ClassVar[int]
    RHO1_FIELD_NUMBER: _ClassVar[int]
    RHO2_FIELD_NUMBER: _ClassVar[int]
    SECTIONS_FIELD_NUMBER: _ClassVar[int]
    SEGMENTS_FIELD_NUMBER: _ClassVar[int]
    grav: float
    reinfs: _rebar_pb2_1.Data
    rho1: float
    rho2: float
    sections: _containers.RepeatedCompositeFieldContainer[_sections_pb2.Section]
    segments: _containers.RepeatedCompositeFieldContainer[_beam_pb2.Segment]
    def __init__(self, sections: _Optional[_Iterable[_Union[_sections_pb2.Section, _Mapping]]] = ..., segments: _Optional[_Iterable[_Union[_beam_pb2.Segment, _Mapping]]] = ..., rho1: _Optional[float] = ..., rho2: _Optional[float] = ..., grav: _Optional[float] = ..., reinfs: _Optional[_Union[_rebar_pb2_1.Data, _Mapping]] = ...) -> None: ...

class SelfWeightOutput(_message.Message):
    __slots__ = ["loads", "log", "pos", "weight"]
    LOADS_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    POS_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    loads: _containers.RepeatedScalarFieldContainer[float]
    log: _log_pb2_1.Log
    pos: _containers.RepeatedScalarFieldContainer[float]
    weight: float
    def __init__(self, loads: _Optional[_Iterable[float]] = ..., pos: _Optional[_Iterable[float]] = ..., weight: _Optional[float] = ..., log: _Optional[_Union[_log_pb2_1.Log, _Mapping]] = ...) -> None: ...
