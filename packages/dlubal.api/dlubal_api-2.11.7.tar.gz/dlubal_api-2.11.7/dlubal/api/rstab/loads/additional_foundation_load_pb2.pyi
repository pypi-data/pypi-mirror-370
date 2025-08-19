from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AdditionalFoundationLoad(_message.Message):
    __slots__ = ("comment", "end_point_x", "end_point_y", "force", "force_x", "force_y", "force_z", "generating_object_info", "is_generated", "load_case", "load_distribution", "load_magnitude", "load_type", "no", "ordinate_x", "ordinate_y", "single_foundations", "start_point_x", "start_point_y", "id_for_export_import", "metadata_for_export_import")
    class LoadDistribution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DISTRIBUTION_UNIFORM: _ClassVar[AdditionalFoundationLoad.LoadDistribution]
        LOAD_DISTRIBUTION_LINEAR: _ClassVar[AdditionalFoundationLoad.LoadDistribution]
        LOAD_DISTRIBUTION_LINEAR_IN_X: _ClassVar[AdditionalFoundationLoad.LoadDistribution]
        LOAD_DISTRIBUTION_LINEAR_IN_Y: _ClassVar[AdditionalFoundationLoad.LoadDistribution]
        LOAD_DISTRIBUTION_UNIFORM_TOTAL: _ClassVar[AdditionalFoundationLoad.LoadDistribution]
    LOAD_DISTRIBUTION_UNIFORM: AdditionalFoundationLoad.LoadDistribution
    LOAD_DISTRIBUTION_LINEAR: AdditionalFoundationLoad.LoadDistribution
    LOAD_DISTRIBUTION_LINEAR_IN_X: AdditionalFoundationLoad.LoadDistribution
    LOAD_DISTRIBUTION_LINEAR_IN_Y: AdditionalFoundationLoad.LoadDistribution
    LOAD_DISTRIBUTION_UNIFORM_TOTAL: AdditionalFoundationLoad.LoadDistribution
    class LoadType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_TYPE_UNKNOWN: _ClassVar[AdditionalFoundationLoad.LoadType]
        LOAD_TYPE_CONCENTRATED_LOAD: _ClassVar[AdditionalFoundationLoad.LoadType]
        LOAD_TYPE_EARTH_COVERING: _ClassVar[AdditionalFoundationLoad.LoadType]
        LOAD_TYPE_GROUND_WATER: _ClassVar[AdditionalFoundationLoad.LoadType]
        LOAD_TYPE_LINE_LOAD: _ClassVar[AdditionalFoundationLoad.LoadType]
        LOAD_TYPE_SURFACE_LOAD: _ClassVar[AdditionalFoundationLoad.LoadType]
    LOAD_TYPE_UNKNOWN: AdditionalFoundationLoad.LoadType
    LOAD_TYPE_CONCENTRATED_LOAD: AdditionalFoundationLoad.LoadType
    LOAD_TYPE_EARTH_COVERING: AdditionalFoundationLoad.LoadType
    LOAD_TYPE_GROUND_WATER: AdditionalFoundationLoad.LoadType
    LOAD_TYPE_LINE_LOAD: AdditionalFoundationLoad.LoadType
    LOAD_TYPE_SURFACE_LOAD: AdditionalFoundationLoad.LoadType
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    END_POINT_X_FIELD_NUMBER: _ClassVar[int]
    END_POINT_Y_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    FORCE_X_FIELD_NUMBER: _ClassVar[int]
    FORCE_Y_FIELD_NUMBER: _ClassVar[int]
    FORCE_Z_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    LOAD_CASE_FIELD_NUMBER: _ClassVar[int]
    LOAD_DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    LOAD_MAGNITUDE_FIELD_NUMBER: _ClassVar[int]
    LOAD_TYPE_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    ORDINATE_X_FIELD_NUMBER: _ClassVar[int]
    ORDINATE_Y_FIELD_NUMBER: _ClassVar[int]
    SINGLE_FOUNDATIONS_FIELD_NUMBER: _ClassVar[int]
    START_POINT_X_FIELD_NUMBER: _ClassVar[int]
    START_POINT_Y_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    comment: str
    end_point_x: float
    end_point_y: float
    force: _common_pb2.Vector3d
    force_x: float
    force_y: float
    force_z: float
    generating_object_info: str
    is_generated: bool
    load_case: int
    load_distribution: AdditionalFoundationLoad.LoadDistribution
    load_magnitude: float
    load_type: AdditionalFoundationLoad.LoadType
    no: int
    ordinate_x: float
    ordinate_y: float
    single_foundations: _containers.RepeatedScalarFieldContainer[int]
    start_point_x: float
    start_point_y: float
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, comment: _Optional[str] = ..., end_point_x: _Optional[float] = ..., end_point_y: _Optional[float] = ..., force: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., force_x: _Optional[float] = ..., force_y: _Optional[float] = ..., force_z: _Optional[float] = ..., generating_object_info: _Optional[str] = ..., is_generated: bool = ..., load_case: _Optional[int] = ..., load_distribution: _Optional[_Union[AdditionalFoundationLoad.LoadDistribution, str]] = ..., load_magnitude: _Optional[float] = ..., load_type: _Optional[_Union[AdditionalFoundationLoad.LoadType, str]] = ..., no: _Optional[int] = ..., ordinate_x: _Optional[float] = ..., ordinate_y: _Optional[float] = ..., single_foundations: _Optional[_Iterable[int]] = ..., start_point_x: _Optional[float] = ..., start_point_y: _Optional[float] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
