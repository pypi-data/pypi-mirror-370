from Utils import utils_pb2 as _utils_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
BEHAVIOUR_COMBINED: Behaviour
BEHAVIOUR_DRAINED: Behaviour
BEHAVIOUR_ROCK: Behaviour
BEHAVIOUR_ROCK_PLANE_GRINDED: Behaviour
BEHAVIOUR_UNDRAINED: Behaviour
BEHAVIOUR_UNSPECIFIED: Behaviour
DESCRIPTOR: _descriptor.FileDescriptor
MATERIAL_MODEL_GENERIC: MaterialModel
MATERIAL_MODEL_LINEAR: MaterialModel
MATERIAL_MODEL_LOG: MaterialModel
MATERIAL_MODEL_NOSETTLEMENT: MaterialModel
MATERIAL_MODEL_OVERCONSOLIDATED: MaterialModel
MATERIAL_MODEL_UNSPECIFIED: MaterialModel
OWNER_COMPANY: _utils_pb2.Owner
OWNER_OFFICE: _utils_pb2.Owner
OWNER_STRUSOFT: _utils_pb2.Owner
OWNER_UNSPECIFIED: _utils_pb2.Owner
OWNER_USER: _utils_pb2.Owner

class CharacteristicData(_message.Message):
    __slots__ = ["Nc", "Nc_d", "Nq", "alfa", "beta", "ck", "ck_d", "cuk", "cuk_d", "gamma", "gamma_effective", "generic", "ksigma", "m", "m0", "m0_d", "m_d", "ml", "ml_d", "mu", "mu_d", "pc", "pc_d", "phi_cvk", "phi_k", "pl", "pl_d", "poissons_ratio", "q", "qbd_max", "qsd_max", "rk", "sigma_c", "sigma_l", "wall_strength"]
    ALFA_FIELD_NUMBER: _ClassVar[int]
    BETA_FIELD_NUMBER: _ClassVar[int]
    CK_D_FIELD_NUMBER: _ClassVar[int]
    CK_FIELD_NUMBER: _ClassVar[int]
    CUK_D_FIELD_NUMBER: _ClassVar[int]
    CUK_FIELD_NUMBER: _ClassVar[int]
    GAMMA_EFFECTIVE_FIELD_NUMBER: _ClassVar[int]
    GAMMA_FIELD_NUMBER: _ClassVar[int]
    GENERIC_FIELD_NUMBER: _ClassVar[int]
    KSIGMA_FIELD_NUMBER: _ClassVar[int]
    M0_D_FIELD_NUMBER: _ClassVar[int]
    M0_FIELD_NUMBER: _ClassVar[int]
    ML_D_FIELD_NUMBER: _ClassVar[int]
    ML_FIELD_NUMBER: _ClassVar[int]
    MU_D_FIELD_NUMBER: _ClassVar[int]
    MU_FIELD_NUMBER: _ClassVar[int]
    M_D_FIELD_NUMBER: _ClassVar[int]
    M_FIELD_NUMBER: _ClassVar[int]
    NC_D_FIELD_NUMBER: _ClassVar[int]
    NC_FIELD_NUMBER: _ClassVar[int]
    NQ_FIELD_NUMBER: _ClassVar[int]
    Nc: float
    Nc_d: float
    Nq: float
    PC_D_FIELD_NUMBER: _ClassVar[int]
    PC_FIELD_NUMBER: _ClassVar[int]
    PHI_CVK_FIELD_NUMBER: _ClassVar[int]
    PHI_K_FIELD_NUMBER: _ClassVar[int]
    PL_D_FIELD_NUMBER: _ClassVar[int]
    PL_FIELD_NUMBER: _ClassVar[int]
    POISSONS_RATIO_FIELD_NUMBER: _ClassVar[int]
    QBD_MAX_FIELD_NUMBER: _ClassVar[int]
    QSD_MAX_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    RK_FIELD_NUMBER: _ClassVar[int]
    SIGMA_C_FIELD_NUMBER: _ClassVar[int]
    SIGMA_L_FIELD_NUMBER: _ClassVar[int]
    WALL_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    alfa: PileShaftResistance
    beta: PileShaftResistance
    ck: float
    ck_d: float
    cuk: float
    cuk_d: float
    gamma: float
    gamma_effective: float
    generic: _containers.RepeatedCompositeFieldContainer[Generic]
    ksigma: float
    m: float
    m0: float
    m0_d: float
    m_d: float
    ml: float
    ml_d: float
    mu: float
    mu_d: float
    pc: float
    pc_d: float
    phi_cvk: float
    phi_k: float
    pl: float
    pl_d: float
    poissons_ratio: float
    q: float
    qbd_max: float
    qsd_max: float
    rk: float
    sigma_c: float
    sigma_l: float
    wall_strength: WallStrength
    def __init__(self, cuk: _Optional[float] = ..., cuk_d: _Optional[float] = ..., ck: _Optional[float] = ..., ck_d: _Optional[float] = ..., phi_k: _Optional[float] = ..., phi_cvk: _Optional[float] = ..., rk: _Optional[float] = ..., gamma: _Optional[float] = ..., gamma_effective: _Optional[float] = ..., m0: _Optional[float] = ..., m0_d: _Optional[float] = ..., mu: _Optional[float] = ..., mu_d: _Optional[float] = ..., ml: _Optional[float] = ..., ml_d: _Optional[float] = ..., m: _Optional[float] = ..., m_d: _Optional[float] = ..., sigma_c: _Optional[float] = ..., pc: _Optional[float] = ..., pc_d: _Optional[float] = ..., sigma_l: _Optional[float] = ..., pl: _Optional[float] = ..., pl_d: _Optional[float] = ..., poissons_ratio: _Optional[float] = ..., q: _Optional[float] = ..., generic: _Optional[_Iterable[_Union[Generic, _Mapping]]] = ..., wall_strength: _Optional[_Union[WallStrength, _Mapping]] = ..., alfa: _Optional[_Union[PileShaftResistance, _Mapping]] = ..., beta: _Optional[_Union[PileShaftResistance, _Mapping]] = ..., Nc: _Optional[float] = ..., Nq: _Optional[float] = ..., Nc_d: _Optional[float] = ..., qsd_max: _Optional[float] = ..., qbd_max: _Optional[float] = ..., ksigma: _Optional[float] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["behaviour", "id", "material_model", "properties", "reference_level"]
    BEHAVIOUR_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_MODEL_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_LEVEL_FIELD_NUMBER: _ClassVar[int]
    behaviour: Behaviour
    id: _utils_pb2.ID
    material_model: MaterialModel
    properties: CharacteristicData
    reference_level: float
    def __init__(self, id: _Optional[_Union[_utils_pb2.ID, _Mapping]] = ..., behaviour: _Optional[_Union[Behaviour, str]] = ..., material_model: _Optional[_Union[MaterialModel, str]] = ..., reference_level: _Optional[float] = ..., properties: _Optional[_Union[CharacteristicData, _Mapping]] = ...) -> None: ...

class Generic(_message.Message):
    __slots__ = ["m", "m_d", "p", "p_d", "sigma"]
    M_D_FIELD_NUMBER: _ClassVar[int]
    M_FIELD_NUMBER: _ClassVar[int]
    P_D_FIELD_NUMBER: _ClassVar[int]
    P_FIELD_NUMBER: _ClassVar[int]
    SIGMA_FIELD_NUMBER: _ClassVar[int]
    m: float
    m_d: float
    p: float
    p_d: float
    sigma: float
    def __init__(self, sigma: _Optional[float] = ..., p: _Optional[float] = ..., p_d: _Optional[float] = ..., m: _Optional[float] = ..., m_d: _Optional[float] = ...) -> None: ...

class PileShaftResistance(_message.Message):
    __slots__ = ["compression", "negative", "tension"]
    COMPRESSION_FIELD_NUMBER: _ClassVar[int]
    NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    TENSION_FIELD_NUMBER: _ClassVar[int]
    compression: float
    negative: float
    tension: float
    def __init__(self, compression: _Optional[float] = ..., tension: _Optional[float] = ..., negative: _Optional[float] = ...) -> None: ...

class WallStrength(_message.Message):
    __slots__ = ["ck", "phik"]
    CK_FIELD_NUMBER: _ClassVar[int]
    PHIK_FIELD_NUMBER: _ClassVar[int]
    ck: float
    phik: float
    def __init__(self, phik: _Optional[float] = ..., ck: _Optional[float] = ...) -> None: ...

class MaterialModel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Behaviour(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
