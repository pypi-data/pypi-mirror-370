from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AluminumMemberLocalSectionReduction(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "members", "member_sets", "components", "is_generated", "generating_object_info", "comment", "id_for_export_import", "metadata_for_export_import")
    class ComponentsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[AluminumMemberLocalSectionReduction.ComponentsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[AluminumMemberLocalSectionReduction.ComponentsRow, _Mapping]]] = ...) -> None: ...
    class ComponentsRow(_message.Message):
        __slots__ = ("no", "description", "reduction_type", "position", "multiple", "note", "multiple_number", "multiple_offset_definition_type", "multiple_offset", "fastener_definition_type", "area_csa_s157", "gross_area", "reduction_area", "reduction_area_factor", "net_area", "elastic_section_modulus_about_y", "elastic_section_modulus_y", "elastic_section_modulus_reduction_y", "elastic_section_modulus_reduction_factor_y", "net_elastic_section_modulus_y", "plastic_section_modulus_about_y", "plastic_section_modulus_y", "plastic_section_modulus_reduction_y", "plastic_section_modulus_reduction_factor_y", "net_plastic_section_modulus_y", "elastic_section_modulus_about_z", "elastic_section_modulus_z", "elastic_section_modulus_reduction_z", "elastic_section_modulus_reduction_factor_z", "net_elastic_section_modulus_z", "plastic_section_modulus_about_z", "plastic_section_modulus_z", "plastic_section_modulus_reduction_z", "plastic_section_modulus_reduction_factor_z", "net_plastic_section_modulus_z", "shear_lag_factor_aisc", "consider_shear_lag_effect_is800", "reduction_factor_alpha_is800", "consider_correction_factor_kt_as4100", "correction_factor_kt_as4100", "calculate_short_connection_gb50017", "calculate_long_connection_gb50017", "calculate_empty_holes_gb50017", "consider_effective_area_factor_gb50017", "parameter_effective_factor_eta_gb50017", "connection_eccentricity_y_adm", "connection_eccentricity_z_adm", "connection_length_adm", "shear_lag_user_defined_csa_s157", "shear_lag_factor_csa_s157", "shear_lag_fastener_position_csa_s157", "shear_lag_connection_eccentricity_csa_s157", "shear_lag_length_of_connection_csa_s157")
        class ReductionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            REDUCTION_TYPE_UNKNOWN: _ClassVar[AluminumMemberLocalSectionReduction.ComponentsRow.ReductionType]
            REDUCTION_TYPE_REDUCTION_COMPONENT_TYPE_DESIGN_PARAMETERS: _ClassVar[AluminumMemberLocalSectionReduction.ComponentsRow.ReductionType]
        REDUCTION_TYPE_UNKNOWN: AluminumMemberLocalSectionReduction.ComponentsRow.ReductionType
        REDUCTION_TYPE_REDUCTION_COMPONENT_TYPE_DESIGN_PARAMETERS: AluminumMemberLocalSectionReduction.ComponentsRow.ReductionType
        class MultipleOffsetDefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            MULTIPLE_OFFSET_DEFINITION_TYPE_ABSOLUTE: _ClassVar[AluminumMemberLocalSectionReduction.ComponentsRow.MultipleOffsetDefinitionType]
            MULTIPLE_OFFSET_DEFINITION_TYPE_RELATIVE: _ClassVar[AluminumMemberLocalSectionReduction.ComponentsRow.MultipleOffsetDefinitionType]
        MULTIPLE_OFFSET_DEFINITION_TYPE_ABSOLUTE: AluminumMemberLocalSectionReduction.ComponentsRow.MultipleOffsetDefinitionType
        MULTIPLE_OFFSET_DEFINITION_TYPE_RELATIVE: AluminumMemberLocalSectionReduction.ComponentsRow.MultipleOffsetDefinitionType
        class FastenerDefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            FASTENER_DEFINITION_TYPE_ABSOLUTE: _ClassVar[AluminumMemberLocalSectionReduction.ComponentsRow.FastenerDefinitionType]
            FASTENER_DEFINITION_TYPE_RELATIVE: _ClassVar[AluminumMemberLocalSectionReduction.ComponentsRow.FastenerDefinitionType]
        FASTENER_DEFINITION_TYPE_ABSOLUTE: AluminumMemberLocalSectionReduction.ComponentsRow.FastenerDefinitionType
        FASTENER_DEFINITION_TYPE_RELATIVE: AluminumMemberLocalSectionReduction.ComponentsRow.FastenerDefinitionType
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        REDUCTION_TYPE_FIELD_NUMBER: _ClassVar[int]
        POSITION_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_NUMBER_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_OFFSET_DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
        MULTIPLE_OFFSET_FIELD_NUMBER: _ClassVar[int]
        FASTENER_DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
        AREA_CSA_S157_FIELD_NUMBER: _ClassVar[int]
        GROSS_AREA_FIELD_NUMBER: _ClassVar[int]
        REDUCTION_AREA_FIELD_NUMBER: _ClassVar[int]
        REDUCTION_AREA_FACTOR_FIELD_NUMBER: _ClassVar[int]
        NET_AREA_FIELD_NUMBER: _ClassVar[int]
        ELASTIC_SECTION_MODULUS_ABOUT_Y_FIELD_NUMBER: _ClassVar[int]
        ELASTIC_SECTION_MODULUS_Y_FIELD_NUMBER: _ClassVar[int]
        ELASTIC_SECTION_MODULUS_REDUCTION_Y_FIELD_NUMBER: _ClassVar[int]
        ELASTIC_SECTION_MODULUS_REDUCTION_FACTOR_Y_FIELD_NUMBER: _ClassVar[int]
        NET_ELASTIC_SECTION_MODULUS_Y_FIELD_NUMBER: _ClassVar[int]
        PLASTIC_SECTION_MODULUS_ABOUT_Y_FIELD_NUMBER: _ClassVar[int]
        PLASTIC_SECTION_MODULUS_Y_FIELD_NUMBER: _ClassVar[int]
        PLASTIC_SECTION_MODULUS_REDUCTION_Y_FIELD_NUMBER: _ClassVar[int]
        PLASTIC_SECTION_MODULUS_REDUCTION_FACTOR_Y_FIELD_NUMBER: _ClassVar[int]
        NET_PLASTIC_SECTION_MODULUS_Y_FIELD_NUMBER: _ClassVar[int]
        ELASTIC_SECTION_MODULUS_ABOUT_Z_FIELD_NUMBER: _ClassVar[int]
        ELASTIC_SECTION_MODULUS_Z_FIELD_NUMBER: _ClassVar[int]
        ELASTIC_SECTION_MODULUS_REDUCTION_Z_FIELD_NUMBER: _ClassVar[int]
        ELASTIC_SECTION_MODULUS_REDUCTION_FACTOR_Z_FIELD_NUMBER: _ClassVar[int]
        NET_ELASTIC_SECTION_MODULUS_Z_FIELD_NUMBER: _ClassVar[int]
        PLASTIC_SECTION_MODULUS_ABOUT_Z_FIELD_NUMBER: _ClassVar[int]
        PLASTIC_SECTION_MODULUS_Z_FIELD_NUMBER: _ClassVar[int]
        PLASTIC_SECTION_MODULUS_REDUCTION_Z_FIELD_NUMBER: _ClassVar[int]
        PLASTIC_SECTION_MODULUS_REDUCTION_FACTOR_Z_FIELD_NUMBER: _ClassVar[int]
        NET_PLASTIC_SECTION_MODULUS_Z_FIELD_NUMBER: _ClassVar[int]
        SHEAR_LAG_FACTOR_AISC_FIELD_NUMBER: _ClassVar[int]
        CONSIDER_SHEAR_LAG_EFFECT_IS800_FIELD_NUMBER: _ClassVar[int]
        REDUCTION_FACTOR_ALPHA_IS800_FIELD_NUMBER: _ClassVar[int]
        CONSIDER_CORRECTION_FACTOR_KT_AS4100_FIELD_NUMBER: _ClassVar[int]
        CORRECTION_FACTOR_KT_AS4100_FIELD_NUMBER: _ClassVar[int]
        CALCULATE_SHORT_CONNECTION_GB50017_FIELD_NUMBER: _ClassVar[int]
        CALCULATE_LONG_CONNECTION_GB50017_FIELD_NUMBER: _ClassVar[int]
        CALCULATE_EMPTY_HOLES_GB50017_FIELD_NUMBER: _ClassVar[int]
        CONSIDER_EFFECTIVE_AREA_FACTOR_GB50017_FIELD_NUMBER: _ClassVar[int]
        PARAMETER_EFFECTIVE_FACTOR_ETA_GB50017_FIELD_NUMBER: _ClassVar[int]
        CONNECTION_ECCENTRICITY_Y_ADM_FIELD_NUMBER: _ClassVar[int]
        CONNECTION_ECCENTRICITY_Z_ADM_FIELD_NUMBER: _ClassVar[int]
        CONNECTION_LENGTH_ADM_FIELD_NUMBER: _ClassVar[int]
        SHEAR_LAG_USER_DEFINED_CSA_S157_FIELD_NUMBER: _ClassVar[int]
        SHEAR_LAG_FACTOR_CSA_S157_FIELD_NUMBER: _ClassVar[int]
        SHEAR_LAG_FASTENER_POSITION_CSA_S157_FIELD_NUMBER: _ClassVar[int]
        SHEAR_LAG_CONNECTION_ECCENTRICITY_CSA_S157_FIELD_NUMBER: _ClassVar[int]
        SHEAR_LAG_LENGTH_OF_CONNECTION_CSA_S157_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        reduction_type: AluminumMemberLocalSectionReduction.ComponentsRow.ReductionType
        position: float
        multiple: bool
        note: str
        multiple_number: int
        multiple_offset_definition_type: AluminumMemberLocalSectionReduction.ComponentsRow.MultipleOffsetDefinitionType
        multiple_offset: float
        fastener_definition_type: AluminumMemberLocalSectionReduction.ComponentsRow.FastenerDefinitionType
        area_csa_s157: str
        gross_area: _common_pb2.Value
        reduction_area: float
        reduction_area_factor: float
        net_area: _common_pb2.Value
        elastic_section_modulus_about_y: str
        elastic_section_modulus_y: _common_pb2.Value
        elastic_section_modulus_reduction_y: float
        elastic_section_modulus_reduction_factor_y: float
        net_elastic_section_modulus_y: _common_pb2.Value
        plastic_section_modulus_about_y: str
        plastic_section_modulus_y: _common_pb2.Value
        plastic_section_modulus_reduction_y: float
        plastic_section_modulus_reduction_factor_y: float
        net_plastic_section_modulus_y: _common_pb2.Value
        elastic_section_modulus_about_z: str
        elastic_section_modulus_z: _common_pb2.Value
        elastic_section_modulus_reduction_z: float
        elastic_section_modulus_reduction_factor_z: float
        net_elastic_section_modulus_z: _common_pb2.Value
        plastic_section_modulus_about_z: str
        plastic_section_modulus_z: _common_pb2.Value
        plastic_section_modulus_reduction_z: float
        plastic_section_modulus_reduction_factor_z: float
        net_plastic_section_modulus_z: _common_pb2.Value
        shear_lag_factor_aisc: float
        consider_shear_lag_effect_is800: bool
        reduction_factor_alpha_is800: float
        consider_correction_factor_kt_as4100: bool
        correction_factor_kt_as4100: float
        calculate_short_connection_gb50017: bool
        calculate_long_connection_gb50017: bool
        calculate_empty_holes_gb50017: bool
        consider_effective_area_factor_gb50017: bool
        parameter_effective_factor_eta_gb50017: float
        connection_eccentricity_y_adm: float
        connection_eccentricity_z_adm: float
        connection_length_adm: float
        shear_lag_user_defined_csa_s157: bool
        shear_lag_factor_csa_s157: float
        shear_lag_fastener_position_csa_s157: bool
        shear_lag_connection_eccentricity_csa_s157: float
        shear_lag_length_of_connection_csa_s157: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., reduction_type: _Optional[_Union[AluminumMemberLocalSectionReduction.ComponentsRow.ReductionType, str]] = ..., position: _Optional[float] = ..., multiple: bool = ..., note: _Optional[str] = ..., multiple_number: _Optional[int] = ..., multiple_offset_definition_type: _Optional[_Union[AluminumMemberLocalSectionReduction.ComponentsRow.MultipleOffsetDefinitionType, str]] = ..., multiple_offset: _Optional[float] = ..., fastener_definition_type: _Optional[_Union[AluminumMemberLocalSectionReduction.ComponentsRow.FastenerDefinitionType, str]] = ..., area_csa_s157: _Optional[str] = ..., gross_area: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., reduction_area: _Optional[float] = ..., reduction_area_factor: _Optional[float] = ..., net_area: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., elastic_section_modulus_about_y: _Optional[str] = ..., elastic_section_modulus_y: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., elastic_section_modulus_reduction_y: _Optional[float] = ..., elastic_section_modulus_reduction_factor_y: _Optional[float] = ..., net_elastic_section_modulus_y: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., plastic_section_modulus_about_y: _Optional[str] = ..., plastic_section_modulus_y: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., plastic_section_modulus_reduction_y: _Optional[float] = ..., plastic_section_modulus_reduction_factor_y: _Optional[float] = ..., net_plastic_section_modulus_y: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., elastic_section_modulus_about_z: _Optional[str] = ..., elastic_section_modulus_z: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., elastic_section_modulus_reduction_z: _Optional[float] = ..., elastic_section_modulus_reduction_factor_z: _Optional[float] = ..., net_elastic_section_modulus_z: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., plastic_section_modulus_about_z: _Optional[str] = ..., plastic_section_modulus_z: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., plastic_section_modulus_reduction_z: _Optional[float] = ..., plastic_section_modulus_reduction_factor_z: _Optional[float] = ..., net_plastic_section_modulus_z: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., shear_lag_factor_aisc: _Optional[float] = ..., consider_shear_lag_effect_is800: bool = ..., reduction_factor_alpha_is800: _Optional[float] = ..., consider_correction_factor_kt_as4100: bool = ..., correction_factor_kt_as4100: _Optional[float] = ..., calculate_short_connection_gb50017: bool = ..., calculate_long_connection_gb50017: bool = ..., calculate_empty_holes_gb50017: bool = ..., consider_effective_area_factor_gb50017: bool = ..., parameter_effective_factor_eta_gb50017: _Optional[float] = ..., connection_eccentricity_y_adm: _Optional[float] = ..., connection_eccentricity_z_adm: _Optional[float] = ..., connection_length_adm: _Optional[float] = ..., shear_lag_user_defined_csa_s157: bool = ..., shear_lag_factor_csa_s157: _Optional[float] = ..., shear_lag_fastener_position_csa_s157: bool = ..., shear_lag_connection_eccentricity_csa_s157: _Optional[float] = ..., shear_lag_length_of_connection_csa_s157: _Optional[float] = ...) -> None: ...
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
    components: AluminumMemberLocalSectionReduction.ComponentsTable
    is_generated: bool
    generating_object_info: str
    comment: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., components: _Optional[_Union[AluminumMemberLocalSectionReduction.ComponentsTable, _Mapping]] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., comment: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
