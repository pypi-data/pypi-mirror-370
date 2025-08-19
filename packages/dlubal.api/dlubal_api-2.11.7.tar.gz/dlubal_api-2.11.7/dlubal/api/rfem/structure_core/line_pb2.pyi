from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Line(_message.Message):
    __slots__ = ("no", "type", "definition_nodes", "length", "comment", "arc_first_node", "arc_second_node", "arc_control_point", "arc_control_point_x", "arc_control_point_y", "arc_control_point_z", "arc_center", "arc_center_x", "arc_center_y", "arc_center_z", "arc_radius", "arc_height", "arc_alpha", "arc_alpha_adjustment_target", "circle_center", "circle_center_coordinate_1", "circle_center_coordinate_2", "circle_center_coordinate_3", "circle_normal", "circle_normal_coordinate_1", "circle_normal_coordinate_2", "circle_normal_coordinate_3", "circle_rotation", "circle_node", "circle_node_coordinate_1", "circle_node_coordinate_2", "circle_node_coordinate_3", "circle_radius", "ellipse_first_node", "ellipse_second_node", "ellipse_control_point", "ellipse_control_point_x", "ellipse_control_point_y", "ellipse_control_point_z", "elliptical_arc_first_node", "elliptical_arc_second_node", "elliptical_arc_alpha", "elliptical_arc_beta", "elliptical_arc_normal", "elliptical_arc_normal_x", "elliptical_arc_normal_y", "elliptical_arc_normal_z", "elliptical_arc_major_radius", "elliptical_arc_minor_radius", "elliptical_arc_center", "elliptical_arc_center_x", "elliptical_arc_center_y", "elliptical_arc_center_z", "elliptical_arc_focus_1", "elliptical_arc_focus_1_x", "elliptical_arc_focus_1_y", "elliptical_arc_focus_1_z", "elliptical_arc_focus_2", "elliptical_arc_focus_2_x", "elliptical_arc_focus_2_y", "elliptical_arc_focus_2_z", "elliptical_arc_first_control_point", "elliptical_arc_first_control_point_x", "elliptical_arc_first_control_point_y", "elliptical_arc_first_control_point_z", "elliptical_arc_second_control_point", "elliptical_arc_second_control_point_x", "elliptical_arc_second_control_point_y", "elliptical_arc_second_control_point_z", "elliptical_arc_perimeter_control_point", "elliptical_arc_perimeter_control_point_x", "elliptical_arc_perimeter_control_point_y", "elliptical_arc_perimeter_control_point_z", "parabola_first_node", "parabola_second_node", "parabola_control_point", "parabola_control_point_x", "parabola_control_point_y", "parabola_control_point_z", "parabola_alpha", "parabola_focus_directrix_distance", "parabola_focus", "parabola_focus_x", "parabola_focus_y", "parabola_focus_z", "nurbs_order", "nurbs_control_points_by_components", "nurbs_control_points", "nurbs_knots", "is_rotated", "rotation_specification_type", "rotation_angle", "rotation_help_node", "rotation_plane", "rotation_surface_plane_type", "rotation_surface", "member", "support", "mesh_refinement", "line_weld_assignment", "has_line_welds", "is_generated", "generating_object_info", "arc_control_point_object", "ellipse_control_point_object", "elliptical_arc_first_control_point_object", "elliptical_arc_perimeter_control_point_object", "elliptical_arc_second_control_point_object", "parabola_control_point_object", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[Line.Type]
        TYPE_ARC: _ClassVar[Line.Type]
        TYPE_CIRCLE: _ClassVar[Line.Type]
        TYPE_CUT_VIA_SECTION: _ClassVar[Line.Type]
        TYPE_CUT_VIA_TWO_LINES: _ClassVar[Line.Type]
        TYPE_ELLIPSE: _ClassVar[Line.Type]
        TYPE_ELLIPTICAL_ARC: _ClassVar[Line.Type]
        TYPE_NURBS: _ClassVar[Line.Type]
        TYPE_PARABOLA: _ClassVar[Line.Type]
        TYPE_POLYLINE: _ClassVar[Line.Type]
        TYPE_SPLINE: _ClassVar[Line.Type]
    TYPE_UNKNOWN: Line.Type
    TYPE_ARC: Line.Type
    TYPE_CIRCLE: Line.Type
    TYPE_CUT_VIA_SECTION: Line.Type
    TYPE_CUT_VIA_TWO_LINES: Line.Type
    TYPE_ELLIPSE: Line.Type
    TYPE_ELLIPTICAL_ARC: Line.Type
    TYPE_NURBS: Line.Type
    TYPE_PARABOLA: Line.Type
    TYPE_POLYLINE: Line.Type
    TYPE_SPLINE: Line.Type
    class ArcAlphaAdjustmentTarget(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ARC_ALPHA_ADJUSTMENT_TARGET_BEGINNING_OF_ARC: _ClassVar[Line.ArcAlphaAdjustmentTarget]
        ARC_ALPHA_ADJUSTMENT_TARGET_ARC_CONTROL_POINT: _ClassVar[Line.ArcAlphaAdjustmentTarget]
        ARC_ALPHA_ADJUSTMENT_TARGET_END_OF_ARC: _ClassVar[Line.ArcAlphaAdjustmentTarget]
    ARC_ALPHA_ADJUSTMENT_TARGET_BEGINNING_OF_ARC: Line.ArcAlphaAdjustmentTarget
    ARC_ALPHA_ADJUSTMENT_TARGET_ARC_CONTROL_POINT: Line.ArcAlphaAdjustmentTarget
    ARC_ALPHA_ADJUSTMENT_TARGET_END_OF_ARC: Line.ArcAlphaAdjustmentTarget
    class RotationSpecificationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROTATION_SPECIFICATION_TYPE_BY_ANGLE: _ClassVar[Line.RotationSpecificationType]
        ROTATION_SPECIFICATION_TYPE_INSIDE: _ClassVar[Line.RotationSpecificationType]
        ROTATION_SPECIFICATION_TYPE_SURFACE: _ClassVar[Line.RotationSpecificationType]
        ROTATION_SPECIFICATION_TYPE_TO_NODE: _ClassVar[Line.RotationSpecificationType]
    ROTATION_SPECIFICATION_TYPE_BY_ANGLE: Line.RotationSpecificationType
    ROTATION_SPECIFICATION_TYPE_INSIDE: Line.RotationSpecificationType
    ROTATION_SPECIFICATION_TYPE_SURFACE: Line.RotationSpecificationType
    ROTATION_SPECIFICATION_TYPE_TO_NODE: Line.RotationSpecificationType
    class RotationPlane(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROTATION_PLANE_XY: _ClassVar[Line.RotationPlane]
        ROTATION_PLANE_XZ: _ClassVar[Line.RotationPlane]
    ROTATION_PLANE_XY: Line.RotationPlane
    ROTATION_PLANE_XZ: Line.RotationPlane
    class RotationSurfacePlaneType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROTATION_SURFACE_PLANE_TYPE_ROTATION_PLANE_XY: _ClassVar[Line.RotationSurfacePlaneType]
        ROTATION_SURFACE_PLANE_TYPE_ROTATION_PLANE_XZ: _ClassVar[Line.RotationSurfacePlaneType]
    ROTATION_SURFACE_PLANE_TYPE_ROTATION_PLANE_XY: Line.RotationSurfacePlaneType
    ROTATION_SURFACE_PLANE_TYPE_ROTATION_PLANE_XZ: Line.RotationSurfacePlaneType
    class NurbsControlPointsByComponentsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[Line.NurbsControlPointsByComponentsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[Line.NurbsControlPointsByComponentsRow, _Mapping]]] = ...) -> None: ...
    class NurbsControlPointsByComponentsRow(_message.Message):
        __slots__ = ("no", "description", "global_coordinate_x", "global_coordinate_y", "global_coordinate_z", "weight")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        GLOBAL_COORDINATE_X_FIELD_NUMBER: _ClassVar[int]
        GLOBAL_COORDINATE_Y_FIELD_NUMBER: _ClassVar[int]
        GLOBAL_COORDINATE_Z_FIELD_NUMBER: _ClassVar[int]
        WEIGHT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        global_coordinate_x: float
        global_coordinate_y: float
        global_coordinate_z: float
        weight: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., global_coordinate_x: _Optional[float] = ..., global_coordinate_y: _Optional[float] = ..., global_coordinate_z: _Optional[float] = ..., weight: _Optional[float] = ...) -> None: ...
    class NurbsControlPointsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[Line.NurbsControlPointsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[Line.NurbsControlPointsRow, _Mapping]]] = ...) -> None: ...
    class NurbsControlPointsRow(_message.Message):
        __slots__ = ("no", "description", "control_point", "global_coordinates", "coordinates", "weight")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        CONTROL_POINT_FIELD_NUMBER: _ClassVar[int]
        GLOBAL_COORDINATES_FIELD_NUMBER: _ClassVar[int]
        COORDINATES_FIELD_NUMBER: _ClassVar[int]
        WEIGHT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        control_point: int
        global_coordinates: _common_pb2.Vector3d
        coordinates: _common_pb2.Vector3d
        weight: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., control_point: _Optional[int] = ..., global_coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., weight: _Optional[float] = ...) -> None: ...
    class NurbsKnotsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[Line.NurbsKnotsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[Line.NurbsKnotsRow, _Mapping]]] = ...) -> None: ...
    class NurbsKnotsRow(_message.Message):
        __slots__ = ("no", "description", "knot_value")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        KNOT_VALUE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        knot_value: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., knot_value: _Optional[float] = ...) -> None: ...
    class LineWeldAssignmentTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[Line.LineWeldAssignmentRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[Line.LineWeldAssignmentRow, _Mapping]]] = ...) -> None: ...
    class LineWeldAssignmentRow(_message.Message):
        __slots__ = ("no", "description", "weld", "surface1", "surface2", "surface3")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        WELD_FIELD_NUMBER: _ClassVar[int]
        SURFACE1_FIELD_NUMBER: _ClassVar[int]
        SURFACE2_FIELD_NUMBER: _ClassVar[int]
        SURFACE3_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        weld: int
        surface1: int
        surface2: int
        surface3: int
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., weld: _Optional[int] = ..., surface1: _Optional[int] = ..., surface2: _Optional[int] = ..., surface3: _Optional[int] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_NODES_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ARC_FIRST_NODE_FIELD_NUMBER: _ClassVar[int]
    ARC_SECOND_NODE_FIELD_NUMBER: _ClassVar[int]
    ARC_CONTROL_POINT_FIELD_NUMBER: _ClassVar[int]
    ARC_CONTROL_POINT_X_FIELD_NUMBER: _ClassVar[int]
    ARC_CONTROL_POINT_Y_FIELD_NUMBER: _ClassVar[int]
    ARC_CONTROL_POINT_Z_FIELD_NUMBER: _ClassVar[int]
    ARC_CENTER_FIELD_NUMBER: _ClassVar[int]
    ARC_CENTER_X_FIELD_NUMBER: _ClassVar[int]
    ARC_CENTER_Y_FIELD_NUMBER: _ClassVar[int]
    ARC_CENTER_Z_FIELD_NUMBER: _ClassVar[int]
    ARC_RADIUS_FIELD_NUMBER: _ClassVar[int]
    ARC_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    ARC_ALPHA_FIELD_NUMBER: _ClassVar[int]
    ARC_ALPHA_ADJUSTMENT_TARGET_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_CENTER_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_CENTER_COORDINATE_1_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_CENTER_COORDINATE_2_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_CENTER_COORDINATE_3_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_NORMAL_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_NORMAL_COORDINATE_1_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_NORMAL_COORDINATE_2_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_NORMAL_COORDINATE_3_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_NODE_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_NODE_COORDINATE_1_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_NODE_COORDINATE_2_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_NODE_COORDINATE_3_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_RADIUS_FIELD_NUMBER: _ClassVar[int]
    ELLIPSE_FIRST_NODE_FIELD_NUMBER: _ClassVar[int]
    ELLIPSE_SECOND_NODE_FIELD_NUMBER: _ClassVar[int]
    ELLIPSE_CONTROL_POINT_FIELD_NUMBER: _ClassVar[int]
    ELLIPSE_CONTROL_POINT_X_FIELD_NUMBER: _ClassVar[int]
    ELLIPSE_CONTROL_POINT_Y_FIELD_NUMBER: _ClassVar[int]
    ELLIPSE_CONTROL_POINT_Z_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_FIRST_NODE_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_SECOND_NODE_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_ALPHA_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_BETA_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_NORMAL_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_NORMAL_X_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_NORMAL_Y_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_NORMAL_Z_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_MAJOR_RADIUS_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_MINOR_RADIUS_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_CENTER_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_CENTER_X_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_CENTER_Y_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_CENTER_Z_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_FOCUS_1_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_FOCUS_1_X_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_FOCUS_1_Y_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_FOCUS_1_Z_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_FOCUS_2_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_FOCUS_2_X_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_FOCUS_2_Y_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_FOCUS_2_Z_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_FIRST_CONTROL_POINT_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_FIRST_CONTROL_POINT_X_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_FIRST_CONTROL_POINT_Y_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_FIRST_CONTROL_POINT_Z_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_SECOND_CONTROL_POINT_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_SECOND_CONTROL_POINT_X_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_SECOND_CONTROL_POINT_Y_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_SECOND_CONTROL_POINT_Z_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_PERIMETER_CONTROL_POINT_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_PERIMETER_CONTROL_POINT_X_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_PERIMETER_CONTROL_POINT_Y_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_PERIMETER_CONTROL_POINT_Z_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_FIRST_NODE_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_SECOND_NODE_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_CONTROL_POINT_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_CONTROL_POINT_X_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_CONTROL_POINT_Y_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_CONTROL_POINT_Z_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_ALPHA_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_FOCUS_DIRECTRIX_DISTANCE_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_FOCUS_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_FOCUS_X_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_FOCUS_Y_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_FOCUS_Z_FIELD_NUMBER: _ClassVar[int]
    NURBS_ORDER_FIELD_NUMBER: _ClassVar[int]
    NURBS_CONTROL_POINTS_BY_COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    NURBS_CONTROL_POINTS_FIELD_NUMBER: _ClassVar[int]
    NURBS_KNOTS_FIELD_NUMBER: _ClassVar[int]
    IS_ROTATED_FIELD_NUMBER: _ClassVar[int]
    ROTATION_SPECIFICATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_HELP_NODE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_PLANE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_SURFACE_PLANE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_SURFACE_FIELD_NUMBER: _ClassVar[int]
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_FIELD_NUMBER: _ClassVar[int]
    MESH_REFINEMENT_FIELD_NUMBER: _ClassVar[int]
    LINE_WELD_ASSIGNMENT_FIELD_NUMBER: _ClassVar[int]
    HAS_LINE_WELDS_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ARC_CONTROL_POINT_OBJECT_FIELD_NUMBER: _ClassVar[int]
    ELLIPSE_CONTROL_POINT_OBJECT_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_FIRST_CONTROL_POINT_OBJECT_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_PERIMETER_CONTROL_POINT_OBJECT_FIELD_NUMBER: _ClassVar[int]
    ELLIPTICAL_ARC_SECOND_CONTROL_POINT_OBJECT_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_CONTROL_POINT_OBJECT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: Line.Type
    definition_nodes: _containers.RepeatedScalarFieldContainer[int]
    length: float
    comment: str
    arc_first_node: int
    arc_second_node: int
    arc_control_point: _common_pb2.Vector3d
    arc_control_point_x: float
    arc_control_point_y: float
    arc_control_point_z: float
    arc_center: _common_pb2.Vector3d
    arc_center_x: float
    arc_center_y: float
    arc_center_z: float
    arc_radius: float
    arc_height: float
    arc_alpha: float
    arc_alpha_adjustment_target: Line.ArcAlphaAdjustmentTarget
    circle_center: _common_pb2.Vector3d
    circle_center_coordinate_1: float
    circle_center_coordinate_2: float
    circle_center_coordinate_3: float
    circle_normal: _common_pb2.Vector3d
    circle_normal_coordinate_1: float
    circle_normal_coordinate_2: float
    circle_normal_coordinate_3: float
    circle_rotation: float
    circle_node: _common_pb2.Vector3d
    circle_node_coordinate_1: float
    circle_node_coordinate_2: float
    circle_node_coordinate_3: float
    circle_radius: float
    ellipse_first_node: int
    ellipse_second_node: int
    ellipse_control_point: _common_pb2.Vector3d
    ellipse_control_point_x: float
    ellipse_control_point_y: float
    ellipse_control_point_z: float
    elliptical_arc_first_node: int
    elliptical_arc_second_node: int
    elliptical_arc_alpha: float
    elliptical_arc_beta: float
    elliptical_arc_normal: _common_pb2.Vector3d
    elliptical_arc_normal_x: float
    elliptical_arc_normal_y: float
    elliptical_arc_normal_z: float
    elliptical_arc_major_radius: float
    elliptical_arc_minor_radius: float
    elliptical_arc_center: _common_pb2.Vector3d
    elliptical_arc_center_x: float
    elliptical_arc_center_y: float
    elliptical_arc_center_z: float
    elliptical_arc_focus_1: _common_pb2.Vector3d
    elliptical_arc_focus_1_x: float
    elliptical_arc_focus_1_y: float
    elliptical_arc_focus_1_z: float
    elliptical_arc_focus_2: _common_pb2.Vector3d
    elliptical_arc_focus_2_x: float
    elliptical_arc_focus_2_y: float
    elliptical_arc_focus_2_z: float
    elliptical_arc_first_control_point: _common_pb2.Vector3d
    elliptical_arc_first_control_point_x: float
    elliptical_arc_first_control_point_y: float
    elliptical_arc_first_control_point_z: float
    elliptical_arc_second_control_point: _common_pb2.Vector3d
    elliptical_arc_second_control_point_x: float
    elliptical_arc_second_control_point_y: float
    elliptical_arc_second_control_point_z: float
    elliptical_arc_perimeter_control_point: _common_pb2.Vector3d
    elliptical_arc_perimeter_control_point_x: float
    elliptical_arc_perimeter_control_point_y: float
    elliptical_arc_perimeter_control_point_z: float
    parabola_first_node: int
    parabola_second_node: int
    parabola_control_point: _common_pb2.Vector3d
    parabola_control_point_x: float
    parabola_control_point_y: float
    parabola_control_point_z: float
    parabola_alpha: float
    parabola_focus_directrix_distance: float
    parabola_focus: _common_pb2.Vector3d
    parabola_focus_x: float
    parabola_focus_y: float
    parabola_focus_z: float
    nurbs_order: int
    nurbs_control_points_by_components: Line.NurbsControlPointsByComponentsTable
    nurbs_control_points: Line.NurbsControlPointsTable
    nurbs_knots: Line.NurbsKnotsTable
    is_rotated: bool
    rotation_specification_type: Line.RotationSpecificationType
    rotation_angle: float
    rotation_help_node: int
    rotation_plane: Line.RotationPlane
    rotation_surface_plane_type: Line.RotationSurfacePlaneType
    rotation_surface: int
    member: int
    support: int
    mesh_refinement: int
    line_weld_assignment: Line.LineWeldAssignmentTable
    has_line_welds: bool
    is_generated: bool
    generating_object_info: str
    arc_control_point_object: int
    ellipse_control_point_object: int
    elliptical_arc_first_control_point_object: int
    elliptical_arc_perimeter_control_point_object: int
    elliptical_arc_second_control_point_object: int
    parabola_control_point_object: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[Line.Type, str]] = ..., definition_nodes: _Optional[_Iterable[int]] = ..., length: _Optional[float] = ..., comment: _Optional[str] = ..., arc_first_node: _Optional[int] = ..., arc_second_node: _Optional[int] = ..., arc_control_point: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., arc_control_point_x: _Optional[float] = ..., arc_control_point_y: _Optional[float] = ..., arc_control_point_z: _Optional[float] = ..., arc_center: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., arc_center_x: _Optional[float] = ..., arc_center_y: _Optional[float] = ..., arc_center_z: _Optional[float] = ..., arc_radius: _Optional[float] = ..., arc_height: _Optional[float] = ..., arc_alpha: _Optional[float] = ..., arc_alpha_adjustment_target: _Optional[_Union[Line.ArcAlphaAdjustmentTarget, str]] = ..., circle_center: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., circle_center_coordinate_1: _Optional[float] = ..., circle_center_coordinate_2: _Optional[float] = ..., circle_center_coordinate_3: _Optional[float] = ..., circle_normal: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., circle_normal_coordinate_1: _Optional[float] = ..., circle_normal_coordinate_2: _Optional[float] = ..., circle_normal_coordinate_3: _Optional[float] = ..., circle_rotation: _Optional[float] = ..., circle_node: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., circle_node_coordinate_1: _Optional[float] = ..., circle_node_coordinate_2: _Optional[float] = ..., circle_node_coordinate_3: _Optional[float] = ..., circle_radius: _Optional[float] = ..., ellipse_first_node: _Optional[int] = ..., ellipse_second_node: _Optional[int] = ..., ellipse_control_point: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., ellipse_control_point_x: _Optional[float] = ..., ellipse_control_point_y: _Optional[float] = ..., ellipse_control_point_z: _Optional[float] = ..., elliptical_arc_first_node: _Optional[int] = ..., elliptical_arc_second_node: _Optional[int] = ..., elliptical_arc_alpha: _Optional[float] = ..., elliptical_arc_beta: _Optional[float] = ..., elliptical_arc_normal: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., elliptical_arc_normal_x: _Optional[float] = ..., elliptical_arc_normal_y: _Optional[float] = ..., elliptical_arc_normal_z: _Optional[float] = ..., elliptical_arc_major_radius: _Optional[float] = ..., elliptical_arc_minor_radius: _Optional[float] = ..., elliptical_arc_center: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., elliptical_arc_center_x: _Optional[float] = ..., elliptical_arc_center_y: _Optional[float] = ..., elliptical_arc_center_z: _Optional[float] = ..., elliptical_arc_focus_1: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., elliptical_arc_focus_1_x: _Optional[float] = ..., elliptical_arc_focus_1_y: _Optional[float] = ..., elliptical_arc_focus_1_z: _Optional[float] = ..., elliptical_arc_focus_2: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., elliptical_arc_focus_2_x: _Optional[float] = ..., elliptical_arc_focus_2_y: _Optional[float] = ..., elliptical_arc_focus_2_z: _Optional[float] = ..., elliptical_arc_first_control_point: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., elliptical_arc_first_control_point_x: _Optional[float] = ..., elliptical_arc_first_control_point_y: _Optional[float] = ..., elliptical_arc_first_control_point_z: _Optional[float] = ..., elliptical_arc_second_control_point: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., elliptical_arc_second_control_point_x: _Optional[float] = ..., elliptical_arc_second_control_point_y: _Optional[float] = ..., elliptical_arc_second_control_point_z: _Optional[float] = ..., elliptical_arc_perimeter_control_point: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., elliptical_arc_perimeter_control_point_x: _Optional[float] = ..., elliptical_arc_perimeter_control_point_y: _Optional[float] = ..., elliptical_arc_perimeter_control_point_z: _Optional[float] = ..., parabola_first_node: _Optional[int] = ..., parabola_second_node: _Optional[int] = ..., parabola_control_point: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., parabola_control_point_x: _Optional[float] = ..., parabola_control_point_y: _Optional[float] = ..., parabola_control_point_z: _Optional[float] = ..., parabola_alpha: _Optional[float] = ..., parabola_focus_directrix_distance: _Optional[float] = ..., parabola_focus: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., parabola_focus_x: _Optional[float] = ..., parabola_focus_y: _Optional[float] = ..., parabola_focus_z: _Optional[float] = ..., nurbs_order: _Optional[int] = ..., nurbs_control_points_by_components: _Optional[_Union[Line.NurbsControlPointsByComponentsTable, _Mapping]] = ..., nurbs_control_points: _Optional[_Union[Line.NurbsControlPointsTable, _Mapping]] = ..., nurbs_knots: _Optional[_Union[Line.NurbsKnotsTable, _Mapping]] = ..., is_rotated: bool = ..., rotation_specification_type: _Optional[_Union[Line.RotationSpecificationType, str]] = ..., rotation_angle: _Optional[float] = ..., rotation_help_node: _Optional[int] = ..., rotation_plane: _Optional[_Union[Line.RotationPlane, str]] = ..., rotation_surface_plane_type: _Optional[_Union[Line.RotationSurfacePlaneType, str]] = ..., rotation_surface: _Optional[int] = ..., member: _Optional[int] = ..., support: _Optional[int] = ..., mesh_refinement: _Optional[int] = ..., line_weld_assignment: _Optional[_Union[Line.LineWeldAssignmentTable, _Mapping]] = ..., has_line_welds: bool = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., arc_control_point_object: _Optional[int] = ..., ellipse_control_point_object: _Optional[int] = ..., elliptical_arc_first_control_point_object: _Optional[int] = ..., elliptical_arc_perimeter_control_point_object: _Optional[int] = ..., elliptical_arc_second_control_point_object: _Optional[int] = ..., parabola_control_point_object: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
