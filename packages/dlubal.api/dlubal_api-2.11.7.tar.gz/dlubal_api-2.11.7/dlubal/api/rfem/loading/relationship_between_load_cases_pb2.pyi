from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RelationshipBetweenLoadCases(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "inclusive_load_cases", "exclusive_load_cases", "comment", "assigned_to", "id_for_export_import", "metadata_for_export_import")
    class InclusiveLoadCasesTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[RelationshipBetweenLoadCases.InclusiveLoadCasesRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[RelationshipBetweenLoadCases.InclusiveLoadCasesRow, _Mapping]]] = ...) -> None: ...
    class InclusiveLoadCasesRow(_message.Message):
        __slots__ = ("no", "description", "selected_load_cases", "assigned_load_cases", "comment")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        SELECTED_LOAD_CASES_FIELD_NUMBER: _ClassVar[int]
        ASSIGNED_LOAD_CASES_FIELD_NUMBER: _ClassVar[int]
        COMMENT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        selected_load_cases: _containers.RepeatedScalarFieldContainer[int]
        assigned_load_cases: _containers.RepeatedScalarFieldContainer[int]
        comment: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., selected_load_cases: _Optional[_Iterable[int]] = ..., assigned_load_cases: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ...) -> None: ...
    class ExclusiveLoadCasesTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[RelationshipBetweenLoadCases.ExclusiveLoadCasesRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[RelationshipBetweenLoadCases.ExclusiveLoadCasesRow, _Mapping]]] = ...) -> None: ...
    class ExclusiveLoadCasesRow(_message.Message):
        __slots__ = ("no", "description", "selected_load_cases", "assigned_load_cases", "comment")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        SELECTED_LOAD_CASES_FIELD_NUMBER: _ClassVar[int]
        ASSIGNED_LOAD_CASES_FIELD_NUMBER: _ClassVar[int]
        COMMENT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        selected_load_cases: _containers.RepeatedScalarFieldContainer[int]
        assigned_load_cases: _containers.RepeatedScalarFieldContainer[int]
        comment: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., selected_load_cases: _Optional[_Iterable[int]] = ..., assigned_load_cases: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    INCLUSIVE_LOAD_CASES_FIELD_NUMBER: _ClassVar[int]
    EXCLUSIVE_LOAD_CASES_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    inclusive_load_cases: RelationshipBetweenLoadCases.InclusiveLoadCasesTable
    exclusive_load_cases: RelationshipBetweenLoadCases.ExclusiveLoadCasesTable
    comment: str
    assigned_to: _containers.RepeatedScalarFieldContainer[int]
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., inclusive_load_cases: _Optional[_Union[RelationshipBetweenLoadCases.InclusiveLoadCasesTable, _Mapping]] = ..., exclusive_load_cases: _Optional[_Union[RelationshipBetweenLoadCases.ExclusiveLoadCasesTable, _Mapping]] = ..., comment: _Optional[str] = ..., assigned_to: _Optional[_Iterable[int]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
