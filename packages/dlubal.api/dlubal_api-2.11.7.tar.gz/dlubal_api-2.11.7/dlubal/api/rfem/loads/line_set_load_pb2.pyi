from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LineSetLoad(_message.Message):
    __slots__ = ("no", "load_type", "line_sets", "load_case", "coordinate_system", "load_distribution", "load_direction", "load_direction_orientation", "magnitude", "magnitude_1", "magnitude_2", "magnitude_3", "mass_global", "mass_x", "mass_y", "mass_z", "count_n", "varying_load_parameters_are_defined_as_relative", "varying_load_parameters", "varying_load_parameters_sorted", "distance_a_is_defined_as_relative", "distance_a_absolute", "distance_a_relative", "distance_b_is_defined_as_relative", "distance_b_absolute", "distance_b_relative", "distance_c_is_defined_as_relative", "distance_c_absolute", "distance_c_relative", "reference_to_list_of_line_sets", "distance_from_line_set_end", "load_is_over_total_length", "individual_mass_components", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class LoadType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_TYPE_UNKNOWN: _ClassVar[LineSetLoad.LoadType]
        LOAD_TYPE_FORCE: _ClassVar[LineSetLoad.LoadType]
        LOAD_TYPE_MASS: _ClassVar[LineSetLoad.LoadType]
        LOAD_TYPE_MOMENT: _ClassVar[LineSetLoad.LoadType]
    LOAD_TYPE_UNKNOWN: LineSetLoad.LoadType
    LOAD_TYPE_FORCE: LineSetLoad.LoadType
    LOAD_TYPE_MASS: LineSetLoad.LoadType
    LOAD_TYPE_MOMENT: LineSetLoad.LoadType
    class LoadDistribution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DISTRIBUTION_UNIFORM: _ClassVar[LineSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_CONCENTRATED_1: _ClassVar[LineSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_CONCENTRATED_2: _ClassVar[LineSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_CONCENTRATED_2_2: _ClassVar[LineSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_CONCENTRATED_N: _ClassVar[LineSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_CONCENTRATED_VARYING: _ClassVar[LineSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_PARABOLIC: _ClassVar[LineSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_TAPERED: _ClassVar[LineSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_TRAPEZOIDAL: _ClassVar[LineSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_UNIFORM_TOTAL: _ClassVar[LineSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_VARYING: _ClassVar[LineSetLoad.LoadDistribution]
    LOAD_DISTRIBUTION_UNIFORM: LineSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_CONCENTRATED_1: LineSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_CONCENTRATED_2: LineSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_CONCENTRATED_2_2: LineSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_CONCENTRATED_N: LineSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_CONCENTRATED_VARYING: LineSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_PARABOLIC: LineSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_TAPERED: LineSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_TRAPEZOIDAL: LineSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_UNIFORM_TOTAL: LineSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_VARYING: LineSetLoad.LoadDistribution
    class LoadDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DIRECTION_LOCAL_X: _ClassVar[LineSetLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED_LENGTH: _ClassVar[LineSetLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: _ClassVar[LineSetLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_PROJECTED_LENGTH: _ClassVar[LineSetLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: _ClassVar[LineSetLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_PROJECTED_LENGTH: _ClassVar[LineSetLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: _ClassVar[LineSetLoad.LoadDirection]
        LOAD_DIRECTION_LOCAL_Y: _ClassVar[LineSetLoad.LoadDirection]
        LOAD_DIRECTION_LOCAL_Z: _ClassVar[LineSetLoad.LoadDirection]
    LOAD_DIRECTION_LOCAL_X: LineSetLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED_LENGTH: LineSetLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: LineSetLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_PROJECTED_LENGTH: LineSetLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: LineSetLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_PROJECTED_LENGTH: LineSetLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: LineSetLoad.LoadDirection
    LOAD_DIRECTION_LOCAL_Y: LineSetLoad.LoadDirection
    LOAD_DIRECTION_LOCAL_Z: LineSetLoad.LoadDirection
    class LoadDirectionOrientation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DIRECTION_ORIENTATION_LOAD_DIRECTION_FORWARD: _ClassVar[LineSetLoad.LoadDirectionOrientation]
        LOAD_DIRECTION_ORIENTATION_LOAD_DIRECTION_REVERSED: _ClassVar[LineSetLoad.LoadDirectionOrientation]
    LOAD_DIRECTION_ORIENTATION_LOAD_DIRECTION_FORWARD: LineSetLoad.LoadDirectionOrientation
    LOAD_DIRECTION_ORIENTATION_LOAD_DIRECTION_REVERSED: LineSetLoad.LoadDirectionOrientation
    class VaryingLoadParametersTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[LineSetLoad.VaryingLoadParametersRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineSetLoad.VaryingLoadParametersRow, _Mapping]]] = ...) -> None: ...
    class VaryingLoadParametersRow(_message.Message):
        __slots__ = ("no", "description", "distance", "delta_distance", "magnitude", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        DISTANCE_FIELD_NUMBER: _ClassVar[int]
        DELTA_DISTANCE_FIELD_NUMBER: _ClassVar[int]
        MAGNITUDE_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        distance: float
        delta_distance: float
        magnitude: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., distance: _Optional[float] = ..., delta_distance: _Optional[float] = ..., magnitude: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    LOAD_TYPE_FIELD_NUMBER: _ClassVar[int]
    LINE_SETS_FIELD_NUMBER: _ClassVar[int]
    LOAD_CASE_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    LOAD_DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    LOAD_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    LOAD_DIRECTION_ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_1_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_2_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_3_FIELD_NUMBER: _ClassVar[int]
    MASS_GLOBAL_FIELD_NUMBER: _ClassVar[int]
    MASS_X_FIELD_NUMBER: _ClassVar[int]
    MASS_Y_FIELD_NUMBER: _ClassVar[int]
    MASS_Z_FIELD_NUMBER: _ClassVar[int]
    COUNT_N_FIELD_NUMBER: _ClassVar[int]
    VARYING_LOAD_PARAMETERS_ARE_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    VARYING_LOAD_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    VARYING_LOAD_PARAMETERS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_A_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_A_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_A_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_B_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_B_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_B_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_C_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_C_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_C_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_TO_LIST_OF_LINE_SETS_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_LINE_SET_END_FIELD_NUMBER: _ClassVar[int]
    LOAD_IS_OVER_TOTAL_LENGTH_FIELD_NUMBER: _ClassVar[int]
    INDIVIDUAL_MASS_COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    load_type: LineSetLoad.LoadType
    line_sets: _containers.RepeatedScalarFieldContainer[int]
    load_case: int
    coordinate_system: _common_pb2.CoordinateSystemRepresentation
    load_distribution: LineSetLoad.LoadDistribution
    load_direction: LineSetLoad.LoadDirection
    load_direction_orientation: LineSetLoad.LoadDirectionOrientation
    magnitude: float
    magnitude_1: float
    magnitude_2: float
    magnitude_3: float
    mass_global: float
    mass_x: float
    mass_y: float
    mass_z: float
    count_n: int
    varying_load_parameters_are_defined_as_relative: bool
    varying_load_parameters: LineSetLoad.VaryingLoadParametersTable
    varying_load_parameters_sorted: bool
    distance_a_is_defined_as_relative: bool
    distance_a_absolute: float
    distance_a_relative: float
    distance_b_is_defined_as_relative: bool
    distance_b_absolute: float
    distance_b_relative: float
    distance_c_is_defined_as_relative: bool
    distance_c_absolute: float
    distance_c_relative: float
    reference_to_list_of_line_sets: bool
    distance_from_line_set_end: bool
    load_is_over_total_length: bool
    individual_mass_components: bool
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., load_type: _Optional[_Union[LineSetLoad.LoadType, str]] = ..., line_sets: _Optional[_Iterable[int]] = ..., load_case: _Optional[int] = ..., coordinate_system: _Optional[_Union[_common_pb2.CoordinateSystemRepresentation, _Mapping]] = ..., load_distribution: _Optional[_Union[LineSetLoad.LoadDistribution, str]] = ..., load_direction: _Optional[_Union[LineSetLoad.LoadDirection, str]] = ..., load_direction_orientation: _Optional[_Union[LineSetLoad.LoadDirectionOrientation, str]] = ..., magnitude: _Optional[float] = ..., magnitude_1: _Optional[float] = ..., magnitude_2: _Optional[float] = ..., magnitude_3: _Optional[float] = ..., mass_global: _Optional[float] = ..., mass_x: _Optional[float] = ..., mass_y: _Optional[float] = ..., mass_z: _Optional[float] = ..., count_n: _Optional[int] = ..., varying_load_parameters_are_defined_as_relative: bool = ..., varying_load_parameters: _Optional[_Union[LineSetLoad.VaryingLoadParametersTable, _Mapping]] = ..., varying_load_parameters_sorted: bool = ..., distance_a_is_defined_as_relative: bool = ..., distance_a_absolute: _Optional[float] = ..., distance_a_relative: _Optional[float] = ..., distance_b_is_defined_as_relative: bool = ..., distance_b_absolute: _Optional[float] = ..., distance_b_relative: _Optional[float] = ..., distance_c_is_defined_as_relative: bool = ..., distance_c_absolute: _Optional[float] = ..., distance_c_relative: _Optional[float] = ..., reference_to_list_of_line_sets: bool = ..., distance_from_line_set_end: bool = ..., load_is_over_total_length: bool = ..., individual_mass_components: bool = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
