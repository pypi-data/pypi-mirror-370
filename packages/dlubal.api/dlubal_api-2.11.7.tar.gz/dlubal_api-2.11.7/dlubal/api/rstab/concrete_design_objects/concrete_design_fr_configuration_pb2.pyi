from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ConcreteDesignFrConfiguration(_message.Message):
    __slots__ = ("assigned_to_all_deep_beams", "assigned_to_all_design_strips", "assigned_to_all_member_sets", "assigned_to_all_members", "assigned_to_all_nodes", "assigned_to_all_shear_walls", "assigned_to_all_surface_sets", "assigned_to_all_surfaces", "assigned_to_deep_beams", "assigned_to_design_strips", "assigned_to_member_sets", "assigned_to_members", "assigned_to_nodes", "assigned_to_shear_walls", "assigned_to_surface_sets", "assigned_to_surfaces", "comment", "generating_object_info", "is_generated", "name", "no", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    ASSIGNED_TO_ALL_DEEP_BEAMS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_ALL_DESIGN_STRIPS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_ALL_MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_ALL_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_ALL_NODES_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_ALL_SHEAR_WALLS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_ALL_SURFACE_SETS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_ALL_SURFACES_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_DEEP_BEAMS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_DESIGN_STRIPS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_NODES_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_SHEAR_WALLS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_SURFACE_SETS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_SURFACES_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    assigned_to_all_deep_beams: bool
    assigned_to_all_design_strips: bool
    assigned_to_all_member_sets: bool
    assigned_to_all_members: bool
    assigned_to_all_nodes: bool
    assigned_to_all_shear_walls: bool
    assigned_to_all_surface_sets: bool
    assigned_to_all_surfaces: bool
    assigned_to_deep_beams: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_design_strips: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_member_sets: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_members: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_nodes: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_shear_walls: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_surface_sets: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_surfaces: _containers.RepeatedScalarFieldContainer[int]
    comment: str
    generating_object_info: str
    is_generated: bool
    name: str
    no: int
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, assigned_to_all_deep_beams: bool = ..., assigned_to_all_design_strips: bool = ..., assigned_to_all_member_sets: bool = ..., assigned_to_all_members: bool = ..., assigned_to_all_nodes: bool = ..., assigned_to_all_shear_walls: bool = ..., assigned_to_all_surface_sets: bool = ..., assigned_to_all_surfaces: bool = ..., assigned_to_deep_beams: _Optional[_Iterable[int]] = ..., assigned_to_design_strips: _Optional[_Iterable[int]] = ..., assigned_to_member_sets: _Optional[_Iterable[int]] = ..., assigned_to_members: _Optional[_Iterable[int]] = ..., assigned_to_nodes: _Optional[_Iterable[int]] = ..., assigned_to_shear_walls: _Optional[_Iterable[int]] = ..., assigned_to_surface_sets: _Optional[_Iterable[int]] = ..., assigned_to_surfaces: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ..., generating_object_info: _Optional[str] = ..., is_generated: bool = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
