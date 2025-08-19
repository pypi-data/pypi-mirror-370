from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberStiffnessModification(_message.Message):
    __slots__ = ("no", "type", "user_defined_name_enabled", "name", "factor_of_axial_stiffness", "factor_of_bending_y_stiffness", "factor_of_bending_z_stiffness", "partial_stiffness_factor_of_shear_y_stiffness", "partial_stiffness_factor_of_shear_z_stiffness", "partial_stiffness_factor_of_torsion_stiffness", "partial_stiffness_factor_of_weight", "total_stiffness_factor_of_total_stiffness", "steel_structure_csa_stiffness_factor_of_shear_y_stiffness", "steel_structure_csa_stiffness_factor_of_shear_z_stiffness", "steel_structure_csa_stiffness_factor_of_torsion_stiffness", "steel_structure_csa_factor_of_axial_stiffness_enable", "steel_structure_csa_factor_of_bending_y_stiffness_enable", "steel_structure_csa_factor_of_bending_z_stiffness_enable", "steel_structure_csa_factor_of_shear_y_stiffness_enable", "steel_structure_csa_factor_of_shear_z_stiffness_enable", "steel_structure_csa_stiffness_factor_of_torsion_stiffness_enable", "steel_structure_csa_determine_tau_b", "steel_structure_gb_direct_method_enabled", "structure_determine_tau_b", "structure_design_method", "concrete_structure_component_type", "assigned_to_structure_modification", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[MemberStiffnessModification.Type]
        TYPE_ALUMINUM_STRUCTURES_ADM_2020: _ClassVar[MemberStiffnessModification.Type]
        TYPE_ALUMINUM_STRUCTURES_CSA_S157_17: _ClassVar[MemberStiffnessModification.Type]
        TYPE_CONCRETE_STRUCTURES_ACI: _ClassVar[MemberStiffnessModification.Type]
        TYPE_CONCRETE_STRUCTURES_CSA: _ClassVar[MemberStiffnessModification.Type]
        TYPE_PARTIAL_STIFFNESSES_FACTORS: _ClassVar[MemberStiffnessModification.Type]
        TYPE_STEEL_STRUCTURES_AISC_360_10: _ClassVar[MemberStiffnessModification.Type]
        TYPE_STEEL_STRUCTURES_AISC_360_16: _ClassVar[MemberStiffnessModification.Type]
        TYPE_STEEL_STRUCTURES_AISC_360_22: _ClassVar[MemberStiffnessModification.Type]
        TYPE_STEEL_STRUCTURES_AISI_S100_16: _ClassVar[MemberStiffnessModification.Type]
        TYPE_STEEL_STRUCTURES_CSA_S136_16: _ClassVar[MemberStiffnessModification.Type]
        TYPE_STEEL_STRUCTURES_CSA_S16_19: _ClassVar[MemberStiffnessModification.Type]
        TYPE_TOTAL_STIFFNESSES_FACTORS: _ClassVar[MemberStiffnessModification.Type]
    TYPE_UNKNOWN: MemberStiffnessModification.Type
    TYPE_ALUMINUM_STRUCTURES_ADM_2020: MemberStiffnessModification.Type
    TYPE_ALUMINUM_STRUCTURES_CSA_S157_17: MemberStiffnessModification.Type
    TYPE_CONCRETE_STRUCTURES_ACI: MemberStiffnessModification.Type
    TYPE_CONCRETE_STRUCTURES_CSA: MemberStiffnessModification.Type
    TYPE_PARTIAL_STIFFNESSES_FACTORS: MemberStiffnessModification.Type
    TYPE_STEEL_STRUCTURES_AISC_360_10: MemberStiffnessModification.Type
    TYPE_STEEL_STRUCTURES_AISC_360_16: MemberStiffnessModification.Type
    TYPE_STEEL_STRUCTURES_AISC_360_22: MemberStiffnessModification.Type
    TYPE_STEEL_STRUCTURES_AISI_S100_16: MemberStiffnessModification.Type
    TYPE_STEEL_STRUCTURES_CSA_S136_16: MemberStiffnessModification.Type
    TYPE_STEEL_STRUCTURES_CSA_S16_19: MemberStiffnessModification.Type
    TYPE_TOTAL_STIFFNESSES_FACTORS: MemberStiffnessModification.Type
    class SteelStructureCsaDetermineTauB(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STEEL_STRUCTURE_CSA_DETERMINE_TAU_B_ITERATIVE: _ClassVar[MemberStiffnessModification.SteelStructureCsaDetermineTauB]
        STEEL_STRUCTURE_CSA_DETERMINE_TAU_B_SET_TO_1: _ClassVar[MemberStiffnessModification.SteelStructureCsaDetermineTauB]
    STEEL_STRUCTURE_CSA_DETERMINE_TAU_B_ITERATIVE: MemberStiffnessModification.SteelStructureCsaDetermineTauB
    STEEL_STRUCTURE_CSA_DETERMINE_TAU_B_SET_TO_1: MemberStiffnessModification.SteelStructureCsaDetermineTauB
    class StructureDetermineTauB(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STRUCTURE_DETERMINE_TAU_B_ITERATIVE: _ClassVar[MemberStiffnessModification.StructureDetermineTauB]
        STRUCTURE_DETERMINE_TAU_B_SET_TO_1: _ClassVar[MemberStiffnessModification.StructureDetermineTauB]
    STRUCTURE_DETERMINE_TAU_B_ITERATIVE: MemberStiffnessModification.StructureDetermineTauB
    STRUCTURE_DETERMINE_TAU_B_SET_TO_1: MemberStiffnessModification.StructureDetermineTauB
    class StructureDesignMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STRUCTURE_DESIGN_METHOD_LRFD: _ClassVar[MemberStiffnessModification.StructureDesignMethod]
        STRUCTURE_DESIGN_METHOD_ASD: _ClassVar[MemberStiffnessModification.StructureDesignMethod]
    STRUCTURE_DESIGN_METHOD_LRFD: MemberStiffnessModification.StructureDesignMethod
    STRUCTURE_DESIGN_METHOD_ASD: MemberStiffnessModification.StructureDesignMethod
    class ConcreteStructureComponentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CONCRETE_STRUCTURE_COMPONENT_TYPE_COLUMNS: _ClassVar[MemberStiffnessModification.ConcreteStructureComponentType]
        CONCRETE_STRUCTURE_COMPONENT_TYPE_BEAMS: _ClassVar[MemberStiffnessModification.ConcreteStructureComponentType]
    CONCRETE_STRUCTURE_COMPONENT_TYPE_COLUMNS: MemberStiffnessModification.ConcreteStructureComponentType
    CONCRETE_STRUCTURE_COMPONENT_TYPE_BEAMS: MemberStiffnessModification.ConcreteStructureComponentType
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FACTOR_OF_AXIAL_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    FACTOR_OF_BENDING_Y_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    FACTOR_OF_BENDING_Z_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_STIFFNESS_FACTOR_OF_SHEAR_Y_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_STIFFNESS_FACTOR_OF_SHEAR_Z_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_STIFFNESS_FACTOR_OF_TORSION_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_STIFFNESS_FACTOR_OF_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_STIFFNESS_FACTOR_OF_TOTAL_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    STEEL_STRUCTURE_CSA_STIFFNESS_FACTOR_OF_SHEAR_Y_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    STEEL_STRUCTURE_CSA_STIFFNESS_FACTOR_OF_SHEAR_Z_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    STEEL_STRUCTURE_CSA_STIFFNESS_FACTOR_OF_TORSION_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    STEEL_STRUCTURE_CSA_FACTOR_OF_AXIAL_STIFFNESS_ENABLE_FIELD_NUMBER: _ClassVar[int]
    STEEL_STRUCTURE_CSA_FACTOR_OF_BENDING_Y_STIFFNESS_ENABLE_FIELD_NUMBER: _ClassVar[int]
    STEEL_STRUCTURE_CSA_FACTOR_OF_BENDING_Z_STIFFNESS_ENABLE_FIELD_NUMBER: _ClassVar[int]
    STEEL_STRUCTURE_CSA_FACTOR_OF_SHEAR_Y_STIFFNESS_ENABLE_FIELD_NUMBER: _ClassVar[int]
    STEEL_STRUCTURE_CSA_FACTOR_OF_SHEAR_Z_STIFFNESS_ENABLE_FIELD_NUMBER: _ClassVar[int]
    STEEL_STRUCTURE_CSA_STIFFNESS_FACTOR_OF_TORSION_STIFFNESS_ENABLE_FIELD_NUMBER: _ClassVar[int]
    STEEL_STRUCTURE_CSA_DETERMINE_TAU_B_FIELD_NUMBER: _ClassVar[int]
    STEEL_STRUCTURE_GB_DIRECT_METHOD_ENABLED_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_DETERMINE_TAU_B_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_DESIGN_METHOD_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_STRUCTURE_COMPONENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_STRUCTURE_MODIFICATION_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: MemberStiffnessModification.Type
    user_defined_name_enabled: bool
    name: str
    factor_of_axial_stiffness: float
    factor_of_bending_y_stiffness: float
    factor_of_bending_z_stiffness: float
    partial_stiffness_factor_of_shear_y_stiffness: float
    partial_stiffness_factor_of_shear_z_stiffness: float
    partial_stiffness_factor_of_torsion_stiffness: float
    partial_stiffness_factor_of_weight: float
    total_stiffness_factor_of_total_stiffness: float
    steel_structure_csa_stiffness_factor_of_shear_y_stiffness: float
    steel_structure_csa_stiffness_factor_of_shear_z_stiffness: float
    steel_structure_csa_stiffness_factor_of_torsion_stiffness: float
    steel_structure_csa_factor_of_axial_stiffness_enable: bool
    steel_structure_csa_factor_of_bending_y_stiffness_enable: bool
    steel_structure_csa_factor_of_bending_z_stiffness_enable: bool
    steel_structure_csa_factor_of_shear_y_stiffness_enable: bool
    steel_structure_csa_factor_of_shear_z_stiffness_enable: bool
    steel_structure_csa_stiffness_factor_of_torsion_stiffness_enable: bool
    steel_structure_csa_determine_tau_b: MemberStiffnessModification.SteelStructureCsaDetermineTauB
    steel_structure_gb_direct_method_enabled: bool
    structure_determine_tau_b: MemberStiffnessModification.StructureDetermineTauB
    structure_design_method: MemberStiffnessModification.StructureDesignMethod
    concrete_structure_component_type: MemberStiffnessModification.ConcreteStructureComponentType
    assigned_to_structure_modification: _containers.RepeatedScalarFieldContainer[int]
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[MemberStiffnessModification.Type, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., factor_of_axial_stiffness: _Optional[float] = ..., factor_of_bending_y_stiffness: _Optional[float] = ..., factor_of_bending_z_stiffness: _Optional[float] = ..., partial_stiffness_factor_of_shear_y_stiffness: _Optional[float] = ..., partial_stiffness_factor_of_shear_z_stiffness: _Optional[float] = ..., partial_stiffness_factor_of_torsion_stiffness: _Optional[float] = ..., partial_stiffness_factor_of_weight: _Optional[float] = ..., total_stiffness_factor_of_total_stiffness: _Optional[float] = ..., steel_structure_csa_stiffness_factor_of_shear_y_stiffness: _Optional[float] = ..., steel_structure_csa_stiffness_factor_of_shear_z_stiffness: _Optional[float] = ..., steel_structure_csa_stiffness_factor_of_torsion_stiffness: _Optional[float] = ..., steel_structure_csa_factor_of_axial_stiffness_enable: bool = ..., steel_structure_csa_factor_of_bending_y_stiffness_enable: bool = ..., steel_structure_csa_factor_of_bending_z_stiffness_enable: bool = ..., steel_structure_csa_factor_of_shear_y_stiffness_enable: bool = ..., steel_structure_csa_factor_of_shear_z_stiffness_enable: bool = ..., steel_structure_csa_stiffness_factor_of_torsion_stiffness_enable: bool = ..., steel_structure_csa_determine_tau_b: _Optional[_Union[MemberStiffnessModification.SteelStructureCsaDetermineTauB, str]] = ..., steel_structure_gb_direct_method_enabled: bool = ..., structure_determine_tau_b: _Optional[_Union[MemberStiffnessModification.StructureDetermineTauB, str]] = ..., structure_design_method: _Optional[_Union[MemberStiffnessModification.StructureDesignMethod, str]] = ..., concrete_structure_component_type: _Optional[_Union[MemberStiffnessModification.ConcreteStructureComponentType, str]] = ..., assigned_to_structure_modification: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
