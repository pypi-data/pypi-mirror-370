from Utils import utils_pb2 as _utils_pb2
from Loading import load_pb2 as _load_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Geometry import geometry_pb2 as _geometry_pb2
from Loading import loadcase_pb2 as _loadcase_pb2
from Utils import utils_pb2 as _utils_pb2_1_1
from Loading import loadgroup_pb2 as _loadgroup_pb2
from Utils import utils_pb2 as _utils_pb2_1_1_1
from Loading import loadcase_pb2 as _loadcase_pb2_1
from Loading import loadcombination_pb2 as _loadcombination_pb2
from Loading import loadcombination_pb2 as _loadcombination_pb2_1
from Utils import utils_pb2 as _utils_pb2_1_1_1_1
from Design import soil_pb2 as _soil_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
from Loading.load_pb2 import Data
from Loading.load_pb2 import Type
from Loading.load_pb2 import DistributionType
from Loading.loadcase_pb2 import Data
from Loading.loadcase_pb2 import Type
from Loading.loadcase_pb2 import DurationClass
from Loading.loadcase_pb2 import Category
from Loading.loadgroup_pb2 import Permanent
from Loading.loadgroup_pb2 import Stress
from Loading.loadgroup_pb2 import Temporary
from Loading.loadgroup_pb2 import Accidental
from Loading.loadgroup_pb2 import Fire
from Loading.loadgroup_pb2 import Seismic
from Loading.loadgroup_pb2 import Group
from Loading.loadgroup_pb2 import Groups
from Loading.loadgroup_pb2 import LoadcaseRelationship
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
CATEGORY_A: _loadcase_pb2_1.Category
CATEGORY_B: _loadcase_pb2_1.Category
CATEGORY_C: _loadcase_pb2_1.Category
CATEGORY_D: _loadcase_pb2_1.Category
CATEGORY_E: _loadcase_pb2_1.Category
CATEGORY_F: _loadcase_pb2_1.Category
CATEGORY_G: _loadcase_pb2_1.Category
CATEGORY_G2: _loadcase_pb2_1.Category
CATEGORY_H: _loadcase_pb2_1.Category
CATEGORY_I1: _loadcase_pb2_1.Category
CATEGORY_I2: _loadcase_pb2_1.Category
CATEGORY_I3: _loadcase_pb2_1.Category
CATEGORY_K: _loadcase_pb2_1.Category
CATEGORY_S1: _loadcase_pb2_1.Category
CATEGORY_S2: _loadcase_pb2_1.Category
CATEGORY_S3_C_G: _loadcase_pb2_1.Category
CATEGORY_S3_H_K: _loadcase_pb2_1.Category
CATEGORY_T: _loadcase_pb2_1.Category
CATEGORY_UNSPECIFIED: _loadcase_pb2_1.Category
COA_TYPE_610: _loadcombination_pb2_1.CoaType
COA_TYPE_6105: _loadcombination_pb2_1.CoaType
COA_TYPE_610A: _loadcombination_pb2_1.CoaType
COA_TYPE_610A3: _loadcombination_pb2_1.CoaType
COA_TYPE_610B: _loadcombination_pb2_1.CoaType
COA_TYPE_610B4: _loadcombination_pb2_1.CoaType
COA_TYPE_611AB: _loadcombination_pb2_1.CoaType
COA_TYPE_614B: _loadcombination_pb2_1.CoaType
COA_TYPE_615B: _loadcombination_pb2_1.CoaType
COA_TYPE_616B: _loadcombination_pb2_1.CoaType
COA_TYPE_812: _loadcombination_pb2_1.CoaType
COA_TYPE_813A: _loadcombination_pb2_1.CoaType
COA_TYPE_813B: _loadcombination_pb2_1.CoaType
COA_TYPE_814A: _loadcombination_pb2_1.CoaType
COA_TYPE_814B: _loadcombination_pb2_1.CoaType
COA_TYPE_815: _loadcombination_pb2_1.CoaType
COA_TYPE_816: _loadcombination_pb2_1.CoaType
COA_TYPE_829: _loadcombination_pb2_1.CoaType
COA_TYPE_830: _loadcombination_pb2_1.CoaType
COA_TYPE_831: _loadcombination_pb2_1.CoaType
COA_TYPE_UNSPECIFIED: _loadcombination_pb2_1.CoaType
COEFFICIENT_TYPE_BASE: _loadcombination_pb2_1.CoefficientType
COEFFICIENT_TYPE_CHI_FACTOR: _loadcombination_pb2_1.CoefficientType
COEFFICIENT_TYPE_ETA: _loadcombination_pb2_1.CoefficientType
COEFFICIENT_TYPE_GAMMA: _loadcombination_pb2_1.CoefficientType
COEFFICIENT_TYPE_KFI: _loadcombination_pb2_1.CoefficientType
COEFFICIENT_TYPE_PSI: _loadcombination_pb2_1.CoefficientType
COEFFICIENT_TYPE_STOREY: _loadcombination_pb2_1.CoefficientType
COEFFICIENT_TYPE_UNSPECIFIED: _loadcombination_pb2_1.CoefficientType
DESCRIPTOR: _descriptor.FileDescriptor
DISTRIBUTION_TYPE_LINE: _load_pb2.DistributionType
DISTRIBUTION_TYPE_NODE: _load_pb2.DistributionType
DISTRIBUTION_TYPE_POINT: _load_pb2.DistributionType
DISTRIBUTION_TYPE_SURFACE: _load_pb2.DistributionType
DISTRIBUTION_TYPE_UNSPECIFIED: _load_pb2.DistributionType
DISTRIBUTION_TYPE_VOLUME: _load_pb2.DistributionType
DURATION_CLASS_INSTANTANEOUS: _loadcase_pb2_1.DurationClass
DURATION_CLASS_LONG: _loadcase_pb2_1.DurationClass
DURATION_CLASS_MEDIUM: _loadcase_pb2_1.DurationClass
DURATION_CLASS_PERMANENT: _loadcase_pb2_1.DurationClass
DURATION_CLASS_SHORT: _loadcase_pb2_1.DurationClass
DURATION_CLASS_UNSPECIFIED: _loadcase_pb2_1.DurationClass
GEO_TYPE_1: _loadcombination_pb2_1.GeoType
GEO_TYPE_2: _loadcombination_pb2_1.GeoType
GEO_TYPE_UNSPECIFIED: _loadcombination_pb2_1.GeoType
LIMIT_STATE_EQU: _loadcombination_pb2_1.LimitState
LIMIT_STATE_GEO: _loadcombination_pb2_1.LimitState
LIMIT_STATE_STR: _loadcombination_pb2_1.LimitState
LIMIT_STATE_UNSPECIFIED: _loadcombination_pb2_1.LimitState
LIMIT_STATE_VC1: _loadcombination_pb2_1.LimitState
LIMIT_STATE_VC2A: _loadcombination_pb2_1.LimitState
LIMIT_STATE_VC2B: _loadcombination_pb2_1.LimitState
LIMIT_STATE_VC3: _loadcombination_pb2_1.LimitState
LIMIT_STATE_VC4: _loadcombination_pb2_1.LimitState
OWNER_COMPANY: _utils_pb2_1_1_1_1.Owner
OWNER_OFFICE: _utils_pb2_1_1_1_1.Owner
OWNER_STRUSOFT: _utils_pb2_1_1_1_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1_1_1_1.Owner
OWNER_USER: _utils_pb2_1_1_1_1.Owner
SERVICEABILITY_TYPE_LONG: _loadcombination_pb2_1.ServiceabilityType
SERVICEABILITY_TYPE_SHORT: _loadcombination_pb2_1.ServiceabilityType
SERVICEABILITY_TYPE_UNSPECIFIED: _loadcombination_pb2_1.ServiceabilityType
TYPE_ACCIDENTAL: _loadcombination_pb2_1.Type
TYPE_ACCIDENT_LOAD: _loadcase_pb2_1.Type
TYPE_BODY_FORCE: _load_pb2.Type
TYPE_CHARACTERISTIC: _loadcombination_pb2_1.Type
TYPE_CONSTRUCTION_LOAD: _loadcase_pb2_1.Type
TYPE_FIRE: _loadcombination_pb2_1.Type
TYPE_FORCE: _load_pb2.Type
TYPE_FREQUENT: _loadcombination_pb2_1.Type
TYPE_ICE_LOAD: _loadcase_pb2_1.Type
TYPE_IMPOSED_LOAD: _loadcase_pb2_1.Type
TYPE_MOMENT: _load_pb2.Type
TYPE_PERMANENT_LOAD: _loadcase_pb2_1.Type
TYPE_PRESSURE: _load_pb2.Type
TYPE_QUASI_PERMANENT: _loadcombination_pb2_1.Type
TYPE_SEISMIC: _loadcombination_pb2_1.Type
TYPE_SEISMIC_LOAD: _loadcase_pb2_1.Type
TYPE_SELF_WEIGHT: _loadcase_pb2_1.Type
TYPE_SNOW_LOAD: _loadcase_pb2_1.Type
TYPE_SOIL_FORCE: _load_pb2.Type
TYPE_SOIL_LOAD: _loadcase_pb2_1.Type
TYPE_SOIL_SELF_WEIGHT: _loadcase_pb2_1.Type
TYPE_TEMPERATURE: _load_pb2.Type
TYPE_TEMPERATURE_LOAD: _loadcase_pb2_1.Type
TYPE_ULTIMATE: _loadcombination_pb2_1.Type
TYPE_UNSPECIFIED: _loadcombination_pb2_1.Type
TYPE_WIND_LOAD: _loadcase_pb2_1.Type
alternative: _loadgroup_pb2.LoadcaseRelationship
entire: _loadgroup_pb2.LoadcaseRelationship
simultaneous: _loadgroup_pb2.LoadcaseRelationship
unspecified: _loadgroup_pb2.LoadcaseRelationship

class Data(_message.Message):
    __slots__ = ["combinations", "loadcases", "loadgroups", "loads"]
    COMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    LOADCASES_FIELD_NUMBER: _ClassVar[int]
    LOADGROUPS_FIELD_NUMBER: _ClassVar[int]
    LOADS_FIELD_NUMBER: _ClassVar[int]
    combinations: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2_1.Data]
    loadcases: _containers.RepeatedCompositeFieldContainer[_loadcase_pb2_1.Data]
    loadgroups: _loadgroup_pb2.Groups
    loads: _containers.RepeatedCompositeFieldContainer[_load_pb2.Data]
    def __init__(self, loads: _Optional[_Iterable[_Union[_load_pb2.Data, _Mapping]]] = ..., loadcases: _Optional[_Iterable[_Union[_loadcase_pb2_1.Data, _Mapping]]] = ..., loadgroups: _Optional[_Union[_loadgroup_pb2.Groups, _Mapping]] = ..., combinations: _Optional[_Iterable[_Union[_loadcombination_pb2_1.Data, _Mapping]]] = ...) -> None: ...
