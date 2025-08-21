from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

ANNEX_BELGIUM: Annex
ANNEX_COMMON: Annex
ANNEX_DENMARK: Annex
ANNEX_ESTONIA: Annex
ANNEX_FINLAND: Annex
ANNEX_GERMANY: Annex
ANNEX_GREAT_BRITAIN: Annex
ANNEX_HUNGARY: Annex
ANNEX_LATVIA: Annex
ANNEX_NETHERLAND: Annex
ANNEX_NORWAY: Annex
ANNEX_POLAND: Annex
ANNEX_ROMANIA: Annex
ANNEX_SPAIN: Annex
ANNEX_SWEDEN: Annex
ANNEX_TURKEY: Annex
ANNEX_UNSPECIFIED: Annex
DESCRIPTOR: _descriptor.FileDescriptor
GENERATION_1: Generation
GENERATION_2: Generation
GENERATION_UNSPECIFIED: Generation
SNOW_ZONE_1: SnowZone
SNOW_ZONE_2: SnowZone
SNOW_ZONE_3: SnowZone
SNOW_ZONE_UNSPECIFIED: SnowZone

class DesignConfiguration(_message.Message):
    __slots__ = ["altitude", "generation", "national_annex", "snow_load"]
    ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    GENERATION_FIELD_NUMBER: _ClassVar[int]
    NATIONAL_ANNEX_FIELD_NUMBER: _ClassVar[int]
    SNOW_LOAD_FIELD_NUMBER: _ClassVar[int]
    altitude: float
    generation: Generation
    national_annex: Annex
    snow_load: float
    def __init__(self, national_annex: _Optional[_Union[Annex, str]] = ..., altitude: _Optional[float] = ..., snow_load: _Optional[float] = ..., generation: _Optional[_Union[Generation, str]] = ...) -> None: ...

class Annex(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class SnowZone(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Generation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
