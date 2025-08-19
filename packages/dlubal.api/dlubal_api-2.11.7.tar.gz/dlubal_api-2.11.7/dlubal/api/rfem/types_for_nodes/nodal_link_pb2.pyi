from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NodalLink(_message.Message):
    __slots__ = ("assigned_nodes", "comment", "include_related_objects", "linking_to_members_allowed", "linking_to_nodes_allowed", "linking_to_surfaces_allowed", "member_hinge_end", "member_hinge_start", "members_exclued_from_search", "name", "no", "nodes_excluded_from_search", "search_method", "search_radius", "surfaces_excluded_from_search", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class SearchMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SEARCH_METHOD_CLOSEST_OBJECTS: _ClassVar[NodalLink.SearchMethod]
    SEARCH_METHOD_CLOSEST_OBJECTS: NodalLink.SearchMethod
    ASSIGNED_NODES_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_RELATED_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    LINKING_TO_MEMBERS_ALLOWED_FIELD_NUMBER: _ClassVar[int]
    LINKING_TO_NODES_ALLOWED_FIELD_NUMBER: _ClassVar[int]
    LINKING_TO_SURFACES_ALLOWED_FIELD_NUMBER: _ClassVar[int]
    MEMBER_HINGE_END_FIELD_NUMBER: _ClassVar[int]
    MEMBER_HINGE_START_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_EXCLUED_FROM_SEARCH_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    NODES_EXCLUDED_FROM_SEARCH_FIELD_NUMBER: _ClassVar[int]
    SEARCH_METHOD_FIELD_NUMBER: _ClassVar[int]
    SEARCH_RADIUS_FIELD_NUMBER: _ClassVar[int]
    SURFACES_EXCLUDED_FROM_SEARCH_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    assigned_nodes: _containers.RepeatedScalarFieldContainer[int]
    comment: str
    include_related_objects: bool
    linking_to_members_allowed: bool
    linking_to_nodes_allowed: bool
    linking_to_surfaces_allowed: bool
    member_hinge_end: int
    member_hinge_start: int
    members_exclued_from_search: _containers.RepeatedScalarFieldContainer[int]
    name: str
    no: int
    nodes_excluded_from_search: _containers.RepeatedScalarFieldContainer[int]
    search_method: NodalLink.SearchMethod
    search_radius: float
    surfaces_excluded_from_search: _containers.RepeatedScalarFieldContainer[int]
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, assigned_nodes: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ..., include_related_objects: bool = ..., linking_to_members_allowed: bool = ..., linking_to_nodes_allowed: bool = ..., linking_to_surfaces_allowed: bool = ..., member_hinge_end: _Optional[int] = ..., member_hinge_start: _Optional[int] = ..., members_exclued_from_search: _Optional[_Iterable[int]] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., nodes_excluded_from_search: _Optional[_Iterable[int]] = ..., search_method: _Optional[_Union[NodalLink.SearchMethod, str]] = ..., search_radius: _Optional[float] = ..., surfaces_excluded_from_search: _Optional[_Iterable[int]] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
