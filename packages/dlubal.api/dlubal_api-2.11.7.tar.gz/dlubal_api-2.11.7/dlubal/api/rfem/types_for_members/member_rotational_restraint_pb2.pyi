from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberRotationalRestraint(_message.Message):
    __slots__ = ("no", "type", "user_defined_name_enabled", "name", "comment", "is_generated", "generating_object_info", "material_name", "modulus_of_elasticity", "continuous_beam_effect", "section_deformation_cdb", "beam_spacing", "sheeting_name", "position_of_sheeting", "sheeting_thickness", "sheeting_moment_of_inertia", "sheeting_distance_of_ribs", "width_of_section_flange", "spring_stiffness", "different_spring_stiffness", "different_spring_stiffness_list", "method_of_determining_cda", "section_name", "rotational_stiffness", "rotational_stiffness_value", "section_moment_of_inertia", "purlin_spacing", "total_rotational_spring_stiffness", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[MemberRotationalRestraint.Type]
        TYPE_CONTINUOUS: _ClassVar[MemberRotationalRestraint.Type]
        TYPE_DISCRETE: _ClassVar[MemberRotationalRestraint.Type]
        TYPE_MANUALLY: _ClassVar[MemberRotationalRestraint.Type]
    TYPE_UNKNOWN: MemberRotationalRestraint.Type
    TYPE_CONTINUOUS: MemberRotationalRestraint.Type
    TYPE_DISCRETE: MemberRotationalRestraint.Type
    TYPE_MANUALLY: MemberRotationalRestraint.Type
    class ContinuousBeamEffect(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CONTINUOUS_BEAM_EFFECT_END_PANEL: _ClassVar[MemberRotationalRestraint.ContinuousBeamEffect]
        CONTINUOUS_BEAM_EFFECT_INTERNAL_PANEL: _ClassVar[MemberRotationalRestraint.ContinuousBeamEffect]
    CONTINUOUS_BEAM_EFFECT_END_PANEL: MemberRotationalRestraint.ContinuousBeamEffect
    CONTINUOUS_BEAM_EFFECT_INTERNAL_PANEL: MemberRotationalRestraint.ContinuousBeamEffect
    class PositionOfSheeting(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        POSITION_OF_SHEETING_POSITIVE: _ClassVar[MemberRotationalRestraint.PositionOfSheeting]
        POSITION_OF_SHEETING_NEGATIVE: _ClassVar[MemberRotationalRestraint.PositionOfSheeting]
    POSITION_OF_SHEETING_POSITIVE: MemberRotationalRestraint.PositionOfSheeting
    POSITION_OF_SHEETING_NEGATIVE: MemberRotationalRestraint.PositionOfSheeting
    class MethodOfDeterminingCda(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        METHOD_OF_DETERMINING_CDA_EN_1993_1_3_TABLE_10_3: _ClassVar[MemberRotationalRestraint.MethodOfDeterminingCda]
    METHOD_OF_DETERMINING_CDA_EN_1993_1_3_TABLE_10_3: MemberRotationalRestraint.MethodOfDeterminingCda
    class RotationalStiffness(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROTATIONAL_STIFFNESS_INFINITELY: _ClassVar[MemberRotationalRestraint.RotationalStiffness]
        ROTATIONAL_STIFFNESS_MANUALLY: _ClassVar[MemberRotationalRestraint.RotationalStiffness]
    ROTATIONAL_STIFFNESS_INFINITELY: MemberRotationalRestraint.RotationalStiffness
    ROTATIONAL_STIFFNESS_MANUALLY: MemberRotationalRestraint.RotationalStiffness
    class DifferentSpringStiffnessListTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberRotationalRestraint.DifferentSpringStiffnessListRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberRotationalRestraint.DifferentSpringStiffnessListRow, _Mapping]]] = ...) -> None: ...
    class DifferentSpringStiffnessListRow(_message.Message):
        __slots__ = ("no", "description", "loading", "is_different", "c100_value", "a_value")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        LOADING_FIELD_NUMBER: _ClassVar[int]
        IS_DIFFERENT_FIELD_NUMBER: _ClassVar[int]
        C100_VALUE_FIELD_NUMBER: _ClassVar[int]
        A_VALUE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        loading: int
        is_different: bool
        c100_value: float
        a_value: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., loading: _Optional[int] = ..., is_different: bool = ..., c100_value: _Optional[float] = ..., a_value: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_NAME_FIELD_NUMBER: _ClassVar[int]
    MODULUS_OF_ELASTICITY_FIELD_NUMBER: _ClassVar[int]
    CONTINUOUS_BEAM_EFFECT_FIELD_NUMBER: _ClassVar[int]
    SECTION_DEFORMATION_CDB_FIELD_NUMBER: _ClassVar[int]
    BEAM_SPACING_FIELD_NUMBER: _ClassVar[int]
    SHEETING_NAME_FIELD_NUMBER: _ClassVar[int]
    POSITION_OF_SHEETING_FIELD_NUMBER: _ClassVar[int]
    SHEETING_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    SHEETING_MOMENT_OF_INERTIA_FIELD_NUMBER: _ClassVar[int]
    SHEETING_DISTANCE_OF_RIBS_FIELD_NUMBER: _ClassVar[int]
    WIDTH_OF_SECTION_FLANGE_FIELD_NUMBER: _ClassVar[int]
    SPRING_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    DIFFERENT_SPRING_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    DIFFERENT_SPRING_STIFFNESS_LIST_FIELD_NUMBER: _ClassVar[int]
    METHOD_OF_DETERMINING_CDA_FIELD_NUMBER: _ClassVar[int]
    SECTION_NAME_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_STIFFNESS_VALUE_FIELD_NUMBER: _ClassVar[int]
    SECTION_MOMENT_OF_INERTIA_FIELD_NUMBER: _ClassVar[int]
    PURLIN_SPACING_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ROTATIONAL_SPRING_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: MemberRotationalRestraint.Type
    user_defined_name_enabled: bool
    name: str
    comment: str
    is_generated: bool
    generating_object_info: str
    material_name: str
    modulus_of_elasticity: float
    continuous_beam_effect: MemberRotationalRestraint.ContinuousBeamEffect
    section_deformation_cdb: bool
    beam_spacing: float
    sheeting_name: str
    position_of_sheeting: MemberRotationalRestraint.PositionOfSheeting
    sheeting_thickness: float
    sheeting_moment_of_inertia: float
    sheeting_distance_of_ribs: float
    width_of_section_flange: float
    spring_stiffness: float
    different_spring_stiffness: bool
    different_spring_stiffness_list: MemberRotationalRestraint.DifferentSpringStiffnessListTable
    method_of_determining_cda: MemberRotationalRestraint.MethodOfDeterminingCda
    section_name: str
    rotational_stiffness: MemberRotationalRestraint.RotationalStiffness
    rotational_stiffness_value: float
    section_moment_of_inertia: float
    purlin_spacing: float
    total_rotational_spring_stiffness: float
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[MemberRotationalRestraint.Type, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., material_name: _Optional[str] = ..., modulus_of_elasticity: _Optional[float] = ..., continuous_beam_effect: _Optional[_Union[MemberRotationalRestraint.ContinuousBeamEffect, str]] = ..., section_deformation_cdb: bool = ..., beam_spacing: _Optional[float] = ..., sheeting_name: _Optional[str] = ..., position_of_sheeting: _Optional[_Union[MemberRotationalRestraint.PositionOfSheeting, str]] = ..., sheeting_thickness: _Optional[float] = ..., sheeting_moment_of_inertia: _Optional[float] = ..., sheeting_distance_of_ribs: _Optional[float] = ..., width_of_section_flange: _Optional[float] = ..., spring_stiffness: _Optional[float] = ..., different_spring_stiffness: bool = ..., different_spring_stiffness_list: _Optional[_Union[MemberRotationalRestraint.DifferentSpringStiffnessListTable, _Mapping]] = ..., method_of_determining_cda: _Optional[_Union[MemberRotationalRestraint.MethodOfDeterminingCda, str]] = ..., section_name: _Optional[str] = ..., rotational_stiffness: _Optional[_Union[MemberRotationalRestraint.RotationalStiffness, str]] = ..., rotational_stiffness_value: _Optional[float] = ..., section_moment_of_inertia: _Optional[float] = ..., purlin_spacing: _Optional[float] = ..., total_rotational_spring_stiffness: _Optional[float] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
