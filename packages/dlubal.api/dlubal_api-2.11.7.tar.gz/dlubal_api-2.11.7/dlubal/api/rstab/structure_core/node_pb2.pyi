from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Node(_message.Message):
    __slots__ = ("no", "type", "reference_node", "coordinate_system", "coordinate_system_type", "coordinates", "coordinate_1", "coordinate_2", "coordinate_3", "global_coordinates", "global_coordinate_1", "global_coordinate_2", "global_coordinate_3", "between_two_nodes_start_node", "between_two_points_start_point_coordinates", "between_two_points_start_point_coordinate_1", "between_two_points_start_point_coordinate_2", "between_two_points_start_point_coordinate_3", "between_two_nodes_end_node", "between_two_points_end_point_coordinates", "between_two_points_end_point_coordinate_1", "between_two_points_end_point_coordinate_2", "between_two_points_end_point_coordinate_3", "on_member_reference_member", "reference_type", "reference_object_projected_length", "distance_from_start_is_defined_as_relative", "distance_from_start_relative", "distance_from_start_absolute", "offset_in_local_direction_y", "offset_in_local_direction_z", "offset_in_global_direction_x", "offset_in_global_direction_y", "offset_in_global_direction_z", "support", "concrete_design_ultimate_configuration", "concrete_design_seismicity_configuration", "punching_design", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[Node.Type]
        TYPE_BETWEEN_TWO_NODES: _ClassVar[Node.Type]
        TYPE_BETWEEN_TWO_POINTS: _ClassVar[Node.Type]
        TYPE_ON_MEMBER: _ClassVar[Node.Type]
        TYPE_STANDARD: _ClassVar[Node.Type]
    TYPE_UNKNOWN: Node.Type
    TYPE_BETWEEN_TWO_NODES: Node.Type
    TYPE_BETWEEN_TWO_POINTS: Node.Type
    TYPE_ON_MEMBER: Node.Type
    TYPE_STANDARD: Node.Type
    class CoordinateSystemType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COORDINATE_SYSTEM_TYPE_CARTESIAN: _ClassVar[Node.CoordinateSystemType]
        COORDINATE_SYSTEM_TYPE_POLAR: _ClassVar[Node.CoordinateSystemType]
        COORDINATE_SYSTEM_TYPE_X_CYLINDRICAL: _ClassVar[Node.CoordinateSystemType]
        COORDINATE_SYSTEM_TYPE_Y_CYLINDRICAL: _ClassVar[Node.CoordinateSystemType]
        COORDINATE_SYSTEM_TYPE_Z_CYLINDRICAL: _ClassVar[Node.CoordinateSystemType]
    COORDINATE_SYSTEM_TYPE_CARTESIAN: Node.CoordinateSystemType
    COORDINATE_SYSTEM_TYPE_POLAR: Node.CoordinateSystemType
    COORDINATE_SYSTEM_TYPE_X_CYLINDRICAL: Node.CoordinateSystemType
    COORDINATE_SYSTEM_TYPE_Y_CYLINDRICAL: Node.CoordinateSystemType
    COORDINATE_SYSTEM_TYPE_Z_CYLINDRICAL: Node.CoordinateSystemType
    class ReferenceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REFERENCE_TYPE_L: _ClassVar[Node.ReferenceType]
        REFERENCE_TYPE_XY: _ClassVar[Node.ReferenceType]
        REFERENCE_TYPE_XZ: _ClassVar[Node.ReferenceType]
        REFERENCE_TYPE_YZ: _ClassVar[Node.ReferenceType]
    REFERENCE_TYPE_L: Node.ReferenceType
    REFERENCE_TYPE_XY: Node.ReferenceType
    REFERENCE_TYPE_XZ: Node.ReferenceType
    REFERENCE_TYPE_YZ: Node.ReferenceType
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_NODE_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_TYPE_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_1_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_2_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_3_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_COORDINATE_1_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_COORDINATE_2_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_COORDINATE_3_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_NODES_START_NODE_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_POINTS_START_POINT_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_POINTS_START_POINT_COORDINATE_1_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_POINTS_START_POINT_COORDINATE_2_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_POINTS_START_POINT_COORDINATE_3_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_NODES_END_NODE_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_POINTS_END_POINT_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_POINTS_END_POINT_COORDINATE_1_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_POINTS_END_POINT_COORDINATE_2_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_TWO_POINTS_END_POINT_COORDINATE_3_FIELD_NUMBER: _ClassVar[int]
    ON_MEMBER_REFERENCE_MEMBER_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_OBJECT_PROJECTED_LENGTH_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_START_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_START_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_START_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_IN_LOCAL_DIRECTION_Y_FIELD_NUMBER: _ClassVar[int]
    OFFSET_IN_LOCAL_DIRECTION_Z_FIELD_NUMBER: _ClassVar[int]
    OFFSET_IN_GLOBAL_DIRECTION_X_FIELD_NUMBER: _ClassVar[int]
    OFFSET_IN_GLOBAL_DIRECTION_Y_FIELD_NUMBER: _ClassVar[int]
    OFFSET_IN_GLOBAL_DIRECTION_Z_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DESIGN_ULTIMATE_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DESIGN_SEISMICITY_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    PUNCHING_DESIGN_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: Node.Type
    reference_node: int
    coordinate_system: int
    coordinate_system_type: Node.CoordinateSystemType
    coordinates: _common_pb2.Vector3d
    coordinate_1: float
    coordinate_2: float
    coordinate_3: float
    global_coordinates: _common_pb2.Vector3d
    global_coordinate_1: float
    global_coordinate_2: float
    global_coordinate_3: float
    between_two_nodes_start_node: int
    between_two_points_start_point_coordinates: _common_pb2.Vector3d
    between_two_points_start_point_coordinate_1: float
    between_two_points_start_point_coordinate_2: float
    between_two_points_start_point_coordinate_3: float
    between_two_nodes_end_node: int
    between_two_points_end_point_coordinates: _common_pb2.Vector3d
    between_two_points_end_point_coordinate_1: float
    between_two_points_end_point_coordinate_2: float
    between_two_points_end_point_coordinate_3: float
    on_member_reference_member: int
    reference_type: Node.ReferenceType
    reference_object_projected_length: float
    distance_from_start_is_defined_as_relative: bool
    distance_from_start_relative: float
    distance_from_start_absolute: float
    offset_in_local_direction_y: float
    offset_in_local_direction_z: float
    offset_in_global_direction_x: float
    offset_in_global_direction_y: float
    offset_in_global_direction_z: float
    support: int
    concrete_design_ultimate_configuration: int
    concrete_design_seismicity_configuration: int
    punching_design: bool
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[Node.Type, str]] = ..., reference_node: _Optional[int] = ..., coordinate_system: _Optional[int] = ..., coordinate_system_type: _Optional[_Union[Node.CoordinateSystemType, str]] = ..., coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., coordinate_1: _Optional[float] = ..., coordinate_2: _Optional[float] = ..., coordinate_3: _Optional[float] = ..., global_coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., global_coordinate_1: _Optional[float] = ..., global_coordinate_2: _Optional[float] = ..., global_coordinate_3: _Optional[float] = ..., between_two_nodes_start_node: _Optional[int] = ..., between_two_points_start_point_coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., between_two_points_start_point_coordinate_1: _Optional[float] = ..., between_two_points_start_point_coordinate_2: _Optional[float] = ..., between_two_points_start_point_coordinate_3: _Optional[float] = ..., between_two_nodes_end_node: _Optional[int] = ..., between_two_points_end_point_coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., between_two_points_end_point_coordinate_1: _Optional[float] = ..., between_two_points_end_point_coordinate_2: _Optional[float] = ..., between_two_points_end_point_coordinate_3: _Optional[float] = ..., on_member_reference_member: _Optional[int] = ..., reference_type: _Optional[_Union[Node.ReferenceType, str]] = ..., reference_object_projected_length: _Optional[float] = ..., distance_from_start_is_defined_as_relative: bool = ..., distance_from_start_relative: _Optional[float] = ..., distance_from_start_absolute: _Optional[float] = ..., offset_in_local_direction_y: _Optional[float] = ..., offset_in_local_direction_z: _Optional[float] = ..., offset_in_global_direction_x: _Optional[float] = ..., offset_in_global_direction_y: _Optional[float] = ..., offset_in_global_direction_z: _Optional[float] = ..., support: _Optional[int] = ..., concrete_design_ultimate_configuration: _Optional[int] = ..., concrete_design_seismicity_configuration: _Optional[int] = ..., punching_design: bool = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
