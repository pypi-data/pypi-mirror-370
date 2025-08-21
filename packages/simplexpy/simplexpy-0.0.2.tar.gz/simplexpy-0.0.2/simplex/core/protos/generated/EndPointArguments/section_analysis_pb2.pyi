from Utils import log_pb2 as _log_pb2
import sections_pb2 as _sections_pb2
from Utils import utils_pb2 as _utils_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

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
DESCRIPTOR: _descriptor.FileDescriptor
LOG_TYPE_ERROR: _log_pb2.LogType
LOG_TYPE_INFORMATION: _log_pb2.LogType
LOG_TYPE_UNSPECIFIED: _log_pb2.LogType
LOG_TYPE_WARNING: _log_pb2.LogType
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

class SectionAnalysis(_message.Message):
    __slots__ = ["log", "parts"]
    class SectionPart(_message.Message):
        __slots__ = ["part"]
        PART_FIELD_NUMBER: _ClassVar[int]
        part: _sections_pb2.Section
        def __init__(self, part: _Optional[_Union[_sections_pb2.Section, _Mapping]] = ...) -> None: ...
    LOG_FIELD_NUMBER: _ClassVar[int]
    PARTS_FIELD_NUMBER: _ClassVar[int]
    log: _log_pb2.Log
    parts: SectionAnalysis.SectionPart
    def __init__(self, parts: _Optional[_Union[SectionAnalysis.SectionPart, _Mapping]] = ..., log: _Optional[_Union[_log_pb2.Log, _Mapping]] = ...) -> None: ...
