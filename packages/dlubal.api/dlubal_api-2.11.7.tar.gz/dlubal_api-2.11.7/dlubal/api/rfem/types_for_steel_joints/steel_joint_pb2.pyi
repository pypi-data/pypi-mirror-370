from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SteelJoint(_message.Message):
    __slots__ = ("all_nodes_to_design", "comment", "name", "no", "nodes", "nodes_to_design", "to_design", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    ALL_NODES_TO_DESIGN_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    NODES_TO_DESIGN_FIELD_NUMBER: _ClassVar[int]
    TO_DESIGN_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    all_nodes_to_design: bool
    comment: str
    name: str
    no: int
    nodes: _containers.RepeatedScalarFieldContainer[int]
    nodes_to_design: _containers.RepeatedScalarFieldContainer[int]
    to_design: bool
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, all_nodes_to_design: bool = ..., comment: _Optional[str] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., nodes: _Optional[_Iterable[int]] = ..., nodes_to_design: _Optional[_Iterable[int]] = ..., to_design: bool = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
