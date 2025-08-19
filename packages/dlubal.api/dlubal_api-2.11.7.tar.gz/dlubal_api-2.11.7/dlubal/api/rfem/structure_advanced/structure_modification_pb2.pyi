from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StructureModification(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "assigned_to", "comment", "modify_stiffnesses_gamma_m", "modify_stiffnesses_materials", "modify_stiffnesses_sections", "modify_stiffnesses_members", "modify_stiffnesses_surfaces", "modify_stiffnesses_member_hinges", "modify_stiffnesses_line_hinges", "modify_stiffnesses_nodal_supports", "modify_stiffnesses_line_supports", "modify_stiffnesses_member_supports", "modify_stiffnesses_surface_supports", "modify_stiffness_member_reinforcement", "modify_stiffness_surface_reinforcement", "modify_stiffness_timber_members_due_moisture_class", "nonlinearities_disabled_material_nonlinearity_models", "nonlinearities_disabled_material_temperature_nonlinearities", "nonlinearities_disabled_line_hinges", "nonlinearities_disabled_member_types", "nonlinearities_disabled_member_hinges", "nonlinearities_disabled_member_nonlinearities", "nonlinearities_disabled_solid_types_contact_or_surfaces_contact", "nonlinearities_disabled_nodal_supports", "nonlinearities_disabled_line_supports", "nonlinearities_disabled_member_supports", "nonlinearities_disabled_surface_supports", "modify_stiffnesses_material_table", "modify_stiffnesses_section_table", "modify_stiffnesses_member_table", "modify_stiffnesses_surface_table", "modify_stiffnesses_member_hinges_table", "modify_stiffnesses_line_hinges_table", "modify_stiffnesses_nodal_supports_table", "modify_stiffnesses_line_supports_table", "modify_stiffnesses_member_supports_table", "modify_stiffnesses_surface_supports_table", "deactivate_members_enabled", "object_selection_for_deactivate_members", "deactivate_surfaces_enabled", "object_selection_for_deactivate_surfaces", "deactivate_solids_enabled", "object_selection_for_deactivate_solids", "deactivate_support_on_nodes_enabled", "object_selection_for_deactivate_support_on_nodes", "deactivate_support_on_lines_enabled", "object_selection_for_deactivate_support_on_lines", "deactivate_support_on_members_enabled", "object_selection_for_deactivate_support_on_members", "deactivate_support_on_surfaces_enabled", "object_selection_for_deactivate_support_on_surfaces", "id_for_export_import", "metadata_for_export_import")
    class ModifyStiffnessesMaterialTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[StructureModification.ModifyStiffnessesMaterialTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[StructureModification.ModifyStiffnessesMaterialTableRow, _Mapping]]] = ...) -> None: ...
    class ModifyStiffnessesMaterialTableRow(_message.Message):
        __slots__ = ("no", "description", "material_name", "modification_type", "E_and_G", "comment")
        class ModificationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            MODIFICATION_TYPE_MULTIPLY_FACTOR: _ClassVar[StructureModification.ModifyStiffnessesMaterialTableRow.ModificationType]
            MODIFICATION_TYPE_DIVISION_FACTOR: _ClassVar[StructureModification.ModifyStiffnessesMaterialTableRow.ModificationType]
        MODIFICATION_TYPE_MULTIPLY_FACTOR: StructureModification.ModifyStiffnessesMaterialTableRow.ModificationType
        MODIFICATION_TYPE_DIVISION_FACTOR: StructureModification.ModifyStiffnessesMaterialTableRow.ModificationType
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        MATERIAL_NAME_FIELD_NUMBER: _ClassVar[int]
        MODIFICATION_TYPE_FIELD_NUMBER: _ClassVar[int]
        E_AND_G_FIELD_NUMBER: _ClassVar[int]
        COMMENT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        material_name: int
        modification_type: StructureModification.ModifyStiffnessesMaterialTableRow.ModificationType
        E_and_G: float
        comment: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., material_name: _Optional[int] = ..., modification_type: _Optional[_Union[StructureModification.ModifyStiffnessesMaterialTableRow.ModificationType, str]] = ..., E_and_G: _Optional[float] = ..., comment: _Optional[str] = ...) -> None: ...
    class ModifyStiffnessesSectionTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[StructureModification.ModifyStiffnessesSectionTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[StructureModification.ModifyStiffnessesSectionTableRow, _Mapping]]] = ...) -> None: ...
    class ModifyStiffnessesSectionTableRow(_message.Message):
        __slots__ = ("no", "description", "section_name", "A", "A_y", "A_z", "J", "I_y", "I_z")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        SECTION_NAME_FIELD_NUMBER: _ClassVar[int]
        A_FIELD_NUMBER: _ClassVar[int]
        A_Y_FIELD_NUMBER: _ClassVar[int]
        A_Z_FIELD_NUMBER: _ClassVar[int]
        J_FIELD_NUMBER: _ClassVar[int]
        I_Y_FIELD_NUMBER: _ClassVar[int]
        I_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        section_name: str
        A: float
        A_y: float
        A_z: float
        J: float
        I_y: float
        I_z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., section_name: _Optional[str] = ..., A: _Optional[float] = ..., A_y: _Optional[float] = ..., A_z: _Optional[float] = ..., J: _Optional[float] = ..., I_y: _Optional[float] = ..., I_z: _Optional[float] = ...) -> None: ...
    class ModifyStiffnessesMemberTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[StructureModification.ModifyStiffnessesMemberTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[StructureModification.ModifyStiffnessesMemberTableRow, _Mapping]]] = ...) -> None: ...
    class ModifyStiffnessesMemberTableRow(_message.Message):
        __slots__ = ("no", "description", "member_modification", "members", "comment")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        MEMBER_MODIFICATION_FIELD_NUMBER: _ClassVar[int]
        MEMBERS_FIELD_NUMBER: _ClassVar[int]
        COMMENT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        member_modification: int
        members: _containers.RepeatedScalarFieldContainer[int]
        comment: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., member_modification: _Optional[int] = ..., members: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ...) -> None: ...
    class ModifyStiffnessesSurfaceTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[StructureModification.ModifyStiffnessesSurfaceTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[StructureModification.ModifyStiffnessesSurfaceTableRow, _Mapping]]] = ...) -> None: ...
    class ModifyStiffnessesSurfaceTableRow(_message.Message):
        __slots__ = ("no", "description", "surface_modification", "surfaces", "comment")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        SURFACE_MODIFICATION_FIELD_NUMBER: _ClassVar[int]
        SURFACES_FIELD_NUMBER: _ClassVar[int]
        COMMENT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        surface_modification: int
        surfaces: _containers.RepeatedScalarFieldContainer[int]
        comment: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., surface_modification: _Optional[int] = ..., surfaces: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ...) -> None: ...
    class ModifyStiffnessesMemberHingesTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[StructureModification.ModifyStiffnessesMemberHingesTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[StructureModification.ModifyStiffnessesMemberHingesTableRow, _Mapping]]] = ...) -> None: ...
    class ModifyStiffnessesMemberHingesTableRow(_message.Message):
        __slots__ = ("no", "description", "member_side", "C_u_x", "C_u_y", "C_u_z", "C_phi_x", "C_phi_y", "C_phi_z")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        MEMBER_SIDE_FIELD_NUMBER: _ClassVar[int]
        C_U_X_FIELD_NUMBER: _ClassVar[int]
        C_U_Y_FIELD_NUMBER: _ClassVar[int]
        C_U_Z_FIELD_NUMBER: _ClassVar[int]
        C_PHI_X_FIELD_NUMBER: _ClassVar[int]
        C_PHI_Y_FIELD_NUMBER: _ClassVar[int]
        C_PHI_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        member_side: str
        C_u_x: float
        C_u_y: float
        C_u_z: float
        C_phi_x: float
        C_phi_y: float
        C_phi_z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., member_side: _Optional[str] = ..., C_u_x: _Optional[float] = ..., C_u_y: _Optional[float] = ..., C_u_z: _Optional[float] = ..., C_phi_x: _Optional[float] = ..., C_phi_y: _Optional[float] = ..., C_phi_z: _Optional[float] = ...) -> None: ...
    class ModifyStiffnessesLineHingesTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[StructureModification.ModifyStiffnessesLineHingesTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[StructureModification.ModifyStiffnessesLineHingesTableRow, _Mapping]]] = ...) -> None: ...
    class ModifyStiffnessesLineHingesTableRow(_message.Message):
        __slots__ = ("no", "description", "C_u_x", "C_u_y", "C_u_z", "C_phi_x")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        C_U_X_FIELD_NUMBER: _ClassVar[int]
        C_U_Y_FIELD_NUMBER: _ClassVar[int]
        C_U_Z_FIELD_NUMBER: _ClassVar[int]
        C_PHI_X_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        C_u_x: float
        C_u_y: float
        C_u_z: float
        C_phi_x: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., C_u_x: _Optional[float] = ..., C_u_y: _Optional[float] = ..., C_u_z: _Optional[float] = ..., C_phi_x: _Optional[float] = ...) -> None: ...
    class ModifyStiffnessesNodalSupportsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[StructureModification.ModifyStiffnessesNodalSupportsTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[StructureModification.ModifyStiffnessesNodalSupportsTableRow, _Mapping]]] = ...) -> None: ...
    class ModifyStiffnessesNodalSupportsTableRow(_message.Message):
        __slots__ = ("no", "description", "C_u_X", "C_u_Y", "C_u_Z", "C_phi_X", "C_phi_Y", "C_phi_Z")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        C_U_X_FIELD_NUMBER: _ClassVar[int]
        C_U_Y_FIELD_NUMBER: _ClassVar[int]
        C_U_Z_FIELD_NUMBER: _ClassVar[int]
        C_PHI_X_FIELD_NUMBER: _ClassVar[int]
        C_PHI_Y_FIELD_NUMBER: _ClassVar[int]
        C_PHI_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        C_u_X: float
        C_u_Y: float
        C_u_Z: float
        C_phi_X: float
        C_phi_Y: float
        C_phi_Z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., C_u_X: _Optional[float] = ..., C_u_Y: _Optional[float] = ..., C_u_Z: _Optional[float] = ..., C_phi_X: _Optional[float] = ..., C_phi_Y: _Optional[float] = ..., C_phi_Z: _Optional[float] = ...) -> None: ...
    class ModifyStiffnessesLineSupportsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[StructureModification.ModifyStiffnessesLineSupportsTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[StructureModification.ModifyStiffnessesLineSupportsTableRow, _Mapping]]] = ...) -> None: ...
    class ModifyStiffnessesLineSupportsTableRow(_message.Message):
        __slots__ = ("no", "description", "C_u_X", "C_u_Y", "C_u_Z", "C_phi_X", "C_phi_Y", "C_phi_Z")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        C_U_X_FIELD_NUMBER: _ClassVar[int]
        C_U_Y_FIELD_NUMBER: _ClassVar[int]
        C_U_Z_FIELD_NUMBER: _ClassVar[int]
        C_PHI_X_FIELD_NUMBER: _ClassVar[int]
        C_PHI_Y_FIELD_NUMBER: _ClassVar[int]
        C_PHI_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        C_u_X: float
        C_u_Y: float
        C_u_Z: float
        C_phi_X: float
        C_phi_Y: float
        C_phi_Z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., C_u_X: _Optional[float] = ..., C_u_Y: _Optional[float] = ..., C_u_Z: _Optional[float] = ..., C_phi_X: _Optional[float] = ..., C_phi_Y: _Optional[float] = ..., C_phi_Z: _Optional[float] = ...) -> None: ...
    class ModifyStiffnessesMemberSupportsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[StructureModification.ModifyStiffnessesMemberSupportsTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[StructureModification.ModifyStiffnessesMemberSupportsTableRow, _Mapping]]] = ...) -> None: ...
    class ModifyStiffnessesMemberSupportsTableRow(_message.Message):
        __slots__ = ("no", "description", "C_u_x", "C_u_y", "C_u_z", "C_s_x", "C_s_y", "C_s_z", "C_phi_x")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        C_U_X_FIELD_NUMBER: _ClassVar[int]
        C_U_Y_FIELD_NUMBER: _ClassVar[int]
        C_U_Z_FIELD_NUMBER: _ClassVar[int]
        C_S_X_FIELD_NUMBER: _ClassVar[int]
        C_S_Y_FIELD_NUMBER: _ClassVar[int]
        C_S_Z_FIELD_NUMBER: _ClassVar[int]
        C_PHI_X_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        C_u_x: float
        C_u_y: float
        C_u_z: float
        C_s_x: float
        C_s_y: float
        C_s_z: float
        C_phi_x: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., C_u_x: _Optional[float] = ..., C_u_y: _Optional[float] = ..., C_u_z: _Optional[float] = ..., C_s_x: _Optional[float] = ..., C_s_y: _Optional[float] = ..., C_s_z: _Optional[float] = ..., C_phi_x: _Optional[float] = ...) -> None: ...
    class ModifyStiffnessesSurfaceSupportsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[StructureModification.ModifyStiffnessesSurfaceSupportsTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[StructureModification.ModifyStiffnessesSurfaceSupportsTableRow, _Mapping]]] = ...) -> None: ...
    class ModifyStiffnessesSurfaceSupportsTableRow(_message.Message):
        __slots__ = ("no", "description", "C_u_X", "C_u_Y", "C_u_Z", "C_v_xz", "C_v_yz")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        C_U_X_FIELD_NUMBER: _ClassVar[int]
        C_U_Y_FIELD_NUMBER: _ClassVar[int]
        C_U_Z_FIELD_NUMBER: _ClassVar[int]
        C_V_XZ_FIELD_NUMBER: _ClassVar[int]
        C_V_YZ_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        C_u_X: float
        C_u_Y: float
        C_u_Z: float
        C_v_xz: float
        C_v_yz: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., C_u_X: _Optional[float] = ..., C_u_Y: _Optional[float] = ..., C_u_Z: _Optional[float] = ..., C_v_xz: _Optional[float] = ..., C_v_yz: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_GAMMA_M_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MATERIALS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_SURFACES_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MEMBER_HINGES_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_LINE_HINGES_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_NODAL_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_LINE_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MEMBER_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_SURFACE_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESS_MEMBER_REINFORCEMENT_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESS_SURFACE_REINFORCEMENT_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESS_TIMBER_MEMBERS_DUE_MOISTURE_CLASS_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_MATERIAL_NONLINEARITY_MODELS_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_MATERIAL_TEMPERATURE_NONLINEARITIES_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_LINE_HINGES_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_MEMBER_TYPES_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_MEMBER_HINGES_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_MEMBER_NONLINEARITIES_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_SOLID_TYPES_CONTACT_OR_SURFACES_CONTACT_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_NODAL_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_LINE_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_MEMBER_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_SURFACE_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MATERIAL_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_SECTION_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MEMBER_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_SURFACE_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MEMBER_HINGES_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_LINE_HINGES_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_NODAL_SUPPORTS_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_LINE_SUPPORTS_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MEMBER_SUPPORTS_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_SURFACE_SUPPORTS_TABLE_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATE_MEMBERS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SELECTION_FOR_DEACTIVATE_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATE_SURFACES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SELECTION_FOR_DEACTIVATE_SURFACES_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATE_SOLIDS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SELECTION_FOR_DEACTIVATE_SOLIDS_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATE_SUPPORT_ON_NODES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SELECTION_FOR_DEACTIVATE_SUPPORT_ON_NODES_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATE_SUPPORT_ON_LINES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SELECTION_FOR_DEACTIVATE_SUPPORT_ON_LINES_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATE_SUPPORT_ON_MEMBERS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SELECTION_FOR_DEACTIVATE_SUPPORT_ON_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATE_SUPPORT_ON_SURFACES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SELECTION_FOR_DEACTIVATE_SUPPORT_ON_SURFACES_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    assigned_to: str
    comment: str
    modify_stiffnesses_gamma_m: bool
    modify_stiffnesses_materials: bool
    modify_stiffnesses_sections: bool
    modify_stiffnesses_members: bool
    modify_stiffnesses_surfaces: bool
    modify_stiffnesses_member_hinges: bool
    modify_stiffnesses_line_hinges: bool
    modify_stiffnesses_nodal_supports: bool
    modify_stiffnesses_line_supports: bool
    modify_stiffnesses_member_supports: bool
    modify_stiffnesses_surface_supports: bool
    modify_stiffness_member_reinforcement: bool
    modify_stiffness_surface_reinforcement: bool
    modify_stiffness_timber_members_due_moisture_class: bool
    nonlinearities_disabled_material_nonlinearity_models: bool
    nonlinearities_disabled_material_temperature_nonlinearities: bool
    nonlinearities_disabled_line_hinges: bool
    nonlinearities_disabled_member_types: bool
    nonlinearities_disabled_member_hinges: bool
    nonlinearities_disabled_member_nonlinearities: bool
    nonlinearities_disabled_solid_types_contact_or_surfaces_contact: bool
    nonlinearities_disabled_nodal_supports: bool
    nonlinearities_disabled_line_supports: bool
    nonlinearities_disabled_member_supports: bool
    nonlinearities_disabled_surface_supports: bool
    modify_stiffnesses_material_table: StructureModification.ModifyStiffnessesMaterialTable
    modify_stiffnesses_section_table: StructureModification.ModifyStiffnessesSectionTable
    modify_stiffnesses_member_table: StructureModification.ModifyStiffnessesMemberTable
    modify_stiffnesses_surface_table: StructureModification.ModifyStiffnessesSurfaceTable
    modify_stiffnesses_member_hinges_table: StructureModification.ModifyStiffnessesMemberHingesTable
    modify_stiffnesses_line_hinges_table: StructureModification.ModifyStiffnessesLineHingesTable
    modify_stiffnesses_nodal_supports_table: StructureModification.ModifyStiffnessesNodalSupportsTable
    modify_stiffnesses_line_supports_table: StructureModification.ModifyStiffnessesLineSupportsTable
    modify_stiffnesses_member_supports_table: StructureModification.ModifyStiffnessesMemberSupportsTable
    modify_stiffnesses_surface_supports_table: StructureModification.ModifyStiffnessesSurfaceSupportsTable
    deactivate_members_enabled: bool
    object_selection_for_deactivate_members: int
    deactivate_surfaces_enabled: bool
    object_selection_for_deactivate_surfaces: int
    deactivate_solids_enabled: bool
    object_selection_for_deactivate_solids: int
    deactivate_support_on_nodes_enabled: bool
    object_selection_for_deactivate_support_on_nodes: int
    deactivate_support_on_lines_enabled: bool
    object_selection_for_deactivate_support_on_lines: int
    deactivate_support_on_members_enabled: bool
    object_selection_for_deactivate_support_on_members: int
    deactivate_support_on_surfaces_enabled: bool
    object_selection_for_deactivate_support_on_surfaces: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., assigned_to: _Optional[str] = ..., comment: _Optional[str] = ..., modify_stiffnesses_gamma_m: bool = ..., modify_stiffnesses_materials: bool = ..., modify_stiffnesses_sections: bool = ..., modify_stiffnesses_members: bool = ..., modify_stiffnesses_surfaces: bool = ..., modify_stiffnesses_member_hinges: bool = ..., modify_stiffnesses_line_hinges: bool = ..., modify_stiffnesses_nodal_supports: bool = ..., modify_stiffnesses_line_supports: bool = ..., modify_stiffnesses_member_supports: bool = ..., modify_stiffnesses_surface_supports: bool = ..., modify_stiffness_member_reinforcement: bool = ..., modify_stiffness_surface_reinforcement: bool = ..., modify_stiffness_timber_members_due_moisture_class: bool = ..., nonlinearities_disabled_material_nonlinearity_models: bool = ..., nonlinearities_disabled_material_temperature_nonlinearities: bool = ..., nonlinearities_disabled_line_hinges: bool = ..., nonlinearities_disabled_member_types: bool = ..., nonlinearities_disabled_member_hinges: bool = ..., nonlinearities_disabled_member_nonlinearities: bool = ..., nonlinearities_disabled_solid_types_contact_or_surfaces_contact: bool = ..., nonlinearities_disabled_nodal_supports: bool = ..., nonlinearities_disabled_line_supports: bool = ..., nonlinearities_disabled_member_supports: bool = ..., nonlinearities_disabled_surface_supports: bool = ..., modify_stiffnesses_material_table: _Optional[_Union[StructureModification.ModifyStiffnessesMaterialTable, _Mapping]] = ..., modify_stiffnesses_section_table: _Optional[_Union[StructureModification.ModifyStiffnessesSectionTable, _Mapping]] = ..., modify_stiffnesses_member_table: _Optional[_Union[StructureModification.ModifyStiffnessesMemberTable, _Mapping]] = ..., modify_stiffnesses_surface_table: _Optional[_Union[StructureModification.ModifyStiffnessesSurfaceTable, _Mapping]] = ..., modify_stiffnesses_member_hinges_table: _Optional[_Union[StructureModification.ModifyStiffnessesMemberHingesTable, _Mapping]] = ..., modify_stiffnesses_line_hinges_table: _Optional[_Union[StructureModification.ModifyStiffnessesLineHingesTable, _Mapping]] = ..., modify_stiffnesses_nodal_supports_table: _Optional[_Union[StructureModification.ModifyStiffnessesNodalSupportsTable, _Mapping]] = ..., modify_stiffnesses_line_supports_table: _Optional[_Union[StructureModification.ModifyStiffnessesLineSupportsTable, _Mapping]] = ..., modify_stiffnesses_member_supports_table: _Optional[_Union[StructureModification.ModifyStiffnessesMemberSupportsTable, _Mapping]] = ..., modify_stiffnesses_surface_supports_table: _Optional[_Union[StructureModification.ModifyStiffnessesSurfaceSupportsTable, _Mapping]] = ..., deactivate_members_enabled: bool = ..., object_selection_for_deactivate_members: _Optional[int] = ..., deactivate_surfaces_enabled: bool = ..., object_selection_for_deactivate_surfaces: _Optional[int] = ..., deactivate_solids_enabled: bool = ..., object_selection_for_deactivate_solids: _Optional[int] = ..., deactivate_support_on_nodes_enabled: bool = ..., object_selection_for_deactivate_support_on_nodes: _Optional[int] = ..., deactivate_support_on_lines_enabled: bool = ..., object_selection_for_deactivate_support_on_lines: _Optional[int] = ..., deactivate_support_on_members_enabled: bool = ..., object_selection_for_deactivate_support_on_members: _Optional[int] = ..., deactivate_support_on_surfaces_enabled: bool = ..., object_selection_for_deactivate_support_on_surfaces: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
