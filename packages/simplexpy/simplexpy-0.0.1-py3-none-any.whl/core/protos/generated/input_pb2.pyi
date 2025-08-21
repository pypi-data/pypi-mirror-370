from Utils import utils_pb2 as _utils_pb2
import structure_pb2 as _structure_pb2
from Utils import utils_pb2 as _utils_pb2_1
import element_pb2 as _element_pb2
import support_pb2 as _support_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Loading import loading_pb2 as _loading_pb2
from Design import design_pb2 as _design_pb2
from Utils import eurocode_pb2 as _eurocode_pb2
import sections_pb2 as _sections_pb2
from Utils import utils_pb2 as _utils_pb2_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1
from Material import material_pb2 as _material_pb2
from Material import concrete_pb2 as _concrete_pb2
from Material import steel_pb2 as _steel_pb2
from Material import timber_pb2 as _timber_pb2
from Material import soil_pb2 as _soil_pb2
from Material import reinforcement_pb2 as _reinforcement_pb2
from FireProtection import steel_pb2 as _steel_pb2_1
from FireProtection import timber_pb2 as _timber_pb2_1
from Material import masonry_pb2 as _masonry_pb2
from Material import custom_pb2 as _custom_pb2
from FireProtection import steel_pb2 as _steel_pb2_1_1
from Utils import utils_pb2 as _utils_pb2_1_1_1
from FireProtection import timber_pb2 as _timber_pb2_1_1
from Utils import utils_pb2 as _utils_pb2_1_1_1_1
from Soilmodel import soil_model_pb2 as _soil_model_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1
from Geometry import geometry_pb2 as _geometry_pb2_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
from structure_pb2 import Data
from structure_pb2 import ConsequenceClass
from structure_pb2 import ReliabilityClass
from Utils.eurocode_pb2 import DesignConfiguration
from Utils.eurocode_pb2 import Annex
from Utils.eurocode_pb2 import SnowZone
from Utils.eurocode_pb2 import Generation
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
from Material.material_pb2 import Data
from Material.material_pb2 import Mtrl
from FireProtection.steel_pb2 import CharacteristicData
from FireProtection.steel_pb2 import Data
from FireProtection.steel_pb2 import Encasement
from FireProtection.timber_pb2 import CharacteristicData
from FireProtection.timber_pb2 import Data
from FireProtection.timber_pb2 import MaterialType
from Soilmodel.soil_model_pb2 import Soil
from Soilmodel.soil_model_pb2 import Borehole
from Soilmodel.soil_model_pb2 import GroundWater
from Soilmodel.soil_model_pb2 import SoilStratum
from Soilmodel.soil_model_pb2 import AllowedSoilPressure
from Soilmodel.soil_model_pb2 import Data
ANNEX_BELGIUM: _eurocode_pb2.Annex
ANNEX_COMMON: _eurocode_pb2.Annex
ANNEX_DENMARK: _eurocode_pb2.Annex
ANNEX_ESTONIA: _eurocode_pb2.Annex
ANNEX_FINLAND: _eurocode_pb2.Annex
ANNEX_GERMANY: _eurocode_pb2.Annex
ANNEX_GREAT_BRITAIN: _eurocode_pb2.Annex
ANNEX_HUNGARY: _eurocode_pb2.Annex
ANNEX_LATVIA: _eurocode_pb2.Annex
ANNEX_NETHERLAND: _eurocode_pb2.Annex
ANNEX_NORWAY: _eurocode_pb2.Annex
ANNEX_POLAND: _eurocode_pb2.Annex
ANNEX_ROMANIA: _eurocode_pb2.Annex
ANNEX_SPAIN: _eurocode_pb2.Annex
ANNEX_SWEDEN: _eurocode_pb2.Annex
ANNEX_TURKEY: _eurocode_pb2.Annex
ANNEX_UNSPECIFIED: _eurocode_pb2.Annex
CONSEQUENCE_CLASS_1: _structure_pb2.ConsequenceClass
CONSEQUENCE_CLASS_2: _structure_pb2.ConsequenceClass
CONSEQUENCE_CLASS_3: _structure_pb2.ConsequenceClass
CONSEQUENCE_CLASS_UNSPECIFIED: _structure_pb2.ConsequenceClass
DESCRIPTOR: _descriptor.FileDescriptor
ENCASEMENT_CONTOUR: _steel_pb2_1_1.Encasement
ENCASEMENT_HOLLOW: _steel_pb2_1_1.Encasement
ENCASEMENT_UNSPECIFIED: _steel_pb2_1_1.Encasement
GENERATION_1: _eurocode_pb2.Generation
GENERATION_2: _eurocode_pb2.Generation
GENERATION_UNSPECIFIED: _eurocode_pb2.Generation
MATERIAL_CATEGORY_CONCRETE: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_STEEL: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_TIMBER: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_UNSPECIFIED: _sections_pb2.MaterialCategory
MATERIAL_TYPE_GYPSUM_BOARD_AH1_INTERNAL: _timber_pb2_1_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_AH1_OTHER: _timber_pb2_1_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_AH2_INTERNAL: _timber_pb2_1_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_AH2_OTHER: _timber_pb2_1_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F1_INTERNAL: _timber_pb2_1_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F1_OTHER: _timber_pb2_1_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F2_INTERNAL: _timber_pb2_1_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F2_OTHER: _timber_pb2_1_1.MaterialType
MATERIAL_TYPE_NONE: _timber_pb2_1_1.MaterialType
MATERIAL_TYPE_ROCK_FIBER: _timber_pb2_1_1.MaterialType
MATERIAL_TYPE_UNSPECIFIED: _timber_pb2_1_1.MaterialType
MATERIAL_TYPE_USER_DEFINED: _timber_pb2_1_1.MaterialType
MATERIAL_TYPE_WOOD: _timber_pb2_1_1.MaterialType
MTRL_CONCRETE: _material_pb2.Mtrl
MTRL_CUSTOM: _material_pb2.Mtrl
MTRL_FIRE_PROTECTION_STEEL: _material_pb2.Mtrl
MTRL_FIRE_PROTECTION_TIMBER: _material_pb2.Mtrl
MTRL_MASONRY: _material_pb2.Mtrl
MTRL_REINFORCEMENT: _material_pb2.Mtrl
MTRL_SOIL: _material_pb2.Mtrl
MTRL_STEEL: _material_pb2.Mtrl
MTRL_TIMBER: _material_pb2.Mtrl
MTRL_UNSPECIFIED: _material_pb2.Mtrl
OWNER_COMPANY: _utils_pb2_1_1_1_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1_1_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1_1_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1_1_1_1.Owner
OWNER_USER: _utils_pb2_1_1_1_1_1.Owner
RELIABILITY_CLASS_1: _structure_pb2.ReliabilityClass
RELIABILITY_CLASS_2: _structure_pb2.ReliabilityClass
RELIABILITY_CLASS_3: _structure_pb2.ReliabilityClass
RELIABILITY_CLASS_UNSPECIFIED: _structure_pb2.ReliabilityClass
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
SNOW_ZONE_1: _eurocode_pb2.SnowZone
SNOW_ZONE_2: _eurocode_pb2.SnowZone
SNOW_ZONE_3: _eurocode_pb2.SnowZone
SNOW_ZONE_UNSPECIFIED: _eurocode_pb2.SnowZone

class Data(_message.Message):
    __slots__ = ["consolidate", "description", "ec", "id", "mtrl_db", "sec_db", "soil_model", "structures"]
    CONSOLIDATE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EC_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MTRL_DB_FIELD_NUMBER: _ClassVar[int]
    SEC_DB_FIELD_NUMBER: _ClassVar[int]
    SOIL_MODEL_FIELD_NUMBER: _ClassVar[int]
    STRUCTURES_FIELD_NUMBER: _ClassVar[int]
    consolidate: bool
    description: str
    ec: _eurocode_pb2.DesignConfiguration
    id: _utils_pb2_1_1_1_1_1.ID
    mtrl_db: _containers.RepeatedCompositeFieldContainer[_material_pb2.Data]
    sec_db: _containers.RepeatedCompositeFieldContainer[_sections_pb2.Section]
    soil_model: _soil_model_pb2.Data
    structures: _containers.RepeatedCompositeFieldContainer[_structure_pb2.Data]
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1_1_1_1.ID, _Mapping]] = ..., description: _Optional[str] = ..., structures: _Optional[_Iterable[_Union[_structure_pb2.Data, _Mapping]]] = ..., mtrl_db: _Optional[_Iterable[_Union[_material_pb2.Data, _Mapping]]] = ..., sec_db: _Optional[_Iterable[_Union[_sections_pb2.Section, _Mapping]]] = ..., ec: _Optional[_Union[_eurocode_pb2.DesignConfiguration, _Mapping]] = ..., consolidate: bool = ..., soil_model: _Optional[_Union[_soil_model_pb2.Data, _Mapping]] = ...) -> None: ...
