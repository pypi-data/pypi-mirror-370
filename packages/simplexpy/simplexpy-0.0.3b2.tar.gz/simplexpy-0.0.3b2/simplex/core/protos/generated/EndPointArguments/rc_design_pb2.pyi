import project_pb2 as _project_pb2
import input_pb2 as _input_pb2
import output_pb2 as _output_pb2
from Utils import log_pb2 as _log_pb2
from Utils import log_pb2 as _log_pb2_1
from Result import result_pb2 as _result_pb2
from Utils import utils_pb2 as _utils_pb2
from Result import concrete_pb2 as _concrete_pb2
from Result import foundation_pb2 as _foundation_pb2
from Result import pile_pb2 as _pile_pb2
from Result import retainingwall_pb2 as _retainingwall_pb2
from Result import steel_pb2 as _steel_pb2
from Result import timber_pb2 as _timber_pb2
from Result import control_pb2 as _control_pb2
from EndPointArguments import common_api_functions_pb2 as _common_api_functions_pb2
from Utils import log_pb2 as _log_pb2_1_1
from Result import result_pb2 as _result_pb2_1
import sections_pb2 as _sections_pb2
from FireProtection import steel_pb2 as _steel_pb2_1
from FireProtection import timber_pb2 as _timber_pb2_1
from Design import concrete_pb2 as _concrete_pb2_1
from Material import reinforcement_pb2 as _reinforcement_pb2
from Material import concrete_pb2 as _concrete_pb2_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from project_pb2 import Data
from Utils.log_pb2 import LogValue
from Utils.log_pb2 import LogEntry
from Utils.log_pb2 import Log
from Utils.log_pb2 import LogType
from Result.result_pb2 import ForceData
from Result.result_pb2 import DisplacementData
from Result.result_pb2 import StressData
from Result.result_pb2 import TemperatureData
from Result.result_pb2 import Data
from Result.result_pb2 import PositionResult
from Result.result_pb2 import ElementResult
from Result.result_pb2 import Element
from Result.result_pb2 import Node
from Result.result_pb2 import Force
from Result.result_pb2 import Displacement
from Result.result_pb2 import Stress
from EndPointArguments.common_api_functions_pb2 import HealthCheckDuration
from EndPointArguments.common_api_functions_pb2 import HealthCheckData
from EndPointArguments.common_api_functions_pb2 import HealthCheckEntry
from EndPointArguments.common_api_functions_pb2 import HealthCheckResponse
from EndPointArguments.common_api_functions_pb2 import AdminReport
from EndPointArguments.common_api_functions_pb2 import ProtectingMaterial
from EndPointArguments.common_api_functions_pb2 import AutoDesignTimberFire
from EndPointArguments.common_api_functions_pb2 import AutoDesignSteelFire
from EndPointArguments.common_api_functions_pb2 import AutoDesignValue
from EndPointArguments.common_api_functions_pb2 import AutoDesignSteel
from EndPointArguments.common_api_functions_pb2 import AutoDesignTimber
from EndPointArguments.common_api_functions_pb2 import AutoDesignConcrete
from EndPointArguments.common_api_functions_pb2 import AutoDesignBeam
from EndPointArguments.common_api_functions_pb2 import AutoDesignColumn
from EndPointArguments.common_api_functions_pb2 import AutoDesignFoundation
from EndPointArguments.common_api_functions_pb2 import AutoDesignSettings
from EndPointArguments.common_api_functions_pb2 import AutoDesign
from EndPointArguments.common_api_functions_pb2 import CodeCheckInput
from EndPointArguments.common_api_functions_pb2 import CodeCheckOutput
from EndPointArguments.common_api_functions_pb2 import HealthCheckStatus
DESCRIPTOR: _descriptor.FileDescriptor
DISPLACEMENT_RU: _result_pb2_1.Displacement
DISPLACEMENT_RV: _result_pb2_1.Displacement
DISPLACEMENT_RW: _result_pb2_1.Displacement
DISPLACEMENT_RX: _result_pb2_1.Displacement
DISPLACEMENT_RY: _result_pb2_1.Displacement
DISPLACEMENT_RZ: _result_pb2_1.Displacement
DISPLACEMENT_U: _result_pb2_1.Displacement
DISPLACEMENT_UNSPECIFIED: _result_pb2_1.Displacement
DISPLACEMENT_V: _result_pb2_1.Displacement
DISPLACEMENT_W: _result_pb2_1.Displacement
DISPLACEMENT_X: _result_pb2_1.Displacement
DISPLACEMENT_Y: _result_pb2_1.Displacement
DISPLACEMENT_Z: _result_pb2_1.Displacement
FORCE_M1: _result_pb2_1.Force
FORCE_M2: _result_pb2_1.Force
FORCE_MX: _result_pb2_1.Force
FORCE_MY: _result_pb2_1.Force
FORCE_MZ: _result_pb2_1.Force
FORCE_N: _result_pb2_1.Force
FORCE_RX: _result_pb2_1.Force
FORCE_RY: _result_pb2_1.Force
FORCE_RZ: _result_pb2_1.Force
FORCE_T: _result_pb2_1.Force
FORCE_UNSPECIFIED: _result_pb2_1.Force
FORCE_V1: _result_pb2_1.Force
FORCE_V2: _result_pb2_1.Force
HEALTH_CHECK_STATUS_DEGRADED: _common_api_functions_pb2.HealthCheckStatus
HEALTH_CHECK_STATUS_HEALTHY: _common_api_functions_pb2.HealthCheckStatus
HEALTH_CHECK_STATUS_UNHEALTHY: _common_api_functions_pb2.HealthCheckStatus
HEALTH_CHECK_STATUS_UNSPECIFIED: _common_api_functions_pb2.HealthCheckStatus
LOG_TYPE_ERROR: _log_pb2_1_1.LogType
LOG_TYPE_INFORMATION: _log_pb2_1_1.LogType
LOG_TYPE_UNSPECIFIED: _log_pb2_1_1.LogType
LOG_TYPE_WARNING: _log_pb2_1_1.LogType
STRESS_MISES: _result_pb2_1.Stress
STRESS_S11: _result_pb2_1.Stress
STRESS_S12: _result_pb2_1.Stress
STRESS_S22: _result_pb2_1.Stress
STRESS_SP1: _result_pb2_1.Stress
STRESS_SP2: _result_pb2_1.Stress
STRESS_UNSPECIFIED: _result_pb2_1.Stress

class CoverSpaceInput(_message.Message):
    __slots__ = ["bar_diameters", "input", "stirrup_diameters"]
    BAR_DIAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    STIRRUP_DIAMETERS_FIELD_NUMBER: _ClassVar[int]
    bar_diameters: _containers.RepeatedScalarFieldContainer[float]
    input: _input_pb2.Data
    stirrup_diameters: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, input: _Optional[_Union[_input_pb2.Data, _Mapping]] = ..., bar_diameters: _Optional[_Iterable[float]] = ..., stirrup_diameters: _Optional[_Iterable[float]] = ...) -> None: ...

class CoverSpaceOutput(_message.Message):
    __slots__ = ["log", "max_bar_spacing_in_layer", "min_bar_distances", "min_stirrup_distances"]
    class RebarCoverSpace(_message.Message):
        __slots__ = ["cover", "diameter", "space_between_layer", "space_in_layer"]
        COVER_FIELD_NUMBER: _ClassVar[int]
        DIAMETER_FIELD_NUMBER: _ClassVar[int]
        SPACE_BETWEEN_LAYER_FIELD_NUMBER: _ClassVar[int]
        SPACE_IN_LAYER_FIELD_NUMBER: _ClassVar[int]
        cover: float
        diameter: float
        space_between_layer: float
        space_in_layer: float
        def __init__(self, diameter: _Optional[float] = ..., cover: _Optional[float] = ..., space_in_layer: _Optional[float] = ..., space_between_layer: _Optional[float] = ...) -> None: ...
    class StirrupCoverSpace(_message.Message):
        __slots__ = ["cover_end", "diameter", "spacing"]
        COVER_END_FIELD_NUMBER: _ClassVar[int]
        DIAMETER_FIELD_NUMBER: _ClassVar[int]
        SPACING_FIELD_NUMBER: _ClassVar[int]
        cover_end: float
        diameter: float
        spacing: float
        def __init__(self, diameter: _Optional[float] = ..., cover_end: _Optional[float] = ..., spacing: _Optional[float] = ...) -> None: ...
    LOG_FIELD_NUMBER: _ClassVar[int]
    MAX_BAR_SPACING_IN_LAYER_FIELD_NUMBER: _ClassVar[int]
    MIN_BAR_DISTANCES_FIELD_NUMBER: _ClassVar[int]
    MIN_STIRRUP_DISTANCES_FIELD_NUMBER: _ClassVar[int]
    log: _log_pb2_1_1.Log
    max_bar_spacing_in_layer: float
    min_bar_distances: _containers.RepeatedCompositeFieldContainer[CoverSpaceOutput.RebarCoverSpace]
    min_stirrup_distances: _containers.RepeatedCompositeFieldContainer[CoverSpaceOutput.StirrupCoverSpace]
    def __init__(self, min_bar_distances: _Optional[_Iterable[_Union[CoverSpaceOutput.RebarCoverSpace, _Mapping]]] = ..., min_stirrup_distances: _Optional[_Iterable[_Union[CoverSpaceOutput.StirrupCoverSpace, _Mapping]]] = ..., max_bar_spacing_in_layer: _Optional[float] = ..., log: _Optional[_Union[_log_pb2_1_1.Log, _Mapping]] = ...) -> None: ...

class RcOutput(_message.Message):
    __slots__ = ["geo_elems", "log", "mesh_update"]
    class GeoElement(_message.Message):
        __slots__ = ["fixForces", "guid", "sub_elem_props"]
        FIXFORCES_FIELD_NUMBER: _ClassVar[int]
        GUID_FIELD_NUMBER: _ClassVar[int]
        SUB_ELEM_PROPS_FIELD_NUMBER: _ClassVar[int]
        fixForces: _containers.RepeatedScalarFieldContainer[float]
        guid: str
        sub_elem_props: _containers.RepeatedCompositeFieldContainer[RcOutput.SubElemProp]
        def __init__(self, guid: _Optional[str] = ..., sub_elem_props: _Optional[_Iterable[_Union[RcOutput.SubElemProp, _Mapping]]] = ..., fixForces: _Optional[_Iterable[float]] = ...) -> None: ...
    class SubElemProp(_message.Message):
        __slots__ = ["a_eff", "cracked", "e", "i12_eff", "i1_eff", "i2_eff", "ind", "j_eff", "side", "x"]
        A_EFF_FIELD_NUMBER: _ClassVar[int]
        CRACKED_FIELD_NUMBER: _ClassVar[int]
        E_FIELD_NUMBER: _ClassVar[int]
        I12_EFF_FIELD_NUMBER: _ClassVar[int]
        I1_EFF_FIELD_NUMBER: _ClassVar[int]
        I2_EFF_FIELD_NUMBER: _ClassVar[int]
        IND_FIELD_NUMBER: _ClassVar[int]
        J_EFF_FIELD_NUMBER: _ClassVar[int]
        SIDE_FIELD_NUMBER: _ClassVar[int]
        X_FIELD_NUMBER: _ClassVar[int]
        a_eff: float
        cracked: bool
        e: float
        i12_eff: float
        i1_eff: float
        i2_eff: float
        ind: int
        j_eff: float
        side: int
        x: float
        def __init__(self, ind: _Optional[int] = ..., x: _Optional[float] = ..., a_eff: _Optional[float] = ..., i1_eff: _Optional[float] = ..., i2_eff: _Optional[float] = ..., i12_eff: _Optional[float] = ..., j_eff: _Optional[float] = ..., cracked: bool = ..., side: _Optional[int] = ..., e: _Optional[float] = ...) -> None: ...
    GEO_ELEMS_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    MESH_UPDATE_FIELD_NUMBER: _ClassVar[int]
    geo_elems: _containers.RepeatedCompositeFieldContainer[RcOutput.GeoElement]
    log: _log_pb2_1_1.Log
    mesh_update: bool
    def __init__(self, geo_elems: _Optional[_Iterable[_Union[RcOutput.GeoElement, _Mapping]]] = ..., mesh_update: bool = ..., log: _Optional[_Union[_log_pb2_1_1.Log, _Mapping]] = ...) -> None: ...
