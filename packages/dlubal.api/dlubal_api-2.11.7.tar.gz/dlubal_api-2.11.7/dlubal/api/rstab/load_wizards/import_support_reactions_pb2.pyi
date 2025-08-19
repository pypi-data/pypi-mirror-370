from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImportSupportReactions(_message.Message):
    __slots__ = ("comment", "connected_model_uid", "create_member_loads_instead_of_line_loads", "generating_object_info", "import_from_all_supported_lines", "import_from_all_supported_nodes", "import_from_supported_lines_no", "import_from_supported_nodes_no", "import_to_all_surfaces", "import_to_lines_no", "import_to_nodes_no", "import_to_surfaces_no", "is_generated", "load_distribution", "loading_connection_type", "name", "no", "objects_connection_type", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class LoadDistribution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DISTRIBUTION_UNKNOWN: _ClassVar[ImportSupportReactions.LoadDistribution]
        LOAD_DISTRIBUTION_UNIFORM_TOTAL: _ClassVar[ImportSupportReactions.LoadDistribution]
        LOAD_DISTRIBUTION_VARYING: _ClassVar[ImportSupportReactions.LoadDistribution]
    LOAD_DISTRIBUTION_UNKNOWN: ImportSupportReactions.LoadDistribution
    LOAD_DISTRIBUTION_UNIFORM_TOTAL: ImportSupportReactions.LoadDistribution
    LOAD_DISTRIBUTION_VARYING: ImportSupportReactions.LoadDistribution
    class LoadingConnectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOADING_CONNECTION_TYPE_MANUALLY: _ClassVar[ImportSupportReactions.LoadingConnectionType]
        LOADING_CONNECTION_TYPE_AUTOMATICALLY: _ClassVar[ImportSupportReactions.LoadingConnectionType]
    LOADING_CONNECTION_TYPE_MANUALLY: ImportSupportReactions.LoadingConnectionType
    LOADING_CONNECTION_TYPE_AUTOMATICALLY: ImportSupportReactions.LoadingConnectionType
    class ObjectsConnectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OBJECTS_CONNECTION_TYPE_MANUALLY: _ClassVar[ImportSupportReactions.ObjectsConnectionType]
    OBJECTS_CONNECTION_TYPE_MANUALLY: ImportSupportReactions.ObjectsConnectionType
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_MODEL_UID_FIELD_NUMBER: _ClassVar[int]
    CREATE_MEMBER_LOADS_INSTEAD_OF_LINE_LOADS_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IMPORT_FROM_ALL_SUPPORTED_LINES_FIELD_NUMBER: _ClassVar[int]
    IMPORT_FROM_ALL_SUPPORTED_NODES_FIELD_NUMBER: _ClassVar[int]
    IMPORT_FROM_SUPPORTED_LINES_NO_FIELD_NUMBER: _ClassVar[int]
    IMPORT_FROM_SUPPORTED_NODES_NO_FIELD_NUMBER: _ClassVar[int]
    IMPORT_TO_ALL_SURFACES_FIELD_NUMBER: _ClassVar[int]
    IMPORT_TO_LINES_NO_FIELD_NUMBER: _ClassVar[int]
    IMPORT_TO_NODES_NO_FIELD_NUMBER: _ClassVar[int]
    IMPORT_TO_SURFACES_NO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    LOAD_DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    LOADING_CONNECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_CONNECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    comment: str
    connected_model_uid: str
    create_member_loads_instead_of_line_loads: bool
    generating_object_info: str
    import_from_all_supported_lines: bool
    import_from_all_supported_nodes: bool
    import_from_supported_lines_no: str
    import_from_supported_nodes_no: str
    import_to_all_surfaces: bool
    import_to_lines_no: _containers.RepeatedScalarFieldContainer[int]
    import_to_nodes_no: _containers.RepeatedScalarFieldContainer[int]
    import_to_surfaces_no: _containers.RepeatedScalarFieldContainer[int]
    is_generated: bool
    load_distribution: ImportSupportReactions.LoadDistribution
    loading_connection_type: ImportSupportReactions.LoadingConnectionType
    name: str
    no: int
    objects_connection_type: ImportSupportReactions.ObjectsConnectionType
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, comment: _Optional[str] = ..., connected_model_uid: _Optional[str] = ..., create_member_loads_instead_of_line_loads: bool = ..., generating_object_info: _Optional[str] = ..., import_from_all_supported_lines: bool = ..., import_from_all_supported_nodes: bool = ..., import_from_supported_lines_no: _Optional[str] = ..., import_from_supported_nodes_no: _Optional[str] = ..., import_to_all_surfaces: bool = ..., import_to_lines_no: _Optional[_Iterable[int]] = ..., import_to_nodes_no: _Optional[_Iterable[int]] = ..., import_to_surfaces_no: _Optional[_Iterable[int]] = ..., is_generated: bool = ..., load_distribution: _Optional[_Union[ImportSupportReactions.LoadDistribution, str]] = ..., loading_connection_type: _Optional[_Union[ImportSupportReactions.LoadingConnectionType, str]] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., objects_connection_type: _Optional[_Union[ImportSupportReactions.ObjectsConnectionType, str]] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
