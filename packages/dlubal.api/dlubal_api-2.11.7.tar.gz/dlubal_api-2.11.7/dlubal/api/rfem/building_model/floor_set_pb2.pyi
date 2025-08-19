from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FloorSet(_message.Message):
    __slots__ = ("no", "type", "building_story", "floor_surfaces", "floor_members", "connected_surfaces", "connected_members", "floor_solids", "area", "mass", "volume", "center_of_gravity", "center_of_gravity_x", "center_of_gravity_y", "center_of_gravity_z", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[FloorSet.Type]
        TYPE_STANDARD: _ClassVar[FloorSet.Type]
    TYPE_UNKNOWN: FloorSet.Type
    TYPE_STANDARD: FloorSet.Type
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    BUILDING_STORY_FIELD_NUMBER: _ClassVar[int]
    FLOOR_SURFACES_FIELD_NUMBER: _ClassVar[int]
    FLOOR_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_SURFACES_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    FLOOR_SOLIDS_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Z_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: FloorSet.Type
    building_story: int
    floor_surfaces: _containers.RepeatedScalarFieldContainer[int]
    floor_members: _containers.RepeatedScalarFieldContainer[int]
    connected_surfaces: _containers.RepeatedScalarFieldContainer[int]
    connected_members: _containers.RepeatedScalarFieldContainer[int]
    floor_solids: _containers.RepeatedScalarFieldContainer[int]
    area: float
    mass: float
    volume: float
    center_of_gravity: _common_pb2.Vector3d
    center_of_gravity_x: float
    center_of_gravity_y: float
    center_of_gravity_z: float
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[FloorSet.Type, str]] = ..., building_story: _Optional[int] = ..., floor_surfaces: _Optional[_Iterable[int]] = ..., floor_members: _Optional[_Iterable[int]] = ..., connected_surfaces: _Optional[_Iterable[int]] = ..., connected_members: _Optional[_Iterable[int]] = ..., floor_solids: _Optional[_Iterable[int]] = ..., area: _Optional[float] = ..., mass: _Optional[float] = ..., volume: _Optional[float] = ..., center_of_gravity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_of_gravity_x: _Optional[float] = ..., center_of_gravity_y: _Optional[float] = ..., center_of_gravity_z: _Optional[float] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
