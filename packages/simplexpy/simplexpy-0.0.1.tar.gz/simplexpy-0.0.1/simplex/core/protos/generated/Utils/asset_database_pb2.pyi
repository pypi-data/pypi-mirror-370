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
from Utils import eurocode_pb2 as _eurocode_pb2
from Utils import utils_pb2 as _utils_pb2
import sections_pb2 as _sections_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Geometry import geometry_pb2 as _geometry_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Material.material_pb2 import Data
from Material.material_pb2 import Mtrl
from Utils.eurocode_pb2 import DesignConfiguration
from Utils.eurocode_pb2 import Annex
from Utils.eurocode_pb2 import SnowZone
from Utils.eurocode_pb2 import Generation
from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
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
DESCRIPTOR: _descriptor.FileDescriptor
GENERATION_1: _eurocode_pb2.Generation
GENERATION_2: _eurocode_pb2.Generation
GENERATION_UNSPECIFIED: _eurocode_pb2.Generation
MATERIAL_CATEGORY_CONCRETE: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_STEEL: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_TIMBER: _sections_pb2.MaterialCategory
MATERIAL_CATEGORY_UNSPECIFIED: _sections_pb2.MaterialCategory
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
OWNER_COMPANY: _utils_pb2_1.Owner
OWNER_OFFICE: _utils_pb2_1.Owner
OWNER_STRUSOFT: _utils_pb2_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1.Owner
OWNER_USER: _utils_pb2_1.Owner
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

class Database(_message.Message):
    __slots__ = ["material_list", "section_list"]
    MATERIAL_LIST_FIELD_NUMBER: _ClassVar[int]
    SECTION_LIST_FIELD_NUMBER: _ClassVar[int]
    material_list: MaterialDbRecordList
    section_list: SectionDbRecordList
    def __init__(self, material_list: _Optional[_Union[MaterialDbRecordList, _Mapping]] = ..., section_list: _Optional[_Union[SectionDbRecordList, _Mapping]] = ...) -> None: ...

class MaterialDbRecord(_message.Message):
    __slots__ = ["annex", "con_product", "custom_product", "data", "e_tag", "guid", "id", "major_version", "masonry_product", "minor_version", "name", "owner_name", "owner_type", "patch_version", "soil_product", "steel_product", "timber_product", "type"]
    ANNEX_FIELD_NUMBER: _ClassVar[int]
    CON_PRODUCT_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_PRODUCT_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    E_TAG_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MAJOR_VERSION_FIELD_NUMBER: _ClassVar[int]
    MASONRY_PRODUCT_FIELD_NUMBER: _ClassVar[int]
    MINOR_VERSION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_TYPE_FIELD_NUMBER: _ClassVar[int]
    PATCH_VERSION_FIELD_NUMBER: _ClassVar[int]
    SOIL_PRODUCT_FIELD_NUMBER: _ClassVar[int]
    STEEL_PRODUCT_FIELD_NUMBER: _ClassVar[int]
    TIMBER_PRODUCT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    annex: _eurocode_pb2.Annex
    con_product: _concrete_pb2.Type
    custom_product: str
    data: _material_pb2.Data
    e_tag: str
    guid: str
    id: int
    major_version: int
    masonry_product: _masonry_pb2.Product
    minor_version: int
    name: str
    owner_name: str
    owner_type: _utils_pb2_1.Owner
    patch_version: int
    soil_product: _soil_pb2.Behaviour
    steel_product: _steel_pb2.Product
    timber_product: _timber_pb2.ProductType
    type: _material_pb2.Mtrl
    def __init__(self, guid: _Optional[str] = ..., e_tag: _Optional[str] = ..., major_version: _Optional[int] = ..., minor_version: _Optional[int] = ..., patch_version: _Optional[int] = ..., owner_type: _Optional[_Union[_utils_pb2_1.Owner, str]] = ..., owner_name: _Optional[str] = ..., id: _Optional[int] = ..., annex: _Optional[_Union[_eurocode_pb2.Annex, str]] = ..., name: _Optional[str] = ..., type: _Optional[_Union[_material_pb2.Mtrl, str]] = ..., data: _Optional[_Union[_material_pb2.Data, _Mapping]] = ..., con_product: _Optional[_Union[_concrete_pb2.Type, str]] = ..., steel_product: _Optional[_Union[_steel_pb2.Product, str]] = ..., timber_product: _Optional[_Union[_timber_pb2.ProductType, str]] = ..., soil_product: _Optional[_Union[_soil_pb2.Behaviour, str]] = ..., masonry_product: _Optional[_Union[_masonry_pb2.Product, str]] = ..., custom_product: _Optional[str] = ...) -> None: ...

class MaterialDbRecordList(_message.Message):
    __slots__ = ["materials"]
    MATERIALS_FIELD_NUMBER: _ClassVar[int]
    materials: _containers.RepeatedCompositeFieldContainer[MaterialDbRecord]
    def __init__(self, materials: _Optional[_Iterable[_Union[MaterialDbRecord, _Mapping]]] = ...) -> None: ...

class SectionDbRecord(_message.Message):
    __slots__ = ["annex", "data", "e_tag", "family", "guid", "id", "major_version", "material", "minor_version", "name", "owner_name", "owner_type", "patch_version"]
    ANNEX_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    E_TAG_FIELD_NUMBER: _ClassVar[int]
    FAMILY_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MAJOR_VERSION_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_FIELD_NUMBER: _ClassVar[int]
    MINOR_VERSION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_TYPE_FIELD_NUMBER: _ClassVar[int]
    PATCH_VERSION_FIELD_NUMBER: _ClassVar[int]
    annex: _eurocode_pb2.Annex
    data: _sections_pb2.Section
    e_tag: str
    family: _sections_pb2.SectionType
    guid: str
    id: int
    major_version: int
    material: _sections_pb2.MaterialCategory
    minor_version: int
    name: str
    owner_name: str
    owner_type: _utils_pb2_1.Owner
    patch_version: int
    def __init__(self, guid: _Optional[str] = ..., e_tag: _Optional[str] = ..., major_version: _Optional[int] = ..., minor_version: _Optional[int] = ..., patch_version: _Optional[int] = ..., owner_type: _Optional[_Union[_utils_pb2_1.Owner, str]] = ..., owner_name: _Optional[str] = ..., id: _Optional[int] = ..., annex: _Optional[_Union[_eurocode_pb2.Annex, str]] = ..., name: _Optional[str] = ..., material: _Optional[_Union[_sections_pb2.MaterialCategory, str]] = ..., family: _Optional[_Union[_sections_pb2.SectionType, str]] = ..., data: _Optional[_Union[_sections_pb2.Section, _Mapping]] = ...) -> None: ...

class SectionDbRecordList(_message.Message):
    __slots__ = ["sections"]
    SECTIONS_FIELD_NUMBER: _ClassVar[int]
    sections: _containers.RepeatedCompositeFieldContainer[SectionDbRecord]
    def __init__(self, sections: _Optional[_Iterable[_Union[SectionDbRecord, _Mapping]]] = ...) -> None: ...
