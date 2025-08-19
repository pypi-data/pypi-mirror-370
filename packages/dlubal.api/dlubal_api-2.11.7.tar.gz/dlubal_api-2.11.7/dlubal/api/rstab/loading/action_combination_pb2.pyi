from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ActionCombination(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "attribute_always_editable", "comment", "design_situation", "items", "active", "combination_type", "generated_load_combinations", "generated_result_combinations", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class CombinationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COMBINATION_TYPE_GENERAL: _ClassVar[ActionCombination.CombinationType]
        COMBINATION_TYPE_ENVELOPE_PERMANENT: _ClassVar[ActionCombination.CombinationType]
        COMBINATION_TYPE_ENVELOPE_TRANSIENT: _ClassVar[ActionCombination.CombinationType]
        COMBINATION_TYPE_SUPERPOSITION: _ClassVar[ActionCombination.CombinationType]
    COMBINATION_TYPE_GENERAL: ActionCombination.CombinationType
    COMBINATION_TYPE_ENVELOPE_PERMANENT: ActionCombination.CombinationType
    COMBINATION_TYPE_ENVELOPE_TRANSIENT: ActionCombination.CombinationType
    COMBINATION_TYPE_SUPERPOSITION: ActionCombination.CombinationType
    class ItemsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[ActionCombination.ItemsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[ActionCombination.ItemsRow, _Mapping]]] = ...) -> None: ...
    class ItemsRow(_message.Message):
        __slots__ = ("no", "description", "action_item", "operator", "left_parenthesis", "right_parenthesis", "group_factor", "action_factor", "action_load_type", "group_load_type", "action", "is_leading", "gamma", "psi", "xi", "k_fi", "c_esl", "k_def", "psi_0", "psi_1", "psi_2", "fi", "gamma_0", "alfa", "k_f", "phi", "rho", "omega_0", "gamma_l_1", "k_creep", "gamma_n", "j_2", "omega_m", "omega_n", "d1", "d2")
        class Operator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            OPERATOR_OR: _ClassVar[ActionCombination.ItemsRow.Operator]
            OPERATOR_AND: _ClassVar[ActionCombination.ItemsRow.Operator]
            OPERATOR_NONE: _ClassVar[ActionCombination.ItemsRow.Operator]
        OPERATOR_OR: ActionCombination.ItemsRow.Operator
        OPERATOR_AND: ActionCombination.ItemsRow.Operator
        OPERATOR_NONE: ActionCombination.ItemsRow.Operator
        class ActionLoadType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            ACTION_LOAD_TYPE_TRANSIENT: _ClassVar[ActionCombination.ItemsRow.ActionLoadType]
            ACTION_LOAD_TYPE_PERMANENT: _ClassVar[ActionCombination.ItemsRow.ActionLoadType]
        ACTION_LOAD_TYPE_TRANSIENT: ActionCombination.ItemsRow.ActionLoadType
        ACTION_LOAD_TYPE_PERMANENT: ActionCombination.ItemsRow.ActionLoadType
        class GroupLoadType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            GROUP_LOAD_TYPE_TRANSIENT: _ClassVar[ActionCombination.ItemsRow.GroupLoadType]
            GROUP_LOAD_TYPE_PERMANENT: _ClassVar[ActionCombination.ItemsRow.GroupLoadType]
        GROUP_LOAD_TYPE_TRANSIENT: ActionCombination.ItemsRow.GroupLoadType
        GROUP_LOAD_TYPE_PERMANENT: ActionCombination.ItemsRow.GroupLoadType
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        ACTION_ITEM_FIELD_NUMBER: _ClassVar[int]
        OPERATOR_FIELD_NUMBER: _ClassVar[int]
        LEFT_PARENTHESIS_FIELD_NUMBER: _ClassVar[int]
        RIGHT_PARENTHESIS_FIELD_NUMBER: _ClassVar[int]
        GROUP_FACTOR_FIELD_NUMBER: _ClassVar[int]
        ACTION_FACTOR_FIELD_NUMBER: _ClassVar[int]
        ACTION_LOAD_TYPE_FIELD_NUMBER: _ClassVar[int]
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
        action_item: int
        operator: ActionCombination.ItemsRow.Operator
        left_parenthesis: bool
        right_parenthesis: bool
        group_factor: float
        action_factor: float
        action_load_type: ActionCombination.ItemsRow.ActionLoadType
        group_load_type: ActionCombination.ItemsRow.GroupLoadType
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
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., action_item: _Optional[int] = ..., operator: _Optional[_Union[ActionCombination.ItemsRow.Operator, str]] = ..., left_parenthesis: bool = ..., right_parenthesis: bool = ..., group_factor: _Optional[float] = ..., action_factor: _Optional[float] = ..., action_load_type: _Optional[_Union[ActionCombination.ItemsRow.ActionLoadType, str]] = ..., group_load_type: _Optional[_Union[ActionCombination.ItemsRow.GroupLoadType, str]] = ..., action: _Optional[int] = ..., is_leading: bool = ..., gamma: _Optional[float] = ..., psi: _Optional[float] = ..., xi: _Optional[float] = ..., k_fi: _Optional[float] = ..., c_esl: _Optional[float] = ..., k_def: _Optional[float] = ..., psi_0: _Optional[float] = ..., psi_1: _Optional[float] = ..., psi_2: _Optional[float] = ..., fi: _Optional[float] = ..., gamma_0: _Optional[float] = ..., alfa: _Optional[float] = ..., k_f: _Optional[float] = ..., phi: _Optional[float] = ..., rho: _Optional[float] = ..., omega_0: _Optional[float] = ..., gamma_l_1: _Optional[float] = ..., k_creep: _Optional[float] = ..., gamma_n: _Optional[float] = ..., j_2: _Optional[float] = ..., omega_m: _Optional[float] = ..., omega_n: _Optional[float] = ..., d1: _Optional[float] = ..., d2: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_ALWAYS_EDITABLE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    DESIGN_SITUATION_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COMBINATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    GENERATED_LOAD_COMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    GENERATED_RESULT_COMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    attribute_always_editable: str
    comment: str
    design_situation: int
    items: ActionCombination.ItemsTable
    active: bool
    combination_type: ActionCombination.CombinationType
    generated_load_combinations: _containers.RepeatedScalarFieldContainer[int]
    generated_result_combinations: _containers.RepeatedScalarFieldContainer[int]
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., attribute_always_editable: _Optional[str] = ..., comment: _Optional[str] = ..., design_situation: _Optional[int] = ..., items: _Optional[_Union[ActionCombination.ItemsTable, _Mapping]] = ..., active: bool = ..., combination_type: _Optional[_Union[ActionCombination.CombinationType, str]] = ..., generated_load_combinations: _Optional[_Iterable[int]] = ..., generated_result_combinations: _Optional[_Iterable[int]] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
