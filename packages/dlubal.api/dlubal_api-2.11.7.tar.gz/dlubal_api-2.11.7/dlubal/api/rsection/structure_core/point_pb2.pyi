from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Point(_message.Message):
    __slots__ = ("no", "type", "reference_point", "coordinate_system", "coordinate_system_type", "coordinates", "coordinate_1", "coordinate_2", "global_coordinates", "global_coordinate_1", "global_coordinate_2", "comment", "between_two_points_start_point", "between_two_points_end_point", "between_two_locations_start_point_coordinates", "between_two_locations_start_point_coordinate_1", "between_two_locations_start_point_coordinate_2", "between_two_locations_end_point_coordinates", "between_two_locations_end_point_coordinate_1", "between_two_locations_end_point_coordinate_2", "on_line_reference_line", "reference_type", "reference_object_projected_length", "distance_from_start_is_defined_as_relative", "distance_from_start_relative", "distance_from_start_absolute", "distance_from_end_relative", "distance_from_end_absolute", "offset_in_local_direction", "offset_in_global_direction_y", "offset_in_global_direction_z", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[Point.Type]
        TYPE_BETWEEN_TWO_NODES: _ClassVar[Point.Type]
        TYPE_BETWEEN_TWO_POINTS: _ClassVar[Point.Type]
        TYPE_ON_LINE: _ClassVar[Point.Type]
        TYPE_STANDARD: _ClassVar[Point.Type]
    TYPE_UNKNOWN: Point.Type
    TYPE_BETWEEN_TWO_NODES: Point.Type
    TYPE_BETWEEN_TWO_POINTS: Point.Type
    TYPE_ON_LINE: Point.Type
    TYPE_STANDARD: Point.Type
    class CoordinateSystemType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COORDINATE_SYSTEM_TYPE_CARTESIAN: _ClassVar[Point.CoordinateSystemType]
    COORDINATE_SYSTEM_TYPE_CARTESIAN: Point.CoordinateSystemType
    class ReferenceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REFERENCE_TYPE_L: _ClassVar[Point.ReferenceType]
        REFERENCE_TYPE_XZ: _ClassVar[Point.ReferenceType]
        REFERENCE_TYPE_YZ: _ClassVar[Point.ReferenceType]
    REFERENCE_TYPE_L: Point.ReferenceType
    REFERENCE_TYPE_XZ: Point.ReferenceType
    REFERENCE_TYPE_YZ: Point.ReferenceType
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_POINT_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_TYPE_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_1_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_2_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_COORDINATE_1_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_COORDINATE_2_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_POINTS_START_POINT_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_POINTS_END_POINT_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_LOCATIONS_START_POINT_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_LOCATIONS_START_POINT_COORDINATE_1_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_LOCATIONS_START_POINT_COORDINATE_2_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_LOCATIONS_END_POINT_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_LOCATIONS_END_POINT_COORDINATE_1_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_LOCATIONS_END_POINT_COORDINATE_2_FIELD_NUMBER: _ClassVar[int]
    ON_LINE_REFERENCE_LINE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_OBJECT_PROJECTED_LENGTH_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_START_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_START_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_START_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_END_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_END_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_IN_LOCAL_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    OFFSET_IN_GLOBAL_DIRECTION_Y_FIELD_NUMBER: _ClassVar[int]
    OFFSET_IN_GLOBAL_DIRECTION_Z_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: Point.Type
    reference_point: int
    coordinate_system: int
    coordinate_system_type: Point.CoordinateSystemType
    coordinates: _common_pb2.Vector3d
    coordinate_1: float
    coordinate_2: float
    global_coordinates: _common_pb2.Vector3d
    global_coordinate_1: float
    global_coordinate_2: float
    comment: str
    between_two_points_start_point: int
    between_two_points_end_point: int
    between_two_locations_start_point_coordinates: _common_pb2.Vector3d
    between_two_locations_start_point_coordinate_1: float
    between_two_locations_start_point_coordinate_2: float
    between_two_locations_end_point_coordinates: _common_pb2.Vector3d
    between_two_locations_end_point_coordinate_1: float
    between_two_locations_end_point_coordinate_2: float
    on_line_reference_line: int
    reference_type: Point.ReferenceType
    reference_object_projected_length: float
    distance_from_start_is_defined_as_relative: bool
    distance_from_start_relative: float
    distance_from_start_absolute: float
    distance_from_end_relative: float
    distance_from_end_absolute: float
    offset_in_local_direction: float
    offset_in_global_direction_y: float
    offset_in_global_direction_z: float
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[Point.Type, str]] = ..., reference_point: _Optional[int] = ..., coordinate_system: _Optional[int] = ..., coordinate_system_type: _Optional[_Union[Point.CoordinateSystemType, str]] = ..., coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., coordinate_1: _Optional[float] = ..., coordinate_2: _Optional[float] = ..., global_coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., global_coordinate_1: _Optional[float] = ..., global_coordinate_2: _Optional[float] = ..., comment: _Optional[str] = ..., between_two_points_start_point: _Optional[int] = ..., between_two_points_end_point: _Optional[int] = ..., between_two_locations_start_point_coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., between_two_locations_start_point_coordinate_1: _Optional[float] = ..., between_two_locations_start_point_coordinate_2: _Optional[float] = ..., between_two_locations_end_point_coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., between_two_locations_end_point_coordinate_1: _Optional[float] = ..., between_two_locations_end_point_coordinate_2: _Optional[float] = ..., on_line_reference_line: _Optional[int] = ..., reference_type: _Optional[_Union[Point.ReferenceType, str]] = ..., reference_object_projected_length: _Optional[float] = ..., distance_from_start_is_defined_as_relative: bool = ..., distance_from_start_relative: _Optional[float] = ..., distance_from_start_absolute: _Optional[float] = ..., distance_from_end_relative: _Optional[float] = ..., distance_from_end_absolute: _Optional[float] = ..., offset_in_local_direction: _Optional[float] = ..., offset_in_global_direction_y: _Optional[float] = ..., offset_in_global_direction_z: _Optional[float] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
