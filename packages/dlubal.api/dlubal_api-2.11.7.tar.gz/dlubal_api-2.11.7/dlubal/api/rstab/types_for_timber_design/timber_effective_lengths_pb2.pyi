from dlubal.api.rstab import object_id_pb2 as _object_id_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TimberEffectiveLengths(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "comment", "members", "member_sets", "flexural_buckling_about_y", "flexural_buckling_about_z", "lateral_torsional_buckling", "buckling_factor_value_type", "is_generated", "generating_object_info", "intermediate_nodes", "different_properties", "factors_definition_absolute", "nodal_supports", "factors", "lengths", "fire_design_nodal_supports", "fire_design_factors", "fire_design_lengths", "fire_design_intermediate_nodes", "fire_design_different_properties", "fire_design_factors_definition_absolute", "fire_design_different_buckling_factors", "import_from_stability_analysis_enabled", "stability_import_data_factors_definition_absolute", "stability_import_data_member_y", "stability_import_data_loading_y", "stability_import_data_mode_number_y", "stability_import_data_member_z", "stability_import_data_loading_z", "stability_import_data_mode_number_z", "stability_import_data_factors", "stability_import_data_lengths", "stability_import_data_user_defined_y", "stability_import_data_user_defined_z", "determination_type", "id_for_export_import", "metadata_for_export_import")
    class BucklingFactorValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BUCKLING_FACTOR_VALUE_TYPE_THEORETICAL: _ClassVar[TimberEffectiveLengths.BucklingFactorValueType]
        BUCKLING_FACTOR_VALUE_TYPE_RECOMMENDED: _ClassVar[TimberEffectiveLengths.BucklingFactorValueType]
    BUCKLING_FACTOR_VALUE_TYPE_THEORETICAL: TimberEffectiveLengths.BucklingFactorValueType
    BUCKLING_FACTOR_VALUE_TYPE_RECOMMENDED: TimberEffectiveLengths.BucklingFactorValueType
    class DeterminationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DETERMINATION_TYPE_ANALYTICAL: _ClassVar[TimberEffectiveLengths.DeterminationType]
        DETERMINATION_TYPE_EIGENVALUE_SOLVER: _ClassVar[TimberEffectiveLengths.DeterminationType]
        DETERMINATION_TYPE_USER_DEFINED: _ClassVar[TimberEffectiveLengths.DeterminationType]
    DETERMINATION_TYPE_ANALYTICAL: TimberEffectiveLengths.DeterminationType
    DETERMINATION_TYPE_EIGENVALUE_SOLVER: TimberEffectiveLengths.DeterminationType
    DETERMINATION_TYPE_USER_DEFINED: TimberEffectiveLengths.DeterminationType
    class NodalSupportsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[TimberEffectiveLengths.NodalSupportsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[TimberEffectiveLengths.NodalSupportsRow, _Mapping]]] = ...) -> None: ...
    class NodalSupportsRow(_message.Message):
        __slots__ = ("no", "description", "support_type", "support_in_z", "support_spring_in_y", "eccentricity_type", "eccentricity_ez", "restraint_spring_about_x", "restraint_spring_about_z", "support_in_y", "restraint_about_x", "restraint_about_z", "nodes")
        class SupportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            SUPPORT_TYPE_NONE: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_ALL: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Y: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION_AND_WARPING: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION_AND_WARPING: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_INDIVIDUALLY: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_RESTRAINT_ABOUT_X: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.SupportType]
        SUPPORT_TYPE_NONE: TimberEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_ALL: TimberEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Y: TimberEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z: TimberEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION: TimberEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION_AND_WARPING: TimberEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION: TimberEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION_AND_WARPING: TimberEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_INDIVIDUALLY: TimberEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_RESTRAINT_ABOUT_X: TimberEffectiveLengths.NodalSupportsRow.SupportType
        class EccentricityType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            ECCENTRICITY_TYPE_NONE: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_AT_LOWER_FLANGE: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_AT_UPPER_FLANGE: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_USER_VALUE: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.EccentricityType]
        ECCENTRICITY_TYPE_NONE: TimberEffectiveLengths.NodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_AT_LOWER_FLANGE: TimberEffectiveLengths.NodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_AT_UPPER_FLANGE: TimberEffectiveLengths.NodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_USER_VALUE: TimberEffectiveLengths.NodalSupportsRow.EccentricityType
        class SupportInY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            SUPPORT_IN_Y_SUPPORT_STATUS_NO: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.SupportInY]
            SUPPORT_IN_Y_SUPPORT_STATUS_SPRING: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.SupportInY]
            SUPPORT_IN_Y_SUPPORT_STATUS_YES: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.SupportInY]
        SUPPORT_IN_Y_SUPPORT_STATUS_NO: TimberEffectiveLengths.NodalSupportsRow.SupportInY
        SUPPORT_IN_Y_SUPPORT_STATUS_SPRING: TimberEffectiveLengths.NodalSupportsRow.SupportInY
        SUPPORT_IN_Y_SUPPORT_STATUS_YES: TimberEffectiveLengths.NodalSupportsRow.SupportInY
        class RestraintAboutX(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_NO: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.RestraintAboutX]
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_SPRING: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.RestraintAboutX]
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_YES: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.RestraintAboutX]
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_NO: TimberEffectiveLengths.NodalSupportsRow.RestraintAboutX
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_SPRING: TimberEffectiveLengths.NodalSupportsRow.RestraintAboutX
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_YES: TimberEffectiveLengths.NodalSupportsRow.RestraintAboutX
        class RestraintAboutZ(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_NO: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.RestraintAboutZ]
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_SPRING: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.RestraintAboutZ]
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_YES: _ClassVar[TimberEffectiveLengths.NodalSupportsRow.RestraintAboutZ]
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_NO: TimberEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_SPRING: TimberEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_YES: TimberEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        SUPPORT_TYPE_FIELD_NUMBER: _ClassVar[int]
        SUPPORT_IN_Z_FIELD_NUMBER: _ClassVar[int]
        SUPPORT_SPRING_IN_Y_FIELD_NUMBER: _ClassVar[int]
        ECCENTRICITY_TYPE_FIELD_NUMBER: _ClassVar[int]
        ECCENTRICITY_EZ_FIELD_NUMBER: _ClassVar[int]
        RESTRAINT_SPRING_ABOUT_X_FIELD_NUMBER: _ClassVar[int]
        RESTRAINT_SPRING_ABOUT_Z_FIELD_NUMBER: _ClassVar[int]
        SUPPORT_IN_Y_FIELD_NUMBER: _ClassVar[int]
        RESTRAINT_ABOUT_X_FIELD_NUMBER: _ClassVar[int]
        RESTRAINT_ABOUT_Z_FIELD_NUMBER: _ClassVar[int]
        NODES_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        support_type: TimberEffectiveLengths.NodalSupportsRow.SupportType
        support_in_z: bool
        support_spring_in_y: float
        eccentricity_type: TimberEffectiveLengths.NodalSupportsRow.EccentricityType
        eccentricity_ez: float
        restraint_spring_about_x: float
        restraint_spring_about_z: float
        support_in_y: TimberEffectiveLengths.NodalSupportsRow.SupportInY
        restraint_about_x: TimberEffectiveLengths.NodalSupportsRow.RestraintAboutX
        restraint_about_z: TimberEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        nodes: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., support_type: _Optional[_Union[TimberEffectiveLengths.NodalSupportsRow.SupportType, str]] = ..., support_in_z: bool = ..., support_spring_in_y: _Optional[float] = ..., eccentricity_type: _Optional[_Union[TimberEffectiveLengths.NodalSupportsRow.EccentricityType, str]] = ..., eccentricity_ez: _Optional[float] = ..., restraint_spring_about_x: _Optional[float] = ..., restraint_spring_about_z: _Optional[float] = ..., support_in_y: _Optional[_Union[TimberEffectiveLengths.NodalSupportsRow.SupportInY, str]] = ..., restraint_about_x: _Optional[_Union[TimberEffectiveLengths.NodalSupportsRow.RestraintAboutX, str]] = ..., restraint_about_z: _Optional[_Union[TimberEffectiveLengths.NodalSupportsRow.RestraintAboutZ, str]] = ..., nodes: _Optional[_Iterable[int]] = ...) -> None: ...
    class FactorsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[TimberEffectiveLengths.FactorsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[TimberEffectiveLengths.FactorsRow, _Mapping]]] = ...) -> None: ...
    class FactorsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_u", "flexural_buckling_v", "lateral_torsional_buckling", "lateral_torsional_buckling_top", "lateral_torsional_buckling_bottom", "critical_moment")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_U_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_V_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_TOP_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_BOTTOM_FIELD_NUMBER: _ClassVar[int]
        CRITICAL_MOMENT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_u: float
        flexural_buckling_v: float
        lateral_torsional_buckling: float
        lateral_torsional_buckling_top: float
        lateral_torsional_buckling_bottom: float
        critical_moment: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_u: _Optional[float] = ..., flexural_buckling_v: _Optional[float] = ..., lateral_torsional_buckling: _Optional[float] = ..., lateral_torsional_buckling_top: _Optional[float] = ..., lateral_torsional_buckling_bottom: _Optional[float] = ..., critical_moment: _Optional[float] = ...) -> None: ...
    class LengthsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[TimberEffectiveLengths.LengthsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[TimberEffectiveLengths.LengthsRow, _Mapping]]] = ...) -> None: ...
    class LengthsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_u", "flexural_buckling_v", "lateral_torsional_buckling", "lateral_torsional_buckling_top", "lateral_torsional_buckling_bottom", "critical_moment")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_U_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_V_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_TOP_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_BOTTOM_FIELD_NUMBER: _ClassVar[int]
        CRITICAL_MOMENT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_u: float
        flexural_buckling_v: float
        lateral_torsional_buckling: float
        lateral_torsional_buckling_top: float
        lateral_torsional_buckling_bottom: float
        critical_moment: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_u: _Optional[float] = ..., flexural_buckling_v: _Optional[float] = ..., lateral_torsional_buckling: _Optional[float] = ..., lateral_torsional_buckling_top: _Optional[float] = ..., lateral_torsional_buckling_bottom: _Optional[float] = ..., critical_moment: _Optional[float] = ...) -> None: ...
    class FireDesignNodalSupportsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[TimberEffectiveLengths.FireDesignNodalSupportsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[TimberEffectiveLengths.FireDesignNodalSupportsRow, _Mapping]]] = ...) -> None: ...
    class FireDesignNodalSupportsRow(_message.Message):
        __slots__ = ("no", "description", "support_type", "support_in_z", "support_spring_in_y", "eccentricity_type", "eccentricity_ez", "restraint_spring_about_x", "restraint_spring_about_z", "support_in_y", "restraint_about_x", "restraint_about_z", "nodes")
        class SupportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            SUPPORT_TYPE_NONE: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_ALL: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Y: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION_AND_WARPING: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION_AND_WARPING: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_INDIVIDUALLY: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_RESTRAINT_ABOUT_X: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
        SUPPORT_TYPE_NONE: TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_ALL: TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Y: TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z: TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION: TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION_AND_WARPING: TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION: TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION_AND_WARPING: TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_INDIVIDUALLY: TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_RESTRAINT_ABOUT_X: TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        class EccentricityType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            ECCENTRICITY_TYPE_NONE: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_AT_LOWER_FLANGE: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_AT_UPPER_FLANGE: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_USER_VALUE: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType]
        ECCENTRICITY_TYPE_NONE: TimberEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_AT_LOWER_FLANGE: TimberEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_AT_UPPER_FLANGE: TimberEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_USER_VALUE: TimberEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType
        class SupportInY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            SUPPORT_IN_Y_SUPPORT_STATUS_NO: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportInY]
            SUPPORT_IN_Y_SUPPORT_STATUS_SPRING: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportInY]
            SUPPORT_IN_Y_SUPPORT_STATUS_YES: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportInY]
        SUPPORT_IN_Y_SUPPORT_STATUS_NO: TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportInY
        SUPPORT_IN_Y_SUPPORT_STATUS_SPRING: TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportInY
        SUPPORT_IN_Y_SUPPORT_STATUS_YES: TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportInY
        class RestraintAboutX(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_NO: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX]
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_SPRING: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX]
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_YES: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX]
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_NO: TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_SPRING: TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_YES: TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX
        class RestraintAboutZ(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_NO: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ]
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_SPRING: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ]
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_YES: _ClassVar[TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ]
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_NO: TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_SPRING: TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_YES: TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        SUPPORT_TYPE_FIELD_NUMBER: _ClassVar[int]
        SUPPORT_IN_Z_FIELD_NUMBER: _ClassVar[int]
        SUPPORT_SPRING_IN_Y_FIELD_NUMBER: _ClassVar[int]
        ECCENTRICITY_TYPE_FIELD_NUMBER: _ClassVar[int]
        ECCENTRICITY_EZ_FIELD_NUMBER: _ClassVar[int]
        RESTRAINT_SPRING_ABOUT_X_FIELD_NUMBER: _ClassVar[int]
        RESTRAINT_SPRING_ABOUT_Z_FIELD_NUMBER: _ClassVar[int]
        SUPPORT_IN_Y_FIELD_NUMBER: _ClassVar[int]
        RESTRAINT_ABOUT_X_FIELD_NUMBER: _ClassVar[int]
        RESTRAINT_ABOUT_Z_FIELD_NUMBER: _ClassVar[int]
        NODES_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        support_type: TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        support_in_z: bool
        support_spring_in_y: float
        eccentricity_type: TimberEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType
        eccentricity_ez: float
        restraint_spring_about_x: float
        restraint_spring_about_z: float
        support_in_y: TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportInY
        restraint_about_x: TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX
        restraint_about_z: TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ
        nodes: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., support_type: _Optional[_Union[TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportType, str]] = ..., support_in_z: bool = ..., support_spring_in_y: _Optional[float] = ..., eccentricity_type: _Optional[_Union[TimberEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType, str]] = ..., eccentricity_ez: _Optional[float] = ..., restraint_spring_about_x: _Optional[float] = ..., restraint_spring_about_z: _Optional[float] = ..., support_in_y: _Optional[_Union[TimberEffectiveLengths.FireDesignNodalSupportsRow.SupportInY, str]] = ..., restraint_about_x: _Optional[_Union[TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX, str]] = ..., restraint_about_z: _Optional[_Union[TimberEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ, str]] = ..., nodes: _Optional[_Iterable[int]] = ...) -> None: ...
    class FireDesignFactorsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[TimberEffectiveLengths.FireDesignFactorsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[TimberEffectiveLengths.FireDesignFactorsRow, _Mapping]]] = ...) -> None: ...
    class FireDesignFactorsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_u", "flexural_buckling_v", "lateral_torsional_buckling", "lateral_torsional_buckling_top", "lateral_torsional_buckling_bottom", "critical_moment")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_U_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_V_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_TOP_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_BOTTOM_FIELD_NUMBER: _ClassVar[int]
        CRITICAL_MOMENT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_u: float
        flexural_buckling_v: float
        lateral_torsional_buckling: float
        lateral_torsional_buckling_top: float
        lateral_torsional_buckling_bottom: float
        critical_moment: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_u: _Optional[float] = ..., flexural_buckling_v: _Optional[float] = ..., lateral_torsional_buckling: _Optional[float] = ..., lateral_torsional_buckling_top: _Optional[float] = ..., lateral_torsional_buckling_bottom: _Optional[float] = ..., critical_moment: _Optional[float] = ...) -> None: ...
    class FireDesignLengthsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[TimberEffectiveLengths.FireDesignLengthsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[TimberEffectiveLengths.FireDesignLengthsRow, _Mapping]]] = ...) -> None: ...
    class FireDesignLengthsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_u", "flexural_buckling_v", "lateral_torsional_buckling", "lateral_torsional_buckling_top", "lateral_torsional_buckling_bottom", "critical_moment")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_U_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_V_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_TOP_FIELD_NUMBER: _ClassVar[int]
        LATERAL_TORSIONAL_BUCKLING_BOTTOM_FIELD_NUMBER: _ClassVar[int]
        CRITICAL_MOMENT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_u: float
        flexural_buckling_v: float
        lateral_torsional_buckling: float
        lateral_torsional_buckling_top: float
        lateral_torsional_buckling_bottom: float
        critical_moment: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_u: _Optional[float] = ..., flexural_buckling_v: _Optional[float] = ..., lateral_torsional_buckling: _Optional[float] = ..., lateral_torsional_buckling_top: _Optional[float] = ..., lateral_torsional_buckling_bottom: _Optional[float] = ..., critical_moment: _Optional[float] = ...) -> None: ...
    class StabilityImportDataFactorsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[TimberEffectiveLengths.StabilityImportDataFactorsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[TimberEffectiveLengths.StabilityImportDataFactorsRow, _Mapping]]] = ...) -> None: ...
    class StabilityImportDataFactorsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_u", "flexural_buckling_v")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_U_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_V_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_u: float
        flexural_buckling_v: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_u: _Optional[float] = ..., flexural_buckling_v: _Optional[float] = ...) -> None: ...
    class StabilityImportDataLengthsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[TimberEffectiveLengths.StabilityImportDataLengthsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[TimberEffectiveLengths.StabilityImportDataLengthsRow, _Mapping]]] = ...) -> None: ...
    class StabilityImportDataLengthsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_u", "flexural_buckling_v")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_U_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_V_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_u: float
        flexural_buckling_v: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_u: _Optional[float] = ..., flexural_buckling_v: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_ABOUT_Y_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_ABOUT_Z_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
    BUCKLING_FACTOR_VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIATE_NODES_FIELD_NUMBER: _ClassVar[int]
    DIFFERENT_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    FACTORS_DEFINITION_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    NODAL_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    FACTORS_FIELD_NUMBER: _ClassVar[int]
    LENGTHS_FIELD_NUMBER: _ClassVar[int]
    FIRE_DESIGN_NODAL_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    FIRE_DESIGN_FACTORS_FIELD_NUMBER: _ClassVar[int]
    FIRE_DESIGN_LENGTHS_FIELD_NUMBER: _ClassVar[int]
    FIRE_DESIGN_INTERMEDIATE_NODES_FIELD_NUMBER: _ClassVar[int]
    FIRE_DESIGN_DIFFERENT_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    FIRE_DESIGN_FACTORS_DEFINITION_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    FIRE_DESIGN_DIFFERENT_BUCKLING_FACTORS_FIELD_NUMBER: _ClassVar[int]
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
    DETERMINATION_TYPE_FIELD_NUMBER: _ClassVar[int]
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
    lateral_torsional_buckling: bool
    buckling_factor_value_type: TimberEffectiveLengths.BucklingFactorValueType
    is_generated: bool
    generating_object_info: str
    intermediate_nodes: bool
    different_properties: bool
    factors_definition_absolute: bool
    nodal_supports: TimberEffectiveLengths.NodalSupportsTable
    factors: TimberEffectiveLengths.FactorsTable
    lengths: TimberEffectiveLengths.LengthsTable
    fire_design_nodal_supports: TimberEffectiveLengths.FireDesignNodalSupportsTable
    fire_design_factors: TimberEffectiveLengths.FireDesignFactorsTable
    fire_design_lengths: TimberEffectiveLengths.FireDesignLengthsTable
    fire_design_intermediate_nodes: bool
    fire_design_different_properties: bool
    fire_design_factors_definition_absolute: bool
    fire_design_different_buckling_factors: bool
    import_from_stability_analysis_enabled: bool
    stability_import_data_factors_definition_absolute: bool
    stability_import_data_member_y: int
    stability_import_data_loading_y: _object_id_pb2.ObjectId
    stability_import_data_mode_number_y: int
    stability_import_data_member_z: int
    stability_import_data_loading_z: _object_id_pb2.ObjectId
    stability_import_data_mode_number_z: int
    stability_import_data_factors: TimberEffectiveLengths.StabilityImportDataFactorsTable
    stability_import_data_lengths: TimberEffectiveLengths.StabilityImportDataLengthsTable
    stability_import_data_user_defined_y: bool
    stability_import_data_user_defined_z: bool
    determination_type: TimberEffectiveLengths.DeterminationType
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., comment: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., flexural_buckling_about_y: bool = ..., flexural_buckling_about_z: bool = ..., lateral_torsional_buckling: bool = ..., buckling_factor_value_type: _Optional[_Union[TimberEffectiveLengths.BucklingFactorValueType, str]] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., intermediate_nodes: bool = ..., different_properties: bool = ..., factors_definition_absolute: bool = ..., nodal_supports: _Optional[_Union[TimberEffectiveLengths.NodalSupportsTable, _Mapping]] = ..., factors: _Optional[_Union[TimberEffectiveLengths.FactorsTable, _Mapping]] = ..., lengths: _Optional[_Union[TimberEffectiveLengths.LengthsTable, _Mapping]] = ..., fire_design_nodal_supports: _Optional[_Union[TimberEffectiveLengths.FireDesignNodalSupportsTable, _Mapping]] = ..., fire_design_factors: _Optional[_Union[TimberEffectiveLengths.FireDesignFactorsTable, _Mapping]] = ..., fire_design_lengths: _Optional[_Union[TimberEffectiveLengths.FireDesignLengthsTable, _Mapping]] = ..., fire_design_intermediate_nodes: bool = ..., fire_design_different_properties: bool = ..., fire_design_factors_definition_absolute: bool = ..., fire_design_different_buckling_factors: bool = ..., import_from_stability_analysis_enabled: bool = ..., stability_import_data_factors_definition_absolute: bool = ..., stability_import_data_member_y: _Optional[int] = ..., stability_import_data_loading_y: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., stability_import_data_mode_number_y: _Optional[int] = ..., stability_import_data_member_z: _Optional[int] = ..., stability_import_data_loading_z: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., stability_import_data_mode_number_z: _Optional[int] = ..., stability_import_data_factors: _Optional[_Union[TimberEffectiveLengths.StabilityImportDataFactorsTable, _Mapping]] = ..., stability_import_data_lengths: _Optional[_Union[TimberEffectiveLengths.StabilityImportDataLengthsTable, _Mapping]] = ..., stability_import_data_user_defined_y: bool = ..., stability_import_data_user_defined_z: bool = ..., determination_type: _Optional[_Union[TimberEffectiveLengths.DeterminationType, str]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
