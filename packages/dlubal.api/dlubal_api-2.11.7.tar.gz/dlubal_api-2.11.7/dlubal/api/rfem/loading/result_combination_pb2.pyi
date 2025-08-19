from dlubal.api.rfem import object_id_pb2 as _object_id_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResultCombination(_message.Message):
    __slots__ = ("no", "design_situation", "user_defined_name_enabled", "name", "to_solve", "comment", "combination_type", "srss_combination", "srss_extreme_value_sign", "srss_use_equivalent_linear_combination", "srss_according_load_case_or_combination", "items", "combination_rule_str", "generate_subcombinations", "load_duration", "is_generated", "consider_construction_stage", "consider_construction_stage_active", "id_for_export_import", "metadata_for_export_import")
    class CombinationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COMBINATION_TYPE_GENERAL: _ClassVar[ResultCombination.CombinationType]
        COMBINATION_TYPE_ENVELOPE_PERMANENT: _ClassVar[ResultCombination.CombinationType]
        COMBINATION_TYPE_ENVELOPE_TRANSIENT: _ClassVar[ResultCombination.CombinationType]
        COMBINATION_TYPE_SUPERPOSITION: _ClassVar[ResultCombination.CombinationType]
    COMBINATION_TYPE_GENERAL: ResultCombination.CombinationType
    COMBINATION_TYPE_ENVELOPE_PERMANENT: ResultCombination.CombinationType
    COMBINATION_TYPE_ENVELOPE_TRANSIENT: ResultCombination.CombinationType
    COMBINATION_TYPE_SUPERPOSITION: ResultCombination.CombinationType
    class SrssExtremeValueSign(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SRSS_EXTREME_VALUE_SIGN_POSITIVE_OR_NEGATIVE: _ClassVar[ResultCombination.SrssExtremeValueSign]
        SRSS_EXTREME_VALUE_SIGN_ACCORDING_TO_LC_OR_CO: _ClassVar[ResultCombination.SrssExtremeValueSign]
        SRSS_EXTREME_VALUE_SIGN_NEGATIVE: _ClassVar[ResultCombination.SrssExtremeValueSign]
        SRSS_EXTREME_VALUE_SIGN_POSITIVE: _ClassVar[ResultCombination.SrssExtremeValueSign]
    SRSS_EXTREME_VALUE_SIGN_POSITIVE_OR_NEGATIVE: ResultCombination.SrssExtremeValueSign
    SRSS_EXTREME_VALUE_SIGN_ACCORDING_TO_LC_OR_CO: ResultCombination.SrssExtremeValueSign
    SRSS_EXTREME_VALUE_SIGN_NEGATIVE: ResultCombination.SrssExtremeValueSign
    SRSS_EXTREME_VALUE_SIGN_POSITIVE: ResultCombination.SrssExtremeValueSign
    class LoadDuration(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DURATION_UNKNOWN: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_10_MINUTES: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_10_SECONDS: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_12_HOURS: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_1_DAY: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_1_HOUR: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_1_MINUTE: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_1_MONTH: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_1_WEEK: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_1_YEAR: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_3_MONTHS: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_3_SECONDS: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_50_YEARS: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_5_DAYS: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_5_HOURS: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_5_MINUTES: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_5_MONTHS: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_5_SECONDS: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_ASD_IMPACT_LRFD_EQUAL_TO_1_25: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_ASD_PERMANENT_LRFD_EQUAL_TO_0_6: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_ASD_SEVEN_DAYS_LRFD_EQUAL_TO_0_9: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_ASD_TEN_MINUTES_LRFD_EQUAL_TO_1_0: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_ASD_TEN_YEARS_LRFD_EQUAL_TO_0_7: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_ASD_TWO_MONTHS_LRFD_EQUAL_TO_0_8: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_BEYOND_1_YEAR: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_IMPACT: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_INSTANTANEOUS: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_LONG_TERM: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_MEDIUM_TERM: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_PERMANENT: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_SEVEN_DAYS: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_SHORT_TERM: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_SHORT_TERM_INSTANTANEOUS: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_STANDARD_TERM: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_TEN_MINUTES: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_TEN_YEARS: _ClassVar[ResultCombination.LoadDuration]
        LOAD_DURATION_TWO_MONTHS: _ClassVar[ResultCombination.LoadDuration]
    LOAD_DURATION_UNKNOWN: ResultCombination.LoadDuration
    LOAD_DURATION_10_MINUTES: ResultCombination.LoadDuration
    LOAD_DURATION_10_SECONDS: ResultCombination.LoadDuration
    LOAD_DURATION_12_HOURS: ResultCombination.LoadDuration
    LOAD_DURATION_1_DAY: ResultCombination.LoadDuration
    LOAD_DURATION_1_HOUR: ResultCombination.LoadDuration
    LOAD_DURATION_1_MINUTE: ResultCombination.LoadDuration
    LOAD_DURATION_1_MONTH: ResultCombination.LoadDuration
    LOAD_DURATION_1_WEEK: ResultCombination.LoadDuration
    LOAD_DURATION_1_YEAR: ResultCombination.LoadDuration
    LOAD_DURATION_3_MONTHS: ResultCombination.LoadDuration
    LOAD_DURATION_3_SECONDS: ResultCombination.LoadDuration
    LOAD_DURATION_50_YEARS: ResultCombination.LoadDuration
    LOAD_DURATION_5_DAYS: ResultCombination.LoadDuration
    LOAD_DURATION_5_HOURS: ResultCombination.LoadDuration
    LOAD_DURATION_5_MINUTES: ResultCombination.LoadDuration
    LOAD_DURATION_5_MONTHS: ResultCombination.LoadDuration
    LOAD_DURATION_5_SECONDS: ResultCombination.LoadDuration
    LOAD_DURATION_ASD_IMPACT_LRFD_EQUAL_TO_1_25: ResultCombination.LoadDuration
    LOAD_DURATION_ASD_PERMANENT_LRFD_EQUAL_TO_0_6: ResultCombination.LoadDuration
    LOAD_DURATION_ASD_SEVEN_DAYS_LRFD_EQUAL_TO_0_9: ResultCombination.LoadDuration
    LOAD_DURATION_ASD_TEN_MINUTES_LRFD_EQUAL_TO_1_0: ResultCombination.LoadDuration
    LOAD_DURATION_ASD_TEN_YEARS_LRFD_EQUAL_TO_0_7: ResultCombination.LoadDuration
    LOAD_DURATION_ASD_TWO_MONTHS_LRFD_EQUAL_TO_0_8: ResultCombination.LoadDuration
    LOAD_DURATION_BEYOND_1_YEAR: ResultCombination.LoadDuration
    LOAD_DURATION_IMPACT: ResultCombination.LoadDuration
    LOAD_DURATION_INSTANTANEOUS: ResultCombination.LoadDuration
    LOAD_DURATION_LONG_TERM: ResultCombination.LoadDuration
    LOAD_DURATION_MEDIUM_TERM: ResultCombination.LoadDuration
    LOAD_DURATION_PERMANENT: ResultCombination.LoadDuration
    LOAD_DURATION_SEVEN_DAYS: ResultCombination.LoadDuration
    LOAD_DURATION_SHORT_TERM: ResultCombination.LoadDuration
    LOAD_DURATION_SHORT_TERM_INSTANTANEOUS: ResultCombination.LoadDuration
    LOAD_DURATION_STANDARD_TERM: ResultCombination.LoadDuration
    LOAD_DURATION_TEN_MINUTES: ResultCombination.LoadDuration
    LOAD_DURATION_TEN_YEARS: ResultCombination.LoadDuration
    LOAD_DURATION_TWO_MONTHS: ResultCombination.LoadDuration
    class ItemsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[ResultCombination.ItemsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[ResultCombination.ItemsRow, _Mapping]]] = ...) -> None: ...
    class ItemsRow(_message.Message):
        __slots__ = ("no", "description", "case_object_item", "operator", "left_parenthesis", "right_parenthesis", "group_factor", "case_object_factor", "case_object_sub_result", "case_object_sub_result_id", "case_object_load_type", "group_load_type", "action", "is_leading", "gamma", "psi", "xi", "k_fi", "c_esl", "k_def", "psi_0", "psi_1", "psi_2", "fi", "gamma_0", "alfa", "k_f", "phi", "rho", "omega_0", "gamma_l_1", "k_creep", "gamma_n", "j_2", "omega_m", "omega_n", "d1", "d2")
        class Operator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            OPERATOR_OR: _ClassVar[ResultCombination.ItemsRow.Operator]
            OPERATOR_AND: _ClassVar[ResultCombination.ItemsRow.Operator]
            OPERATOR_NONE: _ClassVar[ResultCombination.ItemsRow.Operator]
        OPERATOR_OR: ResultCombination.ItemsRow.Operator
        OPERATOR_AND: ResultCombination.ItemsRow.Operator
        OPERATOR_NONE: ResultCombination.ItemsRow.Operator
        class CaseObjectSubResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            CASE_OBJECT_SUB_RESULT_INCREMENTAL_FINAL_STATE: _ClassVar[ResultCombination.ItemsRow.CaseObjectSubResult]
            CASE_OBJECT_SUB_RESULT_INCREMENTAL_ALL: _ClassVar[ResultCombination.ItemsRow.CaseObjectSubResult]
            CASE_OBJECT_SUB_RESULT_INCREMENTAL_SUB_RESULT_ID: _ClassVar[ResultCombination.ItemsRow.CaseObjectSubResult]
            CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_ABSOLUTE_SUM: _ClassVar[ResultCombination.ItemsRow.CaseObjectSubResult]
            CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_DIRECTION_X: _ClassVar[ResultCombination.ItemsRow.CaseObjectSubResult]
            CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_DIRECTION_X_WITH_MODE_SHAPE: _ClassVar[ResultCombination.ItemsRow.CaseObjectSubResult]
            CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_DIRECTION_Y: _ClassVar[ResultCombination.ItemsRow.CaseObjectSubResult]
            CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_DIRECTION_Y_WITH_MODE_SHAPE: _ClassVar[ResultCombination.ItemsRow.CaseObjectSubResult]
            CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_DIRECTION_Z: _ClassVar[ResultCombination.ItemsRow.CaseObjectSubResult]
            CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_DIRECTION_Z_WITH_MODE_SHAPE: _ClassVar[ResultCombination.ItemsRow.CaseObjectSubResult]
            CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_SCALED_SUMS_ENVELOPE: _ClassVar[ResultCombination.ItemsRow.CaseObjectSubResult]
            CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_SCALED_SUM_FULL_X: _ClassVar[ResultCombination.ItemsRow.CaseObjectSubResult]
            CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_SCALED_SUM_FULL_Y: _ClassVar[ResultCombination.ItemsRow.CaseObjectSubResult]
            CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_SCALED_SUM_FULL_Z: _ClassVar[ResultCombination.ItemsRow.CaseObjectSubResult]
            CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_SRSS: _ClassVar[ResultCombination.ItemsRow.CaseObjectSubResult]
        CASE_OBJECT_SUB_RESULT_INCREMENTAL_FINAL_STATE: ResultCombination.ItemsRow.CaseObjectSubResult
        CASE_OBJECT_SUB_RESULT_INCREMENTAL_ALL: ResultCombination.ItemsRow.CaseObjectSubResult
        CASE_OBJECT_SUB_RESULT_INCREMENTAL_SUB_RESULT_ID: ResultCombination.ItemsRow.CaseObjectSubResult
        CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_ABSOLUTE_SUM: ResultCombination.ItemsRow.CaseObjectSubResult
        CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_DIRECTION_X: ResultCombination.ItemsRow.CaseObjectSubResult
        CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_DIRECTION_X_WITH_MODE_SHAPE: ResultCombination.ItemsRow.CaseObjectSubResult
        CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_DIRECTION_Y: ResultCombination.ItemsRow.CaseObjectSubResult
        CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_DIRECTION_Y_WITH_MODE_SHAPE: ResultCombination.ItemsRow.CaseObjectSubResult
        CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_DIRECTION_Z: ResultCombination.ItemsRow.CaseObjectSubResult
        CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_DIRECTION_Z_WITH_MODE_SHAPE: ResultCombination.ItemsRow.CaseObjectSubResult
        CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_SCALED_SUMS_ENVELOPE: ResultCombination.ItemsRow.CaseObjectSubResult
        CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_SCALED_SUM_FULL_X: ResultCombination.ItemsRow.CaseObjectSubResult
        CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_SCALED_SUM_FULL_Y: ResultCombination.ItemsRow.CaseObjectSubResult
        CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_SCALED_SUM_FULL_Z: ResultCombination.ItemsRow.CaseObjectSubResult
        CASE_OBJECT_SUB_RESULT_SPECTRAL_ANALYSIS_SRSS: ResultCombination.ItemsRow.CaseObjectSubResult
        class CaseObjectLoadType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            CASE_OBJECT_LOAD_TYPE_TRANSIENT: _ClassVar[ResultCombination.ItemsRow.CaseObjectLoadType]
            CASE_OBJECT_LOAD_TYPE_PERMANENT: _ClassVar[ResultCombination.ItemsRow.CaseObjectLoadType]
        CASE_OBJECT_LOAD_TYPE_TRANSIENT: ResultCombination.ItemsRow.CaseObjectLoadType
        CASE_OBJECT_LOAD_TYPE_PERMANENT: ResultCombination.ItemsRow.CaseObjectLoadType
        class GroupLoadType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            GROUP_LOAD_TYPE_TRANSIENT: _ClassVar[ResultCombination.ItemsRow.GroupLoadType]
            GROUP_LOAD_TYPE_PERMANENT: _ClassVar[ResultCombination.ItemsRow.GroupLoadType]
        GROUP_LOAD_TYPE_TRANSIENT: ResultCombination.ItemsRow.GroupLoadType
        GROUP_LOAD_TYPE_PERMANENT: ResultCombination.ItemsRow.GroupLoadType
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        CASE_OBJECT_ITEM_FIELD_NUMBER: _ClassVar[int]
        OPERATOR_FIELD_NUMBER: _ClassVar[int]
        LEFT_PARENTHESIS_FIELD_NUMBER: _ClassVar[int]
        RIGHT_PARENTHESIS_FIELD_NUMBER: _ClassVar[int]
        GROUP_FACTOR_FIELD_NUMBER: _ClassVar[int]
        CASE_OBJECT_FACTOR_FIELD_NUMBER: _ClassVar[int]
        CASE_OBJECT_SUB_RESULT_FIELD_NUMBER: _ClassVar[int]
        CASE_OBJECT_SUB_RESULT_ID_FIELD_NUMBER: _ClassVar[int]
        CASE_OBJECT_LOAD_TYPE_FIELD_NUMBER: _ClassVar[int]
        GROUP_LOAD_TYPE_FIELD_NUMBER: _ClassVar[int]
        ACTION_FIELD_NUMBER: _ClassVar[int]
        IS_LEADING_FIELD_NUMBER: _ClassVar[int]
        GAMMA_FIELD_NUMBER: _ClassVar[int]
        PSI_FIELD_NUMBER: _ClassVar[int]
        XI_FIELD_NUMBER: _ClassVar[int]
        K_FI_FIELD_NUMBER: _ClassVar[int]
        C_ESL_FIELD_NUMBER: _ClassVar[int]
        K_DEF_FIELD_NUMBER: _ClassVar[int]
        PSI_0_FIELD_NUMBER: _ClassVar[int]
        PSI_1_FIELD_NUMBER: _ClassVar[int]
        PSI_2_FIELD_NUMBER: _ClassVar[int]
        FI_FIELD_NUMBER: _ClassVar[int]
        GAMMA_0_FIELD_NUMBER: _ClassVar[int]
        ALFA_FIELD_NUMBER: _ClassVar[int]
        K_F_FIELD_NUMBER: _ClassVar[int]
        PHI_FIELD_NUMBER: _ClassVar[int]
        RHO_FIELD_NUMBER: _ClassVar[int]
        OMEGA_0_FIELD_NUMBER: _ClassVar[int]
        GAMMA_L_1_FIELD_NUMBER: _ClassVar[int]
        K_CREEP_FIELD_NUMBER: _ClassVar[int]
        GAMMA_N_FIELD_NUMBER: _ClassVar[int]
        J_2_FIELD_NUMBER: _ClassVar[int]
        OMEGA_M_FIELD_NUMBER: _ClassVar[int]
        OMEGA_N_FIELD_NUMBER: _ClassVar[int]
        D1_FIELD_NUMBER: _ClassVar[int]
        D2_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        case_object_item: _object_id_pb2.ObjectId
        operator: ResultCombination.ItemsRow.Operator
        left_parenthesis: bool
        right_parenthesis: bool
        group_factor: float
        case_object_factor: float
        case_object_sub_result: ResultCombination.ItemsRow.CaseObjectSubResult
        case_object_sub_result_id: int
        case_object_load_type: ResultCombination.ItemsRow.CaseObjectLoadType
        group_load_type: ResultCombination.ItemsRow.GroupLoadType
        action: int
        is_leading: bool
        gamma: float
        psi: float
        xi: float
        k_fi: float
        c_esl: float
        k_def: float
        psi_0: float
        psi_1: float
        psi_2: float
        fi: float
        gamma_0: float
        alfa: float
        k_f: float
        phi: float
        rho: float
        omega_0: float
        gamma_l_1: float
        k_creep: float
        gamma_n: float
        j_2: float
        omega_m: float
        omega_n: float
        d1: float
        d2: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., case_object_item: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., operator: _Optional[_Union[ResultCombination.ItemsRow.Operator, str]] = ..., left_parenthesis: bool = ..., right_parenthesis: bool = ..., group_factor: _Optional[float] = ..., case_object_factor: _Optional[float] = ..., case_object_sub_result: _Optional[_Union[ResultCombination.ItemsRow.CaseObjectSubResult, str]] = ..., case_object_sub_result_id: _Optional[int] = ..., case_object_load_type: _Optional[_Union[ResultCombination.ItemsRow.CaseObjectLoadType, str]] = ..., group_load_type: _Optional[_Union[ResultCombination.ItemsRow.GroupLoadType, str]] = ..., action: _Optional[int] = ..., is_leading: bool = ..., gamma: _Optional[float] = ..., psi: _Optional[float] = ..., xi: _Optional[float] = ..., k_fi: _Optional[float] = ..., c_esl: _Optional[float] = ..., k_def: _Optional[float] = ..., psi_0: _Optional[float] = ..., psi_1: _Optional[float] = ..., psi_2: _Optional[float] = ..., fi: _Optional[float] = ..., gamma_0: _Optional[float] = ..., alfa: _Optional[float] = ..., k_f: _Optional[float] = ..., phi: _Optional[float] = ..., rho: _Optional[float] = ..., omega_0: _Optional[float] = ..., gamma_l_1: _Optional[float] = ..., k_creep: _Optional[float] = ..., gamma_n: _Optional[float] = ..., j_2: _Optional[float] = ..., omega_m: _Optional[float] = ..., omega_n: _Optional[float] = ..., d1: _Optional[float] = ..., d2: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    DESIGN_SITUATION_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TO_SOLVE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    COMBINATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    SRSS_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    SRSS_EXTREME_VALUE_SIGN_FIELD_NUMBER: _ClassVar[int]
    SRSS_USE_EQUIVALENT_LINEAR_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    SRSS_ACCORDING_LOAD_CASE_OR_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    COMBINATION_RULE_STR_FIELD_NUMBER: _ClassVar[int]
    GENERATE_SUBCOMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    LOAD_DURATION_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_CONSTRUCTION_STAGE_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_CONSTRUCTION_STAGE_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    design_situation: int
    user_defined_name_enabled: bool
    name: str
    to_solve: bool
    comment: str
    combination_type: ResultCombination.CombinationType
    srss_combination: bool
    srss_extreme_value_sign: ResultCombination.SrssExtremeValueSign
    srss_use_equivalent_linear_combination: bool
    srss_according_load_case_or_combination: _object_id_pb2.ObjectId
    items: ResultCombination.ItemsTable
    combination_rule_str: str
    generate_subcombinations: bool
    load_duration: ResultCombination.LoadDuration
    is_generated: bool
    consider_construction_stage: int
    consider_construction_stage_active: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., design_situation: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., to_solve: bool = ..., comment: _Optional[str] = ..., combination_type: _Optional[_Union[ResultCombination.CombinationType, str]] = ..., srss_combination: bool = ..., srss_extreme_value_sign: _Optional[_Union[ResultCombination.SrssExtremeValueSign, str]] = ..., srss_use_equivalent_linear_combination: bool = ..., srss_according_load_case_or_combination: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., items: _Optional[_Union[ResultCombination.ItemsTable, _Mapping]] = ..., combination_rule_str: _Optional[str] = ..., generate_subcombinations: bool = ..., load_duration: _Optional[_Union[ResultCombination.LoadDuration, str]] = ..., is_generated: bool = ..., consider_construction_stage: _Optional[int] = ..., consider_construction_stage_active: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
