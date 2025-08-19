from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SurfaceResultsAdjustment(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "surfaces", "shape", "dimension_1", "dimension_2", "angular_rotation", "center_position", "center_position_x", "center_position_y", "center_position_z", "polygon_points", "adjustment_type_in_direction_u", "adjustment_type_in_direction_v", "results_to_adjust_contact_stress_area", "projection_in_direction_type", "vector_of_projection_in_direction_coordinates", "vector_of_projection_in_direction_coordinates_x", "vector_of_projection_in_direction_coordinates_y", "vector_of_projection_in_direction_coordinates_z", "comment", "results_to_adjust_in_direction_u", "results_to_adjust_in_direction_v", "results_to_adjust_zero", "id_for_export_import", "metadata_for_export_import")
    class Shape(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SHAPE_RECTANGLE: _ClassVar[SurfaceResultsAdjustment.Shape]
        SHAPE_CIRCLE: _ClassVar[SurfaceResultsAdjustment.Shape]
        SHAPE_ELLIPSE: _ClassVar[SurfaceResultsAdjustment.Shape]
        SHAPE_POLYGON: _ClassVar[SurfaceResultsAdjustment.Shape]
    SHAPE_RECTANGLE: SurfaceResultsAdjustment.Shape
    SHAPE_CIRCLE: SurfaceResultsAdjustment.Shape
    SHAPE_ELLIPSE: SurfaceResultsAdjustment.Shape
    SHAPE_POLYGON: SurfaceResultsAdjustment.Shape
    class AdjustmentTypeInDirectionU(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ADJUSTMENT_TYPE_IN_DIRECTION_U_AVERAGING_OF_MY_MXY_VY_NY_NXY: _ClassVar[SurfaceResultsAdjustment.AdjustmentTypeInDirectionU]
        ADJUSTMENT_TYPE_IN_DIRECTION_U_AVERAGING_OF_MX_MXY_VX_NX_NXY: _ClassVar[SurfaceResultsAdjustment.AdjustmentTypeInDirectionU]
        ADJUSTMENT_TYPE_IN_DIRECTION_U_CONTACT_STRESS_AREA: _ClassVar[SurfaceResultsAdjustment.AdjustmentTypeInDirectionU]
        ADJUSTMENT_TYPE_IN_DIRECTION_U_NONE: _ClassVar[SurfaceResultsAdjustment.AdjustmentTypeInDirectionU]
        ADJUSTMENT_TYPE_IN_DIRECTION_U_USER_DEFINED: _ClassVar[SurfaceResultsAdjustment.AdjustmentTypeInDirectionU]
        ADJUSTMENT_TYPE_IN_DIRECTION_U_ZERO: _ClassVar[SurfaceResultsAdjustment.AdjustmentTypeInDirectionU]
    ADJUSTMENT_TYPE_IN_DIRECTION_U_AVERAGING_OF_MY_MXY_VY_NY_NXY: SurfaceResultsAdjustment.AdjustmentTypeInDirectionU
    ADJUSTMENT_TYPE_IN_DIRECTION_U_AVERAGING_OF_MX_MXY_VX_NX_NXY: SurfaceResultsAdjustment.AdjustmentTypeInDirectionU
    ADJUSTMENT_TYPE_IN_DIRECTION_U_CONTACT_STRESS_AREA: SurfaceResultsAdjustment.AdjustmentTypeInDirectionU
    ADJUSTMENT_TYPE_IN_DIRECTION_U_NONE: SurfaceResultsAdjustment.AdjustmentTypeInDirectionU
    ADJUSTMENT_TYPE_IN_DIRECTION_U_USER_DEFINED: SurfaceResultsAdjustment.AdjustmentTypeInDirectionU
    ADJUSTMENT_TYPE_IN_DIRECTION_U_ZERO: SurfaceResultsAdjustment.AdjustmentTypeInDirectionU
    class AdjustmentTypeInDirectionV(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ADJUSTMENT_TYPE_IN_DIRECTION_V_AVERAGING_OF_MY_MXY_VY_NY_NXY: _ClassVar[SurfaceResultsAdjustment.AdjustmentTypeInDirectionV]
        ADJUSTMENT_TYPE_IN_DIRECTION_V_AVERAGING_OF_MX_MXY_VX_NX_NXY: _ClassVar[SurfaceResultsAdjustment.AdjustmentTypeInDirectionV]
        ADJUSTMENT_TYPE_IN_DIRECTION_V_CONTACT_STRESS_AREA: _ClassVar[SurfaceResultsAdjustment.AdjustmentTypeInDirectionV]
        ADJUSTMENT_TYPE_IN_DIRECTION_V_NONE: _ClassVar[SurfaceResultsAdjustment.AdjustmentTypeInDirectionV]
        ADJUSTMENT_TYPE_IN_DIRECTION_V_USER_DEFINED: _ClassVar[SurfaceResultsAdjustment.AdjustmentTypeInDirectionV]
        ADJUSTMENT_TYPE_IN_DIRECTION_V_ZERO: _ClassVar[SurfaceResultsAdjustment.AdjustmentTypeInDirectionV]
    ADJUSTMENT_TYPE_IN_DIRECTION_V_AVERAGING_OF_MY_MXY_VY_NY_NXY: SurfaceResultsAdjustment.AdjustmentTypeInDirectionV
    ADJUSTMENT_TYPE_IN_DIRECTION_V_AVERAGING_OF_MX_MXY_VX_NX_NXY: SurfaceResultsAdjustment.AdjustmentTypeInDirectionV
    ADJUSTMENT_TYPE_IN_DIRECTION_V_CONTACT_STRESS_AREA: SurfaceResultsAdjustment.AdjustmentTypeInDirectionV
    ADJUSTMENT_TYPE_IN_DIRECTION_V_NONE: SurfaceResultsAdjustment.AdjustmentTypeInDirectionV
    ADJUSTMENT_TYPE_IN_DIRECTION_V_USER_DEFINED: SurfaceResultsAdjustment.AdjustmentTypeInDirectionV
    ADJUSTMENT_TYPE_IN_DIRECTION_V_ZERO: SurfaceResultsAdjustment.AdjustmentTypeInDirectionV
    class ProjectionInDirectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PROJECTION_IN_DIRECTION_TYPE_PERPENDICULAR: _ClassVar[SurfaceResultsAdjustment.ProjectionInDirectionType]
        PROJECTION_IN_DIRECTION_TYPE_GLOBAL_IN_X: _ClassVar[SurfaceResultsAdjustment.ProjectionInDirectionType]
        PROJECTION_IN_DIRECTION_TYPE_GLOBAL_IN_Y: _ClassVar[SurfaceResultsAdjustment.ProjectionInDirectionType]
        PROJECTION_IN_DIRECTION_TYPE_GLOBAL_IN_Z: _ClassVar[SurfaceResultsAdjustment.ProjectionInDirectionType]
        PROJECTION_IN_DIRECTION_TYPE_VECTOR: _ClassVar[SurfaceResultsAdjustment.ProjectionInDirectionType]
    PROJECTION_IN_DIRECTION_TYPE_PERPENDICULAR: SurfaceResultsAdjustment.ProjectionInDirectionType
    PROJECTION_IN_DIRECTION_TYPE_GLOBAL_IN_X: SurfaceResultsAdjustment.ProjectionInDirectionType
    PROJECTION_IN_DIRECTION_TYPE_GLOBAL_IN_Y: SurfaceResultsAdjustment.ProjectionInDirectionType
    PROJECTION_IN_DIRECTION_TYPE_GLOBAL_IN_Z: SurfaceResultsAdjustment.ProjectionInDirectionType
    PROJECTION_IN_DIRECTION_TYPE_VECTOR: SurfaceResultsAdjustment.ProjectionInDirectionType
    class PolygonPointsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[SurfaceResultsAdjustment.PolygonPointsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[SurfaceResultsAdjustment.PolygonPointsRow, _Mapping]]] = ...) -> None: ...
    class PolygonPointsRow(_message.Message):
        __slots__ = ("no", "description", "x", "y", "z")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        X_FIELD_NUMBER: _ClassVar[int]
        Y_FIELD_NUMBER: _ClassVar[int]
        Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        x: float
        y: float
        z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...
    class ResultsToAdjustContactStressAreaTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[SurfaceResultsAdjustment.ResultsToAdjustContactStressAreaRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[SurfaceResultsAdjustment.ResultsToAdjustContactStressAreaRow, _Mapping]]] = ...) -> None: ...
    class ResultsToAdjustContactStressAreaRow(_message.Message):
        __slots__ = ("no", "description", "contact_stress_type", "lower_limit", "upper_limit")
        class ContactStressType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            CONTACT_STRESS_TYPE_UNKNOWN: _ClassVar[SurfaceResultsAdjustment.ResultsToAdjustContactStressAreaRow.ContactStressType]
        CONTACT_STRESS_TYPE_UNKNOWN: SurfaceResultsAdjustment.ResultsToAdjustContactStressAreaRow.ContactStressType
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        CONTACT_STRESS_TYPE_FIELD_NUMBER: _ClassVar[int]
        LOWER_LIMIT_FIELD_NUMBER: _ClassVar[int]
        UPPER_LIMIT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        contact_stress_type: SurfaceResultsAdjustment.ResultsToAdjustContactStressAreaRow.ContactStressType
        lower_limit: float
        upper_limit: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., contact_stress_type: _Optional[_Union[SurfaceResultsAdjustment.ResultsToAdjustContactStressAreaRow.ContactStressType, str]] = ..., lower_limit: _Optional[float] = ..., upper_limit: _Optional[float] = ...) -> None: ...
    class ResultsToAdjustInDirectionUTable(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class ResultsToAdjustInDirectionVTable(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class ResultsToAdjustZeroTable(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SURFACES_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    DIMENSION_1_FIELD_NUMBER: _ClassVar[int]
    DIMENSION_2_FIELD_NUMBER: _ClassVar[int]
    ANGULAR_ROTATION_FIELD_NUMBER: _ClassVar[int]
    CENTER_POSITION_FIELD_NUMBER: _ClassVar[int]
    CENTER_POSITION_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_POSITION_Z_FIELD_NUMBER: _ClassVar[int]
    POLYGON_POINTS_FIELD_NUMBER: _ClassVar[int]
    ADJUSTMENT_TYPE_IN_DIRECTION_U_FIELD_NUMBER: _ClassVar[int]
    ADJUSTMENT_TYPE_IN_DIRECTION_V_FIELD_NUMBER: _ClassVar[int]
    RESULTS_TO_ADJUST_CONTACT_STRESS_AREA_FIELD_NUMBER: _ClassVar[int]
    PROJECTION_IN_DIRECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    VECTOR_OF_PROJECTION_IN_DIRECTION_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    VECTOR_OF_PROJECTION_IN_DIRECTION_COORDINATES_X_FIELD_NUMBER: _ClassVar[int]
    VECTOR_OF_PROJECTION_IN_DIRECTION_COORDINATES_Y_FIELD_NUMBER: _ClassVar[int]
    VECTOR_OF_PROJECTION_IN_DIRECTION_COORDINATES_Z_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    RESULTS_TO_ADJUST_IN_DIRECTION_U_FIELD_NUMBER: _ClassVar[int]
    RESULTS_TO_ADJUST_IN_DIRECTION_V_FIELD_NUMBER: _ClassVar[int]
    RESULTS_TO_ADJUST_ZERO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    surfaces: _containers.RepeatedScalarFieldContainer[int]
    shape: SurfaceResultsAdjustment.Shape
    dimension_1: float
    dimension_2: float
    angular_rotation: float
    center_position: _common_pb2.Vector3d
    center_position_x: float
    center_position_y: float
    center_position_z: float
    polygon_points: SurfaceResultsAdjustment.PolygonPointsTable
    adjustment_type_in_direction_u: SurfaceResultsAdjustment.AdjustmentTypeInDirectionU
    adjustment_type_in_direction_v: SurfaceResultsAdjustment.AdjustmentTypeInDirectionV
    results_to_adjust_contact_stress_area: SurfaceResultsAdjustment.ResultsToAdjustContactStressAreaTable
    projection_in_direction_type: SurfaceResultsAdjustment.ProjectionInDirectionType
    vector_of_projection_in_direction_coordinates: _common_pb2.Vector3d
    vector_of_projection_in_direction_coordinates_x: float
    vector_of_projection_in_direction_coordinates_y: float
    vector_of_projection_in_direction_coordinates_z: float
    comment: str
    results_to_adjust_in_direction_u: SurfaceResultsAdjustment.ResultsToAdjustInDirectionUTable
    results_to_adjust_in_direction_v: SurfaceResultsAdjustment.ResultsToAdjustInDirectionVTable
    results_to_adjust_zero: SurfaceResultsAdjustment.ResultsToAdjustZeroTable
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., surfaces: _Optional[_Iterable[int]] = ..., shape: _Optional[_Union[SurfaceResultsAdjustment.Shape, str]] = ..., dimension_1: _Optional[float] = ..., dimension_2: _Optional[float] = ..., angular_rotation: _Optional[float] = ..., center_position: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_position_x: _Optional[float] = ..., center_position_y: _Optional[float] = ..., center_position_z: _Optional[float] = ..., polygon_points: _Optional[_Union[SurfaceResultsAdjustment.PolygonPointsTable, _Mapping]] = ..., adjustment_type_in_direction_u: _Optional[_Union[SurfaceResultsAdjustment.AdjustmentTypeInDirectionU, str]] = ..., adjustment_type_in_direction_v: _Optional[_Union[SurfaceResultsAdjustment.AdjustmentTypeInDirectionV, str]] = ..., results_to_adjust_contact_stress_area: _Optional[_Union[SurfaceResultsAdjustment.ResultsToAdjustContactStressAreaTable, _Mapping]] = ..., projection_in_direction_type: _Optional[_Union[SurfaceResultsAdjustment.ProjectionInDirectionType, str]] = ..., vector_of_projection_in_direction_coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., vector_of_projection_in_direction_coordinates_x: _Optional[float] = ..., vector_of_projection_in_direction_coordinates_y: _Optional[float] = ..., vector_of_projection_in_direction_coordinates_z: _Optional[float] = ..., comment: _Optional[str] = ..., results_to_adjust_in_direction_u: _Optional[_Union[SurfaceResultsAdjustment.ResultsToAdjustInDirectionUTable, _Mapping]] = ..., results_to_adjust_in_direction_v: _Optional[_Union[SurfaceResultsAdjustment.ResultsToAdjustInDirectionVTable, _Mapping]] = ..., results_to_adjust_zero: _Optional[_Union[SurfaceResultsAdjustment.ResultsToAdjustZeroTable, _Mapping]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
