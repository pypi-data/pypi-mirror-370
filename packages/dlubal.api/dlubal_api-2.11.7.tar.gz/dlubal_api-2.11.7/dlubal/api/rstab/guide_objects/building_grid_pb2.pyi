from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BuildingGrid(_message.Message):
    __slots__ = ("no", "type", "user_defined_name_enabled", "name", "grid_type", "locked_in_graphics", "include_in_view", "grid_points", "grid_lines", "labels", "dimensions", "is_origin_defined_by_node", "origin_node", "origin_coordinates", "origin_coordinate_x", "origin_coordinate_y", "origin_coordinate_z", "alpha_ux", "alpha_vy", "alpha_wz", "coordinate_system", "rotation_coordinate_system", "has_specific_direction", "specific_direction_type", "axes_sequence", "rotated_about_angle_x", "rotated_about_angle_y", "rotated_about_angle_z", "rotated_about_angle_1", "rotated_about_angle_2", "rotated_about_angle_3", "directed_to_node_direction_node", "directed_to_node_plane_node", "directed_to_node_first_axis", "directed_to_node_second_axis", "parallel_to_two_nodes_first_node", "parallel_to_two_nodes_second_node", "parallel_to_two_nodes_plane_node", "parallel_to_two_nodes_first_axis", "parallel_to_two_nodes_second_axis", "parallel_to_member", "comment", "coordinates_list_x", "coordinates_list_y", "coordinates_list_z", "labels_list_x", "labels_list_y", "labels_list_z", "line_end_extension_x", "line_end_extension_y", "line_end_extension_z", "line_end_label_x", "line_end_label_y", "line_end_label_z", "line_start_extension_x", "line_start_extension_y", "line_start_extension_z", "line_start_label_x", "line_start_label_y", "line_start_label_z", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[BuildingGrid.Type]
        TYPE_STANDARD: _ClassVar[BuildingGrid.Type]
    TYPE_UNKNOWN: BuildingGrid.Type
    TYPE_STANDARD: BuildingGrid.Type
    class GridType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        GRID_TYPE_CARTESIAN: _ClassVar[BuildingGrid.GridType]
        GRID_TYPE_CYLINDRICAL: _ClassVar[BuildingGrid.GridType]
        GRID_TYPE_INCLINED: _ClassVar[BuildingGrid.GridType]
        GRID_TYPE_SPHERICAL: _ClassVar[BuildingGrid.GridType]
    GRID_TYPE_CARTESIAN: BuildingGrid.GridType
    GRID_TYPE_CYLINDRICAL: BuildingGrid.GridType
    GRID_TYPE_INCLINED: BuildingGrid.GridType
    GRID_TYPE_SPHERICAL: BuildingGrid.GridType
    class SpecificDirectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SPECIFIC_DIRECTION_TYPE_ROTATED_VIA_3_ANGLES: _ClassVar[BuildingGrid.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_DIRECTED_TO_NODE: _ClassVar[BuildingGrid.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER: _ClassVar[BuildingGrid.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_TWO_NODES: _ClassVar[BuildingGrid.SpecificDirectionType]
    SPECIFIC_DIRECTION_TYPE_ROTATED_VIA_3_ANGLES: BuildingGrid.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_DIRECTED_TO_NODE: BuildingGrid.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER: BuildingGrid.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_TWO_NODES: BuildingGrid.SpecificDirectionType
    class AxesSequence(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXES_SEQUENCE_XYZ: _ClassVar[BuildingGrid.AxesSequence]
        AXES_SEQUENCE_XZY: _ClassVar[BuildingGrid.AxesSequence]
        AXES_SEQUENCE_YXZ: _ClassVar[BuildingGrid.AxesSequence]
        AXES_SEQUENCE_YZX: _ClassVar[BuildingGrid.AxesSequence]
        AXES_SEQUENCE_ZXY: _ClassVar[BuildingGrid.AxesSequence]
        AXES_SEQUENCE_ZYX: _ClassVar[BuildingGrid.AxesSequence]
    AXES_SEQUENCE_XYZ: BuildingGrid.AxesSequence
    AXES_SEQUENCE_XZY: BuildingGrid.AxesSequence
    AXES_SEQUENCE_YXZ: BuildingGrid.AxesSequence
    AXES_SEQUENCE_YZX: BuildingGrid.AxesSequence
    AXES_SEQUENCE_ZXY: BuildingGrid.AxesSequence
    AXES_SEQUENCE_ZYX: BuildingGrid.AxesSequence
    class DirectedToNodeFirstAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIRECTED_TO_NODE_FIRST_AXIS_X: _ClassVar[BuildingGrid.DirectedToNodeFirstAxis]
        DIRECTED_TO_NODE_FIRST_AXIS_Y: _ClassVar[BuildingGrid.DirectedToNodeFirstAxis]
        DIRECTED_TO_NODE_FIRST_AXIS_Z: _ClassVar[BuildingGrid.DirectedToNodeFirstAxis]
    DIRECTED_TO_NODE_FIRST_AXIS_X: BuildingGrid.DirectedToNodeFirstAxis
    DIRECTED_TO_NODE_FIRST_AXIS_Y: BuildingGrid.DirectedToNodeFirstAxis
    DIRECTED_TO_NODE_FIRST_AXIS_Z: BuildingGrid.DirectedToNodeFirstAxis
    class DirectedToNodeSecondAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIRECTED_TO_NODE_SECOND_AXIS_X: _ClassVar[BuildingGrid.DirectedToNodeSecondAxis]
        DIRECTED_TO_NODE_SECOND_AXIS_Y: _ClassVar[BuildingGrid.DirectedToNodeSecondAxis]
        DIRECTED_TO_NODE_SECOND_AXIS_Z: _ClassVar[BuildingGrid.DirectedToNodeSecondAxis]
    DIRECTED_TO_NODE_SECOND_AXIS_X: BuildingGrid.DirectedToNodeSecondAxis
    DIRECTED_TO_NODE_SECOND_AXIS_Y: BuildingGrid.DirectedToNodeSecondAxis
    DIRECTED_TO_NODE_SECOND_AXIS_Z: BuildingGrid.DirectedToNodeSecondAxis
    class ParallelToTwoNodesFirstAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARALLEL_TO_TWO_NODES_FIRST_AXIS_X: _ClassVar[BuildingGrid.ParallelToTwoNodesFirstAxis]
        PARALLEL_TO_TWO_NODES_FIRST_AXIS_Y: _ClassVar[BuildingGrid.ParallelToTwoNodesFirstAxis]
        PARALLEL_TO_TWO_NODES_FIRST_AXIS_Z: _ClassVar[BuildingGrid.ParallelToTwoNodesFirstAxis]
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_X: BuildingGrid.ParallelToTwoNodesFirstAxis
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_Y: BuildingGrid.ParallelToTwoNodesFirstAxis
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_Z: BuildingGrid.ParallelToTwoNodesFirstAxis
    class ParallelToTwoNodesSecondAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARALLEL_TO_TWO_NODES_SECOND_AXIS_X: _ClassVar[BuildingGrid.ParallelToTwoNodesSecondAxis]
        PARALLEL_TO_TWO_NODES_SECOND_AXIS_Y: _ClassVar[BuildingGrid.ParallelToTwoNodesSecondAxis]
        PARALLEL_TO_TWO_NODES_SECOND_AXIS_Z: _ClassVar[BuildingGrid.ParallelToTwoNodesSecondAxis]
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_X: BuildingGrid.ParallelToTwoNodesSecondAxis
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_Y: BuildingGrid.ParallelToTwoNodesSecondAxis
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_Z: BuildingGrid.ParallelToTwoNodesSecondAxis
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    GRID_TYPE_FIELD_NUMBER: _ClassVar[int]
    LOCKED_IN_GRAPHICS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_IN_VIEW_FIELD_NUMBER: _ClassVar[int]
    GRID_POINTS_FIELD_NUMBER: _ClassVar[int]
    GRID_LINES_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    IS_ORIGIN_DEFINED_BY_NODE_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_NODE_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_COORDINATE_X_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_COORDINATE_Y_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_COORDINATE_Z_FIELD_NUMBER: _ClassVar[int]
    ALPHA_UX_FIELD_NUMBER: _ClassVar[int]
    ALPHA_VY_FIELD_NUMBER: _ClassVar[int]
    ALPHA_WZ_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    ROTATION_COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    HAS_SPECIFIC_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    SPECIFIC_DIRECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    AXES_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_X_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_Y_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_Z_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_1_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_2_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_3_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_DIRECTION_NODE_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_PLANE_NODE_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_FIRST_AXIS_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_SECOND_AXIS_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_FIRST_NODE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_SECOND_NODE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_PLANE_NODE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_MEMBER_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_LIST_X_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_LIST_Y_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_LIST_Z_FIELD_NUMBER: _ClassVar[int]
    LABELS_LIST_X_FIELD_NUMBER: _ClassVar[int]
    LABELS_LIST_Y_FIELD_NUMBER: _ClassVar[int]
    LABELS_LIST_Z_FIELD_NUMBER: _ClassVar[int]
    LINE_END_EXTENSION_X_FIELD_NUMBER: _ClassVar[int]
    LINE_END_EXTENSION_Y_FIELD_NUMBER: _ClassVar[int]
    LINE_END_EXTENSION_Z_FIELD_NUMBER: _ClassVar[int]
    LINE_END_LABEL_X_FIELD_NUMBER: _ClassVar[int]
    LINE_END_LABEL_Y_FIELD_NUMBER: _ClassVar[int]
    LINE_END_LABEL_Z_FIELD_NUMBER: _ClassVar[int]
    LINE_START_EXTENSION_X_FIELD_NUMBER: _ClassVar[int]
    LINE_START_EXTENSION_Y_FIELD_NUMBER: _ClassVar[int]
    LINE_START_EXTENSION_Z_FIELD_NUMBER: _ClassVar[int]
    LINE_START_LABEL_X_FIELD_NUMBER: _ClassVar[int]
    LINE_START_LABEL_Y_FIELD_NUMBER: _ClassVar[int]
    LINE_START_LABEL_Z_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: BuildingGrid.Type
    user_defined_name_enabled: bool
    name: str
    grid_type: BuildingGrid.GridType
    locked_in_graphics: bool
    include_in_view: bool
    grid_points: bool
    grid_lines: bool
    labels: bool
    dimensions: bool
    is_origin_defined_by_node: bool
    origin_node: int
    origin_coordinates: _common_pb2.Vector3d
    origin_coordinate_x: float
    origin_coordinate_y: float
    origin_coordinate_z: float
    alpha_ux: float
    alpha_vy: float
    alpha_wz: float
    coordinate_system: int
    rotation_coordinate_system: int
    has_specific_direction: bool
    specific_direction_type: BuildingGrid.SpecificDirectionType
    axes_sequence: BuildingGrid.AxesSequence
    rotated_about_angle_x: float
    rotated_about_angle_y: float
    rotated_about_angle_z: float
    rotated_about_angle_1: float
    rotated_about_angle_2: float
    rotated_about_angle_3: float
    directed_to_node_direction_node: int
    directed_to_node_plane_node: int
    directed_to_node_first_axis: BuildingGrid.DirectedToNodeFirstAxis
    directed_to_node_second_axis: BuildingGrid.DirectedToNodeSecondAxis
    parallel_to_two_nodes_first_node: int
    parallel_to_two_nodes_second_node: int
    parallel_to_two_nodes_plane_node: int
    parallel_to_two_nodes_first_axis: BuildingGrid.ParallelToTwoNodesFirstAxis
    parallel_to_two_nodes_second_axis: BuildingGrid.ParallelToTwoNodesSecondAxis
    parallel_to_member: int
    comment: str
    coordinates_list_x: str
    coordinates_list_y: str
    coordinates_list_z: str
    labels_list_x: str
    labels_list_y: str
    labels_list_z: str
    line_end_extension_x: float
    line_end_extension_y: float
    line_end_extension_z: float
    line_end_label_x: bool
    line_end_label_y: bool
    line_end_label_z: bool
    line_start_extension_x: float
    line_start_extension_y: float
    line_start_extension_z: float
    line_start_label_x: bool
    line_start_label_y: bool
    line_start_label_z: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[BuildingGrid.Type, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., grid_type: _Optional[_Union[BuildingGrid.GridType, str]] = ..., locked_in_graphics: bool = ..., include_in_view: bool = ..., grid_points: bool = ..., grid_lines: bool = ..., labels: bool = ..., dimensions: bool = ..., is_origin_defined_by_node: bool = ..., origin_node: _Optional[int] = ..., origin_coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., origin_coordinate_x: _Optional[float] = ..., origin_coordinate_y: _Optional[float] = ..., origin_coordinate_z: _Optional[float] = ..., alpha_ux: _Optional[float] = ..., alpha_vy: _Optional[float] = ..., alpha_wz: _Optional[float] = ..., coordinate_system: _Optional[int] = ..., rotation_coordinate_system: _Optional[int] = ..., has_specific_direction: bool = ..., specific_direction_type: _Optional[_Union[BuildingGrid.SpecificDirectionType, str]] = ..., axes_sequence: _Optional[_Union[BuildingGrid.AxesSequence, str]] = ..., rotated_about_angle_x: _Optional[float] = ..., rotated_about_angle_y: _Optional[float] = ..., rotated_about_angle_z: _Optional[float] = ..., rotated_about_angle_1: _Optional[float] = ..., rotated_about_angle_2: _Optional[float] = ..., rotated_about_angle_3: _Optional[float] = ..., directed_to_node_direction_node: _Optional[int] = ..., directed_to_node_plane_node: _Optional[int] = ..., directed_to_node_first_axis: _Optional[_Union[BuildingGrid.DirectedToNodeFirstAxis, str]] = ..., directed_to_node_second_axis: _Optional[_Union[BuildingGrid.DirectedToNodeSecondAxis, str]] = ..., parallel_to_two_nodes_first_node: _Optional[int] = ..., parallel_to_two_nodes_second_node: _Optional[int] = ..., parallel_to_two_nodes_plane_node: _Optional[int] = ..., parallel_to_two_nodes_first_axis: _Optional[_Union[BuildingGrid.ParallelToTwoNodesFirstAxis, str]] = ..., parallel_to_two_nodes_second_axis: _Optional[_Union[BuildingGrid.ParallelToTwoNodesSecondAxis, str]] = ..., parallel_to_member: _Optional[int] = ..., comment: _Optional[str] = ..., coordinates_list_x: _Optional[str] = ..., coordinates_list_y: _Optional[str] = ..., coordinates_list_z: _Optional[str] = ..., labels_list_x: _Optional[str] = ..., labels_list_y: _Optional[str] = ..., labels_list_z: _Optional[str] = ..., line_end_extension_x: _Optional[float] = ..., line_end_extension_y: _Optional[float] = ..., line_end_extension_z: _Optional[float] = ..., line_end_label_x: bool = ..., line_end_label_y: bool = ..., line_end_label_z: bool = ..., line_start_extension_x: _Optional[float] = ..., line_start_extension_y: _Optional[float] = ..., line_start_extension_z: _Optional[float] = ..., line_start_label_x: bool = ..., line_start_label_y: bool = ..., line_start_label_z: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
