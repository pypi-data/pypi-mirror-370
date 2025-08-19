from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GlassDesignSlsConfiguration(_message.Message):
    __slots__ = ("assigned_to_all_solid_sets", "assigned_to_all_solids", "assigned_to_all_surfaces", "assigned_to_solid_sets", "assigned_to_solids", "assigned_to_surfaces", "comment", "name", "no", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    ASSIGNED_TO_ALL_SOLID_SETS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_ALL_SOLIDS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_ALL_SURFACES_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_SOLID_SETS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_SOLIDS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_SURFACES_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    assigned_to_all_solid_sets: bool
    assigned_to_all_solids: bool
    assigned_to_all_surfaces: bool
    assigned_to_solid_sets: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_solids: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_surfaces: _containers.RepeatedScalarFieldContainer[int]
    comment: str
    name: str
    no: int
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, assigned_to_all_solid_sets: bool = ..., assigned_to_all_solids: bool = ..., assigned_to_all_surfaces: bool = ..., assigned_to_solid_sets: _Optional[_Iterable[int]] = ..., assigned_to_solids: _Optional[_Iterable[int]] = ..., assigned_to_surfaces: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
