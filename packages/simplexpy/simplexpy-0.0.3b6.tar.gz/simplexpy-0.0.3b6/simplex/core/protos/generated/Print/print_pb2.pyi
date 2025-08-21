import project_pb2 as _project_pb2
import input_pb2 as _input_pb2
import output_pb2 as _output_pb2
from Utils import log_pb2 as _log_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from project_pb2 import Data
COMPONENT_TYPE_BEAM_PLOT: ComponentType
COMPONENT_TYPE_HTML: ComponentType
COMPONENT_TYPE_LCA: ComponentType
COMPONENT_TYPE_LINE_BREAK: ComponentType
COMPONENT_TYPE_LOAD_PLOT: ComponentType
COMPONENT_TYPE_MIN_MAX: ComponentType
COMPONENT_TYPE_SECTION: ComponentType
COMPONENT_TYPE_TABLE: ComponentType
COMPONENT_TYPE_TABLE_PLOT: ComponentType
COMPONENT_TYPE_TABLE_PLOT_ENVELOPE: ComponentType
COMPONENT_TYPE_UNSPECIFIED: ComponentType
COMPONENT_TYPE_UTILISATION: ComponentType
DESCRIPTOR: _descriptor.FileDescriptor

class Component(_message.Message):
    __slots__ = ["caption", "data", "h", "id", "margin", "resizeOnClient", "settings", "static", "type", "w", "x", "y"]
    CAPTION_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    H_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MARGIN_FIELD_NUMBER: _ClassVar[int]
    RESIZEONCLIENT_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    STATIC_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    W_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    caption: str
    data: str
    h: float
    id: str
    margin: _containers.RepeatedScalarFieldContainer[float]
    resizeOnClient: bool
    settings: ComponentSettings
    static: bool
    type: ComponentType
    w: float
    x: float
    y: float
    def __init__(self, type: _Optional[_Union[ComponentType, str]] = ..., id: _Optional[str] = ..., data: _Optional[str] = ..., caption: _Optional[str] = ..., w: _Optional[float] = ..., h: _Optional[float] = ..., x: _Optional[float] = ..., y: _Optional[float] = ..., settings: _Optional[_Union[ComponentSettings, _Mapping]] = ..., static: bool = ..., margin: _Optional[_Iterable[float]] = ..., resizeOnClient: bool = ...) -> None: ...

class ComponentSettings(_message.Message):
    __slots__ = ["available_headers", "fix_headers", "legend", "menu", "minmax", "split", "visible_headers", "visible_rows", "x_axis_key"]
    AVAILABLE_HEADERS_FIELD_NUMBER: _ClassVar[int]
    FIX_HEADERS_FIELD_NUMBER: _ClassVar[int]
    LEGEND_FIELD_NUMBER: _ClassVar[int]
    MENU_FIELD_NUMBER: _ClassVar[int]
    MINMAX_FIELD_NUMBER: _ClassVar[int]
    SPLIT_FIELD_NUMBER: _ClassVar[int]
    VISIBLE_HEADERS_FIELD_NUMBER: _ClassVar[int]
    VISIBLE_ROWS_FIELD_NUMBER: _ClassVar[int]
    X_AXIS_KEY_FIELD_NUMBER: _ClassVar[int]
    available_headers: _containers.RepeatedScalarFieldContainer[str]
    fix_headers: _containers.RepeatedScalarFieldContainer[str]
    legend: bool
    menu: bool
    minmax: bool
    split: int
    visible_headers: _containers.RepeatedScalarFieldContainer[str]
    visible_rows: ComponentSettingsRows
    x_axis_key: str
    def __init__(self, fix_headers: _Optional[_Iterable[str]] = ..., visible_headers: _Optional[_Iterable[str]] = ..., available_headers: _Optional[_Iterable[str]] = ..., visible_rows: _Optional[_Union[ComponentSettingsRows, _Mapping]] = ..., x_axis_key: _Optional[str] = ..., menu: bool = ..., legend: bool = ..., minmax: bool = ..., split: _Optional[int] = ...) -> None: ...

class ComponentSettingsRows(_message.Message):
    __slots__ = ["active", "col", "list"]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COL_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    active: bool
    col: str
    list: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, col: _Optional[str] = ..., active: bool = ..., list: _Optional[_Iterable[str]] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["beam_properties", "calculation_sections", "code_settings", "distributed_force_loads", "distributed_moment_loads", "element_results", "id", "loadcases", "loadcombination_rc_results", "loadcombination_results", "loadcombination_steel_results", "loadcombination_timber_results", "loadcombinations", "max_code_check", "max_code_check_fire", "max_min", "mtrl_properties", "point_loads", "reactions", "section", "supports", "utilisation"]
    BEAM_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    CALCULATION_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    CODE_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    DISTRIBUTED_FORCE_LOADS_FIELD_NUMBER: _ClassVar[int]
    DISTRIBUTED_MOMENT_LOADS_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_RESULTS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LOADCASES_FIELD_NUMBER: _ClassVar[int]
    LOADCOMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    LOADCOMBINATION_RC_RESULTS_FIELD_NUMBER: _ClassVar[int]
    LOADCOMBINATION_RESULTS_FIELD_NUMBER: _ClassVar[int]
    LOADCOMBINATION_STEEL_RESULTS_FIELD_NUMBER: _ClassVar[int]
    LOADCOMBINATION_TIMBER_RESULTS_FIELD_NUMBER: _ClassVar[int]
    MAX_CODE_CHECK_FIELD_NUMBER: _ClassVar[int]
    MAX_CODE_CHECK_FIRE_FIELD_NUMBER: _ClassVar[int]
    MAX_MIN_FIELD_NUMBER: _ClassVar[int]
    MTRL_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    POINT_LOADS_FIELD_NUMBER: _ClassVar[int]
    REACTIONS_FIELD_NUMBER: _ClassVar[int]
    SECTION_FIELD_NUMBER: _ClassVar[int]
    SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    UTILISATION_FIELD_NUMBER: _ClassVar[int]
    beam_properties: ResultTable
    calculation_sections: ResultColumn
    code_settings: ResultTable
    distributed_force_loads: ResultTable
    distributed_moment_loads: ResultTable
    element_results: ResultTable
    id: str
    loadcases: ResultTable
    loadcombination_rc_results: _containers.RepeatedCompositeFieldContainer[LoadcombinationRcResult]
    loadcombination_results: _containers.RepeatedCompositeFieldContainer[LoadcombinationResult]
    loadcombination_steel_results: _containers.RepeatedCompositeFieldContainer[LoadcombinationSteelResult]
    loadcombination_timber_results: _containers.RepeatedCompositeFieldContainer[LoadcombinationTimberResult]
    loadcombinations: ResultTable
    max_code_check: _containers.RepeatedCompositeFieldContainer[HtmlResult]
    max_code_check_fire: _containers.RepeatedCompositeFieldContainer[HtmlResult]
    max_min: ResultTable
    mtrl_properties: ResultTable
    point_loads: ResultTable
    reactions: ResultTable
    section: SectionResult
    supports: ResultTable
    utilisation: ResultTable
    def __init__(self, id: _Optional[str] = ..., code_settings: _Optional[_Union[ResultTable, _Mapping]] = ..., beam_properties: _Optional[_Union[ResultTable, _Mapping]] = ..., mtrl_properties: _Optional[_Union[ResultTable, _Mapping]] = ..., supports: _Optional[_Union[ResultTable, _Mapping]] = ..., point_loads: _Optional[_Union[ResultTable, _Mapping]] = ..., distributed_force_loads: _Optional[_Union[ResultTable, _Mapping]] = ..., distributed_moment_loads: _Optional[_Union[ResultTable, _Mapping]] = ..., section: _Optional[_Union[SectionResult, _Mapping]] = ..., loadcases: _Optional[_Union[ResultTable, _Mapping]] = ..., loadcombinations: _Optional[_Union[ResultTable, _Mapping]] = ..., loadcombination_results: _Optional[_Iterable[_Union[LoadcombinationResult, _Mapping]]] = ..., loadcombination_rc_results: _Optional[_Iterable[_Union[LoadcombinationRcResult, _Mapping]]] = ..., loadcombination_steel_results: _Optional[_Iterable[_Union[LoadcombinationSteelResult, _Mapping]]] = ..., loadcombination_timber_results: _Optional[_Iterable[_Union[LoadcombinationTimberResult, _Mapping]]] = ..., calculation_sections: _Optional[_Union[ResultColumn, _Mapping]] = ..., element_results: _Optional[_Union[ResultTable, _Mapping]] = ..., max_min: _Optional[_Union[ResultTable, _Mapping]] = ..., reactions: _Optional[_Union[ResultTable, _Mapping]] = ..., utilisation: _Optional[_Union[ResultTable, _Mapping]] = ..., max_code_check: _Optional[_Iterable[_Union[HtmlResult, _Mapping]]] = ..., max_code_check_fire: _Optional[_Iterable[_Union[HtmlResult, _Mapping]]] = ...) -> None: ...

class HtmlResult(_message.Message):
    __slots__ = ["caption", "html", "id"]
    CAPTION_FIELD_NUMBER: _ClassVar[int]
    HTML_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    caption: str
    html: ResultTable
    id: str
    def __init__(self, id: _Optional[str] = ..., caption: _Optional[str] = ..., html: _Optional[_Union[ResultTable, _Mapping]] = ...) -> None: ...

class Layout(_message.Message):
    __slots__ = ["caption", "id", "is_expanded", "ref_guid", "sections"]
    CAPTION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    IS_EXPANDED_FIELD_NUMBER: _ClassVar[int]
    REF_GUID_FIELD_NUMBER: _ClassVar[int]
    SECTIONS_FIELD_NUMBER: _ClassVar[int]
    caption: str
    id: str
    is_expanded: bool
    ref_guid: str
    sections: _containers.RepeatedCompositeFieldContainer[Section]
    def __init__(self, id: _Optional[str] = ..., caption: _Optional[str] = ..., sections: _Optional[_Iterable[_Union[Section, _Mapping]]] = ..., ref_guid: _Optional[str] = ..., is_expanded: bool = ...) -> None: ...

class LayoutState(_message.Message):
    __slots__ = ["layouts"]
    LAYOUTS_FIELD_NUMBER: _ClassVar[int]
    layouts: _containers.RepeatedCompositeFieldContainer[Layout]
    def __init__(self, layouts: _Optional[_Iterable[_Union[Layout, _Mapping]]] = ...) -> None: ...

class LoadcombinationRcResult(_message.Message):
    __slots__ = ["capacity_results", "caption", "id", "max_utilisation_results", "utilisation_results"]
    CAPACITY_RESULTS_FIELD_NUMBER: _ClassVar[int]
    CAPTION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MAX_UTILISATION_RESULTS_FIELD_NUMBER: _ClassVar[int]
    UTILISATION_RESULTS_FIELD_NUMBER: _ClassVar[int]
    capacity_results: ResultTable
    caption: str
    id: str
    max_utilisation_results: ResultTable
    utilisation_results: ResultTable
    def __init__(self, id: _Optional[str] = ..., caption: _Optional[str] = ..., max_utilisation_results: _Optional[_Union[ResultTable, _Mapping]] = ..., utilisation_results: _Optional[_Union[ResultTable, _Mapping]] = ..., capacity_results: _Optional[_Union[ResultTable, _Mapping]] = ...) -> None: ...

class LoadcombinationResult(_message.Message):
    __slots__ = ["caption", "comb_of_action", "element_results", "id", "limit_state", "support_results", "type"]
    CAPTION_FIELD_NUMBER: _ClassVar[int]
    COMB_OF_ACTION_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_RESULTS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_STATE_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_RESULTS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    caption: str
    comb_of_action: str
    element_results: ResultTable
    id: str
    limit_state: str
    support_results: ResultTable
    type: str
    def __init__(self, limit_state: _Optional[str] = ..., comb_of_action: _Optional[str] = ..., type: _Optional[str] = ..., id: _Optional[str] = ..., caption: _Optional[str] = ..., support_results: _Optional[_Union[ResultTable, _Mapping]] = ..., element_results: _Optional[_Union[ResultTable, _Mapping]] = ...) -> None: ...

class LoadcombinationSteelResult(_message.Message):
    __slots__ = ["capacity_results", "caption", "id", "max_utilisation_results", "utilisation_results"]
    CAPACITY_RESULTS_FIELD_NUMBER: _ClassVar[int]
    CAPTION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MAX_UTILISATION_RESULTS_FIELD_NUMBER: _ClassVar[int]
    UTILISATION_RESULTS_FIELD_NUMBER: _ClassVar[int]
    capacity_results: ResultTable
    caption: str
    id: str
    max_utilisation_results: ResultTable
    utilisation_results: ResultTable
    def __init__(self, id: _Optional[str] = ..., caption: _Optional[str] = ..., max_utilisation_results: _Optional[_Union[ResultTable, _Mapping]] = ..., utilisation_results: _Optional[_Union[ResultTable, _Mapping]] = ..., capacity_results: _Optional[_Union[ResultTable, _Mapping]] = ...) -> None: ...

class LoadcombinationTimberResult(_message.Message):
    __slots__ = ["capacity_results", "caption", "id", "max_utilisation_results", "utilisation_results"]
    CAPACITY_RESULTS_FIELD_NUMBER: _ClassVar[int]
    CAPTION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MAX_UTILISATION_RESULTS_FIELD_NUMBER: _ClassVar[int]
    UTILISATION_RESULTS_FIELD_NUMBER: _ClassVar[int]
    capacity_results: ResultTable
    caption: str
    id: str
    max_utilisation_results: ResultTable
    utilisation_results: ResultTable
    def __init__(self, id: _Optional[str] = ..., caption: _Optional[str] = ..., max_utilisation_results: _Optional[_Union[ResultTable, _Mapping]] = ..., utilisation_results: _Optional[_Union[ResultTable, _Mapping]] = ..., capacity_results: _Optional[_Union[ResultTable, _Mapping]] = ...) -> None: ...

class Page(_message.Message):
    __slots__ = ["components", "id"]
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    components: _containers.RepeatedCompositeFieldContainer[Component]
    id: str
    def __init__(self, id: _Optional[str] = ..., components: _Optional[_Iterable[_Union[Component, _Mapping]]] = ...) -> None: ...

class PrintLayout(_message.Message):
    __slots__ = ["state"]
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: LayoutState
    def __init__(self, state: _Optional[_Union[LayoutState, _Mapping]] = ...) -> None: ...

class PrintOutput(_message.Message):
    __slots__ = ["layout", "result"]
    LAYOUT_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    layout: PrintLayout
    result: PrintResult
    def __init__(self, result: _Optional[_Union[PrintResult, _Mapping]] = ..., layout: _Optional[_Union[PrintLayout, _Mapping]] = ...) -> None: ...

class PrintResult(_message.Message):
    __slots__ = ["state"]
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: ResultState
    def __init__(self, state: _Optional[_Union[ResultState, _Mapping]] = ...) -> None: ...

class ResultColumn(_message.Message):
    __slots__ = ["data", "id", "tag", "user_defined"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedScalarFieldContainer[str]
    id: str
    tag: str
    user_defined: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, tag: _Optional[str] = ..., id: _Optional[str] = ..., data: _Optional[_Iterable[str]] = ..., user_defined: _Optional[_Iterable[str]] = ...) -> None: ...

class ResultState(_message.Message):
    __slots__ = ["data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[Data]
    def __init__(self, data: _Optional[_Iterable[_Union[Data, _Mapping]]] = ...) -> None: ...

class ResultTable(_message.Message):
    __slots__ = ["cols"]
    COLS_FIELD_NUMBER: _ClassVar[int]
    cols: _containers.RepeatedCompositeFieldContainer[ResultColumn]
    def __init__(self, cols: _Optional[_Iterable[_Union[ResultColumn, _Mapping]]] = ...) -> None: ...

class Section(_message.Message):
    __slots__ = ["caption", "data", "id", "is_expanded", "pages"]
    CAPTION_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    IS_EXPANDED_FIELD_NUMBER: _ClassVar[int]
    PAGES_FIELD_NUMBER: _ClassVar[int]
    caption: str
    data: str
    id: str
    is_expanded: bool
    pages: _containers.RepeatedCompositeFieldContainer[Page]
    def __init__(self, id: _Optional[str] = ..., caption: _Optional[str] = ..., data: _Optional[str] = ..., pages: _Optional[_Iterable[_Union[Page, _Mapping]]] = ..., is_expanded: bool = ...) -> None: ...

class SectionResult(_message.Message):
    __slots__ = ["holes", "material", "perimeters", "rebars", "stirrups"]
    HOLES_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_FIELD_NUMBER: _ClassVar[int]
    PERIMETERS_FIELD_NUMBER: _ClassVar[int]
    REBARS_FIELD_NUMBER: _ClassVar[int]
    STIRRUPS_FIELD_NUMBER: _ClassVar[int]
    holes: _containers.RepeatedCompositeFieldContainer[_geometry_pb2.PolyLine3D]
    material: _sections_pb2.MaterialCategory
    perimeters: _containers.RepeatedCompositeFieldContainer[_geometry_pb2.PolyLine3D]
    rebars: ResultTable
    stirrups: ResultTable
    def __init__(self, material: _Optional[_Union[_sections_pb2.MaterialCategory, str]] = ..., perimeters: _Optional[_Iterable[_Union[_geometry_pb2.PolyLine3D, _Mapping]]] = ..., holes: _Optional[_Iterable[_Union[_geometry_pb2.PolyLine3D, _Mapping]]] = ..., rebars: _Optional[_Union[ResultTable, _Mapping]] = ..., stirrups: _Optional[_Union[ResultTable, _Mapping]] = ...) -> None: ...

class ComponentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
