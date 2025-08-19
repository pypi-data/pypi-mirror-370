from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StressPoint(_message.Message):
    __slots__ = ("no", "definition_type", "coordinate_system", "coordinate_system_type", "coordinates", "coordinate_1", "coordinate_2", "global_coordinates", "global_coordinate_1", "global_coordinate_2", "comment", "on_line_reference_line", "on_element_reference_element", "reference_type", "reference_object_projected_length", "distance_from_start_is_defined_as_relative", "distance_from_start_relative", "distance_from_start_absolute", "distance_from_end_relative", "distance_from_end_absolute", "is_generated", "generating_object_info", "reference_stress_point", "on_element_element_side", "part", "element", "id_for_export_import", "metadata_for_export_import")
    class DefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFINITION_TYPE_UNKNOWN: _ClassVar[StressPoint.DefinitionType]
        DEFINITION_TYPE_ON_ELEMENT: _ClassVar[StressPoint.DefinitionType]
        DEFINITION_TYPE_ON_LINE: _ClassVar[StressPoint.DefinitionType]
        DEFINITION_TYPE_STANDARD: _ClassVar[StressPoint.DefinitionType]
    DEFINITION_TYPE_UNKNOWN: StressPoint.DefinitionType
    DEFINITION_TYPE_ON_ELEMENT: StressPoint.DefinitionType
    DEFINITION_TYPE_ON_LINE: StressPoint.DefinitionType
    DEFINITION_TYPE_STANDARD: StressPoint.DefinitionType
    class CoordinateSystemType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COORDINATE_SYSTEM_TYPE_CARTESIAN: _ClassVar[StressPoint.CoordinateSystemType]
    COORDINATE_SYSTEM_TYPE_CARTESIAN: StressPoint.CoordinateSystemType
    class ReferenceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REFERENCE_TYPE_L: _ClassVar[StressPoint.ReferenceType]
        REFERENCE_TYPE_XZ: _ClassVar[StressPoint.ReferenceType]
        REFERENCE_TYPE_YZ: _ClassVar[StressPoint.ReferenceType]
    REFERENCE_TYPE_L: StressPoint.ReferenceType
    REFERENCE_TYPE_XZ: StressPoint.ReferenceType
    REFERENCE_TYPE_YZ: StressPoint.ReferenceType
    class OnElementElementSide(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ON_ELEMENT_ELEMENT_SIDE_MIDDLE: _ClassVar[StressPoint.OnElementElementSide]
        ON_ELEMENT_ELEMENT_SIDE_LEFT: _ClassVar[StressPoint.OnElementElementSide]
        ON_ELEMENT_ELEMENT_SIDE_RIGHT: _ClassVar[StressPoint.OnElementElementSide]
    ON_ELEMENT_ELEMENT_SIDE_MIDDLE: StressPoint.OnElementElementSide
    ON_ELEMENT_ELEMENT_SIDE_LEFT: StressPoint.OnElementElementSide
    ON_ELEMENT_ELEMENT_SIDE_RIGHT: StressPoint.OnElementElementSide
    NO_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_TYPE_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_1_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_2_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_COORDINATE_1_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_COORDINATE_2_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ON_LINE_REFERENCE_LINE_FIELD_NUMBER: _ClassVar[int]
    ON_ELEMENT_REFERENCE_ELEMENT_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_OBJECT_PROJECTED_LENGTH_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_START_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_START_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_START_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_END_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_END_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_STRESS_POINT_FIELD_NUMBER: _ClassVar[int]
    ON_ELEMENT_ELEMENT_SIDE_FIELD_NUMBER: _ClassVar[int]
    PART_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    definition_type: StressPoint.DefinitionType
    coordinate_system: int
    coordinate_system_type: StressPoint.CoordinateSystemType
    coordinates: _common_pb2.Vector3d
    coordinate_1: float
    coordinate_2: float
    global_coordinates: _common_pb2.Vector3d
    global_coordinate_1: float
    global_coordinate_2: float
    comment: str
    on_line_reference_line: int
    on_element_reference_element: int
    reference_type: StressPoint.ReferenceType
    reference_object_projected_length: float
    distance_from_start_is_defined_as_relative: bool
    distance_from_start_relative: float
    distance_from_start_absolute: float
    distance_from_end_relative: float
    distance_from_end_absolute: float
    is_generated: bool
    generating_object_info: str
    reference_stress_point: int
    on_element_element_side: StressPoint.OnElementElementSide
    part: int
    element: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., definition_type: _Optional[_Union[StressPoint.DefinitionType, str]] = ..., coordinate_system: _Optional[int] = ..., coordinate_system_type: _Optional[_Union[StressPoint.CoordinateSystemType, str]] = ..., coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., coordinate_1: _Optional[float] = ..., coordinate_2: _Optional[float] = ..., global_coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., global_coordinate_1: _Optional[float] = ..., global_coordinate_2: _Optional[float] = ..., comment: _Optional[str] = ..., on_line_reference_line: _Optional[int] = ..., on_element_reference_element: _Optional[int] = ..., reference_type: _Optional[_Union[StressPoint.ReferenceType, str]] = ..., reference_object_projected_length: _Optional[float] = ..., distance_from_start_is_defined_as_relative: bool = ..., distance_from_start_relative: _Optional[float] = ..., distance_from_start_absolute: _Optional[float] = ..., distance_from_end_relative: _Optional[float] = ..., distance_from_end_absolute: _Optional[float] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., reference_stress_point: _Optional[int] = ..., on_element_element_side: _Optional[_Union[StressPoint.OnElementElementSide, str]] = ..., part: _Optional[int] = ..., element: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
