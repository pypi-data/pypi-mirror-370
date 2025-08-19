from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LoadCombination(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "to_solve", "comment", "items", "combination_rule_str", "id_for_export_import", "metadata_for_export_import")
    class ItemsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[LoadCombination.ItemsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LoadCombination.ItemsRow, _Mapping]]] = ...) -> None: ...
    class ItemsRow(_message.Message):
        __slots__ = ("no", "description", "factor", "load_case", "action", "is_leading", "gamma", "psi", "xi", "k_fi", "c_esl", "k_def", "psi_0", "psi_1", "psi_2", "fi", "gamma_0", "alfa", "k_f", "phi", "rho", "omega_0", "gamma_l_1", "k_creep", "gamma_n", "j_2", "omega_m", "omega_n", "d1", "d2", "shift", "amplitude_function", "time_diagram", "time_slip")
        class AmplitudeFunction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            AMPLITUDE_FUNCTION_CONSTANT: _ClassVar[LoadCombination.ItemsRow.AmplitudeFunction]
            AMPLITUDE_FUNCTION_LINEAR: _ClassVar[LoadCombination.ItemsRow.AmplitudeFunction]
            AMPLITUDE_FUNCTION_QUADRATIC: _ClassVar[LoadCombination.ItemsRow.AmplitudeFunction]
        AMPLITUDE_FUNCTION_CONSTANT: LoadCombination.ItemsRow.AmplitudeFunction
        AMPLITUDE_FUNCTION_LINEAR: LoadCombination.ItemsRow.AmplitudeFunction
        AMPLITUDE_FUNCTION_QUADRATIC: LoadCombination.ItemsRow.AmplitudeFunction
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FACTOR_FIELD_NUMBER: _ClassVar[int]
        LOAD_CASE_FIELD_NUMBER: _ClassVar[int]
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
        SHIFT_FIELD_NUMBER: _ClassVar[int]
        AMPLITUDE_FUNCTION_FIELD_NUMBER: _ClassVar[int]
        TIME_DIAGRAM_FIELD_NUMBER: _ClassVar[int]
        TIME_SLIP_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        factor: float
        load_case: int
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
        shift: float
        amplitude_function: LoadCombination.ItemsRow.AmplitudeFunction
        time_diagram: int
        time_slip: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., factor: _Optional[float] = ..., load_case: _Optional[int] = ..., action: _Optional[int] = ..., is_leading: bool = ..., gamma: _Optional[float] = ..., psi: _Optional[float] = ..., xi: _Optional[float] = ..., k_fi: _Optional[float] = ..., c_esl: _Optional[float] = ..., k_def: _Optional[float] = ..., psi_0: _Optional[float] = ..., psi_1: _Optional[float] = ..., psi_2: _Optional[float] = ..., fi: _Optional[float] = ..., gamma_0: _Optional[float] = ..., alfa: _Optional[float] = ..., k_f: _Optional[float] = ..., phi: _Optional[float] = ..., rho: _Optional[float] = ..., omega_0: _Optional[float] = ..., gamma_l_1: _Optional[float] = ..., k_creep: _Optional[float] = ..., gamma_n: _Optional[float] = ..., j_2: _Optional[float] = ..., omega_m: _Optional[float] = ..., omega_n: _Optional[float] = ..., d1: _Optional[float] = ..., d2: _Optional[float] = ..., shift: _Optional[float] = ..., amplitude_function: _Optional[_Union[LoadCombination.ItemsRow.AmplitudeFunction, str]] = ..., time_diagram: _Optional[int] = ..., time_slip: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TO_SOLVE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    COMBINATION_RULE_STR_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    to_solve: bool
    comment: str
    items: LoadCombination.ItemsTable
    combination_rule_str: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., to_solve: bool = ..., comment: _Optional[str] = ..., items: _Optional[_Union[LoadCombination.ItemsTable, _Mapping]] = ..., combination_rule_str: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
