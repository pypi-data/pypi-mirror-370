from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Intersection(_message.Message):
    __slots__ = ("no", "comment", "generated_lines", "generated_nodes", "surface_a", "surface_b", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    GENERATED_LINES_FIELD_NUMBER: _ClassVar[int]
    GENERATED_NODES_FIELD_NUMBER: _ClassVar[int]
    SURFACE_A_FIELD_NUMBER: _ClassVar[int]
    SURFACE_B_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    comment: str
    generated_lines: _containers.RepeatedScalarFieldContainer[int]
    generated_nodes: _containers.RepeatedScalarFieldContainer[int]
    surface_a: int
    surface_b: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., comment: _Optional[str] = ..., generated_lines: _Optional[_Iterable[int]] = ..., generated_nodes: _Optional[_Iterable[int]] = ..., surface_a: _Optional[int] = ..., surface_b: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
