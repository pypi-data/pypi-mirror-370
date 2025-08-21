from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
OWNER_COMPANY: Owner
OWNER_OFFICE: Owner
OWNER_STRUSOFT: Owner
OWNER_UNSPECIFIED: Owner
OWNER_USER: Owner

class ID(_message.Message):
    __slots__ = ["e_tag", "guid", "name", "version"]
    E_TAG_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    e_tag: str
    guid: str
    name: str
    version: SemVer
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., e_tag: _Optional[str] = ..., version: _Optional[_Union[SemVer, _Mapping]] = ...) -> None: ...

class SemVer(_message.Message):
    __slots__ = ["major_version", "minor_version", "patch_version"]
    MAJOR_VERSION_FIELD_NUMBER: _ClassVar[int]
    MINOR_VERSION_FIELD_NUMBER: _ClassVar[int]
    PATCH_VERSION_FIELD_NUMBER: _ClassVar[int]
    major_version: int
    minor_version: int
    patch_version: int
    def __init__(self, major_version: _Optional[int] = ..., minor_version: _Optional[int] = ..., patch_version: _Optional[int] = ...) -> None: ...

class Owner(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
