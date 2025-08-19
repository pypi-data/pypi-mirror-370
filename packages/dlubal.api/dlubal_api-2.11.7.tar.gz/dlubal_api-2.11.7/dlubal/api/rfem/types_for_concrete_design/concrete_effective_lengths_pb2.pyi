from dlubal.api.rfem import object_id_pb2 as _object_id_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConcreteEffectiveLengths(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "comment", "members", "member_sets", "lateral_torsional_buckling", "buckling_factor_value_type", "is_generated", "generating_object_info", "intermediate_nodes", "different_properties", "factors_definition_absolute", "fire_design_nodal_supports", "fire_design_factors", "fire_design_lengths", "fire_design_intermediate_nodes", "fire_design_different_properties", "fire_design_factors_definition_absolute", "fire_design_different_buckling_factors", "import_from_stability_analysis_enabled", "stability_import_data_factors_definition_absolute", "stability_import_data_member_y", "stability_import_data_loading_y", "stability_import_data_mode_number_y", "stability_import_data_member_z", "stability_import_data_loading_z", "stability_import_data_mode_number_z", "stability_import_data_factors", "stability_import_data_lengths", "stability_import_data_user_defined_y", "stability_import_data_user_defined_z", "structure_type_about_axis_y", "structure_type_about_axis_z", "structural_scheme_about_axis_y", "structural_scheme_about_axis_z", "flexural_buckling_about_y", "flexural_buckling_about_z", "nodal_supports", "factors", "lengths", "structure_type_about_axis_y_sp63", "structure_type_about_axis_z_sp63", "id_for_export_import", "metadata_for_export_import")
    class BucklingFactorValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BUCKLING_FACTOR_VALUE_TYPE_THEORETICAL: _ClassVar[ConcreteEffectiveLengths.BucklingFactorValueType]
        BUCKLING_FACTOR_VALUE_TYPE_RECOMMENDED: _ClassVar[ConcreteEffectiveLengths.BucklingFactorValueType]
    BUCKLING_FACTOR_VALUE_TYPE_THEORETICAL: ConcreteEffectiveLengths.BucklingFactorValueType
    BUCKLING_FACTOR_VALUE_TYPE_RECOMMENDED: ConcreteEffectiveLengths.BucklingFactorValueType
    class StructureTypeAboutAxisY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STRUCTURE_TYPE_ABOUT_AXIS_Y_UNBRACED: _ClassVar[ConcreteEffectiveLengths.StructureTypeAboutAxisY]
        STRUCTURE_TYPE_ABOUT_AXIS_Y_BRACED: _ClassVar[ConcreteEffectiveLengths.StructureTypeAboutAxisY]
    STRUCTURE_TYPE_ABOUT_AXIS_Y_UNBRACED: ConcreteEffectiveLengths.StructureTypeAboutAxisY
    STRUCTURE_TYPE_ABOUT_AXIS_Y_BRACED: ConcreteEffectiveLengths.StructureTypeAboutAxisY
    class StructureTypeAboutAxisZ(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STRUCTURE_TYPE_ABOUT_AXIS_Z_UNBRACED: _ClassVar[ConcreteEffectiveLengths.StructureTypeAboutAxisZ]
        STRUCTURE_TYPE_ABOUT_AXIS_Z_BRACED: _ClassVar[ConcreteEffectiveLengths.StructureTypeAboutAxisZ]
    STRUCTURE_TYPE_ABOUT_AXIS_Z_UNBRACED: ConcreteEffectiveLengths.StructureTypeAboutAxisZ
    STRUCTURE_TYPE_ABOUT_AXIS_Z_BRACED: ConcreteEffectiveLengths.StructureTypeAboutAxisZ
    class StructuralSchemeAboutAxisY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STRUCTURAL_SCHEME_ABOUT_AXIS_Y_DETERMINED: _ClassVar[ConcreteEffectiveLengths.StructuralSchemeAboutAxisY]
        STRUCTURAL_SCHEME_ABOUT_AXIS_Y_NON_DETERMINED: _ClassVar[ConcreteEffectiveLengths.StructuralSchemeAboutAxisY]
    STRUCTURAL_SCHEME_ABOUT_AXIS_Y_DETERMINED: ConcreteEffectiveLengths.StructuralSchemeAboutAxisY
    STRUCTURAL_SCHEME_ABOUT_AXIS_Y_NON_DETERMINED: ConcreteEffectiveLengths.StructuralSchemeAboutAxisY
    class StructuralSchemeAboutAxisZ(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STRUCTURAL_SCHEME_ABOUT_AXIS_Z_DETERMINED: _ClassVar[ConcreteEffectiveLengths.StructuralSchemeAboutAxisZ]
        STRUCTURAL_SCHEME_ABOUT_AXIS_Z_NON_DETERMINED: _ClassVar[ConcreteEffectiveLengths.StructuralSchemeAboutAxisZ]
    STRUCTURAL_SCHEME_ABOUT_AXIS_Z_DETERMINED: ConcreteEffectiveLengths.StructuralSchemeAboutAxisZ
    STRUCTURAL_SCHEME_ABOUT_AXIS_Z_NON_DETERMINED: ConcreteEffectiveLengths.StructuralSchemeAboutAxisZ
    class StructureTypeAboutAxisYSp63(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STRUCTURE_TYPE_ABOUT_AXIS_Y_SP63_UNBRACED: _ClassVar[ConcreteEffectiveLengths.StructureTypeAboutAxisYSp63]
        STRUCTURE_TYPE_ABOUT_AXIS_Y_SP63_BRACED: _ClassVar[ConcreteEffectiveLengths.StructureTypeAboutAxisYSp63]
        STRUCTURE_TYPE_ABOUT_AXIS_Y_SP63_COMBINED: _ClassVar[ConcreteEffectiveLengths.StructureTypeAboutAxisYSp63]
    STRUCTURE_TYPE_ABOUT_AXIS_Y_SP63_UNBRACED: ConcreteEffectiveLengths.StructureTypeAboutAxisYSp63
    STRUCTURE_TYPE_ABOUT_AXIS_Y_SP63_BRACED: ConcreteEffectiveLengths.StructureTypeAboutAxisYSp63
    STRUCTURE_TYPE_ABOUT_AXIS_Y_SP63_COMBINED: ConcreteEffectiveLengths.StructureTypeAboutAxisYSp63
    class StructureTypeAboutAxisZSp63(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STRUCTURE_TYPE_ABOUT_AXIS_Z_SP63_UNBRACED: _ClassVar[ConcreteEffectiveLengths.StructureTypeAboutAxisZSp63]
        STRUCTURE_TYPE_ABOUT_AXIS_Z_SP63_BRACED: _ClassVar[ConcreteEffectiveLengths.StructureTypeAboutAxisZSp63]
        STRUCTURE_TYPE_ABOUT_AXIS_Z_SP63_COMBINED: _ClassVar[ConcreteEffectiveLengths.StructureTypeAboutAxisZSp63]
    STRUCTURE_TYPE_ABOUT_AXIS_Z_SP63_UNBRACED: ConcreteEffectiveLengths.StructureTypeAboutAxisZSp63
    STRUCTURE_TYPE_ABOUT_AXIS_Z_SP63_BRACED: ConcreteEffectiveLengths.StructureTypeAboutAxisZSp63
    STRUCTURE_TYPE_ABOUT_AXIS_Z_SP63_COMBINED: ConcreteEffectiveLengths.StructureTypeAboutAxisZSp63
    class FireDesignNodalSupportsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[ConcreteEffectiveLengths.FireDesignNodalSupportsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[ConcreteEffectiveLengths.FireDesignNodalSupportsRow, _Mapping]]] = ...) -> None: ...
    class FireDesignNodalSupportsRow(_message.Message):
        __slots__ = ("no", "description", "support_type", "support_in_z", "support_spring_in_y", "eccentricity_type", "eccentricity_ez", "restraint_spring_about_x", "restraint_spring_about_z", "restraint_spring_warping", "support_in_y", "restraint_about_x", "restraint_about_z", "restraint_warping", "nodes")
        class SupportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            SUPPORT_TYPE_NONE: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_ALL: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Y: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION_AND_WARPING: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION_AND_WARPING: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_INDIVIDUALLY: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
            SUPPORT_TYPE_RESTRAINT_ABOUT_X: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType]
        SUPPORT_TYPE_NONE: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_ALL: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Y: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION_AND_WARPING: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION_AND_WARPING: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_INDIVIDUALLY: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        SUPPORT_TYPE_RESTRAINT_ABOUT_X: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        class EccentricityType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            ECCENTRICITY_TYPE_NONE: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_AT_LOWER_FLANGE: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_AT_UPPER_FLANGE: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_USER_VALUE: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType]
        ECCENTRICITY_TYPE_NONE: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_AT_LOWER_FLANGE: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_AT_UPPER_FLANGE: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_USER_VALUE: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType
        class SupportInY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            SUPPORT_IN_Y_SUPPORT_STATUS_NO: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportInY]
            SUPPORT_IN_Y_SUPPORT_STATUS_SPRING: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportInY]
            SUPPORT_IN_Y_SUPPORT_STATUS_YES: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportInY]
        SUPPORT_IN_Y_SUPPORT_STATUS_NO: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportInY
        SUPPORT_IN_Y_SUPPORT_STATUS_SPRING: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportInY
        SUPPORT_IN_Y_SUPPORT_STATUS_YES: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportInY
        class RestraintAboutX(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_NO: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX]
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_SPRING: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX]
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_YES: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX]
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_NO: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_SPRING: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_YES: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX
        class RestraintAboutZ(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_NO: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ]
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_SPRING: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ]
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_YES: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ]
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_NO: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_SPRING: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_YES: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ
        class RestraintWarping(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_WARPING_SUPPORT_STATUS_NO: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintWarping]
            RESTRAINT_WARPING_SUPPORT_STATUS_SPRING: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintWarping]
            RESTRAINT_WARPING_SUPPORT_STATUS_YES: _ClassVar[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintWarping]
        RESTRAINT_WARPING_SUPPORT_STATUS_NO: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintWarping
        RESTRAINT_WARPING_SUPPORT_STATUS_SPRING: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintWarping
        RESTRAINT_WARPING_SUPPORT_STATUS_YES: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintWarping
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
        support_type: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType
        support_in_z: bool
        support_spring_in_y: float
        eccentricity_type: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType
        eccentricity_ez: float
        restraint_spring_about_x: float
        restraint_spring_about_z: float
        restraint_spring_warping: float
        support_in_y: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportInY
        restraint_about_x: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX
        restraint_about_z: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ
        restraint_warping: ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintWarping
        nodes: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., support_type: _Optional[_Union[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportType, str]] = ..., support_in_z: bool = ..., support_spring_in_y: _Optional[float] = ..., eccentricity_type: _Optional[_Union[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.EccentricityType, str]] = ..., eccentricity_ez: _Optional[float] = ..., restraint_spring_about_x: _Optional[float] = ..., restraint_spring_about_z: _Optional[float] = ..., restraint_spring_warping: _Optional[float] = ..., support_in_y: _Optional[_Union[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.SupportInY, str]] = ..., restraint_about_x: _Optional[_Union[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutX, str]] = ..., restraint_about_z: _Optional[_Union[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintAboutZ, str]] = ..., restraint_warping: _Optional[_Union[ConcreteEffectiveLengths.FireDesignNodalSupportsRow.RestraintWarping, str]] = ..., nodes: _Optional[_Iterable[int]] = ...) -> None: ...
    class FireDesignFactorsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[ConcreteEffectiveLengths.FireDesignFactorsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[ConcreteEffectiveLengths.FireDesignFactorsRow, _Mapping]]] = ...) -> None: ...
    class FireDesignFactorsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_y", "flexural_buckling_z", "unbraced_flexural_buckling_y", "unbraced_flexural_buckling_z", "braced_flexural_buckling_y", "braced_flexural_buckling_z")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        UNBRACED_FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        UNBRACED_FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        BRACED_FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        BRACED_FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_y: float
        flexural_buckling_z: float
        unbraced_flexural_buckling_y: float
        unbraced_flexural_buckling_z: float
        braced_flexural_buckling_y: float
        braced_flexural_buckling_z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_y: _Optional[float] = ..., flexural_buckling_z: _Optional[float] = ..., unbraced_flexural_buckling_y: _Optional[float] = ..., unbraced_flexural_buckling_z: _Optional[float] = ..., braced_flexural_buckling_y: _Optional[float] = ..., braced_flexural_buckling_z: _Optional[float] = ...) -> None: ...
    class FireDesignLengthsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[ConcreteEffectiveLengths.FireDesignLengthsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[ConcreteEffectiveLengths.FireDesignLengthsRow, _Mapping]]] = ...) -> None: ...
    class FireDesignLengthsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_y", "flexural_buckling_z", "unbraced_flexural_buckling_y", "unbraced_flexural_buckling_z", "braced_flexural_buckling_y", "braced_flexural_buckling_z")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        UNBRACED_FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        UNBRACED_FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        BRACED_FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        BRACED_FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_y: float
        flexural_buckling_z: float
        unbraced_flexural_buckling_y: float
        unbraced_flexural_buckling_z: float
        braced_flexural_buckling_y: float
        braced_flexural_buckling_z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_y: _Optional[float] = ..., flexural_buckling_z: _Optional[float] = ..., unbraced_flexural_buckling_y: _Optional[float] = ..., unbraced_flexural_buckling_z: _Optional[float] = ..., braced_flexural_buckling_y: _Optional[float] = ..., braced_flexural_buckling_z: _Optional[float] = ...) -> None: ...
    class StabilityImportDataFactorsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[ConcreteEffectiveLengths.StabilityImportDataFactorsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[ConcreteEffectiveLengths.StabilityImportDataFactorsRow, _Mapping]]] = ...) -> None: ...
    class StabilityImportDataFactorsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_y", "flexural_buckling_z", "unbraced_flexural_buckling_y", "unbraced_flexural_buckling_z", "braced_flexural_buckling_y", "braced_flexural_buckling_z")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        UNBRACED_FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        UNBRACED_FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        BRACED_FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        BRACED_FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_y: float
        flexural_buckling_z: float
        unbraced_flexural_buckling_y: float
        unbraced_flexural_buckling_z: float
        braced_flexural_buckling_y: float
        braced_flexural_buckling_z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_y: _Optional[float] = ..., flexural_buckling_z: _Optional[float] = ..., unbraced_flexural_buckling_y: _Optional[float] = ..., unbraced_flexural_buckling_z: _Optional[float] = ..., braced_flexural_buckling_y: _Optional[float] = ..., braced_flexural_buckling_z: _Optional[float] = ...) -> None: ...
    class StabilityImportDataLengthsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[ConcreteEffectiveLengths.StabilityImportDataLengthsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[ConcreteEffectiveLengths.StabilityImportDataLengthsRow, _Mapping]]] = ...) -> None: ...
    class StabilityImportDataLengthsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_y", "flexural_buckling_z", "unbraced_flexural_buckling_y", "unbraced_flexural_buckling_z", "braced_flexural_buckling_y", "braced_flexural_buckling_z")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        UNBRACED_FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        UNBRACED_FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        BRACED_FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        BRACED_FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_y: float
        flexural_buckling_z: float
        unbraced_flexural_buckling_y: float
        unbraced_flexural_buckling_z: float
        braced_flexural_buckling_y: float
        braced_flexural_buckling_z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_y: _Optional[float] = ..., flexural_buckling_z: _Optional[float] = ..., unbraced_flexural_buckling_y: _Optional[float] = ..., unbraced_flexural_buckling_z: _Optional[float] = ..., braced_flexural_buckling_y: _Optional[float] = ..., braced_flexural_buckling_z: _Optional[float] = ...) -> None: ...
    class NodalSupportsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[ConcreteEffectiveLengths.NodalSupportsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[ConcreteEffectiveLengths.NodalSupportsRow, _Mapping]]] = ...) -> None: ...
    class NodalSupportsRow(_message.Message):
        __slots__ = ("no", "description", "support_type", "support_in_z", "support_spring_in_y", "eccentricity_type", "eccentricity_ez", "restraint_spring_about_x", "restraint_spring_about_z", "restraint_spring_warping", "support_in_y", "restraint_about_x", "restraint_about_z", "restraint_warping", "nodes")
        class SupportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            SUPPORT_TYPE_NONE: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_ALL: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Y: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION_AND_WARPING: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION_AND_WARPING: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_INDIVIDUALLY: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.SupportType]
            SUPPORT_TYPE_RESTRAINT_ABOUT_X: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.SupportType]
        SUPPORT_TYPE_NONE: ConcreteEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_ALL: ConcreteEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Y: ConcreteEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z: ConcreteEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION: ConcreteEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_AND_TORSION_AND_WARPING: ConcreteEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION: ConcreteEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION_AND_WARPING: ConcreteEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_INDIVIDUALLY: ConcreteEffectiveLengths.NodalSupportsRow.SupportType
        SUPPORT_TYPE_RESTRAINT_ABOUT_X: ConcreteEffectiveLengths.NodalSupportsRow.SupportType
        class EccentricityType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            ECCENTRICITY_TYPE_NONE: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_AT_LOWER_FLANGE: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_AT_UPPER_FLANGE: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.EccentricityType]
            ECCENTRICITY_TYPE_USER_VALUE: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.EccentricityType]
        ECCENTRICITY_TYPE_NONE: ConcreteEffectiveLengths.NodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_AT_LOWER_FLANGE: ConcreteEffectiveLengths.NodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_AT_UPPER_FLANGE: ConcreteEffectiveLengths.NodalSupportsRow.EccentricityType
        ECCENTRICITY_TYPE_USER_VALUE: ConcreteEffectiveLengths.NodalSupportsRow.EccentricityType
        class SupportInY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            SUPPORT_IN_Y_SUPPORT_STATUS_NO: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.SupportInY]
            SUPPORT_IN_Y_SUPPORT_STATUS_SPRING: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.SupportInY]
            SUPPORT_IN_Y_SUPPORT_STATUS_YES: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.SupportInY]
        SUPPORT_IN_Y_SUPPORT_STATUS_NO: ConcreteEffectiveLengths.NodalSupportsRow.SupportInY
        SUPPORT_IN_Y_SUPPORT_STATUS_SPRING: ConcreteEffectiveLengths.NodalSupportsRow.SupportInY
        SUPPORT_IN_Y_SUPPORT_STATUS_YES: ConcreteEffectiveLengths.NodalSupportsRow.SupportInY
        class RestraintAboutX(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_NO: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutX]
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_SPRING: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutX]
            RESTRAINT_ABOUT_X_SUPPORT_STATUS_YES: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutX]
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_NO: ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutX
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_SPRING: ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutX
        RESTRAINT_ABOUT_X_SUPPORT_STATUS_YES: ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutX
        class RestraintAboutZ(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_NO: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutZ]
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_SPRING: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutZ]
            RESTRAINT_ABOUT_Z_SUPPORT_STATUS_YES: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutZ]
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_NO: ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_SPRING: ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        RESTRAINT_ABOUT_Z_SUPPORT_STATUS_YES: ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        class RestraintWarping(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            RESTRAINT_WARPING_SUPPORT_STATUS_NO: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.RestraintWarping]
            RESTRAINT_WARPING_SUPPORT_STATUS_SPRING: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.RestraintWarping]
            RESTRAINT_WARPING_SUPPORT_STATUS_YES: _ClassVar[ConcreteEffectiveLengths.NodalSupportsRow.RestraintWarping]
        RESTRAINT_WARPING_SUPPORT_STATUS_NO: ConcreteEffectiveLengths.NodalSupportsRow.RestraintWarping
        RESTRAINT_WARPING_SUPPORT_STATUS_SPRING: ConcreteEffectiveLengths.NodalSupportsRow.RestraintWarping
        RESTRAINT_WARPING_SUPPORT_STATUS_YES: ConcreteEffectiveLengths.NodalSupportsRow.RestraintWarping
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
        support_type: ConcreteEffectiveLengths.NodalSupportsRow.SupportType
        support_in_z: bool
        support_spring_in_y: float
        eccentricity_type: ConcreteEffectiveLengths.NodalSupportsRow.EccentricityType
        eccentricity_ez: float
        restraint_spring_about_x: float
        restraint_spring_about_z: float
        restraint_spring_warping: float
        support_in_y: ConcreteEffectiveLengths.NodalSupportsRow.SupportInY
        restraint_about_x: ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutX
        restraint_about_z: ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutZ
        restraint_warping: ConcreteEffectiveLengths.NodalSupportsRow.RestraintWarping
        nodes: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., support_type: _Optional[_Union[ConcreteEffectiveLengths.NodalSupportsRow.SupportType, str]] = ..., support_in_z: bool = ..., support_spring_in_y: _Optional[float] = ..., eccentricity_type: _Optional[_Union[ConcreteEffectiveLengths.NodalSupportsRow.EccentricityType, str]] = ..., eccentricity_ez: _Optional[float] = ..., restraint_spring_about_x: _Optional[float] = ..., restraint_spring_about_z: _Optional[float] = ..., restraint_spring_warping: _Optional[float] = ..., support_in_y: _Optional[_Union[ConcreteEffectiveLengths.NodalSupportsRow.SupportInY, str]] = ..., restraint_about_x: _Optional[_Union[ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutX, str]] = ..., restraint_about_z: _Optional[_Union[ConcreteEffectiveLengths.NodalSupportsRow.RestraintAboutZ, str]] = ..., restraint_warping: _Optional[_Union[ConcreteEffectiveLengths.NodalSupportsRow.RestraintWarping, str]] = ..., nodes: _Optional[_Iterable[int]] = ...) -> None: ...
    class FactorsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[ConcreteEffectiveLengths.FactorsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[ConcreteEffectiveLengths.FactorsRow, _Mapping]]] = ...) -> None: ...
    class FactorsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_y", "flexural_buckling_z", "unbraced_flexural_buckling_y", "unbraced_flexural_buckling_z", "braced_flexural_buckling_y", "braced_flexural_buckling_z")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        UNBRACED_FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        UNBRACED_FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        BRACED_FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        BRACED_FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_y: float
        flexural_buckling_z: float
        unbraced_flexural_buckling_y: float
        unbraced_flexural_buckling_z: float
        braced_flexural_buckling_y: float
        braced_flexural_buckling_z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_y: _Optional[float] = ..., flexural_buckling_z: _Optional[float] = ..., unbraced_flexural_buckling_y: _Optional[float] = ..., unbraced_flexural_buckling_z: _Optional[float] = ..., braced_flexural_buckling_y: _Optional[float] = ..., braced_flexural_buckling_z: _Optional[float] = ...) -> None: ...
    class LengthsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[ConcreteEffectiveLengths.LengthsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[ConcreteEffectiveLengths.LengthsRow, _Mapping]]] = ...) -> None: ...
    class LengthsRow(_message.Message):
        __slots__ = ("no", "description", "flexural_buckling_y", "flexural_buckling_z", "unbraced_flexural_buckling_y", "unbraced_flexural_buckling_z", "braced_flexural_buckling_y", "braced_flexural_buckling_z")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        UNBRACED_FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        UNBRACED_FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        BRACED_FLEXURAL_BUCKLING_Y_FIELD_NUMBER: _ClassVar[int]
        BRACED_FLEXURAL_BUCKLING_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        flexural_buckling_y: float
        flexural_buckling_z: float
        unbraced_flexural_buckling_y: float
        unbraced_flexural_buckling_z: float
        braced_flexural_buckling_y: float
        braced_flexural_buckling_z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., flexural_buckling_y: _Optional[float] = ..., flexural_buckling_z: _Optional[float] = ..., unbraced_flexural_buckling_y: _Optional[float] = ..., unbraced_flexural_buckling_z: _Optional[float] = ..., braced_flexural_buckling_y: _Optional[float] = ..., braced_flexural_buckling_z: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
    BUCKLING_FACTOR_VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIATE_NODES_FIELD_NUMBER: _ClassVar[int]
    DIFFERENT_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    FACTORS_DEFINITION_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
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
    STRUCTURE_TYPE_ABOUT_AXIS_Y_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_TYPE_ABOUT_AXIS_Z_FIELD_NUMBER: _ClassVar[int]
    STRUCTURAL_SCHEME_ABOUT_AXIS_Y_FIELD_NUMBER: _ClassVar[int]
    STRUCTURAL_SCHEME_ABOUT_AXIS_Z_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_ABOUT_Y_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_ABOUT_Z_FIELD_NUMBER: _ClassVar[int]
    NODAL_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    FACTORS_FIELD_NUMBER: _ClassVar[int]
    LENGTHS_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_TYPE_ABOUT_AXIS_Y_SP63_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_TYPE_ABOUT_AXIS_Z_SP63_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    comment: str
    members: _containers.RepeatedScalarFieldContainer[int]
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    lateral_torsional_buckling: bool
    buckling_factor_value_type: ConcreteEffectiveLengths.BucklingFactorValueType
    is_generated: bool
    generating_object_info: str
    intermediate_nodes: bool
    different_properties: bool
    factors_definition_absolute: bool
    fire_design_nodal_supports: ConcreteEffectiveLengths.FireDesignNodalSupportsTable
    fire_design_factors: ConcreteEffectiveLengths.FireDesignFactorsTable
    fire_design_lengths: ConcreteEffectiveLengths.FireDesignLengthsTable
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
    stability_import_data_factors: ConcreteEffectiveLengths.StabilityImportDataFactorsTable
    stability_import_data_lengths: ConcreteEffectiveLengths.StabilityImportDataLengthsTable
    stability_import_data_user_defined_y: bool
    stability_import_data_user_defined_z: bool
    structure_type_about_axis_y: ConcreteEffectiveLengths.StructureTypeAboutAxisY
    structure_type_about_axis_z: ConcreteEffectiveLengths.StructureTypeAboutAxisZ
    structural_scheme_about_axis_y: ConcreteEffectiveLengths.StructuralSchemeAboutAxisY
    structural_scheme_about_axis_z: ConcreteEffectiveLengths.StructuralSchemeAboutAxisZ
    flexural_buckling_about_y: bool
    flexural_buckling_about_z: bool
    nodal_supports: ConcreteEffectiveLengths.NodalSupportsTable
    factors: ConcreteEffectiveLengths.FactorsTable
    lengths: ConcreteEffectiveLengths.LengthsTable
    structure_type_about_axis_y_sp63: ConcreteEffectiveLengths.StructureTypeAboutAxisYSp63
    structure_type_about_axis_z_sp63: ConcreteEffectiveLengths.StructureTypeAboutAxisZSp63
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., comment: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., lateral_torsional_buckling: bool = ..., buckling_factor_value_type: _Optional[_Union[ConcreteEffectiveLengths.BucklingFactorValueType, str]] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., intermediate_nodes: bool = ..., different_properties: bool = ..., factors_definition_absolute: bool = ..., fire_design_nodal_supports: _Optional[_Union[ConcreteEffectiveLengths.FireDesignNodalSupportsTable, _Mapping]] = ..., fire_design_factors: _Optional[_Union[ConcreteEffectiveLengths.FireDesignFactorsTable, _Mapping]] = ..., fire_design_lengths: _Optional[_Union[ConcreteEffectiveLengths.FireDesignLengthsTable, _Mapping]] = ..., fire_design_intermediate_nodes: bool = ..., fire_design_different_properties: bool = ..., fire_design_factors_definition_absolute: bool = ..., fire_design_different_buckling_factors: bool = ..., import_from_stability_analysis_enabled: bool = ..., stability_import_data_factors_definition_absolute: bool = ..., stability_import_data_member_y: _Optional[int] = ..., stability_import_data_loading_y: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., stability_import_data_mode_number_y: _Optional[int] = ..., stability_import_data_member_z: _Optional[int] = ..., stability_import_data_loading_z: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., stability_import_data_mode_number_z: _Optional[int] = ..., stability_import_data_factors: _Optional[_Union[ConcreteEffectiveLengths.StabilityImportDataFactorsTable, _Mapping]] = ..., stability_import_data_lengths: _Optional[_Union[ConcreteEffectiveLengths.StabilityImportDataLengthsTable, _Mapping]] = ..., stability_import_data_user_defined_y: bool = ..., stability_import_data_user_defined_z: bool = ..., structure_type_about_axis_y: _Optional[_Union[ConcreteEffectiveLengths.StructureTypeAboutAxisY, str]] = ..., structure_type_about_axis_z: _Optional[_Union[ConcreteEffectiveLengths.StructureTypeAboutAxisZ, str]] = ..., structural_scheme_about_axis_y: _Optional[_Union[ConcreteEffectiveLengths.StructuralSchemeAboutAxisY, str]] = ..., structural_scheme_about_axis_z: _Optional[_Union[ConcreteEffectiveLengths.StructuralSchemeAboutAxisZ, str]] = ..., flexural_buckling_about_y: bool = ..., flexural_buckling_about_z: bool = ..., nodal_supports: _Optional[_Union[ConcreteEffectiveLengths.NodalSupportsTable, _Mapping]] = ..., factors: _Optional[_Union[ConcreteEffectiveLengths.FactorsTable, _Mapping]] = ..., lengths: _Optional[_Union[ConcreteEffectiveLengths.LengthsTable, _Mapping]] = ..., structure_type_about_axis_y_sp63: _Optional[_Union[ConcreteEffectiveLengths.StructureTypeAboutAxisYSp63, str]] = ..., structure_type_about_axis_z_sp63: _Optional[_Union[ConcreteEffectiveLengths.StructureTypeAboutAxisZSp63, str]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
