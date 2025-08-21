from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
LOG_TYPE_ERROR: LogType
LOG_TYPE_INFORMATION: LogType
LOG_TYPE_UNSPECIFIED: LogType
LOG_TYPE_WARNING: LogType

class Log(_message.Message):
    __slots__ = ["entries"]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[LogEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[LogEntry, _Mapping]]] = ...) -> None: ...

class LogEntry(_message.Message):
    __slots__ = ["label", "text", "type", "values"]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    label: str
    text: str
    type: LogType
    values: _containers.RepeatedCompositeFieldContainer[LogValue]
    def __init__(self, type: _Optional[_Union[LogType, str]] = ..., text: _Optional[str] = ..., values: _Optional[_Iterable[_Union[LogValue, _Mapping]]] = ..., label: _Optional[str] = ...) -> None: ...

class LogValue(_message.Message):
    __slots__ = ["bool_value", "double_value", "integer_value", "key", "string_value"]
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    INTEGER_VALUE_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    bool_value: bool
    double_value: float
    integer_value: int
    key: str
    string_value: str
    def __init__(self, key: _Optional[str] = ..., integer_value: _Optional[int] = ..., double_value: _Optional[float] = ..., string_value: _Optional[str] = ..., bool_value: bool = ...) -> None: ...

class LogType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
