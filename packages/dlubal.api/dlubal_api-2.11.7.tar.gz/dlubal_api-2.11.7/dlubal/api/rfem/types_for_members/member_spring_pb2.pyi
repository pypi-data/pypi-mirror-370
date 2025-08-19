from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberSpring(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "assigned_to", "definition_type", "axial_stiffness", "self_weight_definition", "mass", "mass_per_length", "specific_weight", "section_area", "partial_activity_along_x_negative_type", "partial_activity_along_x_negative_displacement", "partial_activity_along_x_negative_force", "partial_activity_along_x_negative_slippage", "partial_activity_along_x_positive_type", "partial_activity_along_x_positive_displacement", "partial_activity_along_x_positive_force", "partial_activity_along_x_positive_slippage", "diagram_along_x_symmetric", "diagram_along_x_is_sorted", "diagram_along_x_table", "diagram_along_x_start", "diagram_along_x_end", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class DefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFINITION_TYPE_UNKNOWN: _ClassVar[MemberSpring.DefinitionType]
        DEFINITION_TYPE_DIAGRAM: _ClassVar[MemberSpring.DefinitionType]
        DEFINITION_TYPE_PARTIAL_ACTIVITY: _ClassVar[MemberSpring.DefinitionType]
    DEFINITION_TYPE_UNKNOWN: MemberSpring.DefinitionType
    DEFINITION_TYPE_DIAGRAM: MemberSpring.DefinitionType
    DEFINITION_TYPE_PARTIAL_ACTIVITY: MemberSpring.DefinitionType
    class SelfWeightDefinition(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SELF_WEIGHT_DEFINITION_MASS: _ClassVar[MemberSpring.SelfWeightDefinition]
        SELF_WEIGHT_DEFINITION_MASS_PER_LENGTH: _ClassVar[MemberSpring.SelfWeightDefinition]
        SELF_WEIGHT_DEFINITION_SPECIFIC_WEIGHT: _ClassVar[MemberSpring.SelfWeightDefinition]
    SELF_WEIGHT_DEFINITION_MASS: MemberSpring.SelfWeightDefinition
    SELF_WEIGHT_DEFINITION_MASS_PER_LENGTH: MemberSpring.SelfWeightDefinition
    SELF_WEIGHT_DEFINITION_SPECIFIC_WEIGHT: MemberSpring.SelfWeightDefinition
    class PartialActivityAlongXNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_COMPLETE: _ClassVar[MemberSpring.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE: _ClassVar[MemberSpring.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[MemberSpring.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIXED: _ClassVar[MemberSpring.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[MemberSpring.PartialActivityAlongXNegativeType]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_COMPLETE: MemberSpring.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE: MemberSpring.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: MemberSpring.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIXED: MemberSpring.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: MemberSpring.PartialActivityAlongXNegativeType
    class PartialActivityAlongXPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_COMPLETE: _ClassVar[MemberSpring.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE: _ClassVar[MemberSpring.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[MemberSpring.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIXED: _ClassVar[MemberSpring.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[MemberSpring.PartialActivityAlongXPositiveType]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_COMPLETE: MemberSpring.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE: MemberSpring.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: MemberSpring.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIXED: MemberSpring.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: MemberSpring.PartialActivityAlongXPositiveType
    class DiagramAlongXStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_X_START_FAILURE: _ClassVar[MemberSpring.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_CONTINUOUS: _ClassVar[MemberSpring.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_STOP: _ClassVar[MemberSpring.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_YIELDING: _ClassVar[MemberSpring.DiagramAlongXStart]
    DIAGRAM_ALONG_X_START_FAILURE: MemberSpring.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_CONTINUOUS: MemberSpring.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_STOP: MemberSpring.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_YIELDING: MemberSpring.DiagramAlongXStart
    class DiagramAlongXEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_X_END_FAILURE: _ClassVar[MemberSpring.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_CONTINUOUS: _ClassVar[MemberSpring.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_STOP: _ClassVar[MemberSpring.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_YIELDING: _ClassVar[MemberSpring.DiagramAlongXEnd]
    DIAGRAM_ALONG_X_END_FAILURE: MemberSpring.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_CONTINUOUS: MemberSpring.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_STOP: MemberSpring.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_YIELDING: MemberSpring.DiagramAlongXEnd
    class DiagramAlongXTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberSpring.DiagramAlongXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberSpring.DiagramAlongXTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAlongXTableRow(_message.Message):
        __slots__ = ("no", "description", "displacement", "force", "spring", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
        FORCE_FIELD_NUMBER: _ClassVar[int]
        SPRING_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        displacement: float
        force: float
        spring: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., displacement: _Optional[float] = ..., force: _Optional[float] = ..., spring: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    AXIAL_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    SELF_WEIGHT_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    MASS_PER_LENGTH_FIELD_NUMBER: _ClassVar[int]
    SPECIFIC_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    SECTION_AREA_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_END_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    assigned_to: _containers.RepeatedScalarFieldContainer[int]
    definition_type: MemberSpring.DefinitionType
    axial_stiffness: float
    self_weight_definition: MemberSpring.SelfWeightDefinition
    mass: float
    mass_per_length: float
    specific_weight: float
    section_area: float
    partial_activity_along_x_negative_type: MemberSpring.PartialActivityAlongXNegativeType
    partial_activity_along_x_negative_displacement: float
    partial_activity_along_x_negative_force: float
    partial_activity_along_x_negative_slippage: float
    partial_activity_along_x_positive_type: MemberSpring.PartialActivityAlongXPositiveType
    partial_activity_along_x_positive_displacement: float
    partial_activity_along_x_positive_force: float
    partial_activity_along_x_positive_slippage: float
    diagram_along_x_symmetric: bool
    diagram_along_x_is_sorted: bool
    diagram_along_x_table: MemberSpring.DiagramAlongXTable
    diagram_along_x_start: MemberSpring.DiagramAlongXStart
    diagram_along_x_end: MemberSpring.DiagramAlongXEnd
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., assigned_to: _Optional[_Iterable[int]] = ..., definition_type: _Optional[_Union[MemberSpring.DefinitionType, str]] = ..., axial_stiffness: _Optional[float] = ..., self_weight_definition: _Optional[_Union[MemberSpring.SelfWeightDefinition, str]] = ..., mass: _Optional[float] = ..., mass_per_length: _Optional[float] = ..., specific_weight: _Optional[float] = ..., section_area: _Optional[float] = ..., partial_activity_along_x_negative_type: _Optional[_Union[MemberSpring.PartialActivityAlongXNegativeType, str]] = ..., partial_activity_along_x_negative_displacement: _Optional[float] = ..., partial_activity_along_x_negative_force: _Optional[float] = ..., partial_activity_along_x_negative_slippage: _Optional[float] = ..., partial_activity_along_x_positive_type: _Optional[_Union[MemberSpring.PartialActivityAlongXPositiveType, str]] = ..., partial_activity_along_x_positive_displacement: _Optional[float] = ..., partial_activity_along_x_positive_force: _Optional[float] = ..., partial_activity_along_x_positive_slippage: _Optional[float] = ..., diagram_along_x_symmetric: bool = ..., diagram_along_x_is_sorted: bool = ..., diagram_along_x_table: _Optional[_Union[MemberSpring.DiagramAlongXTable, _Mapping]] = ..., diagram_along_x_start: _Optional[_Union[MemberSpring.DiagramAlongXStart, str]] = ..., diagram_along_x_end: _Optional[_Union[MemberSpring.DiagramAlongXEnd, str]] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
