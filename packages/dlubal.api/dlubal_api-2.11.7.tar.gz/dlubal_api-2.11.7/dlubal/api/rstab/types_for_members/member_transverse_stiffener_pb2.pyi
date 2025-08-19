from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberTransverseStiffener(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "members", "member_sets", "components", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class ComponentsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberTransverseStiffener.ComponentsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberTransverseStiffener.ComponentsRow, _Mapping]]] = ...) -> None: ...
    class ComponentsRow(_message.Message):
        __slots__ = ("no", "description", "stiffener_type", "position", "position_type", "multiple", "note", "multiple_number", "multiple_offset_definition_type", "multiple_offset", "material", "consider_stiffener", "definition_type", "offset_horizontal", "offset_vertical", "thickness", "width", "height", "non_rigid", "rigid", "width_b_u", "height_h_u", "thickness_t_u", "thickness_s_u", "width_b", "thickness_t", "column_section", "section", "cantilever_l_c", "full_warping_restraint", "user_defined_restraint", "user_defined_restraint_value")
        class StiffenerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_FLAT: _ClassVar[MemberTransverseStiffener.ComponentsRow.StiffenerType]
            STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_ANGLE: _ClassVar[MemberTransverseStiffener.ComponentsRow.StiffenerType]
            STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_CHANNEL_SECTION: _ClassVar[MemberTransverseStiffener.ComponentsRow.StiffenerType]
            STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_CONNECTING_COLUMN_END: _ClassVar[MemberTransverseStiffener.ComponentsRow.StiffenerType]
            STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_CONNECTING_COLUMN_START: _ClassVar[MemberTransverseStiffener.ComponentsRow.StiffenerType]
            STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_END_PLATE_END: _ClassVar[MemberTransverseStiffener.ComponentsRow.StiffenerType]
            STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_END_PLATE_START: _ClassVar[MemberTransverseStiffener.ComponentsRow.StiffenerType]
            STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_WARPING_RESTRAINT: _ClassVar[MemberTransverseStiffener.ComponentsRow.StiffenerType]
        STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_FLAT: MemberTransverseStiffener.ComponentsRow.StiffenerType
        STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_ANGLE: MemberTransverseStiffener.ComponentsRow.StiffenerType
        STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_CHANNEL_SECTION: MemberTransverseStiffener.ComponentsRow.StiffenerType
        STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_CONNECTING_COLUMN_END: MemberTransverseStiffener.ComponentsRow.StiffenerType
        STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_CONNECTING_COLUMN_START: MemberTransverseStiffener.ComponentsRow.StiffenerType
        STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_END_PLATE_END: MemberTransverseStiffener.ComponentsRow.StiffenerType
        STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_END_PLATE_START: MemberTransverseStiffener.ComponentsRow.StiffenerType
        STIFFENER_TYPE_STIFFENER_COMPONENT_TYPE_WARPING_RESTRAINT: MemberTransverseStiffener.ComponentsRow.StiffenerType
        class PositionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            POSITION_TYPE_STIFFENER_COMPONENT_POSITION_DOUBLE_SIDED: _ClassVar[MemberTransverseStiffener.ComponentsRow.PositionType]
            POSITION_TYPE_STIFFENER_COMPONENT_POSITION_SINGLE_SIDED_LEFT: _ClassVar[MemberTransverseStiffener.ComponentsRow.PositionType]
            POSITION_TYPE_STIFFENER_COMPONENT_POSITION_SINGLE_SIDED_RIGHT: _ClassVar[MemberTransverseStiffener.ComponentsRow.PositionType]
        POSITION_TYPE_STIFFENER_COMPONENT_POSITION_DOUBLE_SIDED: MemberTransverseStiffener.ComponentsRow.PositionType
        POSITION_TYPE_STIFFENER_COMPONENT_POSITION_SINGLE_SIDED_LEFT: MemberTransverseStiffener.ComponentsRow.PositionType
        POSITION_TYPE_STIFFENER_COMPONENT_POSITION_SINGLE_SIDED_RIGHT: MemberTransverseStiffener.ComponentsRow.PositionType
        class MultipleOffsetDefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            MULTIPLE_OFFSET_DEFINITION_TYPE_ABSOLUTE: _ClassVar[MemberTransverseStiffener.ComponentsRow.MultipleOffsetDefinitionType]
            MULTIPLE_OFFSET_DEFINITION_TYPE_RELATIVE: _ClassVar[MemberTransverseStiffener.ComponentsRow.MultipleOffsetDefinitionType]
        MULTIPLE_OFFSET_DEFINITION_TYPE_ABSOLUTE: MemberTransverseStiffener.ComponentsRow.MultipleOffsetDefinitionType
        MULTIPLE_OFFSET_DEFINITION_TYPE_RELATIVE: MemberTransverseStiffener.ComponentsRow.MultipleOffsetDefinitionType
        class DefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            DEFINITION_TYPE_DIMENSION_TYPE_OFFSET: _ClassVar[MemberTransverseStiffener.ComponentsRow.DefinitionType]
            DEFINITION_TYPE_DIMENSION_TYPE_SIZE: _ClassVar[MemberTransverseStiffener.ComponentsRow.DefinitionType]
        DEFINITION_TYPE_DIMENSION_TYPE_OFFSET: MemberTransverseStiffener.ComponentsRow.DefinitionType
        DEFINITION_TYPE_DIMENSION_TYPE_SIZE: MemberTransverseStiffener.ComponentsRow.DefinitionType
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        STIFFENER_TYPE_FIELD_NUMBER: _ClassVar[int]
        POSITION_FIELD_NUMBER: _ClassVar[int]
        POSITION_TYPE_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_NUMBER_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_OFFSET_DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_OFFSET_FIELD_NUMBER: _ClassVar[int]
        MATERIAL_FIELD_NUMBER: _ClassVar[int]
        CONSIDER_STIFFENER_FIELD_NUMBER: _ClassVar[int]
        DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
        OFFSET_HORIZONTAL_FIELD_NUMBER: _ClassVar[int]
        OFFSET_VERTICAL_FIELD_NUMBER: _ClassVar[int]
        THICKNESS_FIELD_NUMBER: _ClassVar[int]
        WIDTH_FIELD_NUMBER: _ClassVar[int]
        HEIGHT_FIELD_NUMBER: _ClassVar[int]
        NON_RIGID_FIELD_NUMBER: _ClassVar[int]
        RIGID_FIELD_NUMBER: _ClassVar[int]
        WIDTH_B_U_FIELD_NUMBER: _ClassVar[int]
        HEIGHT_H_U_FIELD_NUMBER: _ClassVar[int]
        THICKNESS_T_U_FIELD_NUMBER: _ClassVar[int]
        THICKNESS_S_U_FIELD_NUMBER: _ClassVar[int]
        WIDTH_B_FIELD_NUMBER: _ClassVar[int]
        THICKNESS_T_FIELD_NUMBER: _ClassVar[int]
        COLUMN_SECTION_FIELD_NUMBER: _ClassVar[int]
        SECTION_FIELD_NUMBER: _ClassVar[int]
        CANTILEVER_L_C_FIELD_NUMBER: _ClassVar[int]
        FULL_WARPING_RESTRAINT_FIELD_NUMBER: _ClassVar[int]
        USER_DEFINED_RESTRAINT_FIELD_NUMBER: _ClassVar[int]
        USER_DEFINED_RESTRAINT_VALUE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        stiffener_type: MemberTransverseStiffener.ComponentsRow.StiffenerType
        position: float
        position_type: MemberTransverseStiffener.ComponentsRow.PositionType
        multiple: bool
        note: str
        multiple_number: int
        multiple_offset_definition_type: MemberTransverseStiffener.ComponentsRow.MultipleOffsetDefinitionType
        multiple_offset: float
        material: int
        consider_stiffener: bool
        definition_type: MemberTransverseStiffener.ComponentsRow.DefinitionType
        offset_horizontal: float
        offset_vertical: float
        thickness: float
        width: float
        height: float
        non_rigid: bool
        rigid: bool
        width_b_u: float
        height_h_u: float
        thickness_t_u: float
        thickness_s_u: float
        width_b: float
        thickness_t: float
        column_section: int
        section: int
        cantilever_l_c: float
        full_warping_restraint: bool
        user_defined_restraint: bool
        user_defined_restraint_value: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., stiffener_type: _Optional[_Union[MemberTransverseStiffener.ComponentsRow.StiffenerType, str]] = ..., position: _Optional[float] = ..., position_type: _Optional[_Union[MemberTransverseStiffener.ComponentsRow.PositionType, str]] = ..., multiple: bool = ..., note: _Optional[str] = ..., multiple_number: _Optional[int] = ..., multiple_offset_definition_type: _Optional[_Union[MemberTransverseStiffener.ComponentsRow.MultipleOffsetDefinitionType, str]] = ..., multiple_offset: _Optional[float] = ..., material: _Optional[int] = ..., consider_stiffener: bool = ..., definition_type: _Optional[_Union[MemberTransverseStiffener.ComponentsRow.DefinitionType, str]] = ..., offset_horizontal: _Optional[float] = ..., offset_vertical: _Optional[float] = ..., thickness: _Optional[float] = ..., width: _Optional[float] = ..., height: _Optional[float] = ..., non_rigid: bool = ..., rigid: bool = ..., width_b_u: _Optional[float] = ..., height_h_u: _Optional[float] = ..., thickness_t_u: _Optional[float] = ..., thickness_s_u: _Optional[float] = ..., width_b: _Optional[float] = ..., thickness_t: _Optional[float] = ..., column_section: _Optional[int] = ..., section: _Optional[int] = ..., cantilever_l_c: _Optional[float] = ..., full_warping_restraint: bool = ..., user_defined_restraint: bool = ..., user_defined_restraint_value: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    members: _containers.RepeatedScalarFieldContainer[int]
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    components: MemberTransverseStiffener.ComponentsTable
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., components: _Optional[_Union[MemberTransverseStiffener.ComponentsTable, _Mapping]] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
