from Utils import utils_pb2 as _utils_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
ANALYSIS_TYPE_NORMAL: AnalysisTypeFoundation
ANALYSIS_TYPE_SOIL_PUNCHING: AnalysisTypeFoundation
ANALYSIS_TYPE_UNSPECIFIED: AnalysisTypeFoundation
CONTROL_TYPE_CONCRETE_ANCHORAGE_BTM: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_ANCHORAGE_TOP: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_AXIAL_FORCE: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_BIAXIAL_MOMENT: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_COMPRESSION_COVER_CHECK: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_COMPRESSION_STRESS: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_DEFLECTION: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_HOLLOWCORE_SPALLING: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_INITIAL_PRESTRESS: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_MOMENT_M2: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_NEGATIVE_CRACK_WIDTH: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_NEGATIVE_MOMENT_M1: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_POSITIVE_CRACK_WIDTH: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_POSITIVE_MOMENT_M1: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_PUNCHING_COLUMN: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_PUNCHING_PERIMETER: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_FORCE: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_FORCE_TOPPING: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_STIRRUPS: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_SHEAR_STIRRUPS_TOPPING: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_STRESS_AFTER_RELEASE: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TOPPING_JOINT: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_COMPRESSION_LONGITUDINAL: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_COMPRESSION_TRANSVERSE: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_LONGITUDINAL: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_TENSION_TRANSVERSE: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_TORSION_TRANSVERSE: ControlTypeConcrete
CONTROL_TYPE_CONCRETE_UNSPECIFIED: ControlTypeConcrete
CONTROL_TYPE_FOUNDATION_BEARING: CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_OVERALL: CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_OVERTURNING: CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_SETTLEMENT: CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_SLIDING: CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_UNREINFORCED: CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_UNSPECIFIED: CtrlTypeFoundation
CONTROL_TYPE_FOUNDATION_UPLIFT: CtrlTypeFoundation
CONTROL_TYPE_STEEL_DEFLECTION: ControlTypeSteel
CONTROL_TYPE_STEEL_FB1: ControlTypeSteel
CONTROL_TYPE_STEEL_FB2: ControlTypeSteel
CONTROL_TYPE_STEEL_FTB: ControlTypeSteel
CONTROL_TYPE_STEEL_IA1: ControlTypeSteel
CONTROL_TYPE_STEEL_IA2: ControlTypeSteel
CONTROL_TYPE_STEEL_IA2ND: ControlTypeSteel
CONTROL_TYPE_STEEL_LTB_BOTTOM: ControlTypeSteel
CONTROL_TYPE_STEEL_LTB_TOP: ControlTypeSteel
CONTROL_TYPE_STEEL_M1: ControlTypeSteel
CONTROL_TYPE_STEEL_M1_FIRE: ControlTypeSteel
CONTROL_TYPE_STEEL_M2: ControlTypeSteel
CONTROL_TYPE_STEEL_M2_FIRE: ControlTypeSteel
CONTROL_TYPE_STEEL_N: ControlTypeSteel
CONTROL_TYPE_STEEL_NORMAL: ControlTypeSteel
CONTROL_TYPE_STEEL_N_FIRE: ControlTypeSteel
CONTROL_TYPE_STEEL_OVERALL: ControlTypeSteel
CONTROL_TYPE_STEEL_PURE_NORMAL: ControlTypeSteel
CONTROL_TYPE_STEEL_SIGMA: ControlTypeSteel
CONTROL_TYPE_STEEL_T: ControlTypeSteel
CONTROL_TYPE_STEEL_TAU: ControlTypeSteel
CONTROL_TYPE_STEEL_UNSPECIFIED: ControlTypeSteel
CONTROL_TYPE_STEEL_V1: ControlTypeSteel
CONTROL_TYPE_STEEL_V2: ControlTypeSteel
CONTROL_TYPE_STEEL_WEB: ControlTypeSteel
CONTROL_TYPE_TIMBER_APEX: ControlTypeTimber
CONTROL_TYPE_TIMBER_COMPRESSION: ControlTypeTimber
CONTROL_TYPE_TIMBER_DEFLECTION: ControlTypeTimber
CONTROL_TYPE_TIMBER_FLEXURAL_BUCKLING1: ControlTypeTimber
CONTROL_TYPE_TIMBER_FLEXURAL_BUCKLING2: ControlTypeTimber
CONTROL_TYPE_TIMBER_OVERALL: ControlTypeTimber
CONTROL_TYPE_TIMBER_SHEAR: ControlTypeTimber
CONTROL_TYPE_TIMBER_TENSION: ControlTypeTimber
CONTROL_TYPE_TIMBER_TORSIONAL_BUCKLING: ControlTypeTimber
CONTROL_TYPE_TIMBER_UNSPECIFIED: ControlTypeTimber
DESCRIPTOR: _descriptor.FileDescriptor
DESIGN_TYPE_ALLOWEDSOILPRESSURE: DesignTypeFoundation
DESIGN_TYPE_DRAINED: DesignTypeFoundation
DESIGN_TYPE_DRAINED_PUNCHNING_ALT: DesignTypeFoundation
DESIGN_TYPE_DRAINED_PUNCHNING_B6: DesignTypeFoundation
DESIGN_TYPE_ROCK: DesignTypeFoundation
DESIGN_TYPE_UNDRAINED: DesignTypeFoundation
DESIGN_TYPE_UNDRAINED_PUNCHING: DesignTypeFoundation
DESIGN_TYPE_UNSPECIFIED: DesignTypeFoundation
ECCENTRICITY_TYPE_HIGH: EccentricityTypeFoundation
ECCENTRICITY_TYPE_NORMAL: EccentricityTypeFoundation
ECCENTRICITY_TYPE_UNSPECIFIED: EccentricityTypeFoundation
OWNER_COMPANY: _utils_pb2.Owner
OWNER_OFFICE: _utils_pb2.Owner
OWNER_STRUSOFT: _utils_pb2.Owner
OWNER_UNSPECIFIED: _utils_pb2.Owner
OWNER_USER: _utils_pb2.Owner

class ControlData(_message.Message):
    __slots__ = ["concrete_type", "foundation_type", "lc_name", "mathml", "mathml_short", "steel_type", "timber_type", "title", "utilization", "values", "x"]
    class ValuesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    CONCRETE_TYPE_FIELD_NUMBER: _ClassVar[int]
    FOUNDATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    LC_NAME_FIELD_NUMBER: _ClassVar[int]
    MATHML_FIELD_NUMBER: _ClassVar[int]
    MATHML_SHORT_FIELD_NUMBER: _ClassVar[int]
    STEEL_TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMBER_TYPE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    concrete_type: ControlTypeConcrete
    foundation_type: ControlTypeFoundation
    lc_name: str
    mathml: str
    mathml_short: str
    steel_type: ControlTypeSteel
    timber_type: ControlTypeTimber
    title: str
    utilization: float
    values: _containers.ScalarMap[str, float]
    x: float
    def __init__(self, title: _Optional[str] = ..., lc_name: _Optional[str] = ..., x: _Optional[float] = ..., utilization: _Optional[float] = ..., mathml: _Optional[str] = ..., mathml_short: _Optional[str] = ..., values: _Optional[_Mapping[str, float]] = ..., concrete_type: _Optional[_Union[ControlTypeConcrete, str]] = ..., steel_type: _Optional[_Union[ControlTypeSteel, str]] = ..., timber_type: _Optional[_Union[ControlTypeTimber, str]] = ..., foundation_type: _Optional[_Union[ControlTypeFoundation, _Mapping]] = ...) -> None: ...

class ControlTypeFoundation(_message.Message):
    __slots__ = ["analysis_type", "design_type", "eccentricity_type", "type"]
    ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    DESIGN_TYPE_FIELD_NUMBER: _ClassVar[int]
    ECCENTRICITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    analysis_type: AnalysisTypeFoundation
    design_type: DesignTypeFoundation
    eccentricity_type: EccentricityTypeFoundation
    type: CtrlTypeFoundation
    def __init__(self, type: _Optional[_Union[CtrlTypeFoundation, str]] = ..., analysis_type: _Optional[_Union[AnalysisTypeFoundation, str]] = ..., design_type: _Optional[_Union[DesignTypeFoundation, str]] = ..., eccentricity_type: _Optional[_Union[EccentricityTypeFoundation, str]] = ...) -> None: ...

class ControlTypeConcrete(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ControlTypeSteel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ControlTypeTimber(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class CtrlTypeFoundation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class AnalysisTypeFoundation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DesignTypeFoundation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class EccentricityTypeFoundation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
