from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Bar(_message.Message):
    __slots__ = ("no", "definition_type", "material", "start_point", "end_point", "distance_between_i_and_j", "distance_between_i_and_j_type", "distribution", "diameter", "area", "weight", "info_number_of_bars", "info_distance_of_bars", "reinforcement_layer", "offset", "offset_y", "offset_z", "multi_uniform_bar_count", "multi_variable_bar_count", "distance_of_bars", "axial_distance_si", "axial_distance_sj", "axial_distance_sn", "distance_from_start_is_defined_as_relative", "distance_from_start_relative", "distance_from_start_absolute", "distance_from_end_relative", "distance_from_end_absolute", "comment", "generating_object_info", "is_generated", "id_for_export_import", "metadata_for_export_import")
    class DefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFINITION_TYPE_UNKNOWN: _ClassVar[Bar.DefinitionType]
        DEFINITION_TYPE_MULTI_UNIFORM: _ClassVar[Bar.DefinitionType]
        DEFINITION_TYPE_MULTI_VARIABLE: _ClassVar[Bar.DefinitionType]
        DEFINITION_TYPE_SINGLE_BETWEEN_TWO_POINTS: _ClassVar[Bar.DefinitionType]
        DEFINITION_TYPE_SINGLE_POINT: _ClassVar[Bar.DefinitionType]
    DEFINITION_TYPE_UNKNOWN: Bar.DefinitionType
    DEFINITION_TYPE_MULTI_UNIFORM: Bar.DefinitionType
    DEFINITION_TYPE_MULTI_VARIABLE: Bar.DefinitionType
    DEFINITION_TYPE_SINGLE_BETWEEN_TWO_POINTS: Bar.DefinitionType
    DEFINITION_TYPE_SINGLE_POINT: Bar.DefinitionType
    class DistanceBetweenIAndJType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DISTANCE_BETWEEN_I_AND_J_TYPE_L: _ClassVar[Bar.DistanceBetweenIAndJType]
        DISTANCE_BETWEEN_I_AND_J_TYPE_XZ: _ClassVar[Bar.DistanceBetweenIAndJType]
        DISTANCE_BETWEEN_I_AND_J_TYPE_YZ: _ClassVar[Bar.DistanceBetweenIAndJType]
    DISTANCE_BETWEEN_I_AND_J_TYPE_L: Bar.DistanceBetweenIAndJType
    DISTANCE_BETWEEN_I_AND_J_TYPE_XZ: Bar.DistanceBetweenIAndJType
    DISTANCE_BETWEEN_I_AND_J_TYPE_YZ: Bar.DistanceBetweenIAndJType
    NO_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_FIELD_NUMBER: _ClassVar[int]
    START_POINT_FIELD_NUMBER: _ClassVar[int]
    END_POINT_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_BETWEEN_I_AND_J_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_BETWEEN_I_AND_J_TYPE_FIELD_NUMBER: _ClassVar[int]
    DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    DIAMETER_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    INFO_NUMBER_OF_BARS_FIELD_NUMBER: _ClassVar[int]
    INFO_DISTANCE_OF_BARS_FIELD_NUMBER: _ClassVar[int]
    REINFORCEMENT_LAYER_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    OFFSET_Y_FIELD_NUMBER: _ClassVar[int]
    OFFSET_Z_FIELD_NUMBER: _ClassVar[int]
    MULTI_UNIFORM_BAR_COUNT_FIELD_NUMBER: _ClassVar[int]
    MULTI_VARIABLE_BAR_COUNT_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_OF_BARS_FIELD_NUMBER: _ClassVar[int]
    AXIAL_DISTANCE_SI_FIELD_NUMBER: _ClassVar[int]
    AXIAL_DISTANCE_SJ_FIELD_NUMBER: _ClassVar[int]
    AXIAL_DISTANCE_SN_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_START_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_START_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_START_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_END_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_END_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    definition_type: Bar.DefinitionType
    material: int
    start_point: int
    end_point: int
    distance_between_i_and_j: float
    distance_between_i_and_j_type: Bar.DistanceBetweenIAndJType
    distribution: str
    diameter: float
    area: float
    weight: float
    info_number_of_bars: int
    info_distance_of_bars: float
    reinforcement_layer: int
    offset: float
    offset_y: float
    offset_z: float
    multi_uniform_bar_count: int
    multi_variable_bar_count: int
    distance_of_bars: float
    axial_distance_si: float
    axial_distance_sj: float
    axial_distance_sn: float
    distance_from_start_is_defined_as_relative: bool
    distance_from_start_relative: float
    distance_from_start_absolute: float
    distance_from_end_relative: float
    distance_from_end_absolute: float
    comment: str
    generating_object_info: str
    is_generated: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., definition_type: _Optional[_Union[Bar.DefinitionType, str]] = ..., material: _Optional[int] = ..., start_point: _Optional[int] = ..., end_point: _Optional[int] = ..., distance_between_i_and_j: _Optional[float] = ..., distance_between_i_and_j_type: _Optional[_Union[Bar.DistanceBetweenIAndJType, str]] = ..., distribution: _Optional[str] = ..., diameter: _Optional[float] = ..., area: _Optional[float] = ..., weight: _Optional[float] = ..., info_number_of_bars: _Optional[int] = ..., info_distance_of_bars: _Optional[float] = ..., reinforcement_layer: _Optional[int] = ..., offset: _Optional[float] = ..., offset_y: _Optional[float] = ..., offset_z: _Optional[float] = ..., multi_uniform_bar_count: _Optional[int] = ..., multi_variable_bar_count: _Optional[int] = ..., distance_of_bars: _Optional[float] = ..., axial_distance_si: _Optional[float] = ..., axial_distance_sj: _Optional[float] = ..., axial_distance_sn: _Optional[float] = ..., distance_from_start_is_defined_as_relative: bool = ..., distance_from_start_relative: _Optional[float] = ..., distance_from_start_absolute: _Optional[float] = ..., distance_from_end_relative: _Optional[float] = ..., distance_from_end_absolute: _Optional[float] = ..., comment: _Optional[str] = ..., generating_object_info: _Optional[str] = ..., is_generated: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
