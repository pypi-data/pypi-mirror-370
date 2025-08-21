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
from Result import foundation_pb2 as _foundation_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1_1
import element_pb2 as _element_pb2_1
import sections_pb2 as _sections_pb2_1
from Loading import load_pb2 as _load_pb2
from Loading import loadcase_pb2 as _loadcase_pb2
from Geometry import geometry_pb2 as _geometry_pb2_1_1
from Result import concrete_pb2 as _concrete_pb2
from Result import control_pb2 as _control_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
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
from Result.foundation_pb2 import ConcreteInput
from Result.foundation_pb2 import EffectiveGeometry
from Result.foundation_pb2 import Stress
from Result.foundation_pb2 import FoundationForce
from Result.foundation_pb2 import SoilWaterLoads
from Result.foundation_pb2 import DetailedFoundationAnalysis
from Result.foundation_pb2 import BearingRes
from Result.foundation_pb2 import BearingResFormula
from Result.foundation_pb2 import DesignStrength
from Result.foundation_pb2 import SlidingRes
from Result.foundation_pb2 import SlidingResFormula
from Result.foundation_pb2 import DetailedFoundationDesign
from Result.foundation_pb2 import RCPunchingCheckConcreteCompression
from Result.foundation_pb2 import RCPunchingCheckConcreteShear
from Result.foundation_pb2 import RCUnreinforced
from Result.foundation_pb2 import Data
from Result.foundation_pb2 import Element
from Result.foundation_pb2 import DesignSummary
ANALYSIS_TYPE_NORMAL: AnalysisType
ANALYSIS_TYPE_SOIL_PUNCHING: AnalysisType
ANALYSIS_TYPE_UNSPECIFIED: AnalysisType
CONTROL_TYPE_COMPRESSION: ControlType
CONTROL_TYPE_OVERALL: ControlType
CONTROL_TYPE_TENSION: ControlType
CONTROL_TYPE_UNSPECIFIED: ControlType
DESCRIPTOR: _descriptor.FileDescriptor
DESIGN_TYPE_DRAINED: DesignType
DESIGN_TYPE_ROCK: DesignType
DESIGN_TYPE_UNDRAINED: DesignType
DESIGN_TYPE_UNSPECIFIED: DesignType
INSPECTION_LEVEL_NORMAL: _element_pb2_1.InspectionLevel
INSPECTION_LEVEL_RELAXED: _element_pb2_1.InspectionLevel
INSPECTION_LEVEL_TIGHTENED: _element_pb2_1.InspectionLevel
INSPECTION_LEVEL_UNSPECIFIED: _element_pb2_1.InspectionLevel
MATERIAL_CATEGORY_CONCRETE: _sections_pb2_1.MaterialCategory
MATERIAL_CATEGORY_STEEL: _sections_pb2_1.MaterialCategory
MATERIAL_CATEGORY_TIMBER: _sections_pb2_1.MaterialCategory
MATERIAL_CATEGORY_UNSPECIFIED: _sections_pb2_1.MaterialCategory
OWNER_COMPANY: _utils_pb2_1_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1_1.Owner
OWNER_USER: _utils_pb2_1_1_1.Owner
SECTION_SIDE_LEFT: _sections_pb2_1.SectionSide
SECTION_SIDE_RIGHT: _sections_pb2_1.SectionSide
SECTION_SIDE_UNSPECIFIED: _sections_pb2_1.SectionSide
SECTION_TYPE_ASB: _sections_pb2_1.SectionType
SECTION_TYPE_C: _sections_pb2_1.SectionType
SECTION_TYPE_CHS: _sections_pb2_1.SectionType
SECTION_TYPE_CO: _sections_pb2_1.SectionType
SECTION_TYPE_CUSTOM: _sections_pb2_1.SectionType
SECTION_TYPE_DESSED_LUMBER: _sections_pb2_1.SectionType
SECTION_TYPE_EA: _sections_pb2_1.SectionType
SECTION_TYPE_F: _sections_pb2_1.SectionType
SECTION_TYPE_GLULAM: _sections_pb2_1.SectionType
SECTION_TYPE_HDX: _sections_pb2_1.SectionType
SECTION_TYPE_HEA: _sections_pb2_1.SectionType
SECTION_TYPE_HEB: _sections_pb2_1.SectionType
SECTION_TYPE_HEM: _sections_pb2_1.SectionType
SECTION_TYPE_HSQ: _sections_pb2_1.SectionType
SECTION_TYPE_I: _sections_pb2_1.SectionType
SECTION_TYPE_IPE: _sections_pb2_1.SectionType
SECTION_TYPE_IV: _sections_pb2_1.SectionType
SECTION_TYPE_KB: _sections_pb2_1.SectionType
SECTION_TYPE_KBE: _sections_pb2_1.SectionType
SECTION_TYPE_KCKR: _sections_pb2_1.SectionType
SECTION_TYPE_KERTO: _sections_pb2_1.SectionType
SECTION_TYPE_KKR: _sections_pb2_1.SectionType
SECTION_TYPE_L: _sections_pb2_1.SectionType
SECTION_TYPE_LE: _sections_pb2_1.SectionType
SECTION_TYPE_LU: _sections_pb2_1.SectionType
SECTION_TYPE_PFC: _sections_pb2_1.SectionType
SECTION_TYPE_PLATE: _sections_pb2_1.SectionType
SECTION_TYPE_R: _sections_pb2_1.SectionType
SECTION_TYPE_RHS: _sections_pb2_1.SectionType
SECTION_TYPE_SAWN_LUMBER: _sections_pb2_1.SectionType
SECTION_TYPE_T: _sections_pb2_1.SectionType
SECTION_TYPE_TOPPING: _sections_pb2_1.SectionType
SECTION_TYPE_TPS: _sections_pb2_1.SectionType
SECTION_TYPE_U: _sections_pb2_1.SectionType
SECTION_TYPE_UA: _sections_pb2_1.SectionType
SECTION_TYPE_UAP: _sections_pb2_1.SectionType
SECTION_TYPE_UB: _sections_pb2_1.SectionType
SECTION_TYPE_UBP: _sections_pb2_1.SectionType
SECTION_TYPE_UC: _sections_pb2_1.SectionType
SECTION_TYPE_UKB: _sections_pb2_1.SectionType
SECTION_TYPE_UKC: _sections_pb2_1.SectionType
SECTION_TYPE_UNSPECIFIED: _sections_pb2_1.SectionType
SECTION_TYPE_UPE_DIN: _sections_pb2_1.SectionType
SECTION_TYPE_UPE_NEN: _sections_pb2_1.SectionType
SECTION_TYPE_UPE_SWE: _sections_pb2_1.SectionType
SECTION_TYPE_UX: _sections_pb2_1.SectionType
SECTION_TYPE_VCKR: _sections_pb2_1.SectionType
SECTION_TYPE_VKR: _sections_pb2_1.SectionType
SECTION_TYPE_VR: _sections_pb2_1.SectionType
SECTION_TYPE_VT: _sections_pb2_1.SectionType
SECTION_TYPE_Z: _sections_pb2_1.SectionType
SECTION_TYPE_ZX: _sections_pb2_1.SectionType

class ControlCapacities(_message.Message):
    __slots__ = ["data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: ControlData
    def __init__(self, data: _Optional[_Union[ControlData, _Mapping]] = ...) -> None: ...

class ControlData(_message.Message):
    __slots__ = ["local_coordsys", "type", "value"]
    LOCAL_COORDSYS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    local_coordsys: bool
    type: _containers.RepeatedScalarFieldContainer[ControlType]
    value: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, local_coordsys: bool = ..., type: _Optional[_Iterable[_Union[ControlType, str]]] = ..., value: _Optional[_Iterable[float]] = ...) -> None: ...

class ControlDistribution(_message.Message):
    __slots__ = ["capacities", "utilizations"]
    CAPACITIES_FIELD_NUMBER: _ClassVar[int]
    UTILIZATIONS_FIELD_NUMBER: _ClassVar[int]
    capacities: ControlCapacities
    utilizations: ControlUtilization
    def __init__(self, capacities: _Optional[_Union[ControlCapacities, _Mapping]] = ..., utilizations: _Optional[_Union[ControlUtilization, _Mapping]] = ...) -> None: ...

class ControlUtilization(_message.Message):
    __slots__ = ["forces"]
    FORCES_FIELD_NUMBER: _ClassVar[int]
    forces: ControlData
    def __init__(self, forces: _Optional[_Union[ControlData, _Mapping]] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["result_analysis", "result_design", "utilization"]
    RESULT_ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    RESULT_DESIGN_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    result_analysis: _containers.RepeatedCompositeFieldContainer[DetailedPileAnalysis]
    result_design: _containers.RepeatedCompositeFieldContainer[DetailedPileDesign]
    utilization: float
    def __init__(self, result_analysis: _Optional[_Iterable[_Union[DetailedPileAnalysis, _Mapping]]] = ..., result_design: _Optional[_Iterable[_Union[DetailedPileDesign, _Mapping]]] = ..., utilization: _Optional[float] = ...) -> None: ...

class DesignStrength(_message.Message):
    __slots__ = ["cuk", "nc", "nq", "phid", "phik", "rk"]
    CUK_FIELD_NUMBER: _ClassVar[int]
    NC_FIELD_NUMBER: _ClassVar[int]
    NQ_FIELD_NUMBER: _ClassVar[int]
    PHID_FIELD_NUMBER: _ClassVar[int]
    PHIK_FIELD_NUMBER: _ClassVar[int]
    RK_FIELD_NUMBER: _ClassVar[int]
    cuk: float
    nc: float
    nq: float
    phid: float
    phik: float
    rk: float
    def __init__(self, cuk: _Optional[float] = ..., phik: _Optional[float] = ..., phid: _Optional[float] = ..., nc: _Optional[float] = ..., nq: _Optional[float] = ..., rk: _Optional[float] = ...) -> None: ...

class DesignSummary(_message.Message):
    __slots__ = ["elem_guid"]
    ELEM_GUID_FIELD_NUMBER: _ClassVar[int]
    elem_guid: str
    def __init__(self, elem_guid: _Optional[str] = ...) -> None: ...

class DetailedPileAnalysis(_message.Message):
    __slots__ = ["analysis_type", "foundation_force", "id", "load", "selfweight", "selfweight_effective", "settlement"]
    ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    FOUNDATION_FORCE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LOAD_FIELD_NUMBER: _ClassVar[int]
    SELFWEIGHT_EFFECTIVE_FIELD_NUMBER: _ClassVar[int]
    SELFWEIGHT_FIELD_NUMBER: _ClassVar[int]
    SETTLEMENT_FIELD_NUMBER: _ClassVar[int]
    analysis_type: AnalysisType
    foundation_force: _foundation_pb2_1.FoundationForce
    id: _utils_pb2_1_1_1.ID
    load: _foundation_pb2_1.FoundationForce
    selfweight: _foundation_pb2_1.FoundationForce
    selfweight_effective: _foundation_pb2_1.FoundationForce
    settlement: float
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1_1.ID, _Mapping]] = ..., analysis_type: _Optional[_Union[AnalysisType, str]] = ..., load: _Optional[_Union[_foundation_pb2_1.FoundationForce, _Mapping]] = ..., selfweight: _Optional[_Union[_foundation_pb2_1.FoundationForce, _Mapping]] = ..., selfweight_effective: _Optional[_Union[_foundation_pb2_1.FoundationForce, _Mapping]] = ..., foundation_force: _Optional[_Union[_foundation_pb2_1.FoundationForce, _Mapping]] = ..., settlement: _Optional[float] = ...) -> None: ...

class DetailedPileDesign(_message.Message):
    __slots__ = ["analysis_type", "bearing_result", "controls", "design_strength", "design_type", "id"]
    ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    BEARING_RESULT_FIELD_NUMBER: _ClassVar[int]
    CONTROLS_FIELD_NUMBER: _ClassVar[int]
    DESIGN_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    DESIGN_TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    analysis_type: AnalysisType
    bearing_result: PileRes
    controls: ControlDistribution
    design_strength: DesignStrength
    design_type: DesignType
    id: _utils_pb2_1_1_1.ID
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1_1.ID, _Mapping]] = ..., analysis_type: _Optional[_Union[AnalysisType, str]] = ..., design_type: _Optional[_Union[DesignType, str]] = ..., bearing_result: _Optional[_Union[PileRes, _Mapping]] = ..., design_strength: _Optional[_Union[DesignStrength, _Mapping]] = ..., controls: _Optional[_Union[ControlDistribution, _Mapping]] = ...) -> None: ...

class Element(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

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

class PileRes(_message.Message):
    __slots__ = ["caracteristic_pile_result", "design_pile_result", "qs_neg_load", "qs_neg_load_layer", "utilization"]
    CARACTERISTIC_PILE_RESULT_FIELD_NUMBER: _ClassVar[int]
    DESIGN_PILE_RESULT_FIELD_NUMBER: _ClassVar[int]
    QS_NEG_LOAD_FIELD_NUMBER: _ClassVar[int]
    QS_NEG_LOAD_LAYER_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    caracteristic_pile_result: PileResDetailed
    design_pile_result: PileResDetailed
    qs_neg_load: float
    qs_neg_load_layer: _containers.RepeatedScalarFieldContainer[float]
    utilization: float
    def __init__(self, caracteristic_pile_result: _Optional[_Union[PileResDetailed, _Mapping]] = ..., design_pile_result: _Optional[_Union[PileResDetailed, _Mapping]] = ..., utilization: _Optional[float] = ..., qs_neg_load: _Optional[float] = ..., qs_neg_load_layer: _Optional[_Iterable[float]] = ...) -> None: ...

class PileResDetailed(_message.Message):
    __slots__ = ["neg_load", "neg_load_layer", "qb", "qc", "qsc", "qsc_layer", "qst", "qst_layer", "qt"]
    NEG_LOAD_FIELD_NUMBER: _ClassVar[int]
    NEG_LOAD_LAYER_FIELD_NUMBER: _ClassVar[int]
    QB_FIELD_NUMBER: _ClassVar[int]
    QC_FIELD_NUMBER: _ClassVar[int]
    QSC_FIELD_NUMBER: _ClassVar[int]
    QSC_LAYER_FIELD_NUMBER: _ClassVar[int]
    QST_FIELD_NUMBER: _ClassVar[int]
    QST_LAYER_FIELD_NUMBER: _ClassVar[int]
    QT_FIELD_NUMBER: _ClassVar[int]
    neg_load: float
    neg_load_layer: _containers.RepeatedScalarFieldContainer[float]
    qb: float
    qc: float
    qsc: float
    qsc_layer: _containers.RepeatedScalarFieldContainer[float]
    qst: float
    qst_layer: _containers.RepeatedScalarFieldContainer[float]
    qt: float
    def __init__(self, qc: _Optional[float] = ..., qt: _Optional[float] = ..., qb: _Optional[float] = ..., qsc: _Optional[float] = ..., qst: _Optional[float] = ..., neg_load: _Optional[float] = ..., qsc_layer: _Optional[_Iterable[float]] = ..., qst_layer: _Optional[_Iterable[float]] = ..., neg_load_layer: _Optional[_Iterable[float]] = ...) -> None: ...

class ControlType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class AnalysisType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DesignType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
