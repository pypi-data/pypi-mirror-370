from Utils import log_pb2 as _log_pb2
from Frontends import beam_pb2 as _beam_pb2
import project_pb2 as _project_pb2
from Utils import utils_pb2 as _utils_pb2
from EndPointArguments import eurocode_pb2 as _eurocode_pb2
from EndPointArguments import fem_design_api_pb2 as _fem_design_api_pb2
from EndPointArguments import common_api_functions_pb2 as _common_api_functions_pb2
from Print import print_pb2 as _print_pb2
import project_pb2 as _project_pb2_1
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.log_pb2 import LogValue
from Utils.log_pb2 import LogEntry
from Utils.log_pb2 import Log
from Utils.log_pb2 import LogType
from Frontends.beam_pb2 import PrintSetting
from Frontends.beam_pb2 import LoadCaseVisuals
from Frontends.beam_pb2 import LoadCombinationVisuals
from Frontends.beam_pb2 import PrintVisuals
from Frontends.beam_pb2 import EndPointParamCache
from Frontends.beam_pb2 import FrontendData
from Frontends.beam_pb2 import ProjectMeta
from Frontends.beam_pb2 import Project
from Frontends.beam_pb2 import PrintModule
from Frontends.beam_pb2 import PrintExtent
from Frontends.beam_pb2 import Language
from Print.print_pb2 import ResultColumn
from Print.print_pb2 import ResultTable
from Print.print_pb2 import LoadcombinationResult
from Print.print_pb2 import LoadcombinationRcResult
from Print.print_pb2 import LoadcombinationSteelResult
from Print.print_pb2 import LoadcombinationTimberResult
from Print.print_pb2 import SectionResult
from Print.print_pb2 import HtmlResult
from Print.print_pb2 import Data
from Print.print_pb2 import ResultState
from Print.print_pb2 import PrintResult
from Print.print_pb2 import ComponentSettingsRows
from Print.print_pb2 import ComponentSettings
from Print.print_pb2 import Component
from Print.print_pb2 import Page
from Print.print_pb2 import Section
from Print.print_pb2 import Layout
from Print.print_pb2 import LayoutState
from Print.print_pb2 import PrintLayout
from Print.print_pb2 import PrintOutput
from Print.print_pb2 import ComponentType
COMPONENT_TYPE_BEAM_PLOT: _print_pb2.ComponentType
COMPONENT_TYPE_HTML: _print_pb2.ComponentType
COMPONENT_TYPE_LCA: _print_pb2.ComponentType
COMPONENT_TYPE_LINE_BREAK: _print_pb2.ComponentType
COMPONENT_TYPE_LOAD_PLOT: _print_pb2.ComponentType
COMPONENT_TYPE_MIN_MAX: _print_pb2.ComponentType
COMPONENT_TYPE_SECTION: _print_pb2.ComponentType
COMPONENT_TYPE_TABLE: _print_pb2.ComponentType
COMPONENT_TYPE_TABLE_PLOT: _print_pb2.ComponentType
COMPONENT_TYPE_TABLE_PLOT_ENVELOPE: _print_pb2.ComponentType
COMPONENT_TYPE_UNSPECIFIED: _print_pb2.ComponentType
COMPONENT_TYPE_UTILISATION: _print_pb2.ComponentType
DESCRIPTOR: _descriptor.FileDescriptor
LANGUAGE_DANISH: _beam_pb2.Language
LANGUAGE_ENGLISH: _beam_pb2.Language
LANGUAGE_SWEDISH: _beam_pb2.Language
LANGUAGE_UNSPECIFIED: _beam_pb2.Language
LOG_TYPE_ERROR: _log_pb2.LogType
LOG_TYPE_INFORMATION: _log_pb2.LogType
LOG_TYPE_UNSPECIFIED: _log_pb2.LogType
LOG_TYPE_WARNING: _log_pb2.LogType
PRINT_EXTENT_MAXIMAL: _beam_pb2.PrintExtent
PRINT_EXTENT_MINIMAL: _beam_pb2.PrintExtent
PRINT_EXTENT_NORMAL: _beam_pb2.PrintExtent
PRINT_EXTENT_UNSPECIFIED: _beam_pb2.PrintExtent
PRINT_MODULE_ANALYSIS: _beam_pb2.PrintModule
PRINT_MODULE_CONCRETE: _beam_pb2.PrintModule
PRINT_MODULE_INPUT: _beam_pb2.PrintModule
PRINT_MODULE_STEEL: _beam_pb2.PrintModule
PRINT_MODULE_SUMMARY: _beam_pb2.PrintModule
PRINT_MODULE_TIMBER: _beam_pb2.PrintModule
PRINT_MODULE_TOC: _beam_pb2.PrintModule
PRINT_MODULE_UNSPECIFIED: _beam_pb2.PrintModule

class LayoutInput(_message.Message):
    __slots__ = ["project"]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    project: _beam_pb2.Project
    def __init__(self, project: _Optional[_Union[_beam_pb2.Project, _Mapping]] = ...) -> None: ...
