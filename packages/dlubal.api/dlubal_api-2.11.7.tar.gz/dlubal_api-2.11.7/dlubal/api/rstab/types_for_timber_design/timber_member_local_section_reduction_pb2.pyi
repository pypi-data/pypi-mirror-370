from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TimberMemberLocalSectionReduction(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "members", "member_sets", "components", "is_generated", "generating_object_info", "comment", "id_for_export_import", "metadata_for_export_import")
    class ComponentsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[TimberMemberLocalSectionReduction.ComponentsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[TimberMemberLocalSectionReduction.ComponentsRow, _Mapping]]] = ...) -> None: ...
    class ComponentsRow(_message.Message):
        __slots__ = ("no", "description", "reduction_type", "position", "multiple", "note", "multiple_number", "multiple_offset_definition_type", "multiple_offset", "length", "orientation", "depth", "direction", "stability", "fire_design", "fire_exposure_top", "fire_exposure_left", "fire_exposure_right", "fire_exposure_bottom", "support", "support_distance", "stiffening_elements_apply", "stiffening_elements_number", "stiffening_elements_object")
        class ReductionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            REDUCTION_TYPE_UNKNOWN: _ClassVar[TimberMemberLocalSectionReduction.ComponentsRow.ReductionType]
            REDUCTION_TYPE_REDUCTION_COMPONENT_TYPE_END_NOTCH: _ClassVar[TimberMemberLocalSectionReduction.ComponentsRow.ReductionType]
            REDUCTION_TYPE_REDUCTION_COMPONENT_TYPE_INNER_NOTCH: _ClassVar[TimberMemberLocalSectionReduction.ComponentsRow.ReductionType]
            REDUCTION_TYPE_REDUCTION_COMPONENT_TYPE_START_NOTCH: _ClassVar[TimberMemberLocalSectionReduction.ComponentsRow.ReductionType]
        REDUCTION_TYPE_UNKNOWN: TimberMemberLocalSectionReduction.ComponentsRow.ReductionType
        REDUCTION_TYPE_REDUCTION_COMPONENT_TYPE_END_NOTCH: TimberMemberLocalSectionReduction.ComponentsRow.ReductionType
        REDUCTION_TYPE_REDUCTION_COMPONENT_TYPE_INNER_NOTCH: TimberMemberLocalSectionReduction.ComponentsRow.ReductionType
        REDUCTION_TYPE_REDUCTION_COMPONENT_TYPE_START_NOTCH: TimberMemberLocalSectionReduction.ComponentsRow.ReductionType
        class MultipleOffsetDefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            MULTIPLE_OFFSET_DEFINITION_TYPE_ABSOLUTE: _ClassVar[TimberMemberLocalSectionReduction.ComponentsRow.MultipleOffsetDefinitionType]
            MULTIPLE_OFFSET_DEFINITION_TYPE_RELATIVE: _ClassVar[TimberMemberLocalSectionReduction.ComponentsRow.MultipleOffsetDefinitionType]
        MULTIPLE_OFFSET_DEFINITION_TYPE_ABSOLUTE: TimberMemberLocalSectionReduction.ComponentsRow.MultipleOffsetDefinitionType
        MULTIPLE_OFFSET_DEFINITION_TYPE_RELATIVE: TimberMemberLocalSectionReduction.ComponentsRow.MultipleOffsetDefinitionType
        class Orientation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            ORIENTATION_E_ORIENTATION_DEPTH: _ClassVar[TimberMemberLocalSectionReduction.ComponentsRow.Orientation]
            ORIENTATION_E_ORIENTATION_WIDTH: _ClassVar[TimberMemberLocalSectionReduction.ComponentsRow.Orientation]
        ORIENTATION_E_ORIENTATION_DEPTH: TimberMemberLocalSectionReduction.ComponentsRow.Orientation
        ORIENTATION_E_ORIENTATION_WIDTH: TimberMemberLocalSectionReduction.ComponentsRow.Orientation
        class Direction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            DIRECTION_E_DIRECTION_DEPTH_POSITIVE: _ClassVar[TimberMemberLocalSectionReduction.ComponentsRow.Direction]
            DIRECTION_E_DIRECTION_DEPTH_NEGATIVE: _ClassVar[TimberMemberLocalSectionReduction.ComponentsRow.Direction]
            DIRECTION_E_DIRECTION_WIDTH_NEGATIVE: _ClassVar[TimberMemberLocalSectionReduction.ComponentsRow.Direction]
            DIRECTION_E_DIRECTION_WIDTH_POSITIVE: _ClassVar[TimberMemberLocalSectionReduction.ComponentsRow.Direction]
        DIRECTION_E_DIRECTION_DEPTH_POSITIVE: TimberMemberLocalSectionReduction.ComponentsRow.Direction
        DIRECTION_E_DIRECTION_DEPTH_NEGATIVE: TimberMemberLocalSectionReduction.ComponentsRow.Direction
        DIRECTION_E_DIRECTION_WIDTH_NEGATIVE: TimberMemberLocalSectionReduction.ComponentsRow.Direction
        DIRECTION_E_DIRECTION_WIDTH_POSITIVE: TimberMemberLocalSectionReduction.ComponentsRow.Direction
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        REDUCTION_TYPE_FIELD_NUMBER: _ClassVar[int]
        POSITION_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_NUMBER_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_OFFSET_DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_OFFSET_FIELD_NUMBER: _ClassVar[int]
        LENGTH_FIELD_NUMBER: _ClassVar[int]
        ORIENTATION_FIELD_NUMBER: _ClassVar[int]
        DEPTH_FIELD_NUMBER: _ClassVar[int]
        DIRECTION_FIELD_NUMBER: _ClassVar[int]
        STABILITY_FIELD_NUMBER: _ClassVar[int]
        FIRE_DESIGN_FIELD_NUMBER: _ClassVar[int]
        FIRE_EXPOSURE_TOP_FIELD_NUMBER: _ClassVar[int]
        FIRE_EXPOSURE_LEFT_FIELD_NUMBER: _ClassVar[int]
        FIRE_EXPOSURE_RIGHT_FIELD_NUMBER: _ClassVar[int]
        FIRE_EXPOSURE_BOTTOM_FIELD_NUMBER: _ClassVar[int]
        SUPPORT_FIELD_NUMBER: _ClassVar[int]
        SUPPORT_DISTANCE_FIELD_NUMBER: _ClassVar[int]
        STIFFENING_ELEMENTS_APPLY_FIELD_NUMBER: _ClassVar[int]
        STIFFENING_ELEMENTS_NUMBER_FIELD_NUMBER: _ClassVar[int]
        STIFFENING_ELEMENTS_OBJECT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        reduction_type: TimberMemberLocalSectionReduction.ComponentsRow.ReductionType
        position: float
        multiple: bool
        note: str
        multiple_number: int
        multiple_offset_definition_type: TimberMemberLocalSectionReduction.ComponentsRow.MultipleOffsetDefinitionType
        multiple_offset: float
        length: float
        orientation: TimberMemberLocalSectionReduction.ComponentsRow.Orientation
        depth: float
        direction: TimberMemberLocalSectionReduction.ComponentsRow.Direction
        stability: bool
        fire_design: bool
        fire_exposure_top: bool
        fire_exposure_left: bool
        fire_exposure_right: bool
        fire_exposure_bottom: bool
        support: bool
        support_distance: float
        stiffening_elements_apply: bool
        stiffening_elements_number: int
        stiffening_elements_object: int
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., reduction_type: _Optional[_Union[TimberMemberLocalSectionReduction.ComponentsRow.ReductionType, str]] = ..., position: _Optional[float] = ..., multiple: bool = ..., note: _Optional[str] = ..., multiple_number: _Optional[int] = ..., multiple_offset_definition_type: _Optional[_Union[TimberMemberLocalSectionReduction.ComponentsRow.MultipleOffsetDefinitionType, str]] = ..., multiple_offset: _Optional[float] = ..., length: _Optional[float] = ..., orientation: _Optional[_Union[TimberMemberLocalSectionReduction.ComponentsRow.Orientation, str]] = ..., depth: _Optional[float] = ..., direction: _Optional[_Union[TimberMemberLocalSectionReduction.ComponentsRow.Direction, str]] = ..., stability: bool = ..., fire_design: bool = ..., fire_exposure_top: bool = ..., fire_exposure_left: bool = ..., fire_exposure_right: bool = ..., fire_exposure_bottom: bool = ..., support: bool = ..., support_distance: _Optional[float] = ..., stiffening_elements_apply: bool = ..., stiffening_elements_number: _Optional[int] = ..., stiffening_elements_object: _Optional[int] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    members: _containers.RepeatedScalarFieldContainer[int]
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    components: TimberMemberLocalSectionReduction.ComponentsTable
    is_generated: bool
    generating_object_info: str
    comment: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., components: _Optional[_Union[TimberMemberLocalSectionReduction.ComponentsTable, _Mapping]] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., comment: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
