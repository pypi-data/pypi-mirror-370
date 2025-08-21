from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BarResultRecord(_message.Message):
    __slots__ = ["comb_result", "number_of_sections"]
    COMB_RESULT_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    comb_result: _containers.RepeatedCompositeFieldContainer[CombResultRecord]
    number_of_sections: int
    def __init__(self, number_of_sections: _Optional[int] = ..., comb_result: _Optional[_Iterable[_Union[CombResultRecord, _Mapping]]] = ...) -> None: ...

class BarSteelFireProtRecord(_message.Message):
    __slots__ = ["encasement", "max_temperature", "mode", "specific_heat", "thermal_conductivity", "thickness", "unit_mass"]
    ENCASEMENT_FIELD_NUMBER: _ClassVar[int]
    MAX_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    SPECIFIC_HEAT_FIELD_NUMBER: _ClassVar[int]
    THERMAL_CONDUCTIVITY_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_FIELD_NUMBER: _ClassVar[int]
    UNIT_MASS_FIELD_NUMBER: _ClassVar[int]
    encasement: int
    max_temperature: float
    mode: int
    specific_heat: float
    thermal_conductivity: float
    thickness: float
    unit_mass: float
    def __init__(self, mode: _Optional[int] = ..., unit_mass: _Optional[float] = ..., specific_heat: _Optional[float] = ..., thermal_conductivity: _Optional[float] = ..., encasement: _Optional[int] = ..., thickness: _Optional[float] = ..., max_temperature: _Optional[float] = ...) -> None: ...

class BarTimberFireProtRecord(_message.Message):
    __slots__ = ["charring_rate", "charring_rate_mod_factor", "charring_start_time", "failure_time", "inner_layer_thickness", "material_type", "mode", "outer_layer_thickness"]
    CHARRING_RATE_FIELD_NUMBER: _ClassVar[int]
    CHARRING_RATE_MOD_FACTOR_FIELD_NUMBER: _ClassVar[int]
    CHARRING_START_TIME_FIELD_NUMBER: _ClassVar[int]
    FAILURE_TIME_FIELD_NUMBER: _ClassVar[int]
    INNER_LAYER_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    OUTER_LAYER_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    charring_rate: float
    charring_rate_mod_factor: float
    charring_start_time: float
    failure_time: float
    inner_layer_thickness: float
    material_type: int
    mode: int
    outer_layer_thickness: float
    def __init__(self, mode: _Optional[int] = ..., material_type: _Optional[int] = ..., inner_layer_thickness: _Optional[float] = ..., outer_layer_thickness: _Optional[float] = ..., charring_rate: _Optional[float] = ..., failure_time: _Optional[float] = ..., charring_start_time: _Optional[float] = ..., charring_rate_mod_factor: _Optional[float] = ...) -> None: ...

class CombResultRecord(_message.Message):
    __slots__ = ["section_result"]
    SECTION_RESULT_FIELD_NUMBER: _ClassVar[int]
    section_result: _containers.RepeatedCompositeFieldContainer[SectionResultRecord]
    def __init__(self, section_result: _Optional[_Iterable[_Union[SectionResultRecord, _Mapping]]] = ...) -> None: ...

class Displacement(_message.Message):
    __slots__ = ["ex", "ey", "ez"]
    EX_FIELD_NUMBER: _ClassVar[int]
    EY_FIELD_NUMBER: _ClassVar[int]
    EZ_FIELD_NUMBER: _ClassVar[int]
    ex: float
    ey: float
    ez: float
    def __init__(self, ex: _Optional[float] = ..., ey: _Optional[float] = ..., ez: _Optional[float] = ...) -> None: ...

class Force(_message.Message):
    __slots__ = ["mx", "my", "mz", "n", "ty", "tz"]
    MX_FIELD_NUMBER: _ClassVar[int]
    MY_FIELD_NUMBER: _ClassVar[int]
    MZ_FIELD_NUMBER: _ClassVar[int]
    N_FIELD_NUMBER: _ClassVar[int]
    TY_FIELD_NUMBER: _ClassVar[int]
    TZ_FIELD_NUMBER: _ClassVar[int]
    mx: float
    my: float
    mz: float
    n: float
    ty: float
    tz: float
    def __init__(self, n: _Optional[float] = ..., ty: _Optional[float] = ..., tz: _Optional[float] = ..., mx: _Optional[float] = ..., my: _Optional[float] = ..., mz: _Optional[float] = ...) -> None: ...

class InformationSteel(_message.Message):
    __slots__ = ["bar_fire_prot", "bar_result", "load_comb", "nbar", "ncomb", "version"]
    BAR_FIRE_PROT_FIELD_NUMBER: _ClassVar[int]
    BAR_RESULT_FIELD_NUMBER: _ClassVar[int]
    LOAD_COMB_FIELD_NUMBER: _ClassVar[int]
    NBAR_FIELD_NUMBER: _ClassVar[int]
    NCOMB_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    bar_fire_prot: _containers.RepeatedCompositeFieldContainer[BarSteelFireProtRecord]
    bar_result: _containers.RepeatedCompositeFieldContainer[BarResultRecord]
    load_comb: _containers.RepeatedCompositeFieldContainer[LoadCombRecord]
    nbar: int
    ncomb: int
    version: int
    def __init__(self, version: _Optional[int] = ..., nbar: _Optional[int] = ..., ncomb: _Optional[int] = ..., load_comb: _Optional[_Iterable[_Union[LoadCombRecord, _Mapping]]] = ..., bar_result: _Optional[_Iterable[_Union[BarResultRecord, _Mapping]]] = ..., bar_fire_prot: _Optional[_Iterable[_Union[BarSteelFireProtRecord, _Mapping]]] = ...) -> None: ...

class InformationTimber(_message.Message):
    __slots__ = ["bar_fire_prot", "bar_result", "load_comb", "nbar", "ncomb", "version"]
    BAR_FIRE_PROT_FIELD_NUMBER: _ClassVar[int]
    BAR_RESULT_FIELD_NUMBER: _ClassVar[int]
    LOAD_COMB_FIELD_NUMBER: _ClassVar[int]
    NBAR_FIELD_NUMBER: _ClassVar[int]
    NCOMB_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    bar_fire_prot: _containers.RepeatedCompositeFieldContainer[BarTimberFireProtRecord]
    bar_result: _containers.RepeatedCompositeFieldContainer[BarResultRecord]
    load_comb: _containers.RepeatedCompositeFieldContainer[LoadCombTimberRecord]
    nbar: int
    ncomb: int
    version: int
    def __init__(self, version: _Optional[int] = ..., nbar: _Optional[int] = ..., ncomb: _Optional[int] = ..., load_comb: _Optional[_Iterable[_Union[LoadCombTimberRecord, _Mapping]]] = ..., bar_result: _Optional[_Iterable[_Union[BarResultRecord, _Mapping]]] = ..., bar_fire_prot: _Optional[_Iterable[_Union[BarTimberFireProtRecord, _Mapping]]] = ...) -> None: ...

class LoadCombRecord(_message.Message):
    __slots__ = ["accidental", "fire", "second_order"]
    ACCIDENTAL_FIELD_NUMBER: _ClassVar[int]
    FIRE_FIELD_NUMBER: _ClassVar[int]
    SECOND_ORDER_FIELD_NUMBER: _ClassVar[int]
    accidental: bool
    fire: bool
    second_order: bool
    def __init__(self, second_order: bool = ..., accidental: bool = ..., fire: bool = ...) -> None: ...

class LoadCombTimberRecord(_message.Message):
    __slots__ = ["accidental", "duration_class", "fire", "second_order"]
    ACCIDENTAL_FIELD_NUMBER: _ClassVar[int]
    DURATION_CLASS_FIELD_NUMBER: _ClassVar[int]
    FIRE_FIELD_NUMBER: _ClassVar[int]
    SECOND_ORDER_FIELD_NUMBER: _ClassVar[int]
    accidental: bool
    duration_class: int
    fire: bool
    second_order: bool
    def __init__(self, second_order: bool = ..., accidental: bool = ..., fire: bool = ..., duration_class: _Optional[int] = ...) -> None: ...

class SectionResultRecord(_message.Message):
    __slots__ = ["displacement", "force", "section_distance_start"]
    DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    SECTION_DISTANCE_START_FIELD_NUMBER: _ClassVar[int]
    displacement: Displacement
    force: Force
    section_distance_start: float
    def __init__(self, section_distance_start: _Optional[float] = ..., displacement: _Optional[_Union[Displacement, _Mapping]] = ..., force: _Optional[_Union[Force, _Mapping]] = ...) -> None: ...
