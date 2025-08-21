import project_pb2 as _project_pb2
import input_pb2 as _input_pb2
import output_pb2 as _output_pb2
from Utils import log_pb2 as _log_pb2
from Utils import utils_pb2 as _utils_pb2
from EndPointArguments import eurocode_pb2 as _eurocode_pb2
from Design import concrete_pb2 as _concrete_pb2
from Loading import loadcombination_pb2 as _loadcombination_pb2
from Utils import eurocode_pb2 as _eurocode_pb2_1
from Utils import log_pb2 as _log_pb2_1
import element_pb2 as _element_pb2
import structure_pb2 as _structure_pb2
import input_pb2 as _input_pb2_1
from Loading import loadgroup_pb2 as _loadgroup_pb2
from EndPointArguments import fem_design_api_pb2 as _fem_design_api_pb2
from EndPointArguments import common_api_functions_pb2 as _common_api_functions_pb2
from EndPointArguments import common_api_functions_pb2 as _common_api_functions_pb2_1
from Utils import log_pb2 as _log_pb2_1_1
from Result import result_pb2 as _result_pb2
import sections_pb2 as _sections_pb2
from FireProtection import steel_pb2 as _steel_pb2
from FireProtection import timber_pb2 as _timber_pb2
from Design import concrete_pb2 as _concrete_pb2_1
from Material import reinforcement_pb2 as _reinforcement_pb2
from Material import concrete_pb2 as _concrete_pb2_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from project_pb2 import Data
from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
from EndPointArguments.eurocode_pb2 import EN1990Gamma0ArgsIn
from EndPointArguments.eurocode_pb2 import EN1990Gamma0ArgsOut
from EndPointArguments.eurocode_pb2 import LoadCombGenSettings
from EndPointArguments.eurocode_pb2 import Simple
from EndPointArguments.eurocode_pb2 import Advanced
from EndPointArguments.eurocode_pb2 import Geotechnical
from EndPointArguments.eurocode_pb2 import UpdateFactorsArgsIn
from EndPointArguments.eurocode_pb2 import UpdateFactorsArgsOut
from EndPointArguments.eurocode_pb2 import LoadCombGenArgsIn
from EndPointArguments.eurocode_pb2 import LoadCombGenArgsOut
from EndPointArguments.eurocode_pb2 import EN1992GammaArgsIn
from EndPointArguments.eurocode_pb2 import EN1992GammaArgsOut
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
HEALTH_CHECK_STATUS_DEGRADED: _common_api_functions_pb2_1.HealthCheckStatus
HEALTH_CHECK_STATUS_HEALTHY: _common_api_functions_pb2_1.HealthCheckStatus
HEALTH_CHECK_STATUS_UNHEALTHY: _common_api_functions_pb2_1.HealthCheckStatus
HEALTH_CHECK_STATUS_UNSPECIFIED: _common_api_functions_pb2_1.HealthCheckStatus
LANGUAGE_DANISH: Language
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
PRINT_MODULE_TOC: PrintModule
PRINT_MODULE_UNSPECIFIED: PrintModule

class EndPointParamCache(_message.Message):
    __slots__ = ["auto_design", "load_comb_gen_settings"]
    AUTO_DESIGN_FIELD_NUMBER: _ClassVar[int]
    LOAD_COMB_GEN_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    auto_design: _common_api_functions_pb2_1.AutoDesign
    load_comb_gen_settings: _eurocode_pb2.LoadCombGenSettings
    def __init__(self, load_comb_gen_settings: _Optional[_Union[_eurocode_pb2.LoadCombGenSettings, _Mapping]] = ..., auto_design: _Optional[_Union[_common_api_functions_pb2_1.AutoDesign, _Mapping]] = ...) -> None: ...

class FrontendData(_message.Message):
    __slots__ = ["endpoint_cache", "print_settings", "visuals"]
    ENDPOINT_CACHE_FIELD_NUMBER: _ClassVar[int]
    PRINT_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    VISUALS_FIELD_NUMBER: _ClassVar[int]
    endpoint_cache: EndPointParamCache
    print_settings: _containers.RepeatedCompositeFieldContainer[PrintSetting]
    visuals: PrintVisuals
    def __init__(self, print_settings: _Optional[_Iterable[_Union[PrintSetting, _Mapping]]] = ..., visuals: _Optional[_Union[PrintVisuals, _Mapping]] = ..., endpoint_cache: _Optional[_Union[EndPointParamCache, _Mapping]] = ...) -> None: ...

class LoadCaseVisuals(_message.Message):
    __slots__ = ["color", "guid", "visible"]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    VISIBLE_FIELD_NUMBER: _ClassVar[int]
    color: str
    guid: str
    visible: bool
    def __init__(self, guid: _Optional[str] = ..., color: _Optional[str] = ..., visible: bool = ...) -> None: ...

class LoadCombinationVisuals(_message.Message):
    __slots__ = ["color", "guid"]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    color: str
    guid: str
    def __init__(self, guid: _Optional[str] = ..., color: _Optional[str] = ...) -> None: ...

class PrintSetting(_message.Message):
    __slots__ = ["extent", "module"]
    EXTENT_FIELD_NUMBER: _ClassVar[int]
    MODULE_FIELD_NUMBER: _ClassVar[int]
    extent: PrintExtent
    module: PrintModule
    def __init__(self, module: _Optional[_Union[PrintModule, str]] = ..., extent: _Optional[_Union[PrintExtent, str]] = ...) -> None: ...

class PrintVisuals(_message.Message):
    __slots__ = ["loadcases", "loadcombinations"]
    LOADCASES_FIELD_NUMBER: _ClassVar[int]
    LOADCOMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    loadcases: _containers.RepeatedCompositeFieldContainer[LoadCaseVisuals]
    loadcombinations: _containers.RepeatedCompositeFieldContainer[LoadCombinationVisuals]
    def __init__(self, loadcases: _Optional[_Iterable[_Union[LoadCaseVisuals, _Mapping]]] = ..., loadcombinations: _Optional[_Iterable[_Union[LoadCombinationVisuals, _Mapping]]] = ...) -> None: ...

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

class PrintModule(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class PrintExtent(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Language(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
