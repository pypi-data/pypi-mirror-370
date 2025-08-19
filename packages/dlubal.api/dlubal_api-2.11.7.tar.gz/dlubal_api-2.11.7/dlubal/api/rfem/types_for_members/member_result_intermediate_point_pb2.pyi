from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberResultIntermediatePoint(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "members", "point_count", "uniform_distribution", "distances_are_defined_as_absolute", "distances", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class DistancesTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberResultIntermediatePoint.DistancesRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberResultIntermediatePoint.DistancesRow, _Mapping]]] = ...) -> None: ...
    class DistancesRow(_message.Message):
        __slots__ = ("no", "description", "value", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        value: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., value: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    POINT_COUNT_FIELD_NUMBER: _ClassVar[int]
    UNIFORM_DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    DISTANCES_ARE_DEFINED_AS_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    DISTANCES_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    members: _containers.RepeatedScalarFieldContainer[int]
    point_count: int
    uniform_distribution: bool
    distances_are_defined_as_absolute: bool
    distances: MemberResultIntermediatePoint.DistancesTable
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., point_count: _Optional[int] = ..., uniform_distribution: bool = ..., distances_are_defined_as_absolute: bool = ..., distances: _Optional[_Union[MemberResultIntermediatePoint.DistancesTable, _Mapping]] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
