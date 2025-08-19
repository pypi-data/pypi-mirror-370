from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Crane(_message.Message):
    __slots__ = ("assigned_to_craneways", "comment", "name", "no", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    ASSIGNED_TO_CRANEWAYS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    assigned_to_craneways: _containers.RepeatedScalarFieldContainer[int]
    comment: str
    name: str
    no: int
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, assigned_to_craneways: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
