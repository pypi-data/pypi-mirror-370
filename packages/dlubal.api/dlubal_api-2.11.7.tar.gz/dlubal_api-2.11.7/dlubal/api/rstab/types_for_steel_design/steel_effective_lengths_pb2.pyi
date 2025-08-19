from dlubal.api.rstab import object_id_pb2 as _object_id_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SteelEffectiveLengths(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "comment", "members", "member_sets", "flexural_buckling_about_y", "flexural_buckling_about_z", "torsional_buckling", "lateral_torsional_buckling", "buckling_factor_value_type", "principal_section_axes", "geometric_section_axes", "is_generated", "generating_object_info", "intermediate_nodes", "different_properties", "factors_definition_absolute", "import_from_stability_analysis_enabled", "stability_import_data_factors_definition_absolute", "stability_import_data_member_y", "stability_import_data_loading_y", "stability_import_data_mode_number_y", "stability_import_data_member_z", "stability_import_data_loading_z", "stability_import_data_mode_number_z", "stability_import_data_factors", "stability_import_data_lengths", "stability_import_data_user_defined_y", "stability_import_data_user_defined_z", "determination_mcr_europe", "determination_mcr_is800", "determination_mcr_aisc", "determination_mcr_gb50", "determination_mcr_sia263", "determination_mcr_nbr8800", "determination_cb_aisc", "cb_factor_aisc", "determination_mcr_csa", "determination_cb_csa", "cb_factor_csa", "determination_mcr_bs5", "determination_cb_nbr", "cb_factor_nbr", "moment_modification_restrained_segments_as", "moment_modification_unrestrained_segments_as", "slenderness_reduction_restrained_segments_as", "slenderness_reduction_unrestrained_segments_as", "modification_factor_alpha_restrained_segments_as", "modification_factor_alpha_unrestrained_segments_as", "member_type", "member_type_yy", "member_type_zz", "nodal_supports", "factors", "lengths", "standard_of_effective_lengths", "determination_of_elastic_critical_stress_aisi", "modification_factor_cb_aisi", "modification_factor_cb_aisi_user_defined_value", "id_for_export_import", "metadata_for_export_import")
    class BucklingFactorValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BUCKLING_FACTOR_VALUE_TYPE_THEORETICAL: _ClassVar[SteelEffectiveLengths.BucklingFactorValueType]
        BUCKLING_FACTOR_VALUE_TYPE_RECOMMENDED: _ClassVar[SteelEffectiveLengths.BucklingFactorValueType]
    BUCKLING_FACTOR_VALUE_TYPE_THEORETICAL: SteelEffectiveLengths.BucklingFactorValueType
    BUCKLING_FACTOR_VALUE_TYPE_RECOMMENDED: SteelEffectiveLengths.BucklingFactorValueType
    class DeterminationMcrEurope(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_MCR_EUROPE_EIGENVALUE: _ClassVar[SteelEffectiveLengths.DeterminationMcrEurope]
        DETERMINATION_MCR_EUROPE_USER_DEFINED: _ClassVar[SteelEffectiveLengths.DeterminationMcrEurope]
    DETERMINATION_MCR_EUROPE_EIGENVALUE: SteelEffectiveLengths.DeterminationMcrEurope
    DETERMINATION_MCR_EUROPE_USER_DEFINED: SteelEffectiveLengths.DeterminationMcrEurope
    class DeterminationMcrIs800(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_MCR_IS800_EIGENVALUE: _ClassVar[SteelEffectiveLengths.DeterminationMcrIs800]
        DETERMINATION_MCR_IS800_USER_DEFINED: _ClassVar[SteelEffectiveLengths.DeterminationMcrIs800]
    DETERMINATION_MCR_IS800_EIGENVALUE: SteelEffectiveLengths.DeterminationMcrIs800
    DETERMINATION_MCR_IS800_USER_DEFINED: SteelEffectiveLengths.DeterminationMcrIs800
    class DeterminationMcrAisc(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_MCR_AISC_EIGENVALUE: _ClassVar[SteelEffectiveLengths.DeterminationMcrAisc]
        DETERMINATION_MCR_AISC_ACC_TO_CHAPTER_F: _ClassVar[SteelEffectiveLengths.DeterminationMcrAisc]
        DETERMINATION_MCR_AISC_USER_DEFINED: _ClassVar[SteelEffectiveLengths.DeterminationMcrAisc]
    DETERMINATION_MCR_AISC_EIGENVALUE: SteelEffectiveLengths.DeterminationMcrAisc
    DETERMINATION_MCR_AISC_ACC_TO_CHAPTER_F: SteelEffectiveLengths.DeterminationMcrAisc
    DETERMINATION_MCR_AISC_USER_DEFINED: SteelEffectiveLengths.DeterminationMcrAisc
    class DeterminationMcrGb50(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_MCR_GB50_EIGENVALUE_METHOD: _ClassVar[SteelEffectiveLengths.DeterminationMcrGb50]
        DETERMINATION_MCR_GB50_ANALYTICAL_METHOD: _ClassVar[SteelEffectiveLengths.DeterminationMcrGb50]
        DETERMINATION_MCR_GB50_USER_DEFINED: _ClassVar[SteelEffectiveLengths.DeterminationMcrGb50]
    DETERMINATION_MCR_GB50_EIGENVALUE_METHOD: SteelEffectiveLengths.DeterminationMcrGb50
    DETERMINATION_MCR_GB50_ANALYTICAL_METHOD: SteelEffectiveLengths.DeterminationMcrGb50
    DETERMINATION_MCR_GB50_USER_DEFINED: SteelEffectiveLengths.DeterminationMcrGb50
    class DeterminationMcrSia263(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_MCR_SIA263_EIGENVALUE: _ClassVar[SteelEffectiveLengths.DeterminationMcrSia263]
        DETERMINATION_MCR_SIA263_USER_DEFINED: _ClassVar[SteelEffectiveLengths.DeterminationMcrSia263]
    DETERMINATION_MCR_SIA263_EIGENVALUE: SteelEffectiveLengths.DeterminationMcrSia263
    DETERMINATION_MCR_SIA263_USER_DEFINED: SteelEffectiveLengths.DeterminationMcrSia263
    class DeterminationMcrNbr8800(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_MCR_NBR8800_EIGENVALUE: _ClassVar[SteelEffectiveLengths.DeterminationMcrNbr8800]
        DETERMINATION_MCR_NBR8800_ACC_TO_TAB_G1: _ClassVar[SteelEffectiveLengths.DeterminationMcrNbr8800]
        DETERMINATION_MCR_NBR8800_USER_DEFINED: _ClassVar[SteelEffectiveLengths.DeterminationMcrNbr8800]
    DETERMINATION_MCR_NBR8800_EIGENVALUE: SteelEffectiveLengths.DeterminationMcrNbr8800
    DETERMINATION_MCR_NBR8800_ACC_TO_TAB_G1: SteelEffectiveLengths.DeterminationMcrNbr8800
    DETERMINATION_MCR_NBR8800_USER_DEFINED: SteelEffectiveLengths.DeterminationMcrNbr8800
    class DeterminationCbAisc(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_CB_AISC_BASIC_VALUE: _ClassVar[SteelEffectiveLengths.DeterminationCbAisc]
        DETERMINATION_CB_AISC_ACC_TO_CHAPTER_F: _ClassVar[SteelEffectiveLengths.DeterminationCbAisc]
        DETERMINATION_CB_AISC_USER_DEFINED: _ClassVar[SteelEffectiveLengths.DeterminationCbAisc]
    DETERMINATION_CB_AISC_BASIC_VALUE: SteelEffectiveLengths.DeterminationCbAisc
    DETERMINATION_CB_AISC_ACC_TO_CHAPTER_F: SteelEffectiveLengths.DeterminationCbAisc
    DETERMINATION_CB_AISC_USER_DEFINED: SteelEffectiveLengths.DeterminationCbAisc
    class DeterminationMcrCsa(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_MCR_CSA_EIGENVALUE: _ClassVar[SteelEffectiveLengths.DeterminationMcrCsa]
        DETERMINATION_MCR_CSA_ACC_TO_CSAS16: _ClassVar[SteelEffectiveLengths.DeterminationMcrCsa]
        DETERMINATION_MCR_CSA_USER_DEFINED: _ClassVar[SteelEffectiveLengths.DeterminationMcrCsa]
    DETERMINATION_MCR_CSA_EIGENVALUE: SteelEffectiveLengths.DeterminationMcrCsa
    DETERMINATION_MCR_CSA_ACC_TO_CSAS16: SteelEffectiveLengths.DeterminationMcrCsa
    DETERMINATION_MCR_CSA_USER_DEFINED: SteelEffectiveLengths.DeterminationMcrCsa
    class DeterminationCbCsa(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_CB_CSA_BASIC_VALUE: _ClassVar[SteelEffectiveLengths.DeterminationCbCsa]
        DETERMINATION_CB_CSA_ACC_TO_CHAPTER_13_6: _ClassVar[SteelEffectiveLengths.DeterminationCbCsa]
        DETERMINATION_CB_CSA_USER_DEFINED: _ClassVar[SteelEffectiveLengths.DeterminationCbCsa]
    DETERMINATION_CB_CSA_BASIC_VALUE: SteelEffectiveLengths.DeterminationCbCsa
    DETERMINATION_CB_CSA_ACC_TO_CHAPTER_13_6: SteelEffectiveLengths.DeterminationCbCsa
    DETERMINATION_CB_CSA_USER_DEFINED: SteelEffectiveLengths.DeterminationCbCsa
    class DeterminationMcrBs5(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_MCR_BS5_EIGENVALUE: _ClassVar[SteelEffectiveLengths.DeterminationMcrBs5]
        DETERMINATION_MCR_BS5_ACC_TO_ANNEX_B: _ClassVar[SteelEffectiveLengths.DeterminationMcrBs5]
        DETERMINATION_MCR_BS5_USER_DEFINED: _ClassVar[SteelEffectiveLengths.DeterminationMcrBs5]
    DETERMINATION_MCR_BS5_EIGENVALUE: SteelEffectiveLengths.DeterminationMcrBs5
    DETERMINATION_MCR_BS5_ACC_TO_ANNEX_B: SteelEffectiveLengths.DeterminationMcrBs5
    DETERMINATION_MCR_BS5_USER_DEFINED: SteelEffectiveLengths.DeterminationMcrBs5
    class DeterminationCbNbr(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_CB_NBR_BASIC_VALUE: _ClassVar[SteelEffectiveLengths.DeterminationCbNbr]
        DETERMINATION_CB_NBR_ACC_TO_5423: _ClassVar[SteelEffectiveLengths.DeterminationCbNbr]
        DETERMINATION_CB_NBR_USER_DEFINED: _ClassVar[SteelEffectiveLengths.DeterminationCbNbr]
    DETERMINATION_CB_NBR_BASIC_VALUE: SteelEffectiveLengths.DeterminationCbNbr
    DETERMINATION_CB_NBR_ACC_TO_5423: SteelEffectiveLengths.DeterminationCbNbr
    DETERMINATION_CB_NBR_USER_DEFINED: SteelEffectiveLengths.DeterminationCbNbr
    class MomentModificationRestrainedSegmentsAs(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MOMENT_MODIFICATION_RESTRAINED_SEGMENTS_AS_BASIC_VALUE: _ClassVar[SteelEffectiveLengths.MomentModificationRestrainedSegmentsAs]
        MOMENT_MODIFICATION_RESTRAINED_SEGMENTS_AS_ACC_TO_5611_II: _ClassVar[SteelEffectiveLengths.MomentModificationRestrainedSegmentsAs]
        MOMENT_MODIFICATION_RESTRAINED_SEGMENTS_AS_ACC_TO_5611_III: _ClassVar[SteelEffectiveLengths.MomentModificationRestrainedSegmentsAs]
        MOMENT_MODIFICATION_RESTRAINED_SEGMENTS_AS_EIGENVALUE_METHOD: _ClassVar[SteelEffectiveLengths.MomentModificationRestrainedSegmentsAs]
        MOMENT_MODIFICATION_RESTRAINED_SEGMENTS_AS_USER_DEFINED: _ClassVar[SteelEffectiveLengths.MomentModificationRestrainedSegmentsAs]
    MOMENT_MODIFICATION_RESTRAINED_SEGMENTS_AS_BASIC_VALUE: SteelEffectiveLengths.MomentModificationRestrainedSegmentsAs
    MOMENT_MODIFICATION_RESTRAINED_SEGMENTS_AS_ACC_TO_5611_II: SteelEffectiveLengths.MomentModificationRestrainedSegmentsAs
    MOMENT_MODIFICATION_RESTRAINED_SEGMENTS_AS_ACC_TO_5611_III: SteelEffectiveLengths.MomentModificationRestrainedSegmentsAs
    MOMENT_MODIFICATION_RESTRAINED_SEGMENTS_AS_EIGENVALUE_METHOD: SteelEffectiveLengths.MomentModificationRestrainedSegmentsAs
    MOMENT_MODIFICATION_RESTRAINED_SEGMENTS_AS_USER_DEFINED: SteelEffectiveLengths.MomentModificationRestrainedSegmentsAs
    class MomentModificationUnrestrainedSegmentsAs(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MOMENT_MODIFICATION_UNRESTRAINED_SEGMENTS_AS_BASIC_VALUE: _ClassVar[SteelEffectiveLengths.MomentModificationUnrestrainedSegmentsAs]
        MOMENT_MODIFICATION_UNRESTRAINED_SEGMENTS_AS_ACC_TO_5611_II: _ClassVar[SteelEffectiveLengths.MomentModificationUnrestrainedSegmentsAs]
        MOMENT_MODIFICATION_UNRESTRAINED_SEGMENTS_AS_USER_DEFINED: _ClassVar[SteelEffectiveLengths.MomentModificationUnrestrainedSegmentsAs]
    MOMENT_MODIFICATION_UNRESTRAINED_SEGMENTS_AS_BASIC_VALUE: SteelEffectiveLengths.MomentModificationUnrestrainedSegmentsAs
    MOMENT_MODIFICATION_UNRESTRAINED_SEGMENTS_AS_ACC_TO_5611_II: SteelEffectiveLengths.MomentModificationUnrestrainedSegmentsAs
    MOMENT_MODIFICATION_UNRESTRAINED_SEGMENTS_AS_USER_DEFINED: SteelEffectiveLengths.MomentModificationUnrestrainedSegmentsAs
    class SlendernessReductionRestrainedSegmentsAs(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SLENDERNESS_REDUCTION_RESTRAINED_SEGMENTS_AS_ACC_TO_5611: _ClassVar[SteelEffectiveLengths.SlendernessReductionRestrainedSegmentsAs]
        SLENDERNESS_REDUCTION_RESTRAINED_SEGMENTS_AS_EIGENVALUE_METHOD: _ClassVar[SteelEffectiveLengths.SlendernessReductionRestrainedSegmentsAs]
    SLENDERNESS_REDUCTION_RESTRAINED_SEGMENTS_AS_ACC_TO_5611: SteelEffectiveLengths.SlendernessReductionRestrainedSegmentsAs
    SLENDERNESS_REDUCTION_RESTRAINED_SEGMENTS_AS_EIGENVALUE_METHOD: SteelEffectiveLengths.SlendernessReductionRestrainedSegmentsAs
    class SlendernessReductionUnrestrainedSegmentsAs(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SLENDERNESS_REDUCTION_UNRESTRAINED_SEGMENTS_AS_ACC_TO_5611: _ClassVar[SteelEffectiveLengths.SlendernessReductionUnrestrainedSegmentsAs]
        SLENDERNESS_REDUCTION_UNRESTRAINED_SEGMENTS_AS_EIGENVALUE_METHOD: _ClassVar[SteelEffectiveLengths.SlendernessReductionUnrestrainedSegmentsAs]
    SLENDERNESS_REDUCTION_UNRESTRAINED_SEGMENTS_AS_ACC_TO_5611: SteelEffectiveLengths.SlendernessReductionUnrestrainedSegmentsAs
    SLENDERNESS_REDUCTION_UNRESTRAINED_SEGMENTS_AS_EIGENVALUE_METHOD: SteelEffectiveLengths.SlendernessReductionUnrestrainedSegmentsAs
    class MemberType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MEMBER_TYPE_BEAM: _ClassVar[SteelEffectiveLengths.MemberType]
        MEMBER_TYPE_CANTILEVER: _ClassVar[SteelEffectiveLengths.MemberType]
    MEMBER_TYPE_BEAM: SteelEffectiveLengths.MemberType
    MEMBER_TYPE_CANTILEVER: SteelEffectiveLengths.MemberType
    class MemberTypeYy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MEMBER_TYPE_YY_BEAM: _ClassVar[SteelEffectiveLengths.MemberTypeYy]
        MEMBER_TYPE_YY_CANTILEVER: _ClassVar[SteelEffectiveLengths.MemberTypeYy]
    MEMBER_TYPE_YY_BEAM: SteelEffectiveLengths.MemberTypeYy
    MEMBER_TYPE_YY_CANTILEVER: SteelEffectiveLengths.MemberTypeYy
    class MemberTypeZz(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MEMBER_TYPE_ZZ_BEAM: _ClassVar[SteelEffectiveLengths.MemberTypeZz]
        MEMBER_TYPE_ZZ_CANTILEVER: _ClassVar[SteelEffectiveLengths.MemberTypeZz]
    MEMBER_TYPE_ZZ_BEAM: SteelEffectiveLengths.MemberTypeZz
    MEMBER_TYPE_ZZ_CANTILEVER: SteelEffectiveLengths.MemberTypeZz
    class StandardOfEffectiveLengths(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STANDARD_OF_EFFECTIVE_LENGTHS_AISC_360: _ClassVar[SteelEffectiveLengths.StandardOfEffectiveLengths]
        STANDARD_OF_EFFECTIVE_LENGTHS_AISI_S100: _ClassVar[SteelEffectiveLengths.StandardOfEffectiveLengths]
        STANDARD_OF_EFFECTIVE_LENGTHS_CSA_S16: _ClassVar[SteelEffectiveLengths.StandardOfEffectiveLengths]
    STANDARD_OF_EFFECTIVE_LENGTHS_AISC_360: SteelEffectiveLengths.StandardOfEffectiveLengths
    STANDARD_OF_EFFECTIVE_LENGTHS_AISI_S100: SteelEffectiveLengths.StandardOfEffectiveLengths
    STANDARD_OF_EFFECTIVE_LENGTHS_CSA_S16: SteelEffectiveLengths.StandardOfEffectiveLengths
    class DeterminationOfElasticCriticalStressAisi(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_OF_ELASTIC_CRITICAL_STRESS_AISI_FINITE_STRIP_METHOD: _ClassVar[SteelEffectiveLengths.DeterminationOfElasticCriticalStressAisi]
        DETERMINATION_OF_ELASTIC_CRITICAL_STRESS_AISI_ACC_TO_CHAPTERS_E2_F21: _ClassVar[SteelEffectiveLengths.DeterminationOfElasticCriticalStressAisi]
    DETERMINATION_OF_ELASTIC_CRITICAL_STRESS_AISI_FINITE_STRIP_METHOD: SteelEffectiveLengths.DeterminationOfElasticCriticalStressAisi
    DETERMINATION_OF_ELASTIC_CRITICAL_STRESS_AISI_ACC_TO_CHAPTERS_E2_F21: SteelEffectiveLengths.DeterminationOfElasticCriticalStressAisi
    class ModificationFactorCbAisi(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MODIFICATION_FACTOR_CB_AISI_BASIC_VALUE: _ClassVar[SteelEffectiveLengths.ModificationFactorCbAisi]
        MODIFICATION_FACTOR_CB_AISI_AUTOMATICALLY_ACC_TO_EQ_F2112: _ClassVar[SteelEffectiveLengths.ModificationFactorCbAisi]
        MODIFICATION_FACTOR_CB_AISI_USER_DEFINED: _ClassVar[SteelEffectiveLengths.ModificationFactorCbAisi]
    MODIFICATION_FACTOR_CB_AISI_BASIC_VALUE: SteelEffectiveLengths.ModificationFactorCbAisi
    MODIFICATION_FACTOR_CB_AISI_AUTOMATICALLY_ACC_TO_EQ_F2112: SteelEffectiveLengths.ModificationFactorCbAisi
    MODIFICATION_FACTOR_CB_AISI_USER_DEFINED: SteelEffectiveLengths.ModificationFactorCbAisi
    class StabilityImportDataFactorsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[SteelEffectiveLengths.StabilityImportDataFactorsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[SteelEffectiveLengths.StabilityImportDataFactorsRow, _Mapping]]] = ...) -> None: ...
    class StabilityImportDataFactorsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_u", "flexural_buckling_v", "flexural_buckling_y", "flexural_buckling_z")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_U_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_V_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_u: float
        flexural_buckling_v: float
        flexural_buckling_y: float
        flexural_buckling_z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_u: _Optional[float] = ..., flexural_buckling_v: _Optional[float] = ..., flexural_buckling_y: _Optional[float] = ..., flexural_buckling_z: _Optional[float] = ...) -> None: ...
    class StabilityImportDataLengthsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[SteelEffectiveLengths.StabilityImportDataLengthsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[SteelEffectiveLengths.StabilityImportDataLengthsRow, _Mapping]]] = ...) -> None: ...
    class StabilityImportDataLengthsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_u", "flexural_buckling_v", "flexural_buckling_y", "flexural_buckling_z")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_U_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_V_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_u: float
        flexural_buckling_v: float
        flexural_buckling_y: float
        flexural_buckling_z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_u: _Optional[float] = ..., flexural_buckling_v: _Optional[float] = ..., flexural_buckling_y: _Optional[float] = ..., flexural_buckling_z: _Optional[float] = ...) -> None: ...
    class NodalSupportsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[SteelEffectiveLengths.NodalSupportsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[SteelEffectiveLengths.NodalSupportsRow, _Mapping]]] = ...) -> None: ...
    class NodalSupportsRow(_message.Message):
        __slots__ = ("no", "description", "support_type", "support_in_z", "support_spring_in_y", "eccentricity_type", "eccentricity_ez", "restraint_spring_about_x", "restraint_spring_about_z", "restraint_spring_warping", "support_in_y", "restraint_about_x", "restraint_about_z", "restraint_warping", "nodes")
        class SupportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            SUPPORT_TYPE_NONE: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_ALL: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Y: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION_AND_WARPING: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION_AND_WARPING: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_INDIVIDUALLY: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_RESTRAINT_ABOUT_X: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.SupportType]
        SUPPORT_TYPE_NONE: SteelEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_ALL: SteelEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Y: SteelEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z: SteelEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION: SteelEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION_AND_WARPING: SteelEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION: SteelEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION_AND_WARPING: SteelEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_INDIVIDUALLY: SteelEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_RESTRAINT_ABOUT_X: SteelEffectiveLengths.NodalSupportsRow.SupportType
        class EccentricityType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            ECCENTRICITY_TYPE_NONE: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_AT_LOWER_FLANGE: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_AT_UPPER_FLANGE: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_USER_VALUE: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.EccentricityType]
        ECCENTRICITY_TYPE_NONE: SteelEffectiveLengths.NodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_AT_LOWER_FLANGE: SteelEffectiveLengths.NodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_AT_UPPER_FLANGE: SteelEffectiveLengths.NodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_USER_VALUE: SteelEffectiveLengths.NodalSupportsRow.EccentricityType
        class SupportInY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            SUPPORT_IN_Y_SUPPORT_STATUS_NO: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.SupportInY]
            SUPPORT_IN_Y_SUPPORT_STATUS_SPRING: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.SupportInY]
            SUPPORT_IN_Y_SUPPORT_STATUS_YES: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.SupportInY]
        SUPPORT_IN_Y_SUPPORT_STATUS_NO: SteelEffectiveLengths.NodalSupportsRow.SupportInY
        SUPPORT_IN_Y_SUPPORT_STATUS_SPRING: SteelEffectiveLengths.NodalSupportsRow.SupportInY
        SUPPORT_IN_Y_SUPPORT_STATUS_YES: SteelEffectiveLengths.NodalSupportsRow.SupportInY
        class RestraintAboutX(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_NO: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.RestraintAboutX]
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_SPRING: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.RestraintAboutX]
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_YES: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.RestraintAboutX]
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_NO: SteelEffectiveLengths.NodalSupportsRow.RestraintAboutX
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_SPRING: SteelEffectiveLengths.NodalSupportsRow.RestraintAboutX
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_YES: SteelEffectiveLengths.NodalSupportsRow.RestraintAboutX
        class RestraintAboutZ(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_NO: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.RestraintAboutZ]
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_SPRING: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.RestraintAboutZ]
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_YES: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.RestraintAboutZ]
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_NO: SteelEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_SPRING: SteelEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_YES: SteelEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        class RestraintWarping(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_WARPING_SUPPORT_STATUS_NO: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.RestraintWarping]
            RESTRAINT_WARPING_SUPPORT_STATUS_SPRING: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.RestraintWarping]
            RESTRAINT_WARPING_SUPPORT_STATUS_YES: _ClassVar[SteelEffectiveLengths.NodalSupportsRow.RestraintWarping]
        RESTRAINT_WARPING_SUPPORT_STATUS_NO: SteelEffectiveLengths.NodalSupportsRow.RestraintWarping
        RESTRAINT_WARPING_SUPPORT_STATUS_SPRING: SteelEffectiveLengths.NodalSupportsRow.RestraintWarping
        RESTRAINT_WARPING_SUPPORT_STATUS_YES: SteelEffectiveLengths.NodalSupportsRow.RestraintWarping
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        SUPPORT_TYPE_FIELD_NUMBER: _ClassVar[int]
        SUPPORT_IN_Z_FIELD_NUMBER: _ClassVar[int]
        SUPPORT_SPRING_IN_Y_FIELD_NUMBER: _ClassVar[int]
        ECCENTRICITY_TYPE_FIELD_NUMBER: _ClassVar[int]
        ECCENTRICITY_EZ_FIELD_NUMBER: _ClassVar[int]
        RESTRAINT_SPRING_ABOUT_X_FIELD_NUMBER: _ClassVar[int]
        RESTRAINT_SPRING_ABOUT_Z_FIELD_NUMBER: _ClassVar[int]
        RESTRAINT_SPRING_WARPING_FIELD_NUMBER: _ClassVar[int]
        SUPPORT_IN_Y_FIELD_NUMBER: _ClassVar[int]
        RESTRAINT_ABOUT_X_FIELD_NUMBER: _ClassVar[int]
        RESTRAINT_ABOUT_Z_FIELD_NUMBER: _ClassVar[int]
        RESTRAINT_WARPING_FIELD_NUMBER: _ClassVar[int]
        NODES_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        support_type: SteelEffectiveLengths.NodalSupportsRow.SupportType
        support_in_z: bool
        support_spring_in_y: float
        eccentricity_type: SteelEffectiveLengths.NodalSupportsRow.EccentricityType
        eccentricity_ez: float
        restraint_spring_about_x: float
        restraint_spring_about_z: float
        restraint_spring_warping: float
        support_in_y: SteelEffectiveLengths.NodalSupportsRow.SupportInY
        restraint_about_x: SteelEffectiveLengths.NodalSupportsRow.RestraintAboutX
        restraint_about_z: SteelEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        restraint_warping: SteelEffectiveLengths.NodalSupportsRow.RestraintWarping
        nodes: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., support_type: _Optional[_Union[SteelEffectiveLengths.NodalSupportsRow.SupportType, str]] = ..., support_in_z: bool = ..., support_spring_in_y: _Optional[float] = ..., eccentricity_type: _Optional[_Union[SteelEffectiveLengths.NodalSupportsRow.EccentricityType, str]] = ..., eccentricity_ez: _Optional[float] = ..., restraint_spring_about_x: _Optional[float] = ..., restraint_spring_about_z: _Optional[float] = ..., restraint_spring_warping: _Optional[float] = ..., support_in_y: _Optional[_Union[SteelEffectiveLengths.NodalSupportsRow.SupportInY, str]] = ..., restraint_about_x: _Optional[_Union[SteelEffectiveLengths.NodalSupportsRow.RestraintAboutX, str]] = ..., restraint_about_z: _Optional[_Union[SteelEffectiveLengths.NodalSupportsRow.RestraintAboutZ, str]] = ..., restraint_warping: _Optional[_Union[SteelEffectiveLengths.NodalSupportsRow.RestraintWarping, str]] = ..., nodes: _Optional[_Iterable[int]] = ...) -> None: ...
    class FactorsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[SteelEffectiveLengths.FactorsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[SteelEffectiveLengths.FactorsRow, _Mapping]]] = ...) -> None: ...
    class FactorsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_u", "flexural_buckling_v", "flexural_buckling_y", "flexural_buckling_z", "torsional_buckling", "lateral_torsional_buckling", "lateral_torsional_buckling_top", "lateral_torsional_buckling_bottom", "twist_restraint", "lateral_torsional_restraint", "critical_moment")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_U_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_V_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_TOP_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_BOTTOM_FIELD_NUMBER: _ClassVar[int]
        TWIST_RESTRAINT_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_RESTRAINT_FIELD_NUMBER: _ClassVar[int]
        CRITICAL_MOMENT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_u: float
        flexural_buckling_v: float
        flexural_buckling_y: float
        flexural_buckling_z: float
        torsional_buckling: float
        lateral_torsional_buckling: float
        lateral_torsional_buckling_top: float
        lateral_torsional_buckling_bottom: float
        twist_restraint: float
        lateral_torsional_restraint: float
        critical_moment: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_u: _Optional[float] = ..., flexural_buckling_v: _Optional[float] = ..., flexural_buckling_y: _Optional[float] = ..., flexural_buckling_z: _Optional[float] = ..., torsional_buckling: _Optional[float] = ..., lateral_torsional_buckling: _Optional[float] = ..., lateral_torsional_buckling_top: _Optional[float] = ..., lateral_torsional_buckling_bottom: _Optional[float] = ..., twist_restraint: _Optional[float] = ..., lateral_torsional_restraint: _Optional[float] = ..., critical_moment: _Optional[float] = ...) -> None: ...
    class LengthsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[SteelEffectiveLengths.LengthsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[SteelEffectiveLengths.LengthsRow, _Mapping]]] = ...) -> None: ...
    class LengthsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_u", "flexural_buckling_v", "flexural_buckling_y", "flexural_buckling_z", "torsional_buckling", "lateral_torsional_buckling", "lateral_torsional_buckling_top", "lateral_torsional_buckling_bottom", "critical_moment")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_U_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_V_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_TOP_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_BOTTOM_FIELD_NUMBER: _ClassVar[int]
        CRITICAL_MOMENT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_u: float
        flexural_buckling_v: float
        flexural_buckling_y: float
        flexural_buckling_z: float
        torsional_buckling: float
        lateral_torsional_buckling: float
        lateral_torsional_buckling_top: float
        lateral_torsional_buckling_bottom: float
        critical_moment: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_u: _Optional[float] = ..., flexural_buckling_v: _Optional[float] = ..., flexural_buckling_y: _Optional[float] = ..., flexural_buckling_z: _Optional[float] = ..., torsional_buckling: _Optional[float] = ..., lateral_torsional_buckling: _Optional[float] = ..., lateral_torsional_buckling_top: _Optional[float] = ..., lateral_torsional_buckling_bottom: _Optional[float] = ..., critical_moment: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_ABOUT_Y_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_ABOUT_Z_FIELD_NUMBER: _ClassVar[int]
    TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
    BUCKLING_FACTOR_VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_SECTION_AXES_FIELD_NUMBER: _ClassVar[int]
    GEOMETRIC_SECTION_AXES_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIATE_NODES_FIELD_NUMBER: _ClassVar[int]
    DIFFERENT_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    FACTORS_DEFINITION_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    IMPORT_FROM_STABILITY_ANALYSIS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_FACTORS_DEFINITION_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_MEMBER_Y_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_LOADING_Y_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_MODE_NUMBER_Y_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_MEMBER_Z_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_LOADING_Z_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_MODE_NUMBER_Z_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_FACTORS_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_LENGTHS_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_USER_DEFINED_Y_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_USER_DEFINED_Z_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_MCR_EUROPE_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_MCR_IS800_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_MCR_AISC_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_MCR_GB50_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_MCR_SIA263_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_MCR_NBR8800_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_CB_AISC_FIELD_NUMBER: _ClassVar[int]
    CB_FACTOR_AISC_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_MCR_CSA_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_CB_CSA_FIELD_NUMBER: _ClassVar[int]
    CB_FACTOR_CSA_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_MCR_BS5_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_CB_NBR_FIELD_NUMBER: _ClassVar[int]
    CB_FACTOR_NBR_FIELD_NUMBER: _ClassVar[int]
    MOMENT_MODIFICATION_RESTRAINED_SEGMENTS_AS_FIELD_NUMBER: _ClassVar[int]
    MOMENT_MODIFICATION_UNRESTRAINED_SEGMENTS_AS_FIELD_NUMBER: _ClassVar[int]
    SLENDERNESS_REDUCTION_RESTRAINED_SEGMENTS_AS_FIELD_NUMBER: _ClassVar[int]
    SLENDERNESS_REDUCTION_UNRESTRAINED_SEGMENTS_AS_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_FACTOR_ALPHA_RESTRAINED_SEGMENTS_AS_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_FACTOR_ALPHA_UNRESTRAINED_SEGMENTS_AS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TYPE_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TYPE_YY_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TYPE_ZZ_FIELD_NUMBER: _ClassVar[int]
    NODAL_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    FACTORS_FIELD_NUMBER: _ClassVar[int]
    LENGTHS_FIELD_NUMBER: _ClassVar[int]
    STANDARD_OF_EFFECTIVE_LENGTHS_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_OF_ELASTIC_CRITICAL_STRESS_AISI_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_FACTOR_CB_AISI_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_FACTOR_CB_AISI_USER_DEFINED_VALUE_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    comment: str
    members: _containers.RepeatedScalarFieldContainer[int]
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    flexural_buckling_about_y: bool
    flexural_buckling_about_z: bool
    torsional_buckling: bool
    lateral_torsional_buckling: bool
    buckling_factor_value_type: SteelEffectiveLengths.BucklingFactorValueType
    principal_section_axes: bool
    geometric_section_axes: bool
    is_generated: bool
    generating_object_info: str
    intermediate_nodes: bool
    different_properties: bool
    factors_definition_absolute: bool
    import_from_stability_analysis_enabled: bool
    stability_import_data_factors_definition_absolute: bool
    stability_import_data_member_y: int
    stability_import_data_loading_y: _object_id_pb2.ObjectId
    stability_import_data_mode_number_y: int
    stability_import_data_member_z: int
    stability_import_data_loading_z: _object_id_pb2.ObjectId
    stability_import_data_mode_number_z: int
    stability_import_data_factors: SteelEffectiveLengths.StabilityImportDataFactorsTable
    stability_import_data_lengths: SteelEffectiveLengths.StabilityImportDataLengthsTable
    stability_import_data_user_defined_y: bool
    stability_import_data_user_defined_z: bool
    determination_mcr_europe: SteelEffectiveLengths.DeterminationMcrEurope
    determination_mcr_is800: SteelEffectiveLengths.DeterminationMcrIs800
    determination_mcr_aisc: SteelEffectiveLengths.DeterminationMcrAisc
    determination_mcr_gb50: SteelEffectiveLengths.DeterminationMcrGb50
    determination_mcr_sia263: SteelEffectiveLengths.DeterminationMcrSia263
    determination_mcr_nbr8800: SteelEffectiveLengths.DeterminationMcrNbr8800
    determination_cb_aisc: SteelEffectiveLengths.DeterminationCbAisc
    cb_factor_aisc: float
    determination_mcr_csa: SteelEffectiveLengths.DeterminationMcrCsa
    determination_cb_csa: SteelEffectiveLengths.DeterminationCbCsa
    cb_factor_csa: float
    determination_mcr_bs5: SteelEffectiveLengths.DeterminationMcrBs5
    determination_cb_nbr: SteelEffectiveLengths.DeterminationCbNbr
    cb_factor_nbr: float
    moment_modification_restrained_segments_as: SteelEffectiveLengths.MomentModificationRestrainedSegmentsAs
    moment_modification_unrestrained_segments_as: SteelEffectiveLengths.MomentModificationUnrestrainedSegmentsAs
    slenderness_reduction_restrained_segments_as: SteelEffectiveLengths.SlendernessReductionRestrainedSegmentsAs
    slenderness_reduction_unrestrained_segments_as: SteelEffectiveLengths.SlendernessReductionUnrestrainedSegmentsAs
    modification_factor_alpha_restrained_segments_as: float
    modification_factor_alpha_unrestrained_segments_as: float
    member_type: SteelEffectiveLengths.MemberType
    member_type_yy: SteelEffectiveLengths.MemberTypeYy
    member_type_zz: SteelEffectiveLengths.MemberTypeZz
    nodal_supports: SteelEffectiveLengths.NodalSupportsTable
    factors: SteelEffectiveLengths.FactorsTable
    lengths: SteelEffectiveLengths.LengthsTable
    standard_of_effective_lengths: SteelEffectiveLengths.StandardOfEffectiveLengths
    determination_of_elastic_critical_stress_aisi: SteelEffectiveLengths.DeterminationOfElasticCriticalStressAisi
    modification_factor_cb_aisi: SteelEffectiveLengths.ModificationFactorCbAisi
    modification_factor_cb_aisi_user_defined_value: float
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., comment: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., flexural_buckling_about_y: bool = ..., flexural_buckling_about_z: bool = ..., torsional_buckling: bool = ..., lateral_torsional_buckling: bool = ..., buckling_factor_value_type: _Optional[_Union[SteelEffectiveLengths.BucklingFactorValueType, str]] = ..., principal_section_axes: bool = ..., geometric_section_axes: bool = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., intermediate_nodes: bool = ..., different_properties: bool = ..., factors_definition_absolute: bool = ..., import_from_stability_analysis_enabled: bool = ..., stability_import_data_factors_definition_absolute: bool = ..., stability_import_data_member_y: _Optional[int] = ..., stability_import_data_loading_y: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., stability_import_data_mode_number_y: _Optional[int] = ..., stability_import_data_member_z: _Optional[int] = ..., stability_import_data_loading_z: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., stability_import_data_mode_number_z: _Optional[int] = ..., stability_import_data_factors: _Optional[_Union[SteelEffectiveLengths.StabilityImportDataFactorsTable, _Mapping]] = ..., stability_import_data_lengths: _Optional[_Union[SteelEffectiveLengths.StabilityImportDataLengthsTable, _Mapping]] = ..., stability_import_data_user_defined_y: bool = ..., stability_import_data_user_defined_z: bool = ..., determination_mcr_europe: _Optional[_Union[SteelEffectiveLengths.DeterminationMcrEurope, str]] = ..., determination_mcr_is800: _Optional[_Union[SteelEffectiveLengths.DeterminationMcrIs800, str]] = ..., determination_mcr_aisc: _Optional[_Union[SteelEffectiveLengths.DeterminationMcrAisc, str]] = ..., determination_mcr_gb50: _Optional[_Union[SteelEffectiveLengths.DeterminationMcrGb50, str]] = ..., determination_mcr_sia263: _Optional[_Union[SteelEffectiveLengths.DeterminationMcrSia263, str]] = ..., determination_mcr_nbr8800: _Optional[_Union[SteelEffectiveLengths.DeterminationMcrNbr8800, str]] = ..., determination_cb_aisc: _Optional[_Union[SteelEffectiveLengths.DeterminationCbAisc, str]] = ..., cb_factor_aisc: _Optional[float] = ..., determination_mcr_csa: _Optional[_Union[SteelEffectiveLengths.DeterminationMcrCsa, str]] = ..., determination_cb_csa: _Optional[_Union[SteelEffectiveLengths.DeterminationCbCsa, str]] = ..., cb_factor_csa: _Optional[float] = ..., determination_mcr_bs5: _Optional[_Union[SteelEffectiveLengths.DeterminationMcrBs5, str]] = ..., determination_cb_nbr: _Optional[_Union[SteelEffectiveLengths.DeterminationCbNbr, str]] = ..., cb_factor_nbr: _Optional[float] = ..., moment_modification_restrained_segments_as: _Optional[_Union[SteelEffectiveLengths.MomentModificationRestrainedSegmentsAs, str]] = ..., moment_modification_unrestrained_segments_as: _Optional[_Union[SteelEffectiveLengths.MomentModificationUnrestrainedSegmentsAs, str]] = ..., slenderness_reduction_restrained_segments_as: _Optional[_Union[SteelEffectiveLengths.SlendernessReductionRestrainedSegmentsAs, str]] = ..., slenderness_reduction_unrestrained_segments_as: _Optional[_Union[SteelEffectiveLengths.SlendernessReductionUnrestrainedSegmentsAs, str]] = ..., modification_factor_alpha_restrained_segments_as: _Optional[float] = ..., modification_factor_alpha_unrestrained_segments_as: _Optional[float] = ..., member_type: _Optional[_Union[SteelEffectiveLengths.MemberType, str]] = ..., member_type_yy: _Optional[_Union[SteelEffectiveLengths.MemberTypeYy, str]] = ..., member_type_zz: _Optional[_Union[SteelEffectiveLengths.MemberTypeZz, str]] = ..., nodal_supports: _Optional[_Union[SteelEffectiveLengths.NodalSupportsTable, _Mapping]] = ..., factors: _Optional[_Union[SteelEffectiveLengths.FactorsTable, _Mapping]] = ..., lengths: _Optional[_Union[SteelEffectiveLengths.LengthsTable, _Mapping]] = ..., standard_of_effective_lengths: _Optional[_Union[SteelEffectiveLengths.StandardOfEffectiveLengths, str]] = ..., determination_of_elastic_critical_stress_aisi: _Optional[_Union[SteelEffectiveLengths.DeterminationOfElasticCriticalStressAisi, str]] = ..., modification_factor_cb_aisi: _Optional[_Union[SteelEffectiveLengths.ModificationFactorCbAisi, str]] = ..., modification_factor_cb_aisi_user_defined_value: _Optional[float] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
