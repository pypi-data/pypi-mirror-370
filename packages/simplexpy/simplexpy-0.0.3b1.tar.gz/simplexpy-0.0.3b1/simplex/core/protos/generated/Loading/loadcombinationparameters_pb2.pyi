from Utils import eurocode_pb2 as _eurocode_pb2
from Loading import loadcase_pb2 as _loadcase_pb2
from Utils import utils_pb2 as _utils_pb2
from Loading import loadcombination_pb2 as _loadcombination_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Design import soil_pb2 as _soil_pb2
import structure_pb2 as _structure_pb2
from Utils import utils_pb2 as _utils_pb2_1_1
import element_pb2 as _element_pb2
import support_pb2 as _support_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from Loading import loading_pb2 as _loading_pb2
from Design import design_pb2 as _design_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.eurocode_pb2 import DesignConfiguration
from Utils.eurocode_pb2 import Annex
from Utils.eurocode_pb2 import SnowZone
from Utils.eurocode_pb2 import Generation
from Loading.loadcase_pb2 import Data
from Loading.loadcase_pb2 import Type
from Loading.loadcase_pb2 import DurationClass
from Loading.loadcase_pb2 import Category
from Loading.loadcombination_pb2 import CombinationPart
from Loading.loadcombination_pb2 import BeamConfiguration
from Loading.loadcombination_pb2 import FoundationConfiguration
from Loading.loadcombination_pb2 import ActiveEarthPressureConfiguration
from Loading.loadcombination_pb2 import PassiveEarthPressureConfiguration
from Loading.loadcombination_pb2 import EarthPressureConfiguration
from Loading.loadcombination_pb2 import PileConfiguration
from Loading.loadcombination_pb2 import Compaction
from Loading.loadcombination_pb2 import Coefficient
from Loading.loadcombination_pb2 import Data
from Loading.loadcombination_pb2 import Type
from Loading.loadcombination_pb2 import CoaType
from Loading.loadcombination_pb2 import ServiceabilityType
from Loading.loadcombination_pb2 import LimitState
from Loading.loadcombination_pb2 import CoefficientType
from Loading.loadcombination_pb2 import GeoType
from structure_pb2 import Data
from structure_pb2 import ConsequenceClass
from structure_pb2 import ReliabilityClass
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
CATEGORY_A: _loadcase_pb2.Category
CATEGORY_B: _loadcase_pb2.Category
CATEGORY_C: _loadcase_pb2.Category
CATEGORY_D: _loadcase_pb2.Category
CATEGORY_E: _loadcase_pb2.Category
CATEGORY_F: _loadcase_pb2.Category
CATEGORY_G: _loadcase_pb2.Category
CATEGORY_G2: _loadcase_pb2.Category
CATEGORY_H: _loadcase_pb2.Category
CATEGORY_I1: _loadcase_pb2.Category
CATEGORY_I2: _loadcase_pb2.Category
CATEGORY_I3: _loadcase_pb2.Category
CATEGORY_K: _loadcase_pb2.Category
CATEGORY_S1: _loadcase_pb2.Category
CATEGORY_S2: _loadcase_pb2.Category
CATEGORY_S3_C_G: _loadcase_pb2.Category
CATEGORY_S3_H_K: _loadcase_pb2.Category
CATEGORY_T: _loadcase_pb2.Category
CATEGORY_UNSPECIFIED: _loadcase_pb2.Category
COA_TYPE_610: _loadcombination_pb2.CoaType
COA_TYPE_6105: _loadcombination_pb2.CoaType
COA_TYPE_610A: _loadcombination_pb2.CoaType
COA_TYPE_610A3: _loadcombination_pb2.CoaType
COA_TYPE_610B: _loadcombination_pb2.CoaType
COA_TYPE_610B4: _loadcombination_pb2.CoaType
COA_TYPE_611AB: _loadcombination_pb2.CoaType
COA_TYPE_614B: _loadcombination_pb2.CoaType
COA_TYPE_615B: _loadcombination_pb2.CoaType
COA_TYPE_616B: _loadcombination_pb2.CoaType
COA_TYPE_812: _loadcombination_pb2.CoaType
COA_TYPE_813A: _loadcombination_pb2.CoaType
COA_TYPE_813B: _loadcombination_pb2.CoaType
COA_TYPE_814A: _loadcombination_pb2.CoaType
COA_TYPE_814B: _loadcombination_pb2.CoaType
COA_TYPE_815: _loadcombination_pb2.CoaType
COA_TYPE_816: _loadcombination_pb2.CoaType
COA_TYPE_829: _loadcombination_pb2.CoaType
COA_TYPE_830: _loadcombination_pb2.CoaType
COA_TYPE_831: _loadcombination_pb2.CoaType
COA_TYPE_UNSPECIFIED: _loadcombination_pb2.CoaType
COEFFICIENT_TYPE_BASE: _loadcombination_pb2.CoefficientType
COEFFICIENT_TYPE_CHI_FACTOR: _loadcombination_pb2.CoefficientType
COEFFICIENT_TYPE_ETA: _loadcombination_pb2.CoefficientType
COEFFICIENT_TYPE_GAMMA: _loadcombination_pb2.CoefficientType
COEFFICIENT_TYPE_KFI: _loadcombination_pb2.CoefficientType
COEFFICIENT_TYPE_PSI: _loadcombination_pb2.CoefficientType
COEFFICIENT_TYPE_STOREY: _loadcombination_pb2.CoefficientType
COEFFICIENT_TYPE_UNSPECIFIED: _loadcombination_pb2.CoefficientType
CONSEQUENCE_CLASS_1: _structure_pb2.ConsequenceClass
CONSEQUENCE_CLASS_2: _structure_pb2.ConsequenceClass
CONSEQUENCE_CLASS_3: _structure_pb2.ConsequenceClass
CONSEQUENCE_CLASS_UNSPECIFIED: _structure_pb2.ConsequenceClass
DESCRIPTOR: _descriptor.FileDescriptor
DURATION_CLASS_INSTANTANEOUS: _loadcase_pb2.DurationClass
DURATION_CLASS_LONG: _loadcase_pb2.DurationClass
DURATION_CLASS_MEDIUM: _loadcase_pb2.DurationClass
DURATION_CLASS_PERMANENT: _loadcase_pb2.DurationClass
DURATION_CLASS_SHORT: _loadcase_pb2.DurationClass
DURATION_CLASS_UNSPECIFIED: _loadcase_pb2.DurationClass
GENERATION_1: _eurocode_pb2.Generation
GENERATION_2: _eurocode_pb2.Generation
GENERATION_UNSPECIFIED: _eurocode_pb2.Generation
GEO_TYPE_1: _loadcombination_pb2.GeoType
GEO_TYPE_2: _loadcombination_pb2.GeoType
GEO_TYPE_UNSPECIFIED: _loadcombination_pb2.GeoType
IS_DOMINATING_TYPE_CAT_E: IsDominatingType
IS_DOMINATING_TYPE_NONE: IsDominatingType
IS_DOMINATING_TYPE_TEMP: IsDominatingType
IS_DOMINATING_TYPE_UNSPECIFIED: IsDominatingType
IS_DOMINATING_TYPE_WIND: IsDominatingType
LIMIT_STATE_EQU: _loadcombination_pb2.LimitState
LIMIT_STATE_GEO: _loadcombination_pb2.LimitState
LIMIT_STATE_STR: _loadcombination_pb2.LimitState
LIMIT_STATE_UNSPECIFIED: _loadcombination_pb2.LimitState
LIMIT_STATE_VC1: _loadcombination_pb2.LimitState
LIMIT_STATE_VC2A: _loadcombination_pb2.LimitState
LIMIT_STATE_VC2B: _loadcombination_pb2.LimitState
LIMIT_STATE_VC3: _loadcombination_pb2.LimitState
LIMIT_STATE_VC4: _loadcombination_pb2.LimitState
PSI_TYPE_0: PsiType
PSI_TYPE_1: PsiType
PSI_TYPE_2: PsiType
PSI_TYPE_UNSPECIFIED: PsiType
RELIABILITY_CLASS_1: _structure_pb2.ReliabilityClass
RELIABILITY_CLASS_2: _structure_pb2.ReliabilityClass
RELIABILITY_CLASS_3: _structure_pb2.ReliabilityClass
RELIABILITY_CLASS_UNSPECIFIED: _structure_pb2.ReliabilityClass
SERVICEABILITY_TYPE_LONG: _loadcombination_pb2.ServiceabilityType
SERVICEABILITY_TYPE_SHORT: _loadcombination_pb2.ServiceabilityType
SERVICEABILITY_TYPE_UNSPECIFIED: _loadcombination_pb2.ServiceabilityType
SNOW_ZONE_1: _eurocode_pb2.SnowZone
SNOW_ZONE_2: _eurocode_pb2.SnowZone
SNOW_ZONE_3: _eurocode_pb2.SnowZone
SNOW_ZONE_UNSPECIFIED: _eurocode_pb2.SnowZone
TYPE_ACCIDENTAL: _loadcombination_pb2.Type
TYPE_ACCIDENT_LOAD: _loadcase_pb2.Type
TYPE_CHARACTERISTIC: _loadcombination_pb2.Type
TYPE_CONSTRUCTION_LOAD: _loadcase_pb2.Type
TYPE_FIRE: _loadcombination_pb2.Type
TYPE_FREQUENT: _loadcombination_pb2.Type
TYPE_ICE_LOAD: _loadcase_pb2.Type
TYPE_IMPOSED_LOAD: _loadcase_pb2.Type
TYPE_PERMANENT_LOAD: _loadcase_pb2.Type
TYPE_QUASI_PERMANENT: _loadcombination_pb2.Type
TYPE_SEISMIC: _loadcombination_pb2.Type
TYPE_SEISMIC_LOAD: _loadcase_pb2.Type
TYPE_SELF_WEIGHT: _loadcase_pb2.Type
TYPE_SNOW_LOAD: _loadcase_pb2.Type
TYPE_SOIL_LOAD: _loadcase_pb2.Type
TYPE_SOIL_SELF_WEIGHT: _loadcase_pb2.Type
TYPE_TEMPERATURE_LOAD: _loadcase_pb2.Type
TYPE_ULTIMATE: _loadcombination_pb2.Type
TYPE_UNSPECIFIED: _loadcombination_pb2.Type
TYPE_WIND_LOAD: _loadcase_pb2.Type

class KFI(_message.Message):
    __slots__ = ["cc", "na", "value"]
    CC_FIELD_NUMBER: _ClassVar[int]
    NA_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    cc: _structure_pb2.ConsequenceClass
    na: _eurocode_pb2.Annex
    value: float
    def __init__(self, na: _Optional[_Union[_eurocode_pb2.Annex, str]] = ..., cc: _Optional[_Union[_structure_pb2.ConsequenceClass, str]] = ..., value: _Optional[float] = ...) -> None: ...

class KFIList(_message.Message):
    __slots__ = ["kfis"]
    KFIS_FIELD_NUMBER: _ClassVar[int]
    kfis: _containers.RepeatedCompositeFieldContainer[KFI]
    def __init__(self, kfis: _Optional[_Iterable[_Union[KFI, _Mapping]]] = ...) -> None: ...

class Kmod(_message.Message):
    __slots__ = ["duration_class", "lc_type", "value"]
    DURATION_CLASS_FIELD_NUMBER: _ClassVar[int]
    LC_TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    duration_class: _loadcase_pb2.DurationClass
    lc_type: _loadcombination_pb2.Type
    value: float
    def __init__(self, lc_type: _Optional[_Union[_loadcombination_pb2.Type, str]] = ..., duration_class: _Optional[_Union[_loadcase_pb2.DurationClass, str]] = ..., value: _Optional[float] = ...) -> None: ...

class KmodList(_message.Message):
    __slots__ = ["kmods"]
    KMODS_FIELD_NUMBER: _ClassVar[int]
    kmods: _containers.RepeatedCompositeFieldContainer[Kmod]
    def __init__(self, kmods: _Optional[_Iterable[_Union[Kmod, _Mapping]]] = ...) -> None: ...

class PsiForLoad(_message.Message):
    __slots__ = ["caracteristic_snow_load_type", "cen_height_bigger1000", "dominating", "imposed_category", "loadcase_type", "na", "psi", "value"]
    CARACTERISTIC_SNOW_LOAD_TYPE_FIELD_NUMBER: _ClassVar[int]
    CEN_HEIGHT_BIGGER1000_FIELD_NUMBER: _ClassVar[int]
    DOMINATING_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    LOADCASE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NA_FIELD_NUMBER: _ClassVar[int]
    PSI_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    caracteristic_snow_load_type: int
    cen_height_bigger1000: bool
    dominating: IsDominatingType
    imposed_category: _loadcase_pb2.Category
    loadcase_type: _loadcase_pb2.Type
    na: _eurocode_pb2.Annex
    psi: PsiType
    value: float
    def __init__(self, na: _Optional[_Union[_eurocode_pb2.Annex, str]] = ..., psi: _Optional[_Union[PsiType, str]] = ..., loadcase_type: _Optional[_Union[_loadcase_pb2.Type, str]] = ..., dominating: _Optional[_Union[IsDominatingType, str]] = ..., imposed_category: _Optional[_Union[_loadcase_pb2.Category, str]] = ..., cen_height_bigger1000: bool = ..., caracteristic_snow_load_type: _Optional[int] = ..., value: _Optional[float] = ...) -> None: ...

class PsiForLoadsList(_message.Message):
    __slots__ = ["psi_for_loads"]
    PSI_FOR_LOADS_FIELD_NUMBER: _ClassVar[int]
    psi_for_loads: _containers.RepeatedCompositeFieldContainer[PsiForLoad]
    def __init__(self, psi_for_loads: _Optional[_Iterable[_Union[PsiForLoad, _Mapping]]] = ...) -> None: ...

class PsiType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class IsDominatingType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
