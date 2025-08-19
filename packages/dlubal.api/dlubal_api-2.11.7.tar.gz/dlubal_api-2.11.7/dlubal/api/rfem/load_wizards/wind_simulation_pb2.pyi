from dlubal.api.rfem import object_id_pb2 as _object_id_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WindSimulation(_message.Message):
    __slots__ = ("no", "type", "user_defined_name_enabled", "name", "active", "wind_profile", "wind_simulation_analysis_settings", "wind_direction_type", "uniform_wind_direction_step", "uniform_wind_direction_range_start", "uniform_wind_direction_range_end", "user_defined_list_of_wind_directions", "generate_into_load_cases", "consider_initial_state", "initial_state_case", "initial_state_definition_type", "individual_factors_of_selected_objects_table", "comment", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[WindSimulation.Type]
        TYPE_STANDARD: _ClassVar[WindSimulation.Type]
    TYPE_UNKNOWN: WindSimulation.Type
    TYPE_STANDARD: WindSimulation.Type
    class WindDirectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        WIND_DIRECTION_TYPE_UNIFORM: _ClassVar[WindSimulation.WindDirectionType]
        WIND_DIRECTION_TYPE_USER_DEFINED: _ClassVar[WindSimulation.WindDirectionType]
    WIND_DIRECTION_TYPE_UNIFORM: WindSimulation.WindDirectionType
    WIND_DIRECTION_TYPE_USER_DEFINED: WindSimulation.WindDirectionType
    class InitialStateDefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        INITIAL_STATE_DEFINITION_TYPE_FINAL_STATE: _ClassVar[WindSimulation.InitialStateDefinitionType]
        INITIAL_STATE_DEFINITION_TYPE_STIFFNESS: _ClassVar[WindSimulation.InitialStateDefinitionType]
        INITIAL_STATE_DEFINITION_TYPE_STRAINS: _ClassVar[WindSimulation.InitialStateDefinitionType]
        INITIAL_STATE_DEFINITION_TYPE_STRAINS_WITH_USER_DEFINED_FACTORS: _ClassVar[WindSimulation.InitialStateDefinitionType]
    INITIAL_STATE_DEFINITION_TYPE_FINAL_STATE: WindSimulation.InitialStateDefinitionType
    INITIAL_STATE_DEFINITION_TYPE_STIFFNESS: WindSimulation.InitialStateDefinitionType
    INITIAL_STATE_DEFINITION_TYPE_STRAINS: WindSimulation.InitialStateDefinitionType
    INITIAL_STATE_DEFINITION_TYPE_STRAINS_WITH_USER_DEFINED_FACTORS: WindSimulation.InitialStateDefinitionType
    class GenerateIntoLoadCasesTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[WindSimulation.GenerateIntoLoadCasesRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[WindSimulation.GenerateIntoLoadCasesRow, _Mapping]]] = ...) -> None: ...
    class GenerateIntoLoadCasesRow(_message.Message):
        __slots__ = ("no", "description", "direction", "load_case")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        DIRECTION_FIELD_NUMBER: _ClassVar[int]
        LOAD_CASE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        direction: float
        load_case: int
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., direction: _Optional[float] = ..., load_case: _Optional[int] = ...) -> None: ...
    class IndividualFactorsOfSelectedObjectsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow, _Mapping]]] = ...) -> None: ...
    class IndividualFactorsOfSelectedObjectsTableRow(_message.Message):
        __slots__ = ("no", "description", "object_type", "object_list", "strain", "factor", "comment")
        class ObjectType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            OBJECT_TYPE_UNKNOWN: _ClassVar[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType]
            OBJECT_TYPE_LINE_HINGE: _ClassVar[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType]
            OBJECT_TYPE_LINE_WITH_SUPPORT: _ClassVar[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType]
            OBJECT_TYPE_MEMBER: _ClassVar[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType]
            OBJECT_TYPE_MEMBER_HINGE: _ClassVar[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType]
            OBJECT_TYPE_NODE_WITH_SUPPORT: _ClassVar[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType]
            OBJECT_TYPE_SOLID: _ClassVar[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType]
            OBJECT_TYPE_SURFACE: _ClassVar[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType]
        OBJECT_TYPE_UNKNOWN: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType
        OBJECT_TYPE_LINE_HINGE: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType
        OBJECT_TYPE_LINE_WITH_SUPPORT: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType
        OBJECT_TYPE_MEMBER: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType
        OBJECT_TYPE_MEMBER_HINGE: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType
        OBJECT_TYPE_NODE_WITH_SUPPORT: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType
        OBJECT_TYPE_SOLID: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType
        OBJECT_TYPE_SURFACE: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType
        class Strain(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            STRAIN_ALL: _ClassVar[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain]
            STRAIN_ALONG_X: _ClassVar[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain]
            STRAIN_ALONG_Y: _ClassVar[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain]
            STRAIN_ALONG_Z: _ClassVar[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain]
            STRAIN_AROUND_X: _ClassVar[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain]
            STRAIN_AROUND_Y: _ClassVar[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain]
            STRAIN_AROUND_Z: _ClassVar[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain]
        STRAIN_ALL: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain
        STRAIN_ALONG_X: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain
        STRAIN_ALONG_Y: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain
        STRAIN_ALONG_Z: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain
        STRAIN_AROUND_X: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain
        STRAIN_AROUND_Y: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain
        STRAIN_AROUND_Z: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
        OBJECT_LIST_FIELD_NUMBER: _ClassVar[int]
        STRAIN_FIELD_NUMBER: _ClassVar[int]
        FACTOR_FIELD_NUMBER: _ClassVar[int]
        COMMENT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        object_type: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType
        object_list: _containers.RepeatedScalarFieldContainer[int]
        strain: WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain
        factor: float
        comment: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., object_type: _Optional[_Union[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.ObjectType, str]] = ..., object_list: _Optional[_Iterable[int]] = ..., strain: _Optional[_Union[WindSimulation.IndividualFactorsOfSelectedObjectsTableRow.Strain, str]] = ..., factor: _Optional[float] = ..., comment: _Optional[str] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    WIND_PROFILE_FIELD_NUMBER: _ClassVar[int]
    WIND_SIMULATION_ANALYSIS_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    WIND_DIRECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    UNIFORM_WIND_DIRECTION_STEP_FIELD_NUMBER: _ClassVar[int]
    UNIFORM_WIND_DIRECTION_RANGE_START_FIELD_NUMBER: _ClassVar[int]
    UNIFORM_WIND_DIRECTION_RANGE_END_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_LIST_OF_WIND_DIRECTIONS_FIELD_NUMBER: _ClassVar[int]
    GENERATE_INTO_LOAD_CASES_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_INITIAL_STATE_FIELD_NUMBER: _ClassVar[int]
    INITIAL_STATE_CASE_FIELD_NUMBER: _ClassVar[int]
    INITIAL_STATE_DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    INDIVIDUAL_FACTORS_OF_SELECTED_OBJECTS_TABLE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: WindSimulation.Type
    user_defined_name_enabled: bool
    name: str
    active: bool
    wind_profile: int
    wind_simulation_analysis_settings: int
    wind_direction_type: WindSimulation.WindDirectionType
    uniform_wind_direction_step: float
    uniform_wind_direction_range_start: float
    uniform_wind_direction_range_end: float
    user_defined_list_of_wind_directions: _containers.RepeatedScalarFieldContainer[int]
    generate_into_load_cases: WindSimulation.GenerateIntoLoadCasesTable
    consider_initial_state: bool
    initial_state_case: _object_id_pb2.ObjectId
    initial_state_definition_type: WindSimulation.InitialStateDefinitionType
    individual_factors_of_selected_objects_table: WindSimulation.IndividualFactorsOfSelectedObjectsTable
    comment: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[WindSimulation.Type, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., active: bool = ..., wind_profile: _Optional[int] = ..., wind_simulation_analysis_settings: _Optional[int] = ..., wind_direction_type: _Optional[_Union[WindSimulation.WindDirectionType, str]] = ..., uniform_wind_direction_step: _Optional[float] = ..., uniform_wind_direction_range_start: _Optional[float] = ..., uniform_wind_direction_range_end: _Optional[float] = ..., user_defined_list_of_wind_directions: _Optional[_Iterable[int]] = ..., generate_into_load_cases: _Optional[_Union[WindSimulation.GenerateIntoLoadCasesTable, _Mapping]] = ..., consider_initial_state: bool = ..., initial_state_case: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., initial_state_definition_type: _Optional[_Union[WindSimulation.InitialStateDefinitionType, str]] = ..., individual_factors_of_selected_objects_table: _Optional[_Union[WindSimulation.IndividualFactorsOfSelectedObjectsTable, _Mapping]] = ..., comment: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
