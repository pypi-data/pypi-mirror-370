from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberShearPanel(_message.Message):
    __slots__ = ("no", "definition_type", "user_defined_name_enabled", "name", "is_generated", "generating_object_info", "comment", "define_girder_length_automatically", "girder_length", "sheeting_name", "material_name", "diagonals_section_name", "modulus_of_elasticity", "posts_section_name", "stiffness", "panel_length", "beam_spacing", "fastening_arrangement", "coefficient_k1", "coefficient_k2", "post_spacing", "number_of_bracings", "diagonals_section_area", "posts_section_area", "id_for_export_import", "metadata_for_export_import")
    class DefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFINITION_TYPE_UNKNOWN: _ClassVar[MemberShearPanel.DefinitionType]
        DEFINITION_TYPE_BRACING: _ClassVar[MemberShearPanel.DefinitionType]
        DEFINITION_TYPE_DEFINE_S_PROV: _ClassVar[MemberShearPanel.DefinitionType]
        DEFINITION_TYPE_TRAPEZOIDAL_SHEETING: _ClassVar[MemberShearPanel.DefinitionType]
        DEFINITION_TYPE_TRAPEZOIDAL_SHEETING_AND_BRACING: _ClassVar[MemberShearPanel.DefinitionType]
    DEFINITION_TYPE_UNKNOWN: MemberShearPanel.DefinitionType
    DEFINITION_TYPE_BRACING: MemberShearPanel.DefinitionType
    DEFINITION_TYPE_DEFINE_S_PROV: MemberShearPanel.DefinitionType
    DEFINITION_TYPE_TRAPEZOIDAL_SHEETING: MemberShearPanel.DefinitionType
    DEFINITION_TYPE_TRAPEZOIDAL_SHEETING_AND_BRACING: MemberShearPanel.DefinitionType
    class FasteningArrangement(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FASTENING_ARRANGEMENT_EVERY_RIB: _ClassVar[MemberShearPanel.FasteningArrangement]
        FASTENING_ARRANGEMENT_EVERY_SECOND_RIB: _ClassVar[MemberShearPanel.FasteningArrangement]
    FASTENING_ARRANGEMENT_EVERY_RIB: MemberShearPanel.FasteningArrangement
    FASTENING_ARRANGEMENT_EVERY_SECOND_RIB: MemberShearPanel.FasteningArrangement
    NO_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    DEFINE_GIRDER_LENGTH_AUTOMATICALLY_FIELD_NUMBER: _ClassVar[int]
    GIRDER_LENGTH_FIELD_NUMBER: _ClassVar[int]
    SHEETING_NAME_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_NAME_FIELD_NUMBER: _ClassVar[int]
    DIAGONALS_SECTION_NAME_FIELD_NUMBER: _ClassVar[int]
    MODULUS_OF_ELASTICITY_FIELD_NUMBER: _ClassVar[int]
    POSTS_SECTION_NAME_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    PANEL_LENGTH_FIELD_NUMBER: _ClassVar[int]
    BEAM_SPACING_FIELD_NUMBER: _ClassVar[int]
    FASTENING_ARRANGEMENT_FIELD_NUMBER: _ClassVar[int]
    COEFFICIENT_K1_FIELD_NUMBER: _ClassVar[int]
    COEFFICIENT_K2_FIELD_NUMBER: _ClassVar[int]
    POST_SPACING_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_BRACINGS_FIELD_NUMBER: _ClassVar[int]
    DIAGONALS_SECTION_AREA_FIELD_NUMBER: _ClassVar[int]
    POSTS_SECTION_AREA_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    definition_type: MemberShearPanel.DefinitionType
    user_defined_name_enabled: bool
    name: str
    is_generated: bool
    generating_object_info: str
    comment: str
    define_girder_length_automatically: bool
    girder_length: float
    sheeting_name: str
    material_name: str
    diagonals_section_name: str
    modulus_of_elasticity: float
    posts_section_name: str
    stiffness: float
    panel_length: float
    beam_spacing: float
    fastening_arrangement: MemberShearPanel.FasteningArrangement
    coefficient_k1: float
    coefficient_k2: float
    post_spacing: float
    number_of_bracings: int
    diagonals_section_area: float
    posts_section_area: float
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., definition_type: _Optional[_Union[MemberShearPanel.DefinitionType, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., comment: _Optional[str] = ..., define_girder_length_automatically: bool = ..., girder_length: _Optional[float] = ..., sheeting_name: _Optional[str] = ..., material_name: _Optional[str] = ..., diagonals_section_name: _Optional[str] = ..., modulus_of_elasticity: _Optional[float] = ..., posts_section_name: _Optional[str] = ..., stiffness: _Optional[float] = ..., panel_length: _Optional[float] = ..., beam_spacing: _Optional[float] = ..., fastening_arrangement: _Optional[_Union[MemberShearPanel.FasteningArrangement, str]] = ..., coefficient_k1: _Optional[float] = ..., coefficient_k2: _Optional[float] = ..., post_spacing: _Optional[float] = ..., number_of_bracings: _Optional[int] = ..., diagonals_section_area: _Optional[float] = ..., posts_section_area: _Optional[float] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
