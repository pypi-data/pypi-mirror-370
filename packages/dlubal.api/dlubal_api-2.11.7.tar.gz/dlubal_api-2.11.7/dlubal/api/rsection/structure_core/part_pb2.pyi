from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Part(_message.Message):
    __slots__ = ("no", "geometry", "only_shear_transfer", "boundary_lines", "material", "generating_object_info", "area", "mass", "center_of_gravity", "center_of_gravity_y", "center_of_gravity_z", "comment", "integrated_openings", "auto_detection_of_integrated_objects", "has_integrated_objects", "is_generated", "id_for_export_import", "metadata_for_export_import")
    class Geometry(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        GEOMETRY_UNKNOWN: _ClassVar[Part.Geometry]
        GEOMETRY_BOUNDARY_LINES: _ClassVar[Part.Geometry]
    GEOMETRY_UNKNOWN: Part.Geometry
    GEOMETRY_BOUNDARY_LINES: Part.Geometry
    NO_FIELD_NUMBER: _ClassVar[int]
    GEOMETRY_FIELD_NUMBER: _ClassVar[int]
    ONLY_SHEAR_TRANSFER_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_LINES_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Z_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    INTEGRATED_OPENINGS_FIELD_NUMBER: _ClassVar[int]
    AUTO_DETECTION_OF_INTEGRATED_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    HAS_INTEGRATED_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    geometry: Part.Geometry
    only_shear_transfer: bool
    boundary_lines: _containers.RepeatedScalarFieldContainer[int]
    material: int
    generating_object_info: str
    area: float
    mass: float
    center_of_gravity: _common_pb2.Vector3d
    center_of_gravity_y: float
    center_of_gravity_z: float
    comment: str
    integrated_openings: _containers.RepeatedScalarFieldContainer[int]
    auto_detection_of_integrated_objects: bool
    has_integrated_objects: bool
    is_generated: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., geometry: _Optional[_Union[Part.Geometry, str]] = ..., only_shear_transfer: bool = ..., boundary_lines: _Optional[_Iterable[int]] = ..., material: _Optional[int] = ..., generating_object_info: _Optional[str] = ..., area: _Optional[float] = ..., mass: _Optional[float] = ..., center_of_gravity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_of_gravity_y: _Optional[float] = ..., center_of_gravity_z: _Optional[float] = ..., comment: _Optional[str] = ..., integrated_openings: _Optional[_Iterable[int]] = ..., auto_detection_of_integrated_objects: bool = ..., has_integrated_objects: bool = ..., is_generated: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
