from Material import concrete_pb2 as _concrete_pb2
from Utils import utils_pb2 as _utils_pb2
from Material import steel_pb2 as _steel_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Material import timber_pb2 as _timber_pb2
from Utils import utils_pb2 as _utils_pb2_1_1
from Material import timber_solid_pb2 as _timber_solid_pb2
from Material import timber_board_pb2 as _timber_board_pb2
from Material import soil_pb2 as _soil_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1
from Material import reinforcement_pb2 as _reinforcement_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1
from Geometry import reinf_pb2 as _reinf_pb2
from FireProtection import steel_pb2 as _steel_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1
from FireProtection import timber_pb2 as _timber_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1_1
from Material import masonry_pb2 as _masonry_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1_1_1
from Material import custom_pb2 as _custom_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1_1_1_1_1_1
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Material.concrete_pb2 import CharacteristicData
from Material.concrete_pb2 import Data
from Material.concrete_pb2 import Type
from Material.concrete_pb2 import DensityClass
from Material.steel_pb2 import Type
from Material.steel_pb2 import CharacteristicData
from Material.steel_pb2 import StrengthValue
from Material.steel_pb2 import Data
from Material.steel_pb2 import ProductionType
from Material.steel_pb2 import Sort
from Material.steel_pb2 import Product
from Material.steel_pb2 import DuctilityClass
from Material.timber_pb2 import Data
from Material.timber_pb2 import ProductType
from Material.timber_pb2 import WoodType
from Material.soil_pb2 import Generic
from Material.soil_pb2 import CharacteristicData
from Material.soil_pb2 import WallStrength
from Material.soil_pb2 import PileShaftResistance
from Material.soil_pb2 import Data
from Material.soil_pb2 import MaterialModel
from Material.soil_pb2 import Behaviour
from Material.reinforcement_pb2 import CharacteristicData
from Material.reinforcement_pb2 import DiameterItem
from Material.reinforcement_pb2 import Data
from FireProtection.steel_pb2 import CharacteristicData
from FireProtection.steel_pb2 import Data
from FireProtection.steel_pb2 import Encasement
from FireProtection.timber_pb2 import CharacteristicData
from FireProtection.timber_pb2 import Data
from FireProtection.timber_pb2 import MaterialType
from Material.masonry_pb2 import CharacteristicData
from Material.masonry_pb2 import Data
from Material.masonry_pb2 import Product
from Material.masonry_pb2 import Manner
from Material.masonry_pb2 import Group
from Material.masonry_pb2 import Class
from Material.masonry_pb2 import Category
from Material.custom_pb2 import CharacteristicData
from Material.custom_pb2 import Data
BEHAVIOUR_COMBINED: _soil_pb2.Behaviour
BEHAVIOUR_DRAINED: _soil_pb2.Behaviour
BEHAVIOUR_ROCK: _soil_pb2.Behaviour
BEHAVIOUR_ROCK_PLANE_GRINDED: _soil_pb2.Behaviour
BEHAVIOUR_UNDRAINED: _soil_pb2.Behaviour
BEHAVIOUR_UNSPECIFIED: _soil_pb2.Behaviour
CATEGORY_ANY_MORTAR_CATEGORY2: _masonry_pb2.Category
CATEGORY_DESIGNED_MORTAR_CATEGORY1: _masonry_pb2.Category
CATEGORY_PRESCRIBED_MORTAR_CATEGORY1: _masonry_pb2.Category
CATEGORY_UNSPECIFIED: _masonry_pb2.Category
CLASS_25: _masonry_pb2.Class
CLASS_UNSPECIFIED: _masonry_pb2.Class
DENSITY_CLASS_LIGHT10: _concrete_pb2.DensityClass
DENSITY_CLASS_LIGHT12: _concrete_pb2.DensityClass
DENSITY_CLASS_LIGHT14: _concrete_pb2.DensityClass
DENSITY_CLASS_LIGHT16: _concrete_pb2.DensityClass
DENSITY_CLASS_LIGHT18: _concrete_pb2.DensityClass
DENSITY_CLASS_LIGHT20: _concrete_pb2.DensityClass
DENSITY_CLASS_REGULAR: _concrete_pb2.DensityClass
DENSITY_CLASS_UNSPECIFIED: _concrete_pb2.DensityClass
DESCRIPTOR: _descriptor.FileDescriptor
DUCTILITY_CLASS_A: _steel_pb2.DuctilityClass
DUCTILITY_CLASS_B: _steel_pb2.DuctilityClass
DUCTILITY_CLASS_C: _steel_pb2.DuctilityClass
DUCTILITY_CLASS_UNSPECIFIED: _steel_pb2.DuctilityClass
ENCASEMENT_CONTOUR: _steel_pb2_1.Encasement
ENCASEMENT_HOLLOW: _steel_pb2_1.Encasement
ENCASEMENT_UNSPECIFIED: _steel_pb2_1.Encasement
GROUP_1: _masonry_pb2.Group
GROUP_2: _masonry_pb2.Group
GROUP_3: _masonry_pb2.Group
GROUP_4: _masonry_pb2.Group
GROUP_UNSPECIFIED: _masonry_pb2.Group
MANNER_FJM: _masonry_pb2.Manner
MANNER_SBM: _masonry_pb2.Manner
MANNER_UMV: _masonry_pb2.Manner
MANNER_UNSPECIFIED: _masonry_pb2.Manner
MATERIAL_MODEL_GENERIC: _soil_pb2.MaterialModel
MATERIAL_MODEL_LINEAR: _soil_pb2.MaterialModel
MATERIAL_MODEL_LOG: _soil_pb2.MaterialModel
MATERIAL_MODEL_NOSETTLEMENT: _soil_pb2.MaterialModel
MATERIAL_MODEL_OVERCONSOLIDATED: _soil_pb2.MaterialModel
MATERIAL_MODEL_UNSPECIFIED: _soil_pb2.MaterialModel
MATERIAL_TYPE_GYPSUM_BOARD_AH1_INTERNAL: _timber_pb2_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_AH1_OTHER: _timber_pb2_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_AH2_INTERNAL: _timber_pb2_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_AH2_OTHER: _timber_pb2_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F1_INTERNAL: _timber_pb2_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F1_OTHER: _timber_pb2_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F2_INTERNAL: _timber_pb2_1.MaterialType
MATERIAL_TYPE_GYPSUM_BOARD_F2_OTHER: _timber_pb2_1.MaterialType
MATERIAL_TYPE_NONE: _timber_pb2_1.MaterialType
MATERIAL_TYPE_ROCK_FIBER: _timber_pb2_1.MaterialType
MATERIAL_TYPE_UNSPECIFIED: _timber_pb2_1.MaterialType
MATERIAL_TYPE_USER_DEFINED: _timber_pb2_1.MaterialType
MATERIAL_TYPE_WOOD: _timber_pb2_1.MaterialType
MTRL_CONCRETE: Mtrl
MTRL_CUSTOM: Mtrl
MTRL_FIRE_PROTECTION_STEEL: Mtrl
MTRL_FIRE_PROTECTION_TIMBER: Mtrl
MTRL_MASONRY: Mtrl
MTRL_REINFORCEMENT: Mtrl
MTRL_SOIL: Mtrl
MTRL_STEEL: Mtrl
MTRL_TIMBER: Mtrl
MTRL_UNSPECIFIED: Mtrl
PRODUCTION_TYPE_COLD_WORKED: _steel_pb2.ProductionType
PRODUCTION_TYPE_ROLLED: _steel_pb2.ProductionType
PRODUCTION_TYPE_UNSPECIFIED: _steel_pb2.ProductionType
PRODUCTION_TYPE_WELDED: _steel_pb2.ProductionType
PRODUCT_AUTOCLAVED_AERATED_CONCRETE_BLOCKS: _masonry_pb2.Product
PRODUCT_CALCIUM_SILICATE_BRICKS: _masonry_pb2.Product
PRODUCT_CLAY_BLOCKS: _masonry_pb2.Product
PRODUCT_CONCRETE_BRICKS: _masonry_pb2.Product
PRODUCT_CONCRETE_HOLE_BLOCKS: _masonry_pb2.Product
PRODUCT_HOLE_BRICKS: _masonry_pb2.Product
PRODUCT_LIGHTWEIGHT_CONCRETE_BLOCKS: _masonry_pb2.Product
PRODUCT_LIGHT_EXPANDED_CLAY_AGGREGATE_BLOCKS: _masonry_pb2.Product
PRODUCT_PLAIN: _steel_pb2.Product
PRODUCT_REINFORCEMENT: _steel_pb2.Product
PRODUCT_SOLID_BRICKS: _masonry_pb2.Product
PRODUCT_SOLID_CONCRETE_BLOCKS: _masonry_pb2.Product
PRODUCT_TYPE_GL: _timber_pb2.ProductType
PRODUCT_TYPE_KERTO: _timber_pb2.ProductType
PRODUCT_TYPE_LVL: _timber_pb2.ProductType
PRODUCT_TYPE_OSB2: _timber_pb2.ProductType
PRODUCT_TYPE_OSB3: _timber_pb2.ProductType
PRODUCT_TYPE_OSB4: _timber_pb2.ProductType
PRODUCT_TYPE_REGULAR: _timber_pb2.ProductType
PRODUCT_TYPE_UNSPECIFIED: _timber_pb2.ProductType
PRODUCT_UNSPECIFIED: _masonry_pb2.Product
SORT_REGULAR: _steel_pb2.Sort
SORT_STAINLESS: _steel_pb2.Sort
SORT_UNSPECIFIED: _steel_pb2.Sort
TYPE_LIGHT: _concrete_pb2.Type
TYPE_REGULAR: _concrete_pb2.Type
TYPE_UNSPECIFIED: _concrete_pb2.Type
WOOD_TYPE_ASH: _timber_pb2.WoodType
WOOD_TYPE_BIRCH: _timber_pb2.WoodType
WOOD_TYPE_OAK: _timber_pb2.WoodType
WOOD_TYPE_PINE: _timber_pb2.WoodType
WOOD_TYPE_UNSPECIFIED: _timber_pb2.WoodType

class Data(_message.Message):
    __slots__ = ["con_data", "custom_data", "fire_steel_data", "fire_timber_data", "id", "masonry_data", "owner_name", "owner_type", "reinforcement_data", "soil_data", "steel_data", "timber_data", "type"]
    CON_DATA_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_DATA_FIELD_NUMBER: _ClassVar[int]
    FIRE_STEEL_DATA_FIELD_NUMBER: _ClassVar[int]
    FIRE_TIMBER_DATA_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MASONRY_DATA_FIELD_NUMBER: _ClassVar[int]
    OWNER_NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_TYPE_FIELD_NUMBER: _ClassVar[int]
    REINFORCEMENT_DATA_FIELD_NUMBER: _ClassVar[int]
    SOIL_DATA_FIELD_NUMBER: _ClassVar[int]
    STEEL_DATA_FIELD_NUMBER: _ClassVar[int]
    TIMBER_DATA_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    con_data: _concrete_pb2.Data
    custom_data: _custom_pb2.Data
    fire_steel_data: _steel_pb2_1.Data
    fire_timber_data: _timber_pb2_1.Data
    id: _utils_pb2_1_1_1_1_1_1_1_1.ID
    masonry_data: _masonry_pb2.Data
    owner_name: str
    owner_type: _utils_pb2_1_1_1_1_1_1_1_1.Owner
    reinforcement_data: _reinforcement_pb2.Data
    soil_data: _soil_pb2.Data
    steel_data: _steel_pb2.Data
    timber_data: _timber_pb2.Data
    type: Mtrl
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1_1_1_1_1_1_1.ID, _Mapping]] = ..., type: _Optional[_Union[Mtrl, str]] = ..., con_data: _Optional[_Union[_concrete_pb2.Data, _Mapping]] = ..., steel_data: _Optional[_Union[_steel_pb2.Data, _Mapping]] = ..., timber_data: _Optional[_Union[_timber_pb2.Data, _Mapping]] = ..., soil_data: _Optional[_Union[_soil_pb2.Data, _Mapping]] = ..., reinforcement_data: _Optional[_Union[_reinforcement_pb2.Data, _Mapping]] = ..., fire_steel_data: _Optional[_Union[_steel_pb2_1.Data, _Mapping]] = ..., fire_timber_data: _Optional[_Union[_timber_pb2_1.Data, _Mapping]] = ..., masonry_data: _Optional[_Union[_masonry_pb2.Data, _Mapping]] = ..., custom_data: _Optional[_Union[_custom_pb2.Data, _Mapping]] = ..., owner_type: _Optional[_Union[_utils_pb2_1_1_1_1_1_1_1_1.Owner, str]] = ..., owner_name: _Optional[str] = ...) -> None: ...

class Mtrl(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
