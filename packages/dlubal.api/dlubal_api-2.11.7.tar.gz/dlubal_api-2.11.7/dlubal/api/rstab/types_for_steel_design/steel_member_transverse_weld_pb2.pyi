from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SteelMemberTransverseWeld(_message.Message):
    __slots__ = ("comment", "generating_object_info", "is_generated", "member_sets", "members", "name", "no", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    comment: str
    generating_object_info: str
    is_generated: bool
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    members: _containers.RepeatedScalarFieldContainer[int]
    name: str
    no: int
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, comment: _Optional[str] = ..., generating_object_info: _Optional[str] = ..., is_generated: bool = ..., member_sets: _Optional[_Iterable[int]] = ..., members: _Optional[_Iterable[int]] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
