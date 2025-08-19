from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResultPoint(_message.Message):
    __slots__ = ("assigned_to_solid", "assigned_to_surface", "comment", "coordinate_point", "coordinate_system", "coordinate_system_type", "generating_object_info", "global_coordinate_point", "global_point_coordinate_x", "global_point_coordinate_y", "global_point_coordinate_z", "is_generated", "name", "no", "point_coordinate_x", "point_coordinate_y", "point_coordinate_z", "result_point_type", "surface_probe_for_wind_analysis_active", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class CoordinateSystemType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COORDINATE_SYSTEM_TYPE_CARTESIAN: _ClassVar[ResultPoint.CoordinateSystemType]
        COORDINATE_SYSTEM_TYPE_POLAR: _ClassVar[ResultPoint.CoordinateSystemType]
        COORDINATE_SYSTEM_TYPE_X_CYLINDRICAL: _ClassVar[ResultPoint.CoordinateSystemType]
        COORDINATE_SYSTEM_TYPE_Y_CYLINDRICAL: _ClassVar[ResultPoint.CoordinateSystemType]
        COORDINATE_SYSTEM_TYPE_Z_CYLINDRICAL: _ClassVar[ResultPoint.CoordinateSystemType]
    COORDINATE_SYSTEM_TYPE_CARTESIAN: ResultPoint.CoordinateSystemType
    COORDINATE_SYSTEM_TYPE_POLAR: ResultPoint.CoordinateSystemType
    COORDINATE_SYSTEM_TYPE_X_CYLINDRICAL: ResultPoint.CoordinateSystemType
    COORDINATE_SYSTEM_TYPE_Y_CYLINDRICAL: ResultPoint.CoordinateSystemType
    COORDINATE_SYSTEM_TYPE_Z_CYLINDRICAL: ResultPoint.CoordinateSystemType
    class ResultPointType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        RESULT_POINT_TYPE_ON_SURFACE: _ClassVar[ResultPoint.ResultPointType]
        RESULT_POINT_TYPE_IN_SOLID: _ClassVar[ResultPoint.ResultPointType]
        RESULT_POINT_TYPE_SPATIAL: _ClassVar[ResultPoint.ResultPointType]
    RESULT_POINT_TYPE_ON_SURFACE: ResultPoint.ResultPointType
    RESULT_POINT_TYPE_IN_SOLID: ResultPoint.ResultPointType
    RESULT_POINT_TYPE_SPATIAL: ResultPoint.ResultPointType
    ASSIGNED_TO_SOLID_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_SURFACE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_POINT_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_TYPE_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_COORDINATE_POINT_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_POINT_COORDINATE_X_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_POINT_COORDINATE_Y_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_POINT_COORDINATE_Z_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    POINT_COORDINATE_X_FIELD_NUMBER: _ClassVar[int]
    POINT_COORDINATE_Y_FIELD_NUMBER: _ClassVar[int]
    POINT_COORDINATE_Z_FIELD_NUMBER: _ClassVar[int]
    RESULT_POINT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SURFACE_PROBE_FOR_WIND_ANALYSIS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    assigned_to_solid: int
    assigned_to_surface: int
    comment: str
    coordinate_point: _common_pb2.Vector3d
    coordinate_system: int
    coordinate_system_type: ResultPoint.CoordinateSystemType
    generating_object_info: str
    global_coordinate_point: _common_pb2.Vector3d
    global_point_coordinate_x: float
    global_point_coordinate_y: float
    global_point_coordinate_z: float
    is_generated: bool
    name: str
    no: int
    point_coordinate_x: float
    point_coordinate_y: float
    point_coordinate_z: float
    result_point_type: ResultPoint.ResultPointType
    surface_probe_for_wind_analysis_active: bool
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, assigned_to_solid: _Optional[int] = ..., assigned_to_surface: _Optional[int] = ..., comment: _Optional[str] = ..., coordinate_point: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., coordinate_system: _Optional[int] = ..., coordinate_system_type: _Optional[_Union[ResultPoint.CoordinateSystemType, str]] = ..., generating_object_info: _Optional[str] = ..., global_coordinate_point: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., global_point_coordinate_x: _Optional[float] = ..., global_point_coordinate_y: _Optional[float] = ..., global_point_coordinate_z: _Optional[float] = ..., is_generated: bool = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., point_coordinate_x: _Optional[float] = ..., point_coordinate_y: _Optional[float] = ..., point_coordinate_z: _Optional[float] = ..., result_point_type: _Optional[_Union[ResultPoint.ResultPointType, str]] = ..., surface_probe_for_wind_analysis_active: bool = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
