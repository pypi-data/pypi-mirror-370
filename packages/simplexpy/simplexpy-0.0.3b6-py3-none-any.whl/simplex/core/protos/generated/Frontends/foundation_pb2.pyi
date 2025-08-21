import project_pb2 as _project_pb2
import input_pb2 as _input_pb2
import output_pb2 as _output_pb2
from Utils import log_pb2 as _log_pb2
from Utils import utils_pb2 as _utils_pb2
from EndPointArguments import common_api_functions_pb2 as _common_api_functions_pb2
from Utils import log_pb2 as _log_pb2_1
from Result import result_pb2 as _result_pb2
import sections_pb2 as _sections_pb2
from FireProtection import steel_pb2 as _steel_pb2
from FireProtection import timber_pb2 as _timber_pb2
from Design import concrete_pb2 as _concrete_pb2
from Material import reinforcement_pb2 as _reinforcement_pb2
from Material import concrete_pb2 as _concrete_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from project_pb2 import Data
from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
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
HEALTH_CHECK_STATUS_DEGRADED: _common_api_functions_pb2.HealthCheckStatus
HEALTH_CHECK_STATUS_HEALTHY: _common_api_functions_pb2.HealthCheckStatus
HEALTH_CHECK_STATUS_UNHEALTHY: _common_api_functions_pb2.HealthCheckStatus
HEALTH_CHECK_STATUS_UNSPECIFIED: _common_api_functions_pb2.HealthCheckStatus
LANGUAGE_ENGLISH: Language
LANGUAGE_SWEDISH: Language
LANGUAGE_UNSPECIFIED: Language
OWNER_COMPANY: _utils_pb2.Owner
OWNER_OFFICE: _utils_pb2.Owner
OWNER_STRUSOFT: _utils_pb2.Owner
OWNER_UNSPECIFIED: _utils_pb2.Owner
OWNER_USER: _utils_pb2.Owner
PRINT_EXTENT_MAXIMAL: PrintExtent
PRINT_EXTENT_MINIMAL: PrintExtent
PRINT_EXTENT_NORMAL: PrintExtent
PRINT_EXTENT_UNSPECIFIED: PrintExtent
PRINT_MODULE_ANALYSIS: PrintModule
PRINT_MODULE_CONCRETE: PrintModule
PRINT_MODULE_INPUT: PrintModule
PRINT_MODULE_STEEL: PrintModule
PRINT_MODULE_SUMMARY: PrintModule
PRINT_MODULE_TIMBER: PrintModule
PRINT_MODULE_UNSPECIFIED: PrintModule

class ColorSettings(_message.Message):
    __slots__ = ["background", "graph_negative", "graph_positive", "grid_lines_major", "grid_lines_minor"]
    BACKGROUND_FIELD_NUMBER: _ClassVar[int]
    GRAPH_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    GRAPH_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    GRID_LINES_MAJOR_FIELD_NUMBER: _ClassVar[int]
    GRID_LINES_MINOR_FIELD_NUMBER: _ClassVar[int]
    background: str
    graph_negative: str
    graph_positive: str
    grid_lines_major: str
    grid_lines_minor: str
    def __init__(self, background: _Optional[str] = ..., grid_lines_major: _Optional[str] = ..., grid_lines_minor: _Optional[str] = ..., graph_positive: _Optional[str] = ..., graph_negative: _Optional[str] = ...) -> None: ...

class EndPointParamCache(_message.Message):
    __slots__ = ["auto_design"]
    AUTO_DESIGN_FIELD_NUMBER: _ClassVar[int]
    auto_design: _common_api_functions_pb2.AutoDesign
    def __init__(self, auto_design: _Optional[_Union[_common_api_functions_pb2.AutoDesign, _Mapping]] = ...) -> None: ...

class FrontendData(_message.Message):
    __slots__ = ["endpoint_cache", "print_settings"]
    ENDPOINT_CACHE_FIELD_NUMBER: _ClassVar[int]
    PRINT_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    endpoint_cache: EndPointParamCache
    print_settings: _containers.RepeatedCompositeFieldContainer[PrintSetting]
    def __init__(self, print_settings: _Optional[_Iterable[_Union[PrintSetting, _Mapping]]] = ..., endpoint_cache: _Optional[_Union[EndPointParamCache, _Mapping]] = ...) -> None: ...

class GeneralSettings(_message.Message):
    __slots__ = ["colors", "result", "unit", "viewport"]
    COLORS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    VIEWPORT_FIELD_NUMBER: _ClassVar[int]
    colors: ColorSettings
    result: ResultSettings
    unit: UnitSettings
    viewport: ViewPortSettings
    def __init__(self, viewport: _Optional[_Union[ViewPortSettings, _Mapping]] = ..., unit: _Optional[_Union[UnitSettings, _Mapping]] = ..., colors: _Optional[_Union[ColorSettings, _Mapping]] = ..., result: _Optional[_Union[ResultSettings, _Mapping]] = ...) -> None: ...

class PrintSetting(_message.Message):
    __slots__ = ["extent", "module"]
    EXTENT_FIELD_NUMBER: _ClassVar[int]
    MODULE_FIELD_NUMBER: _ClassVar[int]
    extent: PrintExtent
    module: PrintModule
    def __init__(self, module: _Optional[_Union[PrintModule, str]] = ..., extent: _Optional[_Union[PrintExtent, str]] = ...) -> None: ...

class Project(_message.Message):
    __slots__ = ["data", "meta", "settings"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    data: _project_pb2.Data
    meta: ProjectMeta
    settings: FrontendData
    def __init__(self, meta: _Optional[_Union[ProjectMeta, _Mapping]] = ..., data: _Optional[_Union[_project_pb2.Data, _Mapping]] = ..., settings: _Optional[_Union[FrontendData, _Mapping]] = ...) -> None: ...

class ProjectMeta(_message.Message):
    __slots__ = ["app_version", "author", "build_number", "comments", "company", "created", "description", "e_tag", "guid", "keywords", "last_modified", "location", "modified_by", "name", "project", "revision", "signature"]
    APP_VERSION_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    BUILD_NUMBER_FIELD_NUMBER: _ClassVar[int]
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    COMPANY_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    E_TAG_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    KEYWORDS_FIELD_NUMBER: _ClassVar[int]
    LAST_MODIFIED_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_BY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    app_version: _utils_pb2.SemVer
    author: str
    build_number: str
    comments: str
    company: str
    created: str
    description: str
    e_tag: str
    guid: str
    keywords: _containers.RepeatedScalarFieldContainer[str]
    last_modified: str
    location: str
    modified_by: str
    name: str
    project: str
    revision: int
    signature: str
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., e_tag: _Optional[str] = ..., revision: _Optional[int] = ..., description: _Optional[str] = ..., author: _Optional[str] = ..., company: _Optional[str] = ..., created: _Optional[str] = ..., signature: _Optional[str] = ..., comments: _Optional[str] = ..., keywords: _Optional[_Iterable[str]] = ..., app_version: _Optional[_Union[_utils_pb2.SemVer, _Mapping]] = ..., build_number: _Optional[str] = ..., last_modified: _Optional[str] = ..., modified_by: _Optional[str] = ..., location: _Optional[str] = ..., project: _Optional[str] = ...) -> None: ...

class ResultSettings(_message.Message):
    __slots__ = ["diagram_scale", "show_numerical_values_in_graph", "show_only_min_max"]
    DIAGRAM_SCALE_FIELD_NUMBER: _ClassVar[int]
    SHOW_NUMERICAL_VALUES_IN_GRAPH_FIELD_NUMBER: _ClassVar[int]
    SHOW_ONLY_MIN_MAX_FIELD_NUMBER: _ClassVar[int]
    diagram_scale: float
    show_numerical_values_in_graph: bool
    show_only_min_max: bool
    def __init__(self, diagram_scale: _Optional[float] = ..., show_numerical_values_in_graph: bool = ..., show_only_min_max: bool = ...) -> None: ...

class UnitSettings(_message.Message):
    __slots__ = ["force", "length"]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    force: str
    length: str
    def __init__(self, length: _Optional[str] = ..., force: _Optional[str] = ...) -> None: ...

class ViewPortSettings(_message.Message):
    __slots__ = ["analyse_on_save", "center_line", "center_line_size", "graph_number_decimal", "graph_scale_factor", "grid_square_size", "invert_zoom_mouse", "language", "major_line_each", "major_line_width", "minor_line_width", "proportional_loads", "show_foundation_id", "show_foundation_representation", "show_lcs", "show_material_id", "show_section", "show_section_id", "snap_sense", "snap_to_grid", "support_symbols"]
    ANALYSE_ON_SAVE_FIELD_NUMBER: _ClassVar[int]
    CENTER_LINE_FIELD_NUMBER: _ClassVar[int]
    CENTER_LINE_SIZE_FIELD_NUMBER: _ClassVar[int]
    GRAPH_NUMBER_DECIMAL_FIELD_NUMBER: _ClassVar[int]
    GRAPH_SCALE_FACTOR_FIELD_NUMBER: _ClassVar[int]
    GRID_SQUARE_SIZE_FIELD_NUMBER: _ClassVar[int]
    INVERT_ZOOM_MOUSE_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    MAJOR_LINE_EACH_FIELD_NUMBER: _ClassVar[int]
    MAJOR_LINE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    MINOR_LINE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    PROPORTIONAL_LOADS_FIELD_NUMBER: _ClassVar[int]
    SHOW_FOUNDATION_ID_FIELD_NUMBER: _ClassVar[int]
    SHOW_FOUNDATION_REPRESENTATION_FIELD_NUMBER: _ClassVar[int]
    SHOW_LCS_FIELD_NUMBER: _ClassVar[int]
    SHOW_MATERIAL_ID_FIELD_NUMBER: _ClassVar[int]
    SHOW_SECTION_FIELD_NUMBER: _ClassVar[int]
    SHOW_SECTION_ID_FIELD_NUMBER: _ClassVar[int]
    SNAP_SENSE_FIELD_NUMBER: _ClassVar[int]
    SNAP_TO_GRID_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    analyse_on_save: bool
    center_line: bool
    center_line_size: float
    graph_number_decimal: int
    graph_scale_factor: float
    grid_square_size: int
    invert_zoom_mouse: bool
    language: Language
    major_line_each: int
    major_line_width: float
    minor_line_width: float
    proportional_loads: bool
    show_foundation_id: bool
    show_foundation_representation: bool
    show_lcs: bool
    show_material_id: bool
    show_section: bool
    show_section_id: bool
    snap_sense: int
    snap_to_grid: bool
    support_symbols: bool
    def __init__(self, grid_square_size: _Optional[int] = ..., snap_to_grid: bool = ..., center_line: bool = ..., center_line_size: _Optional[float] = ..., analyse_on_save: bool = ..., snap_sense: _Optional[int] = ..., graph_scale_factor: _Optional[float] = ..., graph_number_decimal: _Optional[int] = ..., invert_zoom_mouse: bool = ..., major_line_width: _Optional[float] = ..., minor_line_width: _Optional[float] = ..., major_line_each: _Optional[int] = ..., show_lcs: bool = ..., show_section_id: bool = ..., show_material_id: bool = ..., show_foundation_id: bool = ..., show_section: bool = ..., support_symbols: bool = ..., show_foundation_representation: bool = ..., proportional_loads: bool = ..., language: _Optional[_Union[Language, str]] = ...) -> None: ...

class PrintModule(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class PrintExtent(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Language(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
