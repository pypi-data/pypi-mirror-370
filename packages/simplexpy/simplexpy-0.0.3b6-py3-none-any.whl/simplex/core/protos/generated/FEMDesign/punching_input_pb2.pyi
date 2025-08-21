from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

ACCIDENTAL: FDLimitStateEnum
CHARACTERISTIC: FDLimitStateEnum
DESCRIPTOR: _descriptor.FileDescriptor
FREQUENT: FDLimitStateEnum
QUASIPERMANENT: FDLimitStateEnum
SEISMIC: FDLimitStateEnum
ULTIMATE: FDLimitStateEnum

class FDRCPunchingDesignForce(_message.Message):
    __slots__ = ["limit_state", "m_edx", "m_edy", "sigmacp", "v_ed"]
    LIMIT_STATE_FIELD_NUMBER: _ClassVar[int]
    M_EDX_FIELD_NUMBER: _ClassVar[int]
    M_EDY_FIELD_NUMBER: _ClassVar[int]
    SIGMACP_FIELD_NUMBER: _ClassVar[int]
    V_ED_FIELD_NUMBER: _ClassVar[int]
    limit_state: int
    m_edx: float
    m_edy: float
    sigmacp: float
    v_ed: float
    def __init__(self, limit_state: _Optional[int] = ..., v_ed: _Optional[float] = ..., m_edx: _Optional[float] = ..., m_edy: _Optional[float] = ..., sigmacp: _Optional[float] = ...) -> None: ...

class FDRCPunchingDesignForcesDatabaseView(_message.Message):
    __slots__ = ["EntityDesignForcesNo", "SchemaId", "entity_design_forces"]
    ENTITYDESIGNFORCESNO_FIELD_NUMBER: _ClassVar[int]
    ENTITY_DESIGN_FORCES_FIELD_NUMBER: _ClassVar[int]
    EntityDesignForcesNo: int
    SCHEMAID_FIELD_NUMBER: _ClassVar[int]
    SchemaId: int
    entity_design_forces: _containers.RepeatedCompositeFieldContainer[FDRCPunchingEntityDesignForcesView]
    def __init__(self, SchemaId: _Optional[int] = ..., EntityDesignForcesNo: _Optional[int] = ..., entity_design_forces: _Optional[_Iterable[_Union[FDRCPunchingEntityDesignForcesView, _Mapping]]] = ...) -> None: ...

class FDRCPunchingEntityDesignForcesView(_message.Message):
    __slots__ = ["design_forces", "design_forces_no", "guid"]
    DESIGN_FORCES_FIELD_NUMBER: _ClassVar[int]
    DESIGN_FORCES_NO_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    design_forces: _containers.RepeatedCompositeFieldContainer[FDRCPunchingDesignForce]
    design_forces_no: int
    guid: str
    def __init__(self, guid: _Optional[str] = ..., design_forces_no: _Optional[int] = ..., design_forces: _Optional[_Iterable[_Union[FDRCPunchingDesignForce, _Mapping]]] = ...) -> None: ...

class FDLimitStateEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
