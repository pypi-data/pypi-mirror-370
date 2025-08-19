from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SurfacesContact(_message.Message):
    __slots__ = ("no", "surfaces_contact_type", "surfaces_group1", "surfaces_group2", "comment", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    SURFACES_CONTACT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SURFACES_GROUP1_FIELD_NUMBER: _ClassVar[int]
    SURFACES_GROUP2_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    surfaces_contact_type: int
    surfaces_group1: _containers.RepeatedScalarFieldContainer[int]
    surfaces_group2: _containers.RepeatedScalarFieldContainer[int]
    comment: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., surfaces_contact_type: _Optional[int] = ..., surfaces_group1: _Optional[_Iterable[int]] = ..., surfaces_group2: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
