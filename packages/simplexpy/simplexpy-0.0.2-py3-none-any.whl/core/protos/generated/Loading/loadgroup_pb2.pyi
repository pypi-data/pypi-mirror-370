from Utils import utils_pb2 as _utils_pb2
from Loading import loadcase_pb2 as _loadcase_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Loading import loadcombination_pb2 as _loadcombination_pb2
from Utils import utils_pb2 as _utils_pb2_1_1
from Design import soil_pb2 as _soil_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
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
DESCRIPTOR: _descriptor.FileDescriptor
DURATION_CLASS_INSTANTANEOUS: _loadcase_pb2.DurationClass
DURATION_CLASS_LONG: _loadcase_pb2.DurationClass
DURATION_CLASS_MEDIUM: _loadcase_pb2.DurationClass
DURATION_CLASS_PERMANENT: _loadcase_pb2.DurationClass
DURATION_CLASS_SHORT: _loadcase_pb2.DurationClass
DURATION_CLASS_UNSPECIFIED: _loadcase_pb2.DurationClass
GEO_TYPE_1: _loadcombination_pb2.GeoType
GEO_TYPE_2: _loadcombination_pb2.GeoType
GEO_TYPE_UNSPECIFIED: _loadcombination_pb2.GeoType
LIMIT_STATE_EQU: _loadcombination_pb2.LimitState
LIMIT_STATE_GEO: _loadcombination_pb2.LimitState
LIMIT_STATE_STR: _loadcombination_pb2.LimitState
LIMIT_STATE_UNSPECIFIED: _loadcombination_pb2.LimitState
LIMIT_STATE_VC1: _loadcombination_pb2.LimitState
LIMIT_STATE_VC2A: _loadcombination_pb2.LimitState
LIMIT_STATE_VC2B: _loadcombination_pb2.LimitState
LIMIT_STATE_VC3: _loadcombination_pb2.LimitState
LIMIT_STATE_VC4: _loadcombination_pb2.LimitState
OWNER_COMPANY: _utils_pb2_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1.Owner
OWNER_USER: _utils_pb2_1_1.Owner
SERVICEABILITY_TYPE_LONG: _loadcombination_pb2.ServiceabilityType
SERVICEABILITY_TYPE_SHORT: _loadcombination_pb2.ServiceabilityType
SERVICEABILITY_TYPE_UNSPECIFIED: _loadcombination_pb2.ServiceabilityType
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
alternative: LoadcaseRelationship
entire: LoadcaseRelationship
simultaneous: LoadcaseRelationship
unspecified: LoadcaseRelationship

class Accidental(_message.Message):
    __slots__ = ["safety_factor"]
    SAFETY_FACTOR_FIELD_NUMBER: _ClassVar[int]
    safety_factor: float
    def __init__(self, safety_factor: _Optional[float] = ...) -> None: ...

class Fire(_message.Message):
    __slots__ = ["safety_factor"]
    SAFETY_FACTOR_FIELD_NUMBER: _ClassVar[int]
    safety_factor: float
    def __init__(self, safety_factor: _Optional[float] = ...) -> None: ...

class Group(_message.Message):
    __slots__ = ["accidental", "id", "loadcase_id", "loadcase_relationship", "permanent", "seismic", "stress", "temporary"]
    ACCIDENTAL_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LOADCASE_ID_FIELD_NUMBER: _ClassVar[int]
    LOADCASE_RELATIONSHIP_FIELD_NUMBER: _ClassVar[int]
    PERMANENT_FIELD_NUMBER: _ClassVar[int]
    SEISMIC_FIELD_NUMBER: _ClassVar[int]
    STRESS_FIELD_NUMBER: _ClassVar[int]
    TEMPORARY_FIELD_NUMBER: _ClassVar[int]
    accidental: Accidental
    id: _utils_pb2_1_1.ID
    loadcase_id: _containers.RepeatedScalarFieldContainer[str]
    loadcase_relationship: LoadcaseRelationship
    permanent: Permanent
    seismic: Seismic
    stress: Stress
    temporary: Temporary
    def __init__(self, id: _Optional[_Union[_utils_pb2_1_1.ID, _Mapping]] = ..., permanent: _Optional[_Union[Permanent, _Mapping]] = ..., stress: _Optional[_Union[Stress, _Mapping]] = ..., temporary: _Optional[_Union[Temporary, _Mapping]] = ..., accidental: _Optional[_Union[Accidental, _Mapping]] = ..., seismic: _Optional[_Union[Seismic, _Mapping]] = ..., loadcase_relationship: _Optional[_Union[LoadcaseRelationship, str]] = ..., loadcase_id: _Optional[_Iterable[str]] = ...) -> None: ...

class Groups(_message.Message):
    __slots__ = ["include_min_one_loadcase_in_temp_loadgroup", "loadgroups", "simple_serviceability"]
    INCLUDE_MIN_ONE_LOADCASE_IN_TEMP_LOADGROUP_FIELD_NUMBER: _ClassVar[int]
    LOADGROUPS_FIELD_NUMBER: _ClassVar[int]
    SIMPLE_SERVICEABILITY_FIELD_NUMBER: _ClassVar[int]
    include_min_one_loadcase_in_temp_loadgroup: bool
    loadgroups: _containers.RepeatedCompositeFieldContainer[Group]
    simple_serviceability: bool
    def __init__(self, simple_serviceability: bool = ..., include_min_one_loadcase_in_temp_loadgroup: bool = ..., loadgroups: _Optional[_Iterable[_Union[Group, _Mapping]]] = ...) -> None: ...

class Permanent(_message.Message):
    __slots__ = ["accident_favourable", "accident_unfavourable", "favourable", "include_permanent_load_favorable", "unfavourable", "xi"]
    ACCIDENT_FAVOURABLE_FIELD_NUMBER: _ClassVar[int]
    ACCIDENT_UNFAVOURABLE_FIELD_NUMBER: _ClassVar[int]
    FAVOURABLE_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_PERMANENT_LOAD_FAVORABLE_FIELD_NUMBER: _ClassVar[int]
    UNFAVOURABLE_FIELD_NUMBER: _ClassVar[int]
    XI_FIELD_NUMBER: _ClassVar[int]
    accident_favourable: float
    accident_unfavourable: float
    favourable: float
    include_permanent_load_favorable: bool
    unfavourable: float
    xi: float
    def __init__(self, favourable: _Optional[float] = ..., unfavourable: _Optional[float] = ..., xi: _Optional[float] = ..., accident_favourable: _Optional[float] = ..., accident_unfavourable: _Optional[float] = ..., include_permanent_load_favorable: bool = ...) -> None: ...

class Seismic(_message.Message):
    __slots__ = ["safety_factor"]
    SAFETY_FACTOR_FIELD_NUMBER: _ClassVar[int]
    safety_factor: float
    def __init__(self, safety_factor: _Optional[float] = ...) -> None: ...

class Stress(_message.Message):
    __slots__ = ["Accidental", "standard"]
    ACCIDENTAL_FIELD_NUMBER: _ClassVar[int]
    Accidental: float
    STANDARD_FIELD_NUMBER: _ClassVar[int]
    standard: float
    def __init__(self, standard: _Optional[float] = ..., Accidental: _Optional[float] = ...) -> None: ...

class Temporary(_message.Message):
    __slots__ = ["ignore_in_sls", "pot_dominating", "psi0", "psi1", "psi2", "safety_factor"]
    IGNORE_IN_SLS_FIELD_NUMBER: _ClassVar[int]
    POT_DOMINATING_FIELD_NUMBER: _ClassVar[int]
    PSI0_FIELD_NUMBER: _ClassVar[int]
    PSI1_FIELD_NUMBER: _ClassVar[int]
    PSI2_FIELD_NUMBER: _ClassVar[int]
    SAFETY_FACTOR_FIELD_NUMBER: _ClassVar[int]
    ignore_in_sls: bool
    pot_dominating: bool
    psi0: float
    psi1: float
    psi2: float
    safety_factor: float
    def __init__(self, safety_factor: _Optional[float] = ..., psi0: _Optional[float] = ..., psi1: _Optional[float] = ..., psi2: _Optional[float] = ..., ignore_in_sls: bool = ..., pot_dominating: bool = ...) -> None: ...

class LoadcaseRelationship(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
