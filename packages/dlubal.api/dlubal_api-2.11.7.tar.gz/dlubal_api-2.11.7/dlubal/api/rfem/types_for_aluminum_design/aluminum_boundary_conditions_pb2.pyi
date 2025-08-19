from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AluminumBoundaryConditions(_message.Message):
    __slots__ = ("comment", "coordinate_system", "definition_type", "different_properties_hinges", "different_properties_supports", "generating_object_info", "intermediate_nodes", "is_generated", "member_sets", "members", "name", "no", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class DefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFINITION_TYPE_UNKNOWN: _ClassVar[AluminumBoundaryConditions.DefinitionType]
        DEFINITION_TYPE_2D: _ClassVar[AluminumBoundaryConditions.DefinitionType]
    DEFINITION_TYPE_UNKNOWN: AluminumBoundaryConditions.DefinitionType
    DEFINITION_TYPE_2D: AluminumBoundaryConditions.DefinitionType
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    DIFFERENT_PROPERTIES_HINGES_FIELD_NUMBER: _ClassVar[int]
    DIFFERENT_PROPERTIES_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIATE_NODES_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    comment: str
    coordinate_system: _common_pb2.CoordinateSystemRepresentation
    definition_type: AluminumBoundaryConditions.DefinitionType
    different_properties_hinges: bool
    different_properties_supports: bool
    generating_object_info: str
    intermediate_nodes: bool
    is_generated: bool
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    members: _containers.RepeatedScalarFieldContainer[int]
    name: str
    no: int
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, comment: _Optional[str] = ..., coordinate_system: _Optional[_Union[_common_pb2.CoordinateSystemRepresentation, _Mapping]] = ..., definition_type: _Optional[_Union[AluminumBoundaryConditions.DefinitionType, str]] = ..., different_properties_hinges: bool = ..., different_properties_supports: bool = ..., generating_object_info: _Optional[str] = ..., intermediate_nodes: bool = ..., is_generated: bool = ..., member_sets: _Optional[_Iterable[int]] = ..., members: _Optional[_Iterable[int]] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
