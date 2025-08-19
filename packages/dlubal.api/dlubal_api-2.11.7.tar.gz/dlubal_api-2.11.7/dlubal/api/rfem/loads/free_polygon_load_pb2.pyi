from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FreePolygonLoad(_message.Message):
    __slots__ = ("no", "surfaces", "load_case", "coordinate_system", "load_projection", "load_direction", "load_acting_region_from", "load_acting_region_to", "load_distribution", "magnitude_uniform", "magnitude_linear_1", "magnitude_linear_2", "magnitude_linear_3", "magnitude_linear_location_1", "magnitude_linear_location_2", "magnitude_linear_location_3", "load_location", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class LoadProjection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_PROJECTION_XY_OR_UV: _ClassVar[FreePolygonLoad.LoadProjection]
        LOAD_PROJECTION_XZ_OR_UW: _ClassVar[FreePolygonLoad.LoadProjection]
        LOAD_PROJECTION_YZ_OR_VW: _ClassVar[FreePolygonLoad.LoadProjection]
    LOAD_PROJECTION_XY_OR_UV: FreePolygonLoad.LoadProjection
    LOAD_PROJECTION_XZ_OR_UW: FreePolygonLoad.LoadProjection
    LOAD_PROJECTION_YZ_OR_VW: FreePolygonLoad.LoadProjection
    class LoadDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DIRECTION_LOCAL_X: _ClassVar[FreePolygonLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED_LENGTH: _ClassVar[FreePolygonLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: _ClassVar[FreePolygonLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_PROJECTED_LENGTH: _ClassVar[FreePolygonLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_TRUE_LENGTH: _ClassVar[FreePolygonLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_PROJECTED_LENGTH: _ClassVar[FreePolygonLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: _ClassVar[FreePolygonLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_PROJECTED_LENGTH: _ClassVar[FreePolygonLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_TRUE_LENGTH: _ClassVar[FreePolygonLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_PROJECTED_LENGTH: _ClassVar[FreePolygonLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: _ClassVar[FreePolygonLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_PROJECTED_LENGTH: _ClassVar[FreePolygonLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_TRUE_LENGTH: _ClassVar[FreePolygonLoad.LoadDirection]
        LOAD_DIRECTION_LOCAL_Y: _ClassVar[FreePolygonLoad.LoadDirection]
        LOAD_DIRECTION_LOCAL_Z: _ClassVar[FreePolygonLoad.LoadDirection]
    LOAD_DIRECTION_LOCAL_X: FreePolygonLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED_LENGTH: FreePolygonLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: FreePolygonLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_PROJECTED_LENGTH: FreePolygonLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_TRUE_LENGTH: FreePolygonLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_PROJECTED_LENGTH: FreePolygonLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: FreePolygonLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_PROJECTED_LENGTH: FreePolygonLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_TRUE_LENGTH: FreePolygonLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_PROJECTED_LENGTH: FreePolygonLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: FreePolygonLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_PROJECTED_LENGTH: FreePolygonLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_TRUE_LENGTH: FreePolygonLoad.LoadDirection
    LOAD_DIRECTION_LOCAL_Y: FreePolygonLoad.LoadDirection
    LOAD_DIRECTION_LOCAL_Z: FreePolygonLoad.LoadDirection
    class LoadDistribution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DISTRIBUTION_UNIFORM: _ClassVar[FreePolygonLoad.LoadDistribution]
        LOAD_DISTRIBUTION_LINEAR: _ClassVar[FreePolygonLoad.LoadDistribution]
        LOAD_DISTRIBUTION_LINEAR_FIRST: _ClassVar[FreePolygonLoad.LoadDistribution]
        LOAD_DISTRIBUTION_LINEAR_SECOND: _ClassVar[FreePolygonLoad.LoadDistribution]
    LOAD_DISTRIBUTION_UNIFORM: FreePolygonLoad.LoadDistribution
    LOAD_DISTRIBUTION_LINEAR: FreePolygonLoad.LoadDistribution
    LOAD_DISTRIBUTION_LINEAR_FIRST: FreePolygonLoad.LoadDistribution
    LOAD_DISTRIBUTION_LINEAR_SECOND: FreePolygonLoad.LoadDistribution
    class LoadLocationTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[FreePolygonLoad.LoadLocationRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[FreePolygonLoad.LoadLocationRow, _Mapping]]] = ...) -> None: ...
    class LoadLocationRow(_message.Message):
        __slots__ = ("no", "description", "first_coordinate", "second_coordinate", "magnitude")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FIRST_COORDINATE_FIELD_NUMBER: _ClassVar[int]
        SECOND_COORDINATE_FIELD_NUMBER: _ClassVar[int]
        MAGNITUDE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        first_coordinate: float
        second_coordinate: float
        magnitude: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., first_coordinate: _Optional[float] = ..., second_coordinate: _Optional[float] = ..., magnitude: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    SURFACES_FIELD_NUMBER: _ClassVar[int]
    LOAD_CASE_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    LOAD_PROJECTION_FIELD_NUMBER: _ClassVar[int]
    LOAD_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    LOAD_ACTING_REGION_FROM_FIELD_NUMBER: _ClassVar[int]
    LOAD_ACTING_REGION_TO_FIELD_NUMBER: _ClassVar[int]
    LOAD_DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_UNIFORM_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_LINEAR_1_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_LINEAR_2_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_LINEAR_3_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_LINEAR_LOCATION_1_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_LINEAR_LOCATION_2_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_LINEAR_LOCATION_3_FIELD_NUMBER: _ClassVar[int]
    LOAD_LOCATION_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    surfaces: _containers.RepeatedScalarFieldContainer[int]
    load_case: int
    coordinate_system: int
    load_projection: FreePolygonLoad.LoadProjection
    load_direction: FreePolygonLoad.LoadDirection
    load_acting_region_from: float
    load_acting_region_to: float
    load_distribution: FreePolygonLoad.LoadDistribution
    magnitude_uniform: float
    magnitude_linear_1: float
    magnitude_linear_2: float
    magnitude_linear_3: float
    magnitude_linear_location_1: int
    magnitude_linear_location_2: int
    magnitude_linear_location_3: int
    load_location: FreePolygonLoad.LoadLocationTable
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., surfaces: _Optional[_Iterable[int]] = ..., load_case: _Optional[int] = ..., coordinate_system: _Optional[int] = ..., load_projection: _Optional[_Union[FreePolygonLoad.LoadProjection, str]] = ..., load_direction: _Optional[_Union[FreePolygonLoad.LoadDirection, str]] = ..., load_acting_region_from: _Optional[float] = ..., load_acting_region_to: _Optional[float] = ..., load_distribution: _Optional[_Union[FreePolygonLoad.LoadDistribution, str]] = ..., magnitude_uniform: _Optional[float] = ..., magnitude_linear_1: _Optional[float] = ..., magnitude_linear_2: _Optional[float] = ..., magnitude_linear_3: _Optional[float] = ..., magnitude_linear_location_1: _Optional[int] = ..., magnitude_linear_location_2: _Optional[int] = ..., magnitude_linear_location_3: _Optional[int] = ..., load_location: _Optional[_Union[FreePolygonLoad.LoadLocationTable, _Mapping]] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
