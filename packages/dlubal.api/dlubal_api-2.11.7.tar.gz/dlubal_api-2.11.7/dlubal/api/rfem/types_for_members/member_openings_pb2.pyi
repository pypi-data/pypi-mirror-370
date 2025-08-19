from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberOpenings(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "members", "member_sets", "components", "is_generated", "generating_object_info", "comment", "id_for_export_import", "metadata_for_export_import")
    class ComponentsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberOpenings.ComponentsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberOpenings.ComponentsRow, _Mapping]]] = ...) -> None: ...
    class ComponentsRow(_message.Message):
        __slots__ = ("no", "description", "reduction_type", "position", "multiple", "note", "multiple_number", "multiple_offset_definition_type", "multiple_offset", "width", "height", "z_axis_reference", "distance", "diameter", "width_center")
        class ReductionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            REDUCTION_TYPE_REDUCTION_COMPONENT_TYPE_RECTANGLE_OPENING: _ClassVar[MemberOpenings.ComponentsRow.ReductionType]
            REDUCTION_TYPE_REDUCTION_COMPONENT_TYPE_CIRCLE_OPENING: _ClassVar[MemberOpenings.ComponentsRow.ReductionType]
            REDUCTION_TYPE_REDUCTION_COMPONENT_TYPE_HEXAGONAL_OPENING: _ClassVar[MemberOpenings.ComponentsRow.ReductionType]
        REDUCTION_TYPE_REDUCTION_COMPONENT_TYPE_RECTANGLE_OPENING: MemberOpenings.ComponentsRow.ReductionType
        REDUCTION_TYPE_REDUCTION_COMPONENT_TYPE_CIRCLE_OPENING: MemberOpenings.ComponentsRow.ReductionType
        REDUCTION_TYPE_REDUCTION_COMPONENT_TYPE_HEXAGONAL_OPENING: MemberOpenings.ComponentsRow.ReductionType
        class MultipleOffsetDefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            MULTIPLE_OFFSET_DEFINITION_TYPE_ABSOLUTE: _ClassVar[MemberOpenings.ComponentsRow.MultipleOffsetDefinitionType]
            MULTIPLE_OFFSET_DEFINITION_TYPE_RELATIVE: _ClassVar[MemberOpenings.ComponentsRow.MultipleOffsetDefinitionType]
        MULTIPLE_OFFSET_DEFINITION_TYPE_ABSOLUTE: MemberOpenings.ComponentsRow.MultipleOffsetDefinitionType
        MULTIPLE_OFFSET_DEFINITION_TYPE_RELATIVE: MemberOpenings.ComponentsRow.MultipleOffsetDefinitionType
        class ZAxisReference(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            Z_AXIS_REFERENCE_E_POSITION_REFERENCE_TOP: _ClassVar[MemberOpenings.ComponentsRow.ZAxisReference]
            Z_AXIS_REFERENCE_E_POSITION_REFERENCE_BOTTOM: _ClassVar[MemberOpenings.ComponentsRow.ZAxisReference]
            Z_AXIS_REFERENCE_E_POSITION_REFERENCE_CENTER: _ClassVar[MemberOpenings.ComponentsRow.ZAxisReference]
        Z_AXIS_REFERENCE_E_POSITION_REFERENCE_TOP: MemberOpenings.ComponentsRow.ZAxisReference
        Z_AXIS_REFERENCE_E_POSITION_REFERENCE_BOTTOM: MemberOpenings.ComponentsRow.ZAxisReference
        Z_AXIS_REFERENCE_E_POSITION_REFERENCE_CENTER: MemberOpenings.ComponentsRow.ZAxisReference
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        REDUCTION_TYPE_FIELD_NUMBER: _ClassVar[int]
        POSITION_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_NUMBER_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_OFFSET_DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_OFFSET_FIELD_NUMBER: _ClassVar[int]
        WIDTH_FIELD_NUMBER: _ClassVar[int]
        HEIGHT_FIELD_NUMBER: _ClassVar[int]
        Z_AXIS_REFERENCE_FIELD_NUMBER: _ClassVar[int]
        DISTANCE_FIELD_NUMBER: _ClassVar[int]
        DIAMETER_FIELD_NUMBER: _ClassVar[int]
        WIDTH_CENTER_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        reduction_type: MemberOpenings.ComponentsRow.ReductionType
        position: float
        multiple: bool
        note: str
        multiple_number: int
        multiple_offset_definition_type: MemberOpenings.ComponentsRow.MultipleOffsetDefinitionType
        multiple_offset: float
        width: float
        height: float
        z_axis_reference: MemberOpenings.ComponentsRow.ZAxisReference
        distance: float
        diameter: float
        width_center: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., reduction_type: _Optional[_Union[MemberOpenings.ComponentsRow.ReductionType, str]] = ..., position: _Optional[float] = ..., multiple: bool = ..., note: _Optional[str] = ..., multiple_number: _Optional[int] = ..., multiple_offset_definition_type: _Optional[_Union[MemberOpenings.ComponentsRow.MultipleOffsetDefinitionType, str]] = ..., multiple_offset: _Optional[float] = ..., width: _Optional[float] = ..., height: _Optional[float] = ..., z_axis_reference: _Optional[_Union[MemberOpenings.ComponentsRow.ZAxisReference, str]] = ..., distance: _Optional[float] = ..., diameter: _Optional[float] = ..., width_center: _Optional[float] = ...) -> None: ...
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
    components: MemberOpenings.ComponentsTable
    is_generated: bool
    generating_object_info: str
    comment: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., components: _Optional[_Union[MemberOpenings.ComponentsTable, _Mapping]] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., comment: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
