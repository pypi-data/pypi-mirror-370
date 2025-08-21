from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FDForeignKey(_message.Message):
    __slots__ = ["key"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: int
    def __init__(self, key: _Optional[int] = ...) -> None: ...

class FDPoint3D(_message.Message):
    __slots__ = ["x", "y", "z"]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...

class FDPrimaryKey(_message.Message):
    __slots__ = ["key"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: int
    def __init__(self, key: _Optional[int] = ...) -> None: ...

class FDRCPunchingCheckConcreteCompression(_message.Message):
    __slots__ = ["r_V_ed0", "r_beta", "rdeff", "rdy", "rdz", "rnu", "ru0", "ru1", "rv_ed", "rv_rdc", "rv_rdmax"]
    RDEFF_FIELD_NUMBER: _ClassVar[int]
    RDY_FIELD_NUMBER: _ClassVar[int]
    RDZ_FIELD_NUMBER: _ClassVar[int]
    RNU_FIELD_NUMBER: _ClassVar[int]
    RU0_FIELD_NUMBER: _ClassVar[int]
    RU1_FIELD_NUMBER: _ClassVar[int]
    RV_ED_FIELD_NUMBER: _ClassVar[int]
    RV_RDC_FIELD_NUMBER: _ClassVar[int]
    RV_RDMAX_FIELD_NUMBER: _ClassVar[int]
    R_BETA_FIELD_NUMBER: _ClassVar[int]
    R_V_ED0_FIELD_NUMBER: _ClassVar[int]
    r_V_ed0: float
    r_beta: float
    rdeff: float
    rdy: float
    rdz: float
    rnu: float
    ru0: float
    ru1: float
    rv_ed: float
    rv_rdc: float
    rv_rdmax: float
    def __init__(self, r_beta: _Optional[float] = ..., rdy: _Optional[float] = ..., rdz: _Optional[float] = ..., rdeff: _Optional[float] = ..., ru0: _Optional[float] = ..., ru1: _Optional[float] = ..., rnu: _Optional[float] = ..., r_V_ed0: _Optional[float] = ..., rv_ed: _Optional[float] = ..., rv_rdmax: _Optional[float] = ..., rv_rdc: _Optional[float] = ...) -> None: ...

class FDRCPunchingCheckConcreteShear(_message.Message):
    __slots__ = ["n_p_s_h_sShear_section", "rV_rddow", "r_C_rdc", "r_Dist", "r_V_ed", "r_beta", "r_rhol", "r_rholy", "r_rholz", "r_sigmacp", "rdeff", "rdy", "rdz", "rk", "rk1", "rkmax_p_s_b", "ru", "rv_rdc", "rv_rdmax", "rvmin", "rvv_ed"]
    N_P_S_H_SSHEAR_SECTION_FIELD_NUMBER: _ClassVar[int]
    RDEFF_FIELD_NUMBER: _ClassVar[int]
    RDY_FIELD_NUMBER: _ClassVar[int]
    RDZ_FIELD_NUMBER: _ClassVar[int]
    RK1_FIELD_NUMBER: _ClassVar[int]
    RKMAX_P_S_B_FIELD_NUMBER: _ClassVar[int]
    RK_FIELD_NUMBER: _ClassVar[int]
    RU_FIELD_NUMBER: _ClassVar[int]
    RVMIN_FIELD_NUMBER: _ClassVar[int]
    RVV_ED_FIELD_NUMBER: _ClassVar[int]
    RV_RDC_FIELD_NUMBER: _ClassVar[int]
    RV_RDDOW_FIELD_NUMBER: _ClassVar[int]
    RV_RDMAX_FIELD_NUMBER: _ClassVar[int]
    R_BETA_FIELD_NUMBER: _ClassVar[int]
    R_C_RDC_FIELD_NUMBER: _ClassVar[int]
    R_DIST_FIELD_NUMBER: _ClassVar[int]
    R_RHOLY_FIELD_NUMBER: _ClassVar[int]
    R_RHOLZ_FIELD_NUMBER: _ClassVar[int]
    R_RHOL_FIELD_NUMBER: _ClassVar[int]
    R_SIGMACP_FIELD_NUMBER: _ClassVar[int]
    R_V_ED_FIELD_NUMBER: _ClassVar[int]
    n_p_s_h_sShear_section: int
    rV_rddow: float
    r_C_rdc: float
    r_Dist: float
    r_V_ed: float
    r_beta: float
    r_rhol: float
    r_rholy: float
    r_rholz: float
    r_sigmacp: float
    rdeff: float
    rdy: float
    rdz: float
    rk: float
    rk1: float
    rkmax_p_s_b: float
    ru: float
    rv_rdc: float
    rv_rdmax: float
    rvmin: float
    rvv_ed: float
    def __init__(self, r_beta: _Optional[float] = ..., rdy: _Optional[float] = ..., rdz: _Optional[float] = ..., rdeff: _Optional[float] = ..., ru: _Optional[float] = ..., r_Dist: _Optional[float] = ..., r_V_ed: _Optional[float] = ..., rvv_ed: _Optional[float] = ..., rk: _Optional[float] = ..., r_rhol: _Optional[float] = ..., r_rholy: _Optional[float] = ..., r_rholz: _Optional[float] = ..., r_sigmacp: _Optional[float] = ..., r_C_rdc: _Optional[float] = ..., rvmin: _Optional[float] = ..., rk1: _Optional[float] = ..., rv_rdc: _Optional[float] = ..., rkmax_p_s_b: _Optional[float] = ..., rv_rdmax: _Optional[float] = ..., rV_rddow: _Optional[float] = ..., n_p_s_h_sShear_section: _Optional[int] = ...) -> None: ...

class FDRCPunchingCheckDetail(_message.Message):
    __slots__ = ["DataTypeId", "IsRelevant", "PSBReinforcement", "ReinforcementShear", "Type", "Utilization", "concrete_compression", "concrete_shear"]
    CONCRETE_COMPRESSION_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_SHEAR_FIELD_NUMBER: _ClassVar[int]
    DATATYPEID_FIELD_NUMBER: _ClassVar[int]
    DataTypeId: int
    ISRELEVANT_FIELD_NUMBER: _ClassVar[int]
    IsRelevant: bool
    PSBREINFORCEMENT_FIELD_NUMBER: _ClassVar[int]
    PSBReinforcement: FDRCPunchingCheckReinforcementShearPSBRegionC
    REINFORCEMENTSHEAR_FIELD_NUMBER: _ClassVar[int]
    ReinforcementShear: FDRCPunchingCheckReinforcementShear
    TYPE_FIELD_NUMBER: _ClassVar[int]
    Type: int
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    Utilization: float
    concrete_compression: FDRCPunchingCheckConcreteCompression
    concrete_shear: FDRCPunchingCheckConcreteShear
    def __init__(self, Utilization: _Optional[float] = ..., IsRelevant: bool = ..., Type: _Optional[int] = ..., DataTypeId: _Optional[int] = ..., concrete_compression: _Optional[_Union[FDRCPunchingCheckConcreteCompression, _Mapping]] = ..., concrete_shear: _Optional[_Union[FDRCPunchingCheckConcreteShear, _Mapping]] = ..., ReinforcementShear: _Optional[_Union[FDRCPunchingCheckReinforcementShear, _Mapping]] = ..., PSBReinforcement: _Optional[_Union[FDRCPunchingCheckReinforcementShearPSBRegionC, _Mapping]] = ...) -> None: ...

class FDRCPunchingCheckDetailRecord(_message.Message):
    __slots__ = ["content", "id_combination", "id_entity", "id_perimeter"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ID_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    ID_ENTITY_FIELD_NUMBER: _ClassVar[int]
    ID_PERIMETER_FIELD_NUMBER: _ClassVar[int]
    content: FDRCPunchingCheckDetail
    id_combination: FDForeignKey
    id_entity: FDForeignKey
    id_perimeter: FDPrimaryKey
    def __init__(self, id_perimeter: _Optional[_Union[FDPrimaryKey, _Mapping]] = ..., id_entity: _Optional[_Union[FDForeignKey, _Mapping]] = ..., id_combination: _Optional[_Union[FDForeignKey, _Mapping]] = ..., content: _Optional[_Union[FDRCPunchingCheckDetail, _Mapping]] = ...) -> None: ...

class FDRCPunchingCheckReinforcementShear(_message.Message):
    __slots__ = ["conc_shear", "r_C_rdc_sw", "r_capacity", "rsr", "rv_rdcs", "rv_rdcsw", "rv_rdsw"]
    CONC_SHEAR_FIELD_NUMBER: _ClassVar[int]
    RSR_FIELD_NUMBER: _ClassVar[int]
    RV_RDCSW_FIELD_NUMBER: _ClassVar[int]
    RV_RDCS_FIELD_NUMBER: _ClassVar[int]
    RV_RDSW_FIELD_NUMBER: _ClassVar[int]
    R_CAPACITY_FIELD_NUMBER: _ClassVar[int]
    R_C_RDC_SW_FIELD_NUMBER: _ClassVar[int]
    conc_shear: FDRCPunchingCheckConcreteShear
    r_C_rdc_sw: float
    r_capacity: float
    rsr: float
    rv_rdcs: float
    rv_rdcsw: float
    rv_rdsw: float
    def __init__(self, conc_shear: _Optional[_Union[FDRCPunchingCheckConcreteShear, _Mapping]] = ..., rsr: _Optional[float] = ..., r_capacity: _Optional[float] = ..., rv_rdsw: _Optional[float] = ..., rv_rdcs: _Optional[float] = ..., rv_rdcsw: _Optional[float] = ..., r_C_rdc_sw: _Optional[float] = ...) -> None: ...

class FDRCPunchingCheckReinforcementShearPSBRegionC(_message.Message):
    __slots__ = ["conc_shear", "n_stud_region_c", "r_V_rdsy", "r_asi", "reta", "rfyd", "rs_r"]
    CONC_SHEAR_FIELD_NUMBER: _ClassVar[int]
    N_STUD_REGION_C_FIELD_NUMBER: _ClassVar[int]
    RETA_FIELD_NUMBER: _ClassVar[int]
    RFYD_FIELD_NUMBER: _ClassVar[int]
    RS_R_FIELD_NUMBER: _ClassVar[int]
    R_ASI_FIELD_NUMBER: _ClassVar[int]
    R_V_RDSY_FIELD_NUMBER: _ClassVar[int]
    conc_shear: FDRCPunchingCheckConcreteShear
    n_stud_region_c: int
    r_V_rdsy: float
    r_asi: float
    reta: float
    rfyd: float
    rs_r: float
    def __init__(self, conc_shear: _Optional[_Union[FDRCPunchingCheckConcreteShear, _Mapping]] = ..., rs_r: _Optional[float] = ..., n_stud_region_c: _Optional[int] = ..., rfyd: _Optional[float] = ..., reta: _Optional[float] = ..., r_asi: _Optional[float] = ..., r_V_rdsy: _Optional[float] = ...) -> None: ...

class FDRCPunchingCheckResultCombinationRecord(_message.Message):
    __slots__ = ["combination_id", "id_combination", "id_entity", "utilization"]
    COMBINATION_ID_FIELD_NUMBER: _ClassVar[int]
    ID_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    ID_ENTITY_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    combination_id: int
    id_combination: FDPrimaryKey
    id_entity: FDForeignKey
    utilization: float
    def __init__(self, id_combination: _Optional[_Union[FDPrimaryKey, _Mapping]] = ..., id_entity: _Optional[_Union[FDForeignKey, _Mapping]] = ..., combination_id: _Optional[int] = ..., utilization: _Optional[float] = ...) -> None: ...

class FDRCPunchingCheckResultDatabaseView(_message.Message):
    __slots__ = ["SchemaId", "combination_Table", "combination_table_no", "detailed_results_table", "detailed_results_table_no", "entity_results_table", "entity_results_table_no", "punching_perimeter_regions", "punching_perimeter_regions_no"]
    COMBINATION_TABLE_FIELD_NUMBER: _ClassVar[int]
    COMBINATION_TABLE_NO_FIELD_NUMBER: _ClassVar[int]
    DETAILED_RESULTS_TABLE_FIELD_NUMBER: _ClassVar[int]
    DETAILED_RESULTS_TABLE_NO_FIELD_NUMBER: _ClassVar[int]
    ENTITY_RESULTS_TABLE_FIELD_NUMBER: _ClassVar[int]
    ENTITY_RESULTS_TABLE_NO_FIELD_NUMBER: _ClassVar[int]
    PUNCHING_PERIMETER_REGIONS_FIELD_NUMBER: _ClassVar[int]
    PUNCHING_PERIMETER_REGIONS_NO_FIELD_NUMBER: _ClassVar[int]
    SCHEMAID_FIELD_NUMBER: _ClassVar[int]
    SchemaId: int
    combination_Table: _containers.RepeatedCompositeFieldContainer[FDRCPunchingCheckResultCombinationRecord]
    combination_table_no: FDSize32
    detailed_results_table: _containers.RepeatedCompositeFieldContainer[FDRCPunchingCheckDetailRecord]
    detailed_results_table_no: FDSize32
    entity_results_table: _containers.RepeatedCompositeFieldContainer[FDRCPunchingCheckResultEntityRecord]
    entity_results_table_no: FDSize32
    punching_perimeter_regions: _containers.RepeatedCompositeFieldContainer[FDRegionPolyline3DRecordView]
    punching_perimeter_regions_no: FDSize32
    def __init__(self, SchemaId: _Optional[int] = ..., entity_results_table_no: _Optional[_Union[FDSize32, _Mapping]] = ..., entity_results_table: _Optional[_Iterable[_Union[FDRCPunchingCheckResultEntityRecord, _Mapping]]] = ..., combination_table_no: _Optional[_Union[FDSize32, _Mapping]] = ..., combination_Table: _Optional[_Iterable[_Union[FDRCPunchingCheckResultCombinationRecord, _Mapping]]] = ..., detailed_results_table_no: _Optional[_Union[FDSize32, _Mapping]] = ..., detailed_results_table: _Optional[_Iterable[_Union[FDRCPunchingCheckDetailRecord, _Mapping]]] = ..., punching_perimeter_regions_no: _Optional[_Union[FDSize32, _Mapping]] = ..., punching_perimeter_regions: _Optional[_Iterable[_Union[FDRegionPolyline3DRecordView, _Mapping]]] = ...) -> None: ...

class FDRCPunchingCheckResultEntityRecord(_message.Message):
    __slots__ = ["combination_max_id", "guid", "id_entity", "is_ok", "utilization_max"]
    COMBINATION_MAX_ID_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    ID_ENTITY_FIELD_NUMBER: _ClassVar[int]
    IS_OK_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_MAX_FIELD_NUMBER: _ClassVar[int]
    combination_max_id: int
    guid: str
    id_entity: FDPrimaryKey
    is_ok: bool
    utilization_max: float
    def __init__(self, id_entity: _Optional[_Union[FDPrimaryKey, _Mapping]] = ..., guid: _Optional[str] = ..., is_ok: bool = ..., combination_max_id: _Optional[int] = ..., utilization_max: _Optional[float] = ...) -> None: ...

class FDRegionPolyline3DRecordView(_message.Message):
    __slots__ = ["id_entity", "id_region", "region"]
    ID_ENTITY_FIELD_NUMBER: _ClassVar[int]
    ID_REGION_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    id_entity: FDForeignKey
    id_region: FDPrimaryKey
    region: FDRegionPolyline3DView
    def __init__(self, id_region: _Optional[_Union[FDPrimaryKey, _Mapping]] = ..., id_entity: _Optional[_Union[FDForeignKey, _Mapping]] = ..., region: _Optional[_Union[FDRegionPolyline3DView, _Mapping]] = ...) -> None: ...

class FDRegionPolyline3DView(_message.Message):
    __slots__ = ["contours_no", "points", "points_no", "points_no_on_contours"]
    CONTOURS_NO_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    POINTS_NO_FIELD_NUMBER: _ClassVar[int]
    POINTS_NO_ON_CONTOURS_FIELD_NUMBER: _ClassVar[int]
    contours_no: int
    points: _containers.RepeatedCompositeFieldContainer[FDPoint3D]
    points_no: FDSize32
    points_no_on_contours: _containers.RepeatedCompositeFieldContainer[FDSize32]
    def __init__(self, contours_no: _Optional[int] = ..., points_no_on_contours: _Optional[_Iterable[_Union[FDSize32, _Mapping]]] = ..., points_no: _Optional[_Union[FDSize32, _Mapping]] = ..., points: _Optional[_Iterable[_Union[FDPoint3D, _Mapping]]] = ...) -> None: ...

class FDSize32(_message.Message):
    __slots__ = ["key"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: int
    def __init__(self, key: _Optional[int] = ...) -> None: ...
