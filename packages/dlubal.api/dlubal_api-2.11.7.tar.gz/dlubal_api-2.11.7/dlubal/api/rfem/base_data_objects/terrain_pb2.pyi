from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Terrain(_message.Message):
    __slots__ = ("no", "type", "comment", "bounding_box_offset_x", "bounding_box_offset_y", "center_of_terrain_z", "rotation_around_Z", "consider_boreholes", "coordinate_system", "terrain_table", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[Terrain.Type]
        TYPE_BOREHOLES: _ClassVar[Terrain.Type]
        TYPE_HORIZONTAL_PLANE: _ClassVar[Terrain.Type]
        TYPE_INCLINED_PLANE: _ClassVar[Terrain.Type]
        TYPE_NO_TERRAIN: _ClassVar[Terrain.Type]
        TYPE_TABLE: _ClassVar[Terrain.Type]
    TYPE_UNKNOWN: Terrain.Type
    TYPE_BOREHOLES: Terrain.Type
    TYPE_HORIZONTAL_PLANE: Terrain.Type
    TYPE_INCLINED_PLANE: Terrain.Type
    TYPE_NO_TERRAIN: Terrain.Type
    TYPE_TABLE: Terrain.Type
    class TerrainTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[Terrain.TerrainTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[Terrain.TerrainTableRow, _Mapping]]] = ...) -> None: ...
    class TerrainTableRow(_message.Message):
        __slots__ = ("no", "description", "global_x", "global_y", "global_z")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        GLOBAL_X_FIELD_NUMBER: _ClassVar[int]
        GLOBAL_Y_FIELD_NUMBER: _ClassVar[int]
        GLOBAL_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        global_x: float
        global_y: float
        global_z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., global_x: _Optional[float] = ..., global_y: _Optional[float] = ..., global_z: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    BOUNDING_BOX_OFFSET_X_FIELD_NUMBER: _ClassVar[int]
    BOUNDING_BOX_OFFSET_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_TERRAIN_Z_FIELD_NUMBER: _ClassVar[int]
    ROTATION_AROUND_Z_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_BOREHOLES_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    TERRAIN_TABLE_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: Terrain.Type
    comment: str
    bounding_box_offset_x: float
    bounding_box_offset_y: float
    center_of_terrain_z: float
    rotation_around_Z: float
    consider_boreholes: bool
    coordinate_system: int
    terrain_table: Terrain.TerrainTable
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[Terrain.Type, str]] = ..., comment: _Optional[str] = ..., bounding_box_offset_x: _Optional[float] = ..., bounding_box_offset_y: _Optional[float] = ..., center_of_terrain_z: _Optional[float] = ..., rotation_around_Z: _Optional[float] = ..., consider_boreholes: bool = ..., coordinate_system: _Optional[int] = ..., terrain_table: _Optional[_Union[Terrain.TerrainTable, _Mapping]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
