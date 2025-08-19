from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Layer(_message.Message):
    __slots__ = ("color", "comment", "current", "locked", "name", "no", "id_for_export_import", "metadata_for_export_import")
    COLOR_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    CURRENT_FIELD_NUMBER: _ClassVar[int]
    LOCKED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    color: str
    comment: str
    current: bool
    locked: bool
    name: str
    no: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, color: _Optional[str] = ..., comment: _Optional[str] = ..., current: bool = ..., locked: bool = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
