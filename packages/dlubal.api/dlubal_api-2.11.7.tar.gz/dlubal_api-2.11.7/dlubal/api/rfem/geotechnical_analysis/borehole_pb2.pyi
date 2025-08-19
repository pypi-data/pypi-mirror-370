from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Borehole(_message.Message):
    __slots__ = ("no", "type", "user_defined_name_enabled", "name", "coordinates", "coordinate_0", "coordinate_1", "coordinate_2", "import_coordinate_z_from_terrain", "groundwater", "groundwater_ordinate", "layers_table", "layers_thickness_sum", "comment", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_PHANTOM: _ClassVar[Borehole.Type]
        TYPE_STANDARD: _ClassVar[Borehole.Type]
    TYPE_PHANTOM: Borehole.Type
    TYPE_STANDARD: Borehole.Type
    class LayersTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[Borehole.LayersTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[Borehole.LayersTableRow, _Mapping]]] = ...) -> None: ...
    class LayersTableRow(_message.Message):
        __slots__ = ("no", "description", "layer_no", "soil_material", "depth", "bottom_ordinate")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        LAYER_NO_FIELD_NUMBER: _ClassVar[int]
        SOIL_MATERIAL_FIELD_NUMBER: _ClassVar[int]
        DEPTH_FIELD_NUMBER: _ClassVar[int]
        BOTTOM_ORDINATE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        layer_no: int
        soil_material: int
        depth: float
        bottom_ordinate: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., layer_no: _Optional[int] = ..., soil_material: _Optional[int] = ..., depth: _Optional[float] = ..., bottom_ordinate: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_0_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_1_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_2_FIELD_NUMBER: _ClassVar[int]
    IMPORT_COORDINATE_Z_FROM_TERRAIN_FIELD_NUMBER: _ClassVar[int]
    GROUNDWATER_FIELD_NUMBER: _ClassVar[int]
    GROUNDWATER_ORDINATE_FIELD_NUMBER: _ClassVar[int]
    LAYERS_TABLE_FIELD_NUMBER: _ClassVar[int]
    LAYERS_THICKNESS_SUM_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: Borehole.Type
    user_defined_name_enabled: bool
    name: str
    coordinates: _common_pb2.Vector3d
    coordinate_0: float
    coordinate_1: float
    coordinate_2: float
    import_coordinate_z_from_terrain: bool
    groundwater: bool
    groundwater_ordinate: float
    layers_table: Borehole.LayersTable
    layers_thickness_sum: float
    comment: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[Borehole.Type, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., coordinate_0: _Optional[float] = ..., coordinate_1: _Optional[float] = ..., coordinate_2: _Optional[float] = ..., import_coordinate_z_from_terrain: bool = ..., groundwater: bool = ..., groundwater_ordinate: _Optional[float] = ..., layers_table: _Optional[_Union[Borehole.LayersTable, _Mapping]] = ..., layers_thickness_sum: _Optional[float] = ..., comment: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
