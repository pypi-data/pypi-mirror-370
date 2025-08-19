from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Dimension(_message.Message):
    __slots__ = ("no", "type", "user_defined_name_enabled", "name", "display_properties_index", "dimension_line_offset", "is_custom_vertical_position", "custom_vertical_position", "is_custom_horizontal_position", "custom_horizontal_position", "symbol", "comment", "measured_length", "measured_lengths", "measured_angle", "measured_angles", "measured_slope", "is_global_dimension_line_offset", "linear_coordinate_system", "linear_reference", "linear_plane", "linear_global_dimension_line_offset", "linear_global_dimension_line_offset_x", "linear_global_dimension_line_offset_y", "linear_global_dimension_line_offset_z", "linear_reference_table", "angular_reference_table", "angular_quadrant", "angular_angle_greater_than_180", "slope_coordinate_system", "slope_plane", "slope_direction", "slope_refer_distance_from_line_end", "slope_position_is_relative", "slope_position_absolute", "slope_position_relative", "elevation_reference_object_type", "elevation_reference_node", "elevation_reference_point_coordinates", "elevation_reference_point_coordinate_x", "elevation_reference_point_coordinate_y", "elevation_reference_point_coordinate_z", "elevation_distance_from_picked_position", "elevation_rotation_around_z", "elevation_reference_level_height", "elevation_is_altitude", "elevation_altitude", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[Dimension.Type]
        TYPE_ANGULAR: _ClassVar[Dimension.Type]
        TYPE_ELEVATION: _ClassVar[Dimension.Type]
        TYPE_LINEAR: _ClassVar[Dimension.Type]
        TYPE_SLOPE: _ClassVar[Dimension.Type]
    TYPE_UNKNOWN: Dimension.Type
    TYPE_ANGULAR: Dimension.Type
    TYPE_ELEVATION: Dimension.Type
    TYPE_LINEAR: Dimension.Type
    TYPE_SLOPE: Dimension.Type
    class CustomVerticalPosition(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CUSTOM_VERTICAL_POSITION_CENTER: _ClassVar[Dimension.CustomVerticalPosition]
        CUSTOM_VERTICAL_POSITION_ABOVE: _ClassVar[Dimension.CustomVerticalPosition]
        CUSTOM_VERTICAL_POSITION_UNDER: _ClassVar[Dimension.CustomVerticalPosition]
    CUSTOM_VERTICAL_POSITION_CENTER: Dimension.CustomVerticalPosition
    CUSTOM_VERTICAL_POSITION_ABOVE: Dimension.CustomVerticalPosition
    CUSTOM_VERTICAL_POSITION_UNDER: Dimension.CustomVerticalPosition
    class CustomHorizontalPosition(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CUSTOM_HORIZONTAL_POSITION_CENTER: _ClassVar[Dimension.CustomHorizontalPosition]
        CUSTOM_HORIZONTAL_POSITION_LEFT: _ClassVar[Dimension.CustomHorizontalPosition]
        CUSTOM_HORIZONTAL_POSITION_RIGHT: _ClassVar[Dimension.CustomHorizontalPosition]
    CUSTOM_HORIZONTAL_POSITION_CENTER: Dimension.CustomHorizontalPosition
    CUSTOM_HORIZONTAL_POSITION_LEFT: Dimension.CustomHorizontalPosition
    CUSTOM_HORIZONTAL_POSITION_RIGHT: Dimension.CustomHorizontalPosition
    class LinearReference(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LINEAR_REFERENCE_LENGTH: _ClassVar[Dimension.LinearReference]
        LINEAR_REFERENCE_PROJECTION_IN_X: _ClassVar[Dimension.LinearReference]
        LINEAR_REFERENCE_PROJECTION_IN_Y: _ClassVar[Dimension.LinearReference]
        LINEAR_REFERENCE_PROJECTION_IN_Z: _ClassVar[Dimension.LinearReference]
    LINEAR_REFERENCE_LENGTH: Dimension.LinearReference
    LINEAR_REFERENCE_PROJECTION_IN_X: Dimension.LinearReference
    LINEAR_REFERENCE_PROJECTION_IN_Y: Dimension.LinearReference
    LINEAR_REFERENCE_PROJECTION_IN_Z: Dimension.LinearReference
    class LinearPlane(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LINEAR_PLANE_FIRST: _ClassVar[Dimension.LinearPlane]
        LINEAR_PLANE_SECOND: _ClassVar[Dimension.LinearPlane]
    LINEAR_PLANE_FIRST: Dimension.LinearPlane
    LINEAR_PLANE_SECOND: Dimension.LinearPlane
    class AngularQuadrant(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ANGULAR_QUADRANT_POSITIVE: _ClassVar[Dimension.AngularQuadrant]
        ANGULAR_QUADRANT_LEFT: _ClassVar[Dimension.AngularQuadrant]
        ANGULAR_QUADRANT_NEGATIVE: _ClassVar[Dimension.AngularQuadrant]
        ANGULAR_QUADRANT_RIGHT: _ClassVar[Dimension.AngularQuadrant]
    ANGULAR_QUADRANT_POSITIVE: Dimension.AngularQuadrant
    ANGULAR_QUADRANT_LEFT: Dimension.AngularQuadrant
    ANGULAR_QUADRANT_NEGATIVE: Dimension.AngularQuadrant
    ANGULAR_QUADRANT_RIGHT: Dimension.AngularQuadrant
    class SlopePlane(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SLOPE_PLANE_XY: _ClassVar[Dimension.SlopePlane]
        SLOPE_PLANE_XZ: _ClassVar[Dimension.SlopePlane]
        SLOPE_PLANE_YZ: _ClassVar[Dimension.SlopePlane]
    SLOPE_PLANE_XY: Dimension.SlopePlane
    SLOPE_PLANE_XZ: Dimension.SlopePlane
    SLOPE_PLANE_YZ: Dimension.SlopePlane
    class SlopeDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SLOPE_DIRECTION_UPWARD: _ClassVar[Dimension.SlopeDirection]
        SLOPE_DIRECTION_DOWNWARD: _ClassVar[Dimension.SlopeDirection]
    SLOPE_DIRECTION_UPWARD: Dimension.SlopeDirection
    SLOPE_DIRECTION_DOWNWARD: Dimension.SlopeDirection
    class ElevationReferenceObjectType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ELEVATION_REFERENCE_OBJECT_TYPE_UNKNOWN: _ClassVar[Dimension.ElevationReferenceObjectType]
        ELEVATION_REFERENCE_OBJECT_TYPE_NODE: _ClassVar[Dimension.ElevationReferenceObjectType]
        ELEVATION_REFERENCE_OBJECT_TYPE_POINT: _ClassVar[Dimension.ElevationReferenceObjectType]
    ELEVATION_REFERENCE_OBJECT_TYPE_UNKNOWN: Dimension.ElevationReferenceObjectType
    ELEVATION_REFERENCE_OBJECT_TYPE_NODE: Dimension.ElevationReferenceObjectType
    ELEVATION_REFERENCE_OBJECT_TYPE_POINT: Dimension.ElevationReferenceObjectType
    class LinearReferenceTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[Dimension.LinearReferenceTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[Dimension.LinearReferenceTableRow, _Mapping]]] = ...) -> None: ...
    class LinearReferenceTableRow(_message.Message):
        __slots__ = ("no", "description", "reference_object_type", "reference_object", "line_relative_distance", "coordinate_x", "coordinate_y", "coordinate_z")
        class ReferenceObjectType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            REFERENCE_OBJECT_TYPE_NODE: _ClassVar[Dimension.LinearReferenceTableRow.ReferenceObjectType]
            REFERENCE_OBJECT_TYPE_CONTROL_POINT: _ClassVar[Dimension.LinearReferenceTableRow.ReferenceObjectType]
            REFERENCE_OBJECT_TYPE_MEMBER: _ClassVar[Dimension.LinearReferenceTableRow.ReferenceObjectType]
            REFERENCE_OBJECT_TYPE_POINT: _ClassVar[Dimension.LinearReferenceTableRow.ReferenceObjectType]
            REFERENCE_OBJECT_TYPE_SNAP_POSITION: _ClassVar[Dimension.LinearReferenceTableRow.ReferenceObjectType]
        REFERENCE_OBJECT_TYPE_NODE: Dimension.LinearReferenceTableRow.ReferenceObjectType
        REFERENCE_OBJECT_TYPE_CONTROL_POINT: Dimension.LinearReferenceTableRow.ReferenceObjectType
        REFERENCE_OBJECT_TYPE_MEMBER: Dimension.LinearReferenceTableRow.ReferenceObjectType
        REFERENCE_OBJECT_TYPE_POINT: Dimension.LinearReferenceTableRow.ReferenceObjectType
        REFERENCE_OBJECT_TYPE_SNAP_POSITION: Dimension.LinearReferenceTableRow.ReferenceObjectType
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        REFERENCE_OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
        REFERENCE_OBJECT_FIELD_NUMBER: _ClassVar[int]
        LINE_RELATIVE_DISTANCE_FIELD_NUMBER: _ClassVar[int]
        COORDINATE_X_FIELD_NUMBER: _ClassVar[int]
        COORDINATE_Y_FIELD_NUMBER: _ClassVar[int]
        COORDINATE_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        reference_object_type: Dimension.LinearReferenceTableRow.ReferenceObjectType
        reference_object: int
        line_relative_distance: float
        coordinate_x: float
        coordinate_y: float
        coordinate_z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., reference_object_type: _Optional[_Union[Dimension.LinearReferenceTableRow.ReferenceObjectType, str]] = ..., reference_object: _Optional[int] = ..., line_relative_distance: _Optional[float] = ..., coordinate_x: _Optional[float] = ..., coordinate_y: _Optional[float] = ..., coordinate_z: _Optional[float] = ...) -> None: ...
    class AngularReferenceTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[Dimension.AngularReferenceTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[Dimension.AngularReferenceTableRow, _Mapping]]] = ...) -> None: ...
    class AngularReferenceTableRow(_message.Message):
        __slots__ = ("no", "description", "reference_object_type", "reference_object", "line_relative_distance", "coordinate_x", "coordinate_y", "coordinate_z")
        class ReferenceObjectType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            REFERENCE_OBJECT_TYPE_NODE: _ClassVar[Dimension.AngularReferenceTableRow.ReferenceObjectType]
            REFERENCE_OBJECT_TYPE_CONTROL_POINT: _ClassVar[Dimension.AngularReferenceTableRow.ReferenceObjectType]
            REFERENCE_OBJECT_TYPE_MEMBER: _ClassVar[Dimension.AngularReferenceTableRow.ReferenceObjectType]
            REFERENCE_OBJECT_TYPE_POINT: _ClassVar[Dimension.AngularReferenceTableRow.ReferenceObjectType]
            REFERENCE_OBJECT_TYPE_SNAP_POSITION: _ClassVar[Dimension.AngularReferenceTableRow.ReferenceObjectType]
        REFERENCE_OBJECT_TYPE_NODE: Dimension.AngularReferenceTableRow.ReferenceObjectType
        REFERENCE_OBJECT_TYPE_CONTROL_POINT: Dimension.AngularReferenceTableRow.ReferenceObjectType
        REFERENCE_OBJECT_TYPE_MEMBER: Dimension.AngularReferenceTableRow.ReferenceObjectType
        REFERENCE_OBJECT_TYPE_POINT: Dimension.AngularReferenceTableRow.ReferenceObjectType
        REFERENCE_OBJECT_TYPE_SNAP_POSITION: Dimension.AngularReferenceTableRow.ReferenceObjectType
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        REFERENCE_OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
        REFERENCE_OBJECT_FIELD_NUMBER: _ClassVar[int]
        LINE_RELATIVE_DISTANCE_FIELD_NUMBER: _ClassVar[int]
        COORDINATE_X_FIELD_NUMBER: _ClassVar[int]
        COORDINATE_Y_FIELD_NUMBER: _ClassVar[int]
        COORDINATE_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        reference_object_type: Dimension.AngularReferenceTableRow.ReferenceObjectType
        reference_object: int
        line_relative_distance: float
        coordinate_x: float
        coordinate_y: float
        coordinate_z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., reference_object_type: _Optional[_Union[Dimension.AngularReferenceTableRow.ReferenceObjectType, str]] = ..., reference_object: _Optional[int] = ..., line_relative_distance: _Optional[float] = ..., coordinate_x: _Optional[float] = ..., coordinate_y: _Optional[float] = ..., coordinate_z: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_PROPERTIES_INDEX_FIELD_NUMBER: _ClassVar[int]
    DIMENSION_LINE_OFFSET_FIELD_NUMBER: _ClassVar[int]
    IS_CUSTOM_VERTICAL_POSITION_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_VERTICAL_POSITION_FIELD_NUMBER: _ClassVar[int]
    IS_CUSTOM_HORIZONTAL_POSITION_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_HORIZONTAL_POSITION_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEASURED_LENGTH_FIELD_NUMBER: _ClassVar[int]
    MEASURED_LENGTHS_FIELD_NUMBER: _ClassVar[int]
    MEASURED_ANGLE_FIELD_NUMBER: _ClassVar[int]
    MEASURED_ANGLES_FIELD_NUMBER: _ClassVar[int]
    MEASURED_SLOPE_FIELD_NUMBER: _ClassVar[int]
    IS_GLOBAL_DIMENSION_LINE_OFFSET_FIELD_NUMBER: _ClassVar[int]
    LINEAR_COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    LINEAR_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    LINEAR_PLANE_FIELD_NUMBER: _ClassVar[int]
    LINEAR_GLOBAL_DIMENSION_LINE_OFFSET_FIELD_NUMBER: _ClassVar[int]
    LINEAR_GLOBAL_DIMENSION_LINE_OFFSET_X_FIELD_NUMBER: _ClassVar[int]
    LINEAR_GLOBAL_DIMENSION_LINE_OFFSET_Y_FIELD_NUMBER: _ClassVar[int]
    LINEAR_GLOBAL_DIMENSION_LINE_OFFSET_Z_FIELD_NUMBER: _ClassVar[int]
    LINEAR_REFERENCE_TABLE_FIELD_NUMBER: _ClassVar[int]
    ANGULAR_REFERENCE_TABLE_FIELD_NUMBER: _ClassVar[int]
    ANGULAR_QUADRANT_FIELD_NUMBER: _ClassVar[int]
    ANGULAR_ANGLE_GREATER_THAN_180_FIELD_NUMBER: _ClassVar[int]
    SLOPE_COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    SLOPE_PLANE_FIELD_NUMBER: _ClassVar[int]
    SLOPE_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    SLOPE_REFER_DISTANCE_FROM_LINE_END_FIELD_NUMBER: _ClassVar[int]
    SLOPE_POSITION_IS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    SLOPE_POSITION_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    SLOPE_POSITION_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_REFERENCE_OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_REFERENCE_NODE_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_REFERENCE_POINT_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_REFERENCE_POINT_COORDINATE_X_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_REFERENCE_POINT_COORDINATE_Y_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_REFERENCE_POINT_COORDINATE_Z_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_DISTANCE_FROM_PICKED_POSITION_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_ROTATION_AROUND_Z_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_REFERENCE_LEVEL_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_IS_ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: Dimension.Type
    user_defined_name_enabled: bool
    name: str
    display_properties_index: int
    dimension_line_offset: float
    is_custom_vertical_position: bool
    custom_vertical_position: Dimension.CustomVerticalPosition
    is_custom_horizontal_position: bool
    custom_horizontal_position: Dimension.CustomHorizontalPosition
    symbol: str
    comment: str
    measured_length: float
    measured_lengths: _containers.RepeatedScalarFieldContainer[int]
    measured_angle: float
    measured_angles: _containers.RepeatedScalarFieldContainer[int]
    measured_slope: float
    is_global_dimension_line_offset: bool
    linear_coordinate_system: int
    linear_reference: Dimension.LinearReference
    linear_plane: Dimension.LinearPlane
    linear_global_dimension_line_offset: _common_pb2.Vector3d
    linear_global_dimension_line_offset_x: float
    linear_global_dimension_line_offset_y: float
    linear_global_dimension_line_offset_z: float
    linear_reference_table: Dimension.LinearReferenceTable
    angular_reference_table: Dimension.AngularReferenceTable
    angular_quadrant: Dimension.AngularQuadrant
    angular_angle_greater_than_180: bool
    slope_coordinate_system: int
    slope_plane: Dimension.SlopePlane
    slope_direction: Dimension.SlopeDirection
    slope_refer_distance_from_line_end: bool
    slope_position_is_relative: bool
    slope_position_absolute: float
    slope_position_relative: float
    elevation_reference_object_type: Dimension.ElevationReferenceObjectType
    elevation_reference_node: int
    elevation_reference_point_coordinates: _common_pb2.Vector3d
    elevation_reference_point_coordinate_x: float
    elevation_reference_point_coordinate_y: float
    elevation_reference_point_coordinate_z: float
    elevation_distance_from_picked_position: float
    elevation_rotation_around_z: float
    elevation_reference_level_height: float
    elevation_is_altitude: bool
    elevation_altitude: float
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[Dimension.Type, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., display_properties_index: _Optional[int] = ..., dimension_line_offset: _Optional[float] = ..., is_custom_vertical_position: bool = ..., custom_vertical_position: _Optional[_Union[Dimension.CustomVerticalPosition, str]] = ..., is_custom_horizontal_position: bool = ..., custom_horizontal_position: _Optional[_Union[Dimension.CustomHorizontalPosition, str]] = ..., symbol: _Optional[str] = ..., comment: _Optional[str] = ..., measured_length: _Optional[float] = ..., measured_lengths: _Optional[_Iterable[int]] = ..., measured_angle: _Optional[float] = ..., measured_angles: _Optional[_Iterable[int]] = ..., measured_slope: _Optional[float] = ..., is_global_dimension_line_offset: bool = ..., linear_coordinate_system: _Optional[int] = ..., linear_reference: _Optional[_Union[Dimension.LinearReference, str]] = ..., linear_plane: _Optional[_Union[Dimension.LinearPlane, str]] = ..., linear_global_dimension_line_offset: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., linear_global_dimension_line_offset_x: _Optional[float] = ..., linear_global_dimension_line_offset_y: _Optional[float] = ..., linear_global_dimension_line_offset_z: _Optional[float] = ..., linear_reference_table: _Optional[_Union[Dimension.LinearReferenceTable, _Mapping]] = ..., angular_reference_table: _Optional[_Union[Dimension.AngularReferenceTable, _Mapping]] = ..., angular_quadrant: _Optional[_Union[Dimension.AngularQuadrant, str]] = ..., angular_angle_greater_than_180: bool = ..., slope_coordinate_system: _Optional[int] = ..., slope_plane: _Optional[_Union[Dimension.SlopePlane, str]] = ..., slope_direction: _Optional[_Union[Dimension.SlopeDirection, str]] = ..., slope_refer_distance_from_line_end: bool = ..., slope_position_is_relative: bool = ..., slope_position_absolute: _Optional[float] = ..., slope_position_relative: _Optional[float] = ..., elevation_reference_object_type: _Optional[_Union[Dimension.ElevationReferenceObjectType, str]] = ..., elevation_reference_node: _Optional[int] = ..., elevation_reference_point_coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., elevation_reference_point_coordinate_x: _Optional[float] = ..., elevation_reference_point_coordinate_y: _Optional[float] = ..., elevation_reference_point_coordinate_z: _Optional[float] = ..., elevation_distance_from_picked_position: _Optional[float] = ..., elevation_rotation_around_z: _Optional[float] = ..., elevation_reference_level_height: _Optional[float] = ..., elevation_is_altitude: bool = ..., elevation_altitude: _Optional[float] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
