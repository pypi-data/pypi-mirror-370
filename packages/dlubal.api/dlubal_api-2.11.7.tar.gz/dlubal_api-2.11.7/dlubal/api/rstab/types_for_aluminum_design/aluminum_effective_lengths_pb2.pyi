from dlubal.api.rstab import object_id_pb2 as _object_id_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AluminumEffectiveLengths(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "comment", "members", "member_sets", "flexural_buckling_about_y", "flexural_buckling_about_z", "torsional_buckling", "lateral_torsional_buckling", "buckling_factor_value_type", "principal_section_axes", "geometric_section_axes", "is_generated", "generating_object_info", "factors_definition_absolute", "intermediate_nodes", "different_properties", "determination_mcr_europe", "determination_me_adm", "determination_cb_adm", "cb_factor_adm", "determination_cb_member_type_adm", "nodal_supports", "factors", "lengths", "import_from_stability_analysis_enabled", "stability_import_data_factors_definition_absolute", "stability_import_data_member_y", "stability_import_data_loading_y", "stability_import_data_mode_number_y", "stability_import_data_member_z", "stability_import_data_loading_z", "stability_import_data_mode_number_z", "stability_import_data_factors", "stability_import_data_lengths", "stability_import_data_user_defined_y", "stability_import_data_user_defined_z", "id_for_export_import", "metadata_for_export_import")
    class BucklingFactorValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BUCKLING_FACTOR_VALUE_TYPE_THEORETICAL: _ClassVar[AluminumEffectiveLengths.BucklingFactorValueType]
        BUCKLING_FACTOR_VALUE_TYPE_RECOMMENDED: _ClassVar[AluminumEffectiveLengths.BucklingFactorValueType]
    BUCKLING_FACTOR_VALUE_TYPE_THEORETICAL: AluminumEffectiveLengths.BucklingFactorValueType
    BUCKLING_FACTOR_VALUE_TYPE_RECOMMENDED: AluminumEffectiveLengths.BucklingFactorValueType
    class DeterminationMcrEurope(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_MCR_EUROPE_EIGENVALUE: _ClassVar[AluminumEffectiveLengths.DeterminationMcrEurope]
        DETERMINATION_MCR_EUROPE_USER_DEFINED: _ClassVar[AluminumEffectiveLengths.DeterminationMcrEurope]
    DETERMINATION_MCR_EUROPE_EIGENVALUE: AluminumEffectiveLengths.DeterminationMcrEurope
    DETERMINATION_MCR_EUROPE_USER_DEFINED: AluminumEffectiveLengths.DeterminationMcrEurope
    class DeterminationMeAdm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_ME_ADM_EIGENVALUE_METHOD: _ClassVar[AluminumEffectiveLengths.DeterminationMeAdm]
        DETERMINATION_ME_ADM_ACC_TO_CHAPTER_F: _ClassVar[AluminumEffectiveLengths.DeterminationMeAdm]
        DETERMINATION_ME_ADM_USER_DEFINED: _ClassVar[AluminumEffectiveLengths.DeterminationMeAdm]
    DETERMINATION_ME_ADM_EIGENVALUE_METHOD: AluminumEffectiveLengths.DeterminationMeAdm
    DETERMINATION_ME_ADM_ACC_TO_CHAPTER_F: AluminumEffectiveLengths.DeterminationMeAdm
    DETERMINATION_ME_ADM_USER_DEFINED: AluminumEffectiveLengths.DeterminationMeAdm
    class DeterminationCbAdm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_CB_ADM_BASIC_VALUE: _ClassVar[AluminumEffectiveLengths.DeterminationCbAdm]
        DETERMINATION_CB_ADM_AUTOMATICALLY_ACC_TO_F_4_1: _ClassVar[AluminumEffectiveLengths.DeterminationCbAdm]
        DETERMINATION_CB_ADM_USER_DEFINED: _ClassVar[AluminumEffectiveLengths.DeterminationCbAdm]
    DETERMINATION_CB_ADM_BASIC_VALUE: AluminumEffectiveLengths.DeterminationCbAdm
    DETERMINATION_CB_ADM_AUTOMATICALLY_ACC_TO_F_4_1: AluminumEffectiveLengths.DeterminationCbAdm
    DETERMINATION_CB_ADM_USER_DEFINED: AluminumEffectiveLengths.DeterminationCbAdm
    class DeterminationCbMemberTypeAdm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_CB_MEMBER_TYPE_ADM_BEAM: _ClassVar[AluminumEffectiveLengths.DeterminationCbMemberTypeAdm]
        DETERMINATION_CB_MEMBER_TYPE_ADM_CANTILEVER: _ClassVar[AluminumEffectiveLengths.DeterminationCbMemberTypeAdm]
    DETERMINATION_CB_MEMBER_TYPE_ADM_BEAM: AluminumEffectiveLengths.DeterminationCbMemberTypeAdm
    DETERMINATION_CB_MEMBER_TYPE_ADM_CANTILEVER: AluminumEffectiveLengths.DeterminationCbMemberTypeAdm
    class NodalSupportsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[AluminumEffectiveLengths.NodalSupportsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[AluminumEffectiveLengths.NodalSupportsRow, _Mapping]]] = ...) -> None: ...
    class NodalSupportsRow(_message.Message):
        __slots__ = ("no", "description", "support_type", "support_in_z", "support_spring_in_y", "eccentricity_type", "eccentricity_ez", "restraint_spring_about_x", "restraint_spring_about_z", "restraint_spring_warping", "support_in_y", "restraint_about_x", "restraint_about_z", "restraint_warping", "nodes")
        class SupportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            SUPPORT_TYPE_NONE: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_ALL: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Y: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION_AND_WARPING: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION_AND_WARPING: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_INDIVIDUALLY: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_RESTRAINT_ABOUT_X: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.SupportType]
        SUPPORT_TYPE_NONE: AluminumEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_ALL: AluminumEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Y: AluminumEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z: AluminumEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION: AluminumEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION_AND_WARPING: AluminumEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION: AluminumEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION_AND_WARPING: AluminumEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_INDIVIDUALLY: AluminumEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_RESTRAINT_ABOUT_X: AluminumEffectiveLengths.NodalSupportsRow.SupportType
        class EccentricityType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            ECCENTRICITY_TYPE_NONE: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_AT_LOWER_FLANGE: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_AT_UPPER_FLANGE: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_USER_VALUE: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.EccentricityType]
        ECCENTRICITY_TYPE_NONE: AluminumEffectiveLengths.NodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_AT_LOWER_FLANGE: AluminumEffectiveLengths.NodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_AT_UPPER_FLANGE: AluminumEffectiveLengths.NodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_USER_VALUE: AluminumEffectiveLengths.NodalSupportsRow.EccentricityType
        class SupportInY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            SUPPORT_IN_Y_SUPPORT_STATUS_NO: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.SupportInY]
            SUPPORT_IN_Y_SUPPORT_STATUS_SPRING: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.SupportInY]
            SUPPORT_IN_Y_SUPPORT_STATUS_YES: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.SupportInY]
        SUPPORT_IN_Y_SUPPORT_STATUS_NO: AluminumEffectiveLengths.NodalSupportsRow.SupportInY
        SUPPORT_IN_Y_SUPPORT_STATUS_SPRING: AluminumEffectiveLengths.NodalSupportsRow.SupportInY
        SUPPORT_IN_Y_SUPPORT_STATUS_YES: AluminumEffectiveLengths.NodalSupportsRow.SupportInY
        class RestraintAboutX(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_NO: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutX]
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_SPRING: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutX]
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_YES: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutX]
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_NO: AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutX
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_SPRING: AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutX
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_YES: AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutX
        class RestraintAboutZ(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_NO: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutZ]
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_SPRING: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutZ]
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_YES: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutZ]
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_NO: AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_SPRING: AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_YES: AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        class RestraintWarping(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_WARPING_SUPPORT_STATUS_NO: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.RestraintWarping]
            RESTRAINT_WARPING_SUPPORT_STATUS_SPRING: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.RestraintWarping]
            RESTRAINT_WARPING_SUPPORT_STATUS_YES: _ClassVar[AluminumEffectiveLengths.NodalSupportsRow.RestraintWarping]
        RESTRAINT_WARPING_SUPPORT_STATUS_NO: AluminumEffectiveLengths.NodalSupportsRow.RestraintWarping
        RESTRAINT_WARPING_SUPPORT_STATUS_SPRING: AluminumEffectiveLengths.NodalSupportsRow.RestraintWarping
        RESTRAINT_WARPING_SUPPORT_STATUS_YES: AluminumEffectiveLengths.NodalSupportsRow.RestraintWarping
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
        support_type: AluminumEffectiveLengths.NodalSupportsRow.SupportType
        support_in_z: bool
        support_spring_in_y: float
        eccentricity_type: AluminumEffectiveLengths.NodalSupportsRow.EccentricityType
        eccentricity_ez: float
        restraint_spring_about_x: float
        restraint_spring_about_z: float
        restraint_spring_warping: float
        support_in_y: AluminumEffectiveLengths.NodalSupportsRow.SupportInY
        restraint_about_x: AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutX
        restraint_about_z: AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        restraint_warping: AluminumEffectiveLengths.NodalSupportsRow.RestraintWarping
        nodes: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., support_type: _Optional[_Union[AluminumEffectiveLengths.NodalSupportsRow.SupportType, str]] = ..., support_in_z: bool = ..., support_spring_in_y: _Optional[float] = ..., eccentricity_type: _Optional[_Union[AluminumEffectiveLengths.NodalSupportsRow.EccentricityType, str]] = ..., eccentricity_ez: _Optional[float] = ..., restraint_spring_about_x: _Optional[float] = ..., restraint_spring_about_z: _Optional[float] = ..., restraint_spring_warping: _Optional[float] = ..., support_in_y: _Optional[_Union[AluminumEffectiveLengths.NodalSupportsRow.SupportInY, str]] = ..., restraint_about_x: _Optional[_Union[AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutX, str]] = ..., restraint_about_z: _Optional[_Union[AluminumEffectiveLengths.NodalSupportsRow.RestraintAboutZ, str]] = ..., restraint_warping: _Optional[_Union[AluminumEffectiveLengths.NodalSupportsRow.RestraintWarping, str]] = ..., nodes: _Optional[_Iterable[int]] = ...) -> None: ...
    class FactorsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[AluminumEffectiveLengths.FactorsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[AluminumEffectiveLengths.FactorsRow, _Mapping]]] = ...) -> None: ...
    class FactorsRow(_message.Message):
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
    class LengthsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[AluminumEffectiveLengths.LengthsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[AluminumEffectiveLengths.LengthsRow, _Mapping]]] = ...) -> None: ...
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
    class StabilityImportDataFactorsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[AluminumEffectiveLengths.StabilityImportDataFactorsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[AluminumEffectiveLengths.StabilityImportDataFactorsRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[AluminumEffectiveLengths.StabilityImportDataLengthsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[AluminumEffectiveLengths.StabilityImportDataLengthsRow, _Mapping]]] = ...) -> None: ...
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
    FACTORS_DEFINITION_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIATE_NODES_FIELD_NUMBER: _ClassVar[int]
    DIFFERENT_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_MCR_EUROPE_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_ME_ADM_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_CB_ADM_FIELD_NUMBER: _ClassVar[int]
    CB_FACTOR_ADM_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_CB_MEMBER_TYPE_ADM_FIELD_NUMBER: _ClassVar[int]
    NODAL_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    FACTORS_FIELD_NUMBER: _ClassVar[int]
    LENGTHS_FIELD_NUMBER: _ClassVar[int]
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
    buckling_factor_value_type: AluminumEffectiveLengths.BucklingFactorValueType
    principal_section_axes: bool
    geometric_section_axes: bool
    is_generated: bool
    generating_object_info: str
    factors_definition_absolute: bool
    intermediate_nodes: bool
    different_properties: bool
    determination_mcr_europe: AluminumEffectiveLengths.DeterminationMcrEurope
    determination_me_adm: AluminumEffectiveLengths.DeterminationMeAdm
    determination_cb_adm: AluminumEffectiveLengths.DeterminationCbAdm
    cb_factor_adm: float
    determination_cb_member_type_adm: AluminumEffectiveLengths.DeterminationCbMemberTypeAdm
    nodal_supports: AluminumEffectiveLengths.NodalSupportsTable
    factors: AluminumEffectiveLengths.FactorsTable
    lengths: AluminumEffectiveLengths.LengthsTable
    import_from_stability_analysis_enabled: bool
    stability_import_data_factors_definition_absolute: bool
    stability_import_data_member_y: int
    stability_import_data_loading_y: _object_id_pb2.ObjectId
    stability_import_data_mode_number_y: int
    stability_import_data_member_z: int
    stability_import_data_loading_z: _object_id_pb2.ObjectId
    stability_import_data_mode_number_z: int
    stability_import_data_factors: AluminumEffectiveLengths.StabilityImportDataFactorsTable
    stability_import_data_lengths: AluminumEffectiveLengths.StabilityImportDataLengthsTable
    stability_import_data_user_defined_y: bool
    stability_import_data_user_defined_z: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., comment: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., flexural_buckling_about_y: bool = ..., flexural_buckling_about_z: bool = ..., torsional_buckling: bool = ..., lateral_torsional_buckling: bool = ..., buckling_factor_value_type: _Optional[_Union[AluminumEffectiveLengths.BucklingFactorValueType, str]] = ..., principal_section_axes: bool = ..., geometric_section_axes: bool = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., factors_definition_absolute: bool = ..., intermediate_nodes: bool = ..., different_properties: bool = ..., determination_mcr_europe: _Optional[_Union[AluminumEffectiveLengths.DeterminationMcrEurope, str]] = ..., determination_me_adm: _Optional[_Union[AluminumEffectiveLengths.DeterminationMeAdm, str]] = ..., determination_cb_adm: _Optional[_Union[AluminumEffectiveLengths.DeterminationCbAdm, str]] = ..., cb_factor_adm: _Optional[float] = ..., determination_cb_member_type_adm: _Optional[_Union[AluminumEffectiveLengths.DeterminationCbMemberTypeAdm, str]] = ..., nodal_supports: _Optional[_Union[AluminumEffectiveLengths.NodalSupportsTable, _Mapping]] = ..., factors: _Optional[_Union[AluminumEffectiveLengths.FactorsTable, _Mapping]] = ..., lengths: _Optional[_Union[AluminumEffectiveLengths.LengthsTable, _Mapping]] = ..., import_from_stability_analysis_enabled: bool = ..., stability_import_data_factors_definition_absolute: bool = ..., stability_import_data_member_y: _Optional[int] = ..., stability_import_data_loading_y: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., stability_import_data_mode_number_y: _Optional[int] = ..., stability_import_data_member_z: _Optional[int] = ..., stability_import_data_loading_z: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., stability_import_data_mode_number_z: _Optional[int] = ..., stability_import_data_factors: _Optional[_Union[AluminumEffectiveLengths.StabilityImportDataFactorsTable, _Mapping]] = ..., stability_import_data_lengths: _Optional[_Union[AluminumEffectiveLengths.StabilityImportDataLengthsTable, _Mapping]] = ..., stability_import_data_user_defined_y: bool = ..., stability_import_data_user_defined_z: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
