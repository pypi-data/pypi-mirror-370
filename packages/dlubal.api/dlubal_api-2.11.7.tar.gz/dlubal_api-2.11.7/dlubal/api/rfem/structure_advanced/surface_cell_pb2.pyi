from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SurfaceCell(_message.Message):
    __slots__ = ("no", "area", "cell_number", "center_of_gravity", "center_of_gravity_x", "center_of_gravity_y", "center_of_gravity_z", "center_point", "center_point_x", "center_point_y", "center_point_z", "comment", "fe_elements", "generating_object_info", "geometry_type", "is_generated", "mass", "nodes", "overwrite_surface_thickness", "surface", "thickness", "type", "volume", "id_for_export_import", "metadata_for_export_import")
    class GeometryType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        GEOMETRY_TYPE_OWNER_ONLY: _ClassVar[SurfaceCell.GeometryType]
        GEOMETRY_TYPE_EDGES: _ClassVar[SurfaceCell.GeometryType]
    GEOMETRY_TYPE_OWNER_ONLY: SurfaceCell.GeometryType
    GEOMETRY_TYPE_EDGES: SurfaceCell.GeometryType
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[SurfaceCell.Type]
        TYPE_STANDARD: _ClassVar[SurfaceCell.Type]
    TYPE_UNKNOWN: SurfaceCell.Type
    TYPE_STANDARD: SurfaceCell.Type
    NO_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    CELL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Z_FIELD_NUMBER: _ClassVar[int]
    CENTER_POINT_FIELD_NUMBER: _ClassVar[int]
    CENTER_POINT_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_POINT_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_POINT_Z_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    FE_ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    GEOMETRY_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_SURFACE_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    SURFACE_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    area: float
    cell_number: int
    center_of_gravity: _common_pb2.Vector3d
    center_of_gravity_x: float
    center_of_gravity_y: float
    center_of_gravity_z: float
    center_point: _common_pb2.Vector3d
    center_point_x: float
    center_point_y: float
    center_point_z: float
    comment: str
    fe_elements: str
    generating_object_info: str
    geometry_type: SurfaceCell.GeometryType
    is_generated: bool
    mass: float
    nodes: _containers.RepeatedScalarFieldContainer[int]
    overwrite_surface_thickness: bool
    surface: int
    thickness: int
    type: SurfaceCell.Type
    volume: float
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., area: _Optional[float] = ..., cell_number: _Optional[int] = ..., center_of_gravity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_of_gravity_x: _Optional[float] = ..., center_of_gravity_y: _Optional[float] = ..., center_of_gravity_z: _Optional[float] = ..., center_point: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_point_x: _Optional[float] = ..., center_point_y: _Optional[float] = ..., center_point_z: _Optional[float] = ..., comment: _Optional[str] = ..., fe_elements: _Optional[str] = ..., generating_object_info: _Optional[str] = ..., geometry_type: _Optional[_Union[SurfaceCell.GeometryType, str]] = ..., is_generated: bool = ..., mass: _Optional[float] = ..., nodes: _Optional[_Iterable[int]] = ..., overwrite_surface_thickness: bool = ..., surface: _Optional[int] = ..., thickness: _Optional[int] = ..., type: _Optional[_Union[SurfaceCell.Type, str]] = ..., volume: _Optional[float] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
