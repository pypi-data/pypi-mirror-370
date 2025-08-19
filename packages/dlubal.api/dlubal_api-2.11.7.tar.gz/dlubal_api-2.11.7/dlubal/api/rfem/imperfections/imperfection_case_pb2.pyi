from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImperfectionCase(_message.Message):
    __slots__ = ("no", "type", "user_defined_name_enabled", "name", "assigned_to_load_cases", "assigned_to_load_combinations", "is_active", "assign_to_combinations_without_assigned_imperfection_case", "direction", "direction_for_level_direction", "coordinate_system", "load_case_for_notional_loads", "sway_coefficients_reciprocal", "level_imperfections", "source", "shape_from_load_case", "shape_from_load_combination", "buckling_shape", "delta_zero", "magnitude_assignment_type", "reference_node", "amount_of_modes_to_investigate", "eigenmode_automatically", "imperfection_cases_items", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[ImperfectionCase.Type]
        TYPE_BUCKLING_MODE: _ClassVar[ImperfectionCase.Type]
        TYPE_DYNAMIC_EIGENMODE: _ClassVar[ImperfectionCase.Type]
        TYPE_IMPERFECTION_CASES_GROUP: _ClassVar[ImperfectionCase.Type]
        TYPE_INITIAL_SWAY_VIA_TABLE: _ClassVar[ImperfectionCase.Type]
        TYPE_LOCAL_IMPERFECTIONS: _ClassVar[ImperfectionCase.Type]
        TYPE_NOTIONAL_LOADS_FROM_LOAD_CASE: _ClassVar[ImperfectionCase.Type]
        TYPE_STATIC_DEFORMATION: _ClassVar[ImperfectionCase.Type]
    TYPE_UNKNOWN: ImperfectionCase.Type
    TYPE_BUCKLING_MODE: ImperfectionCase.Type
    TYPE_DYNAMIC_EIGENMODE: ImperfectionCase.Type
    TYPE_IMPERFECTION_CASES_GROUP: ImperfectionCase.Type
    TYPE_INITIAL_SWAY_VIA_TABLE: ImperfectionCase.Type
    TYPE_LOCAL_IMPERFECTIONS: ImperfectionCase.Type
    TYPE_NOTIONAL_LOADS_FROM_LOAD_CASE: ImperfectionCase.Type
    TYPE_STATIC_DEFORMATION: ImperfectionCase.Type
    class Direction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIRECTION_LOCAL_X: _ClassVar[ImperfectionCase.Direction]
        DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: _ClassVar[ImperfectionCase.Direction]
        DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH_REVERSED: _ClassVar[ImperfectionCase.Direction]
        DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: _ClassVar[ImperfectionCase.Direction]
        DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH_REVERSED: _ClassVar[ImperfectionCase.Direction]
        DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: _ClassVar[ImperfectionCase.Direction]
        DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH_REVERSED: _ClassVar[ImperfectionCase.Direction]
        DIRECTION_LOCAL_Y: _ClassVar[ImperfectionCase.Direction]
        DIRECTION_LOCAL_Y_NEGATIVE: _ClassVar[ImperfectionCase.Direction]
        DIRECTION_LOCAL_Z: _ClassVar[ImperfectionCase.Direction]
        DIRECTION_LOCAL_Z_NEGATIVE: _ClassVar[ImperfectionCase.Direction]
        DIRECTION_SPATIAL: _ClassVar[ImperfectionCase.Direction]
        DIRECTION_SPATIAL_NEGATIVE: _ClassVar[ImperfectionCase.Direction]
    DIRECTION_LOCAL_X: ImperfectionCase.Direction
    DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: ImperfectionCase.Direction
    DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH_REVERSED: ImperfectionCase.Direction
    DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: ImperfectionCase.Direction
    DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH_REVERSED: ImperfectionCase.Direction
    DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: ImperfectionCase.Direction
    DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH_REVERSED: ImperfectionCase.Direction
    DIRECTION_LOCAL_Y: ImperfectionCase.Direction
    DIRECTION_LOCAL_Y_NEGATIVE: ImperfectionCase.Direction
    DIRECTION_LOCAL_Z: ImperfectionCase.Direction
    DIRECTION_LOCAL_Z_NEGATIVE: ImperfectionCase.Direction
    DIRECTION_SPATIAL: ImperfectionCase.Direction
    DIRECTION_SPATIAL_NEGATIVE: ImperfectionCase.Direction
    class DirectionForLevelDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIRECTION_FOR_LEVEL_DIRECTION_ALONG_X: _ClassVar[ImperfectionCase.DirectionForLevelDirection]
        DIRECTION_FOR_LEVEL_DIRECTION_ALONG_XY: _ClassVar[ImperfectionCase.DirectionForLevelDirection]
        DIRECTION_FOR_LEVEL_DIRECTION_ALONG_XZ: _ClassVar[ImperfectionCase.DirectionForLevelDirection]
        DIRECTION_FOR_LEVEL_DIRECTION_ALONG_Y: _ClassVar[ImperfectionCase.DirectionForLevelDirection]
        DIRECTION_FOR_LEVEL_DIRECTION_ALONG_YZ: _ClassVar[ImperfectionCase.DirectionForLevelDirection]
        DIRECTION_FOR_LEVEL_DIRECTION_ALONG_Z: _ClassVar[ImperfectionCase.DirectionForLevelDirection]
    DIRECTION_FOR_LEVEL_DIRECTION_ALONG_X: ImperfectionCase.DirectionForLevelDirection
    DIRECTION_FOR_LEVEL_DIRECTION_ALONG_XY: ImperfectionCase.DirectionForLevelDirection
    DIRECTION_FOR_LEVEL_DIRECTION_ALONG_XZ: ImperfectionCase.DirectionForLevelDirection
    DIRECTION_FOR_LEVEL_DIRECTION_ALONG_Y: ImperfectionCase.DirectionForLevelDirection
    DIRECTION_FOR_LEVEL_DIRECTION_ALONG_YZ: ImperfectionCase.DirectionForLevelDirection
    DIRECTION_FOR_LEVEL_DIRECTION_ALONG_Z: ImperfectionCase.DirectionForLevelDirection
    class Source(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SOURCE_OWN_LOAD_CASE_OR_COMBINATION: _ClassVar[ImperfectionCase.Source]
        SOURCE_AUTOMATICALLY: _ClassVar[ImperfectionCase.Source]
        SOURCE_LOAD_CASE: _ClassVar[ImperfectionCase.Source]
        SOURCE_LOAD_COMBINATION: _ClassVar[ImperfectionCase.Source]
    SOURCE_OWN_LOAD_CASE_OR_COMBINATION: ImperfectionCase.Source
    SOURCE_AUTOMATICALLY: ImperfectionCase.Source
    SOURCE_LOAD_CASE: ImperfectionCase.Source
    SOURCE_LOAD_COMBINATION: ImperfectionCase.Source
    class MagnitudeAssignmentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MAGNITUDE_ASSIGNMENT_TYPE_LOCATION_WITH_LARGEST_DISPLACEMENT: _ClassVar[ImperfectionCase.MagnitudeAssignmentType]
        MAGNITUDE_ASSIGNMENT_TYPE_SPECIFIC_NODE: _ClassVar[ImperfectionCase.MagnitudeAssignmentType]
    MAGNITUDE_ASSIGNMENT_TYPE_LOCATION_WITH_LARGEST_DISPLACEMENT: ImperfectionCase.MagnitudeAssignmentType
    MAGNITUDE_ASSIGNMENT_TYPE_SPECIFIC_NODE: ImperfectionCase.MagnitudeAssignmentType
    class LevelImperfectionsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[ImperfectionCase.LevelImperfectionsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[ImperfectionCase.LevelImperfectionsRow, _Mapping]]] = ...) -> None: ...
    class LevelImperfectionsRow(_message.Message):
        __slots__ = ("no", "description", "level", "e_1", "theta_1", "e_2", "theta_2", "comment")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        LEVEL_FIELD_NUMBER: _ClassVar[int]
        E_1_FIELD_NUMBER: _ClassVar[int]
        THETA_1_FIELD_NUMBER: _ClassVar[int]
        E_2_FIELD_NUMBER: _ClassVar[int]
        THETA_2_FIELD_NUMBER: _ClassVar[int]
        COMMENT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        level: float
        e_1: float
        theta_1: float
        e_2: float
        theta_2: float
        comment: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., level: _Optional[float] = ..., e_1: _Optional[float] = ..., theta_1: _Optional[float] = ..., e_2: _Optional[float] = ..., theta_2: _Optional[float] = ..., comment: _Optional[str] = ...) -> None: ...
    class ImperfectionCasesItemsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[ImperfectionCase.ImperfectionCasesItemsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[ImperfectionCase.ImperfectionCasesItemsRow, _Mapping]]] = ...) -> None: ...
    class ImperfectionCasesItemsRow(_message.Message):
        __slots__ = ("no", "description", "name", "factor", "operator", "comment")
        class Operator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            OPERATOR_OR: _ClassVar[ImperfectionCase.ImperfectionCasesItemsRow.Operator]
            OPERATOR_AND: _ClassVar[ImperfectionCase.ImperfectionCasesItemsRow.Operator]
            OPERATOR_NONE: _ClassVar[ImperfectionCase.ImperfectionCasesItemsRow.Operator]
        OPERATOR_OR: ImperfectionCase.ImperfectionCasesItemsRow.Operator
        OPERATOR_AND: ImperfectionCase.ImperfectionCasesItemsRow.Operator
        OPERATOR_NONE: ImperfectionCase.ImperfectionCasesItemsRow.Operator
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        FACTOR_FIELD_NUMBER: _ClassVar[int]
        OPERATOR_FIELD_NUMBER: _ClassVar[int]
        COMMENT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        name: int
        factor: float
        operator: ImperfectionCase.ImperfectionCasesItemsRow.Operator
        comment: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., name: _Optional[int] = ..., factor: _Optional[float] = ..., operator: _Optional[_Union[ImperfectionCase.ImperfectionCasesItemsRow.Operator, str]] = ..., comment: _Optional[str] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_LOAD_CASES_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_LOAD_COMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    ASSIGN_TO_COMBINATIONS_WITHOUT_ASSIGNED_IMPERFECTION_CASE_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FOR_LEVEL_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    LOAD_CASE_FOR_NOTIONAL_LOADS_FIELD_NUMBER: _ClassVar[int]
    SWAY_COEFFICIENTS_RECIPROCAL_FIELD_NUMBER: _ClassVar[int]
    LEVEL_IMPERFECTIONS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FROM_LOAD_CASE_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FROM_LOAD_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    BUCKLING_SHAPE_FIELD_NUMBER: _ClassVar[int]
    DELTA_ZERO_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_ASSIGNMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_NODE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_OF_MODES_TO_INVESTIGATE_FIELD_NUMBER: _ClassVar[int]
    EIGENMODE_AUTOMATICALLY_FIELD_NUMBER: _ClassVar[int]
    IMPERFECTION_CASES_ITEMS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: ImperfectionCase.Type
    user_defined_name_enabled: bool
    name: str
    assigned_to_load_cases: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_load_combinations: _containers.RepeatedScalarFieldContainer[int]
    is_active: bool
    assign_to_combinations_without_assigned_imperfection_case: bool
    direction: ImperfectionCase.Direction
    direction_for_level_direction: ImperfectionCase.DirectionForLevelDirection
    coordinate_system: int
    load_case_for_notional_loads: int
    sway_coefficients_reciprocal: bool
    level_imperfections: ImperfectionCase.LevelImperfectionsTable
    source: ImperfectionCase.Source
    shape_from_load_case: int
    shape_from_load_combination: int
    buckling_shape: int
    delta_zero: float
    magnitude_assignment_type: ImperfectionCase.MagnitudeAssignmentType
    reference_node: int
    amount_of_modes_to_investigate: int
    eigenmode_automatically: bool
    imperfection_cases_items: ImperfectionCase.ImperfectionCasesItemsTable
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[ImperfectionCase.Type, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., assigned_to_load_cases: _Optional[_Iterable[int]] = ..., assigned_to_load_combinations: _Optional[_Iterable[int]] = ..., is_active: bool = ..., assign_to_combinations_without_assigned_imperfection_case: bool = ..., direction: _Optional[_Union[ImperfectionCase.Direction, str]] = ..., direction_for_level_direction: _Optional[_Union[ImperfectionCase.DirectionForLevelDirection, str]] = ..., coordinate_system: _Optional[int] = ..., load_case_for_notional_loads: _Optional[int] = ..., sway_coefficients_reciprocal: bool = ..., level_imperfections: _Optional[_Union[ImperfectionCase.LevelImperfectionsTable, _Mapping]] = ..., source: _Optional[_Union[ImperfectionCase.Source, str]] = ..., shape_from_load_case: _Optional[int] = ..., shape_from_load_combination: _Optional[int] = ..., buckling_shape: _Optional[int] = ..., delta_zero: _Optional[float] = ..., magnitude_assignment_type: _Optional[_Union[ImperfectionCase.MagnitudeAssignmentType, str]] = ..., reference_node: _Optional[int] = ..., amount_of_modes_to_investigate: _Optional[int] = ..., eigenmode_automatically: bool = ..., imperfection_cases_items: _Optional[_Union[ImperfectionCase.ImperfectionCasesItemsTable, _Mapping]] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
