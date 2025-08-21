from Loading import loadcombination_pb2 as _loadcombination_pb2
from Utils import utils_pb2 as _utils_pb2
from Design import soil_pb2 as _soil_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

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
FORMULA_812: Formula
FORMULA_813: Formula
FORMULA_814: Formula
FORMULA_UNSPECIFIED: Formula
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
SERVICEABILITY_TYPE_LONG: _loadcombination_pb2.ServiceabilityType
SERVICEABILITY_TYPE_SHORT: _loadcombination_pb2.ServiceabilityType
SERVICEABILITY_TYPE_UNSPECIFIED: _loadcombination_pb2.ServiceabilityType
TYPE_ACCIDENTAL: _loadcombination_pb2.Type
TYPE_CHARACTERISTIC: _loadcombination_pb2.Type
TYPE_FIRE: _loadcombination_pb2.Type
TYPE_FREQUENT: _loadcombination_pb2.Type
TYPE_QUASI_PERMANENT: _loadcombination_pb2.Type
TYPE_SEISMIC: _loadcombination_pb2.Type
TYPE_ULTIMATE: _loadcombination_pb2.Type
TYPE_UNSPECIFIED: _loadcombination_pb2.Type

class ElementDesignSettings(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GammaLoad(_message.Message):
    __slots__ = ["gamma_accident", "gamma_gj", "gamma_q1", "gamma_qi"]
    GAMMA_ACCIDENT_FIELD_NUMBER: _ClassVar[int]
    GAMMA_GJ_FIELD_NUMBER: _ClassVar[int]
    GAMMA_Q1_FIELD_NUMBER: _ClassVar[int]
    GAMMA_QI_FIELD_NUMBER: _ClassVar[int]
    gamma_accident: GammaSupInf
    gamma_gj: GammaSupInf
    gamma_q1: GammaSupInf
    gamma_qi: GammaSupInf
    def __init__(self, gamma_gj: _Optional[_Union[GammaSupInf, _Mapping]] = ..., gamma_q1: _Optional[_Union[GammaSupInf, _Mapping]] = ..., gamma_qi: _Optional[_Union[GammaSupInf, _Mapping]] = ..., gamma_accident: _Optional[_Union[GammaSupInf, _Mapping]] = ...) -> None: ...

class GammaSet(_message.Message):
    __slots__ = ["accidental", "fire", "seismic", "serviceability_fq", "serviceability_k", "serviceability_qp", "set_812", "set_813a", "set_813b", "set_814a", "set_814b", "set_VC3", "set_VC4", "set_a", "set_b610", "set_b610a", "set_b610b", "set_c610", "set_c6103", "set_c6104", "set_c6105"]
    ACCIDENTAL_FIELD_NUMBER: _ClassVar[int]
    FIRE_FIELD_NUMBER: _ClassVar[int]
    SEISMIC_FIELD_NUMBER: _ClassVar[int]
    SERVICEABILITY_FQ_FIELD_NUMBER: _ClassVar[int]
    SERVICEABILITY_K_FIELD_NUMBER: _ClassVar[int]
    SERVICEABILITY_QP_FIELD_NUMBER: _ClassVar[int]
    SET_812_FIELD_NUMBER: _ClassVar[int]
    SET_813A_FIELD_NUMBER: _ClassVar[int]
    SET_813B_FIELD_NUMBER: _ClassVar[int]
    SET_814A_FIELD_NUMBER: _ClassVar[int]
    SET_814B_FIELD_NUMBER: _ClassVar[int]
    SET_A_FIELD_NUMBER: _ClassVar[int]
    SET_B610A_FIELD_NUMBER: _ClassVar[int]
    SET_B610B_FIELD_NUMBER: _ClassVar[int]
    SET_B610_FIELD_NUMBER: _ClassVar[int]
    SET_C6103_FIELD_NUMBER: _ClassVar[int]
    SET_C6104_FIELD_NUMBER: _ClassVar[int]
    SET_C6105_FIELD_NUMBER: _ClassVar[int]
    SET_C610_FIELD_NUMBER: _ClassVar[int]
    SET_VC3_FIELD_NUMBER: _ClassVar[int]
    SET_VC4_FIELD_NUMBER: _ClassVar[int]
    accidental: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    fire: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    seismic: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    serviceability_fq: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    serviceability_k: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    serviceability_qp: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    set_812: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    set_813a: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    set_813b: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    set_814a: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    set_814b: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    set_VC3: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    set_VC4: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    set_a: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    set_b610: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    set_b610a: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    set_b610b: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    set_c610: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    set_c6103: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    set_c6104: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    set_c6105: _containers.RepeatedCompositeFieldContainer[_loadcombination_pb2.Coefficient]
    def __init__(self, serviceability_k: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., serviceability_fq: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., serviceability_qp: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., set_a: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., set_b610: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., set_b610a: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., set_b610b: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., set_c610: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., set_c6103: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., set_c6104: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., set_c6105: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., accidental: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., fire: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., seismic: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., set_812: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., set_813a: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., set_813b: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., set_814a: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., set_814b: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., set_VC3: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ..., set_VC4: _Optional[_Iterable[_Union[_loadcombination_pb2.Coefficient, _Mapping]]] = ...) -> None: ...

class GammaSupInf(_message.Message):
    __slots__ = ["gamma_inf", "gamma_sup"]
    GAMMA_INF_FIELD_NUMBER: _ClassVar[int]
    GAMMA_SUP_FIELD_NUMBER: _ClassVar[int]
    gamma_inf: GammaSet
    gamma_sup: GammaSet
    def __init__(self, gamma_sup: _Optional[_Union[GammaSet, _Mapping]] = ..., gamma_inf: _Optional[_Union[GammaSet, _Mapping]] = ...) -> None: ...

class GeneralDesignSettings(_message.Message):
    __slots__ = ["gamma_load", "use610ab", "use_psi1"]
    GAMMA_LOAD_FIELD_NUMBER: _ClassVar[int]
    USE610AB_FIELD_NUMBER: _ClassVar[int]
    USE_PSI1_FIELD_NUMBER: _ClassVar[int]
    gamma_load: GammaLoad
    use610ab: bool
    use_psi1: bool
    def __init__(self, use610ab: bool = ..., use_psi1: bool = ..., gamma_load: _Optional[_Union[GammaLoad, _Mapping]] = ...) -> None: ...

class Formula(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
