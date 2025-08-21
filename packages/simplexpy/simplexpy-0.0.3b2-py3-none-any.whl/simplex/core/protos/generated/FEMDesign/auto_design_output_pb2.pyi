from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AutoDesign(_message.Message):
    __slots__ = ["AutoDesignData", "version"]
    AUTODESIGNDATA_FIELD_NUMBER: _ClassVar[int]
    AutoDesignData: _containers.RepeatedCompositeFieldContainer[AutoDesignData]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    version: str
    def __init__(self, version: _Optional[str] = ..., AutoDesignData: _Optional[_Iterable[_Union[AutoDesignData, _Mapping]]] = ...) -> None: ...

class AutoDesignData(_message.Message):
    __slots__ = ["BarGuid", "FireProtData", "FireProtMode", "SecGuidEnd", "SecGuidStart"]
    BARGUID_FIELD_NUMBER: _ClassVar[int]
    BarGuid: str
    FIREPROTDATA_FIELD_NUMBER: _ClassVar[int]
    FIREPROTMODE_FIELD_NUMBER: _ClassVar[int]
    FireProtData: float
    FireProtMode: int
    SECGUIDEND_FIELD_NUMBER: _ClassVar[int]
    SECGUIDSTART_FIELD_NUMBER: _ClassVar[int]
    SecGuidEnd: str
    SecGuidStart: str
    def __init__(self, BarGuid: _Optional[str] = ..., SecGuidStart: _Optional[str] = ..., SecGuidEnd: _Optional[str] = ..., FireProtMode: _Optional[int] = ..., FireProtData: _Optional[float] = ...) -> None: ...
