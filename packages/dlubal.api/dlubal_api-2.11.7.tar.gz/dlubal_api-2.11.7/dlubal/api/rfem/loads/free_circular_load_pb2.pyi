from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FreeCircularLoad(_message.Message):
    __slots__ = ("no", "surfaces", "load_case", "coordinate_system", "load_projection", "load_direction", "load_acting_region_from", "load_acting_region_to", "load_distribution", "magnitude_uniform", "magnitude_center", "magnitude_radius", "load_location_x", "load_location_y", "load_location_radius", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class LoadProjection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_PROJECTION_XY_OR_UV: _ClassVar[FreeCircularLoad.LoadProjection]
        LOAD_PROJECTION_XZ_OR_UW: _ClassVar[FreeCircularLoad.LoadProjection]
        LOAD_PROJECTION_YZ_OR_VW: _ClassVar[FreeCircularLoad.LoadProjection]
    LOAD_PROJECTION_XY_OR_UV: FreeCircularLoad.LoadProjection
    LOAD_PROJECTION_XZ_OR_UW: FreeCircularLoad.LoadProjection
    LOAD_PROJECTION_YZ_OR_VW: FreeCircularLoad.LoadProjection
    class LoadDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DIRECTION_LOCAL_X: _ClassVar[FreeCircularLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED_LENGTH: _ClassVar[FreeCircularLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: _ClassVar[FreeCircularLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_PROJECTED_LENGTH: _ClassVar[FreeCircularLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_TRUE_LENGTH: _ClassVar[FreeCircularLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_PROJECTED_LENGTH: _ClassVar[FreeCircularLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: _ClassVar[FreeCircularLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_PROJECTED_LENGTH: _ClassVar[FreeCircularLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_TRUE_LENGTH: _ClassVar[FreeCircularLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_PROJECTED_LENGTH: _ClassVar[FreeCircularLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: _ClassVar[FreeCircularLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_PROJECTED_LENGTH: _ClassVar[FreeCircularLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_TRUE_LENGTH: _ClassVar[FreeCircularLoad.LoadDirection]
        LOAD_DIRECTION_LOCAL_Y: _ClassVar[FreeCircularLoad.LoadDirection]
        LOAD_DIRECTION_LOCAL_Z: _ClassVar[FreeCircularLoad.LoadDirection]
    LOAD_DIRECTION_LOCAL_X: FreeCircularLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED_LENGTH: FreeCircularLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: FreeCircularLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_PROJECTED_LENGTH: FreeCircularLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_TRUE_LENGTH: FreeCircularLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_PROJECTED_LENGTH: FreeCircularLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: FreeCircularLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_PROJECTED_LENGTH: FreeCircularLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_TRUE_LENGTH: FreeCircularLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_PROJECTED_LENGTH: FreeCircularLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: FreeCircularLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_PROJECTED_LENGTH: FreeCircularLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_TRUE_LENGTH: FreeCircularLoad.LoadDirection
    LOAD_DIRECTION_LOCAL_Y: FreeCircularLoad.LoadDirection
    LOAD_DIRECTION_LOCAL_Z: FreeCircularLoad.LoadDirection
    class LoadDistribution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DISTRIBUTION_UNIFORM: _ClassVar[FreeCircularLoad.LoadDistribution]
        LOAD_DISTRIBUTION_LINEAR: _ClassVar[FreeCircularLoad.LoadDistribution]
    LOAD_DISTRIBUTION_UNIFORM: FreeCircularLoad.LoadDistribution
    LOAD_DISTRIBUTION_LINEAR: FreeCircularLoad.LoadDistribution
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
    MAGNITUDE_CENTER_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_RADIUS_FIELD_NUMBER: _ClassVar[int]
    LOAD_LOCATION_X_FIELD_NUMBER: _ClassVar[int]
    LOAD_LOCATION_Y_FIELD_NUMBER: _ClassVar[int]
    LOAD_LOCATION_RADIUS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    surfaces: _containers.RepeatedScalarFieldContainer[int]
    load_case: int
    coordinate_system: int
    load_projection: FreeCircularLoad.LoadProjection
    load_direction: FreeCircularLoad.LoadDirection
    load_acting_region_from: float
    load_acting_region_to: float
    load_distribution: FreeCircularLoad.LoadDistribution
    magnitude_uniform: float
    magnitude_center: float
    magnitude_radius: float
    load_location_x: float
    load_location_y: float
    load_location_radius: float
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., surfaces: _Optional[_Iterable[int]] = ..., load_case: _Optional[int] = ..., coordinate_system: _Optional[int] = ..., load_projection: _Optional[_Union[FreeCircularLoad.LoadProjection, str]] = ..., load_direction: _Optional[_Union[FreeCircularLoad.LoadDirection, str]] = ..., load_acting_region_from: _Optional[float] = ..., load_acting_region_to: _Optional[float] = ..., load_distribution: _Optional[_Union[FreeCircularLoad.LoadDistribution, str]] = ..., magnitude_uniform: _Optional[float] = ..., magnitude_center: _Optional[float] = ..., magnitude_radius: _Optional[float] = ..., load_location_x: _Optional[float] = ..., load_location_y: _Optional[float] = ..., load_location_radius: _Optional[float] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
