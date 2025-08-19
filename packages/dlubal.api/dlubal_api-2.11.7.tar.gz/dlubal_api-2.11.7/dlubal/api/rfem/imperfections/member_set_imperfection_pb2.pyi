from dlubal.api.common import common_pb2 as _common_pb2
from dlubal.api.rfem import object_id_pb2 as _object_id_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberSetImperfection(_message.Message):
    __slots__ = ("no", "imperfection_type", "member_sets", "imperfection_case", "definition_type", "coordinate_system", "imperfection_direction", "basic_value_absolute", "basic_value_relative", "basic_value_coefficient", "basic_value_force", "section_design", "active_criterion", "active_bow", "column_in_row", "number_of_floors", "standard_factor_enumeration", "standard_factor_number", "height", "case_object", "reduction_factor_h", "reduction_factor_h_limit", "reduction_factor_m", "initial_sway", "initial_sway_inverted", "delta", "parameters", "refer_distance_from_objects_to_assign", "imperfection_over_total_length_of_objects_to_assign", "distance_a_is_defined_as_relative", "distance_b_is_defined_as_relative", "distance_a_relative", "distance_b_relative", "distance_a_absolute", "distance_b_absolute", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class ImperfectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        IMPERFECTION_TYPE_UNKNOWN: _ClassVar[MemberSetImperfection.ImperfectionType]
        IMPERFECTION_TYPE_INITIAL_BOW: _ClassVar[MemberSetImperfection.ImperfectionType]
        IMPERFECTION_TYPE_INITIAL_BOW_AND_CRITERION: _ClassVar[MemberSetImperfection.ImperfectionType]
        IMPERFECTION_TYPE_INITIAL_SWAY: _ClassVar[MemberSetImperfection.ImperfectionType]
    IMPERFECTION_TYPE_UNKNOWN: MemberSetImperfection.ImperfectionType
    IMPERFECTION_TYPE_INITIAL_BOW: MemberSetImperfection.ImperfectionType
    IMPERFECTION_TYPE_INITIAL_BOW_AND_CRITERION: MemberSetImperfection.ImperfectionType
    IMPERFECTION_TYPE_INITIAL_SWAY: MemberSetImperfection.ImperfectionType
    class DefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFINITION_TYPE_RELATIVE: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_ABSOLUTE: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_AISI_S100_16_CURRENT: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_AISI_S100_16_GRAVITY_LOAD: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_ANSI_CURRENT: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_ANSI_GRAVITY_LOAD: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_CSA_136_16_CURRENT: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_CSA_136_16_GRAVITY_LOAD: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_CSA_CURRENT: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_CSA_GRAVITY_LOAD: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_EN_1992_1: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_EN_1993_1: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_EN_1995_1: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_EN_1999_1: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_GB_50017_2017: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_GB_50017_2017_CURRENT: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_GB_50017_2017_GRAVITY_LOAD: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_GB_50429_2007_GRAVITY_LOAD: _ClassVar[MemberSetImperfection.DefinitionType]
        DEFINITION_TYPE_NOTIONAL_LOAD: _ClassVar[MemberSetImperfection.DefinitionType]
    DEFINITION_TYPE_RELATIVE: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_ABSOLUTE: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_AISI_S100_16_CURRENT: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_AISI_S100_16_GRAVITY_LOAD: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_ANSI_CURRENT: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_ANSI_GRAVITY_LOAD: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_CSA_136_16_CURRENT: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_CSA_136_16_GRAVITY_LOAD: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_CSA_CURRENT: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_CSA_GRAVITY_LOAD: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_EN_1992_1: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_EN_1993_1: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_EN_1995_1: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_EN_1999_1: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_GB_50017_2017: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_GB_50017_2017_CURRENT: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_GB_50017_2017_GRAVITY_LOAD: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_GB_50429_2007_GRAVITY_LOAD: MemberSetImperfection.DefinitionType
    DEFINITION_TYPE_NOTIONAL_LOAD: MemberSetImperfection.DefinitionType
    class ImperfectionDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        IMPERFECTION_DIRECTION_UNKNOWN: _ClassVar[MemberSetImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: _ClassVar[MemberSetImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH_REVERSED: _ClassVar[MemberSetImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: _ClassVar[MemberSetImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH_REVERSED: _ClassVar[MemberSetImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: _ClassVar[MemberSetImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH_REVERSED: _ClassVar[MemberSetImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_LOCAL_Y: _ClassVar[MemberSetImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_LOCAL_Y_NEGATIVE: _ClassVar[MemberSetImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_LOCAL_Z: _ClassVar[MemberSetImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_LOCAL_Z_NEGATIVE: _ClassVar[MemberSetImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_PRINCIPAL_U: _ClassVar[MemberSetImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_PRINCIPAL_U_NEGATIVE: _ClassVar[MemberSetImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_PRINCIPAL_V: _ClassVar[MemberSetImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_PRINCIPAL_V_NEGATIVE: _ClassVar[MemberSetImperfection.ImperfectionDirection]
    IMPERFECTION_DIRECTION_UNKNOWN: MemberSetImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: MemberSetImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH_REVERSED: MemberSetImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: MemberSetImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH_REVERSED: MemberSetImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: MemberSetImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH_REVERSED: MemberSetImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_LOCAL_Y: MemberSetImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_LOCAL_Y_NEGATIVE: MemberSetImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_LOCAL_Z: MemberSetImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_LOCAL_Z_NEGATIVE: MemberSetImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_PRINCIPAL_U: MemberSetImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_PRINCIPAL_U_NEGATIVE: MemberSetImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_PRINCIPAL_V: MemberSetImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_PRINCIPAL_V_NEGATIVE: MemberSetImperfection.ImperfectionDirection
    class SectionDesign(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SECTION_DESIGN_ELASTIC: _ClassVar[MemberSetImperfection.SectionDesign]
        SECTION_DESIGN_PLASTIC: _ClassVar[MemberSetImperfection.SectionDesign]
    SECTION_DESIGN_ELASTIC: MemberSetImperfection.SectionDesign
    SECTION_DESIGN_PLASTIC: MemberSetImperfection.SectionDesign
    class ActiveCriterion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ACTIVE_CRITERION_ALWAYS: _ClassVar[MemberSetImperfection.ActiveCriterion]
        ACTIVE_CRITERION_DEFINE: _ClassVar[MemberSetImperfection.ActiveCriterion]
        ACTIVE_CRITERION_DIN_18800: _ClassVar[MemberSetImperfection.ActiveCriterion]
        ACTIVE_CRITERION_EN_1993: _ClassVar[MemberSetImperfection.ActiveCriterion]
        ACTIVE_CRITERION_EN_1999: _ClassVar[MemberSetImperfection.ActiveCriterion]
    ACTIVE_CRITERION_ALWAYS: MemberSetImperfection.ActiveCriterion
    ACTIVE_CRITERION_DEFINE: MemberSetImperfection.ActiveCriterion
    ACTIVE_CRITERION_DIN_18800: MemberSetImperfection.ActiveCriterion
    ACTIVE_CRITERION_EN_1993: MemberSetImperfection.ActiveCriterion
    ACTIVE_CRITERION_EN_1999: MemberSetImperfection.ActiveCriterion
    class StandardFactorEnumeration(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STANDARD_FACTOR_ENUMERATION_LRFD: _ClassVar[MemberSetImperfection.StandardFactorEnumeration]
        STANDARD_FACTOR_ENUMERATION_ASD: _ClassVar[MemberSetImperfection.StandardFactorEnumeration]
    STANDARD_FACTOR_ENUMERATION_LRFD: MemberSetImperfection.StandardFactorEnumeration
    STANDARD_FACTOR_ENUMERATION_ASD: MemberSetImperfection.StandardFactorEnumeration
    NO_FIELD_NUMBER: _ClassVar[int]
    IMPERFECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    IMPERFECTION_CASE_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    IMPERFECTION_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    BASIC_VALUE_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    BASIC_VALUE_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    BASIC_VALUE_COEFFICIENT_FIELD_NUMBER: _ClassVar[int]
    BASIC_VALUE_FORCE_FIELD_NUMBER: _ClassVar[int]
    SECTION_DESIGN_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_CRITERION_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_BOW_FIELD_NUMBER: _ClassVar[int]
    COLUMN_IN_ROW_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_FLOORS_FIELD_NUMBER: _ClassVar[int]
    STANDARD_FACTOR_ENUMERATION_FIELD_NUMBER: _ClassVar[int]
    STANDARD_FACTOR_NUMBER_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    CASE_OBJECT_FIELD_NUMBER: _ClassVar[int]
    REDUCTION_FACTOR_H_FIELD_NUMBER: _ClassVar[int]
    REDUCTION_FACTOR_H_LIMIT_FIELD_NUMBER: _ClassVar[int]
    REDUCTION_FACTOR_M_FIELD_NUMBER: _ClassVar[int]
    INITIAL_SWAY_FIELD_NUMBER: _ClassVar[int]
    INITIAL_SWAY_INVERTED_FIELD_NUMBER: _ClassVar[int]
    DELTA_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    REFER_DISTANCE_FROM_OBJECTS_TO_ASSIGN_FIELD_NUMBER: _ClassVar[int]
    IMPERFECTION_OVER_TOTAL_LENGTH_OF_OBJECTS_TO_ASSIGN_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_A_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_B_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_A_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_B_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_A_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_B_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    imperfection_type: MemberSetImperfection.ImperfectionType
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    imperfection_case: int
    definition_type: MemberSetImperfection.DefinitionType
    coordinate_system: _common_pb2.CoordinateSystemRepresentation
    imperfection_direction: MemberSetImperfection.ImperfectionDirection
    basic_value_absolute: float
    basic_value_relative: float
    basic_value_coefficient: float
    basic_value_force: float
    section_design: MemberSetImperfection.SectionDesign
    active_criterion: MemberSetImperfection.ActiveCriterion
    active_bow: float
    column_in_row: int
    number_of_floors: int
    standard_factor_enumeration: MemberSetImperfection.StandardFactorEnumeration
    standard_factor_number: float
    height: float
    case_object: _object_id_pb2.ObjectId
    reduction_factor_h: float
    reduction_factor_h_limit: bool
    reduction_factor_m: float
    initial_sway: float
    initial_sway_inverted: float
    delta: float
    parameters: _containers.RepeatedScalarFieldContainer[int]
    refer_distance_from_objects_to_assign: bool
    imperfection_over_total_length_of_objects_to_assign: bool
    distance_a_is_defined_as_relative: bool
    distance_b_is_defined_as_relative: bool
    distance_a_relative: float
    distance_b_relative: float
    distance_a_absolute: float
    distance_b_absolute: float
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., imperfection_type: _Optional[_Union[MemberSetImperfection.ImperfectionType, str]] = ..., member_sets: _Optional[_Iterable[int]] = ..., imperfection_case: _Optional[int] = ..., definition_type: _Optional[_Union[MemberSetImperfection.DefinitionType, str]] = ..., coordinate_system: _Optional[_Union[_common_pb2.CoordinateSystemRepresentation, _Mapping]] = ..., imperfection_direction: _Optional[_Union[MemberSetImperfection.ImperfectionDirection, str]] = ..., basic_value_absolute: _Optional[float] = ..., basic_value_relative: _Optional[float] = ..., basic_value_coefficient: _Optional[float] = ..., basic_value_force: _Optional[float] = ..., section_design: _Optional[_Union[MemberSetImperfection.SectionDesign, str]] = ..., active_criterion: _Optional[_Union[MemberSetImperfection.ActiveCriterion, str]] = ..., active_bow: _Optional[float] = ..., column_in_row: _Optional[int] = ..., number_of_floors: _Optional[int] = ..., standard_factor_enumeration: _Optional[_Union[MemberSetImperfection.StandardFactorEnumeration, str]] = ..., standard_factor_number: _Optional[float] = ..., height: _Optional[float] = ..., case_object: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., reduction_factor_h: _Optional[float] = ..., reduction_factor_h_limit: bool = ..., reduction_factor_m: _Optional[float] = ..., initial_sway: _Optional[float] = ..., initial_sway_inverted: _Optional[float] = ..., delta: _Optional[float] = ..., parameters: _Optional[_Iterable[int]] = ..., refer_distance_from_objects_to_assign: bool = ..., imperfection_over_total_length_of_objects_to_assign: bool = ..., distance_a_is_defined_as_relative: bool = ..., distance_b_is_defined_as_relative: bool = ..., distance_a_relative: _Optional[float] = ..., distance_b_relative: _Optional[float] = ..., distance_a_absolute: _Optional[float] = ..., distance_b_absolute: _Optional[float] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
