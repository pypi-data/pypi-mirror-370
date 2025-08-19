from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NodalRelease(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "nodes", "nodal_release_type", "release_location", "released_members", "generated_released_objects", "deactivated", "comment", "id_for_export_import", "metadata_for_export_import")
    class ReleaseLocation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        RELEASE_LOCATION_ORIGIN: _ClassVar[NodalRelease.ReleaseLocation]
        RELEASE_LOCATION_RELEASED: _ClassVar[NodalRelease.ReleaseLocation]
    RELEASE_LOCATION_ORIGIN: NodalRelease.ReleaseLocation
    RELEASE_LOCATION_RELEASED: NodalRelease.ReleaseLocation
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    NODAL_RELEASE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RELEASE_LOCATION_FIELD_NUMBER: _ClassVar[int]
    RELEASED_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    GENERATED_RELEASED_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATED_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    nodes: _containers.RepeatedScalarFieldContainer[int]
    nodal_release_type: int
    release_location: NodalRelease.ReleaseLocation
    released_members: _containers.RepeatedScalarFieldContainer[int]
    generated_released_objects: _containers.RepeatedScalarFieldContainer[int]
    deactivated: bool
    comment: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., nodes: _Optional[_Iterable[int]] = ..., nodal_release_type: _Optional[int] = ..., release_location: _Optional[_Union[NodalRelease.ReleaseLocation, str]] = ..., released_members: _Optional[_Iterable[int]] = ..., generated_released_objects: _Optional[_Iterable[int]] = ..., deactivated: bool = ..., comment: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
