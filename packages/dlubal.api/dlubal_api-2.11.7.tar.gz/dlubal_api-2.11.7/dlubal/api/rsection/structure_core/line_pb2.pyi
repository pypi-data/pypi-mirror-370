from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Line(_message.Message):
    __slots__ = ("no", "type", "definition_points", "length", "circle_point", "comment", "arc_first_point", "arc_second_point", "arc_control_point", "arc_control_point_y", "arc_control_point_z", "arc_center", "arc_center_y", "arc_center_z", "arc_radius", "arc_height", "arc_alpha", "arc_alpha_adjustment_target", "circle_center", "circle_center_coordinate_y", "circle_center_coordinate_z", "circle_rotation", "circle_radius", "ellipse_first_point", "ellipse_second_point", "ellipse_control_point", "ellipse_control_point_y", "ellipse_control_point_z", "parabola_first_point", "parabola_second_point", "parabola_control_point", "parabola_control_point_y", "parabola_control_point_z", "parabola_focus_directrix_distance", "parabola_alpha", "parabola_focus", "parabola_focus_y", "parabola_focus_z", "nurbs_order", "nurbs_control_points_by_components", "nurbs_control_points", "nurbs_knots", "id_for_export_import", "metadata_for_export_import")
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
    class NurbsControlPointsByComponentsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[Line.NurbsControlPointsByComponentsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[Line.NurbsControlPointsByComponentsRow, _Mapping]]] = ...) -> None: ...
    class NurbsControlPointsByComponentsRow(_message.Message):
        __slots__ = ("no", "description", "global_coordinate_y", "global_coordinate_z", "weight")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        GLOBAL_COORDINATE_Y_FIELD_NUMBER: _ClassVar[int]
        GLOBAL_COORDINATE_Z_FIELD_NUMBER: _ClassVar[int]
        WEIGHT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        global_coordinate_y: float
        global_coordinate_z: float
        weight: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., global_coordinate_y: _Optional[float] = ..., global_coordinate_z: _Optional[float] = ..., weight: _Optional[float] = ...) -> None: ...
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
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_POINTS_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_POINT_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ARC_FIRST_POINT_FIELD_NUMBER: _ClassVar[int]
    ARC_SECOND_POINT_FIELD_NUMBER: _ClassVar[int]
    ARC_CONTROL_POINT_FIELD_NUMBER: _ClassVar[int]
    ARC_CONTROL_POINT_Y_FIELD_NUMBER: _ClassVar[int]
    ARC_CONTROL_POINT_Z_FIELD_NUMBER: _ClassVar[int]
    ARC_CENTER_FIELD_NUMBER: _ClassVar[int]
    ARC_CENTER_Y_FIELD_NUMBER: _ClassVar[int]
    ARC_CENTER_Z_FIELD_NUMBER: _ClassVar[int]
    ARC_RADIUS_FIELD_NUMBER: _ClassVar[int]
    ARC_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    ARC_ALPHA_FIELD_NUMBER: _ClassVar[int]
    ARC_ALPHA_ADJUSTMENT_TARGET_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_CENTER_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_CENTER_COORDINATE_Y_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_CENTER_COORDINATE_Z_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_RADIUS_FIELD_NUMBER: _ClassVar[int]
    ELLIPSE_FIRST_POINT_FIELD_NUMBER: _ClassVar[int]
    ELLIPSE_SECOND_POINT_FIELD_NUMBER: _ClassVar[int]
    ELLIPSE_CONTROL_POINT_FIELD_NUMBER: _ClassVar[int]
    ELLIPSE_CONTROL_POINT_Y_FIELD_NUMBER: _ClassVar[int]
    ELLIPSE_CONTROL_POINT_Z_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_FIRST_POINT_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_SECOND_POINT_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_CONTROL_POINT_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_CONTROL_POINT_Y_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_CONTROL_POINT_Z_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_FOCUS_DIRECTRIX_DISTANCE_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_ALPHA_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_FOCUS_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_FOCUS_Y_FIELD_NUMBER: _ClassVar[int]
    PARABOLA_FOCUS_Z_FIELD_NUMBER: _ClassVar[int]
    NURBS_ORDER_FIELD_NUMBER: _ClassVar[int]
    NURBS_CONTROL_POINTS_BY_COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    NURBS_CONTROL_POINTS_FIELD_NUMBER: _ClassVar[int]
    NURBS_KNOTS_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: Line.Type
    definition_points: _containers.RepeatedScalarFieldContainer[int]
    length: float
    circle_point: _common_pb2.Vector3d
    comment: str
    arc_first_point: int
    arc_second_point: int
    arc_control_point: _common_pb2.Vector3d
    arc_control_point_y: float
    arc_control_point_z: float
    arc_center: _common_pb2.Vector3d
    arc_center_y: float
    arc_center_z: float
    arc_radius: float
    arc_height: float
    arc_alpha: float
    arc_alpha_adjustment_target: Line.ArcAlphaAdjustmentTarget
    circle_center: _common_pb2.Vector3d
    circle_center_coordinate_y: float
    circle_center_coordinate_z: float
    circle_rotation: float
    circle_radius: float
    ellipse_first_point: int
    ellipse_second_point: int
    ellipse_control_point: _common_pb2.Vector3d
    ellipse_control_point_y: float
    ellipse_control_point_z: float
    parabola_first_point: int
    parabola_second_point: int
    parabola_control_point: _common_pb2.Vector3d
    parabola_control_point_y: float
    parabola_control_point_z: float
    parabola_focus_directrix_distance: float
    parabola_alpha: float
    parabola_focus: _common_pb2.Vector3d
    parabola_focus_y: float
    parabola_focus_z: float
    nurbs_order: int
    nurbs_control_points_by_components: Line.NurbsControlPointsByComponentsTable
    nurbs_control_points: Line.NurbsControlPointsTable
    nurbs_knots: Line.NurbsKnotsTable
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[Line.Type, str]] = ..., definition_points: _Optional[_Iterable[int]] = ..., length: _Optional[float] = ..., circle_point: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., comment: _Optional[str] = ..., arc_first_point: _Optional[int] = ..., arc_second_point: _Optional[int] = ..., arc_control_point: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., arc_control_point_y: _Optional[float] = ..., arc_control_point_z: _Optional[float] = ..., arc_center: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., arc_center_y: _Optional[float] = ..., arc_center_z: _Optional[float] = ..., arc_radius: _Optional[float] = ..., arc_height: _Optional[float] = ..., arc_alpha: _Optional[float] = ..., arc_alpha_adjustment_target: _Optional[_Union[Line.ArcAlphaAdjustmentTarget, str]] = ..., circle_center: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., circle_center_coordinate_y: _Optional[float] = ..., circle_center_coordinate_z: _Optional[float] = ..., circle_rotation: _Optional[float] = ..., circle_radius: _Optional[float] = ..., ellipse_first_point: _Optional[int] = ..., ellipse_second_point: _Optional[int] = ..., ellipse_control_point: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., ellipse_control_point_y: _Optional[float] = ..., ellipse_control_point_z: _Optional[float] = ..., parabola_first_point: _Optional[int] = ..., parabola_second_point: _Optional[int] = ..., parabola_control_point: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., parabola_control_point_y: _Optional[float] = ..., parabola_control_point_z: _Optional[float] = ..., parabola_focus_directrix_distance: _Optional[float] = ..., parabola_alpha: _Optional[float] = ..., parabola_focus: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., parabola_focus_y: _Optional[float] = ..., parabola_focus_z: _Optional[float] = ..., nurbs_order: _Optional[int] = ..., nurbs_control_points_by_components: _Optional[_Union[Line.NurbsControlPointsByComponentsTable, _Mapping]] = ..., nurbs_control_points: _Optional[_Union[Line.NurbsControlPointsTable, _Mapping]] = ..., nurbs_knots: _Optional[_Union[Line.NurbsKnotsTable, _Mapping]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
