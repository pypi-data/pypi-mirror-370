from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TimeHistoryAnalysisSettings(_message.Message):
    __slots__ = ("acting_masses_about_axis_x_enabled", "acting_masses_about_axis_y_enabled", "acting_masses_about_axis_z_enabled", "acting_masses_in_direction_x_enabled", "acting_masses_in_direction_y_enabled", "acting_masses_in_direction_z_enabled", "analysis_type", "assigned_to", "calculate_from_lehrs_damping_enabled", "comment", "damping_type", "lehrs_damping_constant", "lehrs_damping_constant_1", "lehrs_damping_constant_2", "mass_conversion_type", "mass_matrix_type", "maximum_time", "name", "natural_frequency_1", "natural_frequency_2", "neglect_masses", "no", "rayleigh_damping_parameter_alpha", "rayleigh_damping_parameter_beta", "saved_time_step", "split_saved_time_steps", "time_step_for_calculation", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class AnalysisType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ANALYSIS_TYPE_LINEAR_MODAL: _ClassVar[TimeHistoryAnalysisSettings.AnalysisType]
        ANALYSIS_TYPE_LINEAR_IMPLICIT_NEWMARK: _ClassVar[TimeHistoryAnalysisSettings.AnalysisType]
    ANALYSIS_TYPE_LINEAR_MODAL: TimeHistoryAnalysisSettings.AnalysisType
    ANALYSIS_TYPE_LINEAR_IMPLICIT_NEWMARK: TimeHistoryAnalysisSettings.AnalysisType
    class DampingType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DAMPING_TYPE_LEHRS_CONSTANT: _ClassVar[TimeHistoryAnalysisSettings.DampingType]
        DAMPING_TYPE_LEHRS_DIFFERENT_FOR_EACH_MODE: _ClassVar[TimeHistoryAnalysisSettings.DampingType]
        DAMPING_TYPE_RAYLEIGH: _ClassVar[TimeHistoryAnalysisSettings.DampingType]
    DAMPING_TYPE_LEHRS_CONSTANT: TimeHistoryAnalysisSettings.DampingType
    DAMPING_TYPE_LEHRS_DIFFERENT_FOR_EACH_MODE: TimeHistoryAnalysisSettings.DampingType
    DAMPING_TYPE_RAYLEIGH: TimeHistoryAnalysisSettings.DampingType
    class MassConversionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MASS_CONVERSION_TYPE_Z_COMPONENT_OF_LOADS: _ClassVar[TimeHistoryAnalysisSettings.MassConversionType]
        MASS_CONVERSION_TYPE_FULL_LOADS_AS_MASS: _ClassVar[TimeHistoryAnalysisSettings.MassConversionType]
        MASS_CONVERSION_TYPE_Z_COMPONENT_OF_LOADS_IN_DIRECTION_OF_GRAVITY: _ClassVar[TimeHistoryAnalysisSettings.MassConversionType]
    MASS_CONVERSION_TYPE_Z_COMPONENT_OF_LOADS: TimeHistoryAnalysisSettings.MassConversionType
    MASS_CONVERSION_TYPE_FULL_LOADS_AS_MASS: TimeHistoryAnalysisSettings.MassConversionType
    MASS_CONVERSION_TYPE_Z_COMPONENT_OF_LOADS_IN_DIRECTION_OF_GRAVITY: TimeHistoryAnalysisSettings.MassConversionType
    class MassMatrixType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MASS_MATRIX_TYPE_DIAGONAL: _ClassVar[TimeHistoryAnalysisSettings.MassMatrixType]
        MASS_MATRIX_TYPE_CONSISTENT: _ClassVar[TimeHistoryAnalysisSettings.MassMatrixType]
        MASS_MATRIX_TYPE_DIAGONAL_TRANSLATIONAL_AND_ROTATIONAL_DOFS: _ClassVar[TimeHistoryAnalysisSettings.MassMatrixType]
        MASS_MATRIX_TYPE_UNIT: _ClassVar[TimeHistoryAnalysisSettings.MassMatrixType]
    MASS_MATRIX_TYPE_DIAGONAL: TimeHistoryAnalysisSettings.MassMatrixType
    MASS_MATRIX_TYPE_CONSISTENT: TimeHistoryAnalysisSettings.MassMatrixType
    MASS_MATRIX_TYPE_DIAGONAL_TRANSLATIONAL_AND_ROTATIONAL_DOFS: TimeHistoryAnalysisSettings.MassMatrixType
    MASS_MATRIX_TYPE_UNIT: TimeHistoryAnalysisSettings.MassMatrixType
    class NeglectMasses(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NEGLECT_MASSES_IN_ALL_FIXED_SUPPORTS: _ClassVar[TimeHistoryAnalysisSettings.NeglectMasses]
        NEGLECT_MASSES_NO_NEGLECTION: _ClassVar[TimeHistoryAnalysisSettings.NeglectMasses]
        NEGLECT_MASSES_USER_DEFINED: _ClassVar[TimeHistoryAnalysisSettings.NeglectMasses]
    NEGLECT_MASSES_IN_ALL_FIXED_SUPPORTS: TimeHistoryAnalysisSettings.NeglectMasses
    NEGLECT_MASSES_NO_NEGLECTION: TimeHistoryAnalysisSettings.NeglectMasses
    NEGLECT_MASSES_USER_DEFINED: TimeHistoryAnalysisSettings.NeglectMasses
    class TimeStepForCalculation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TIME_STEP_FOR_CALCULATION_AUTOMATIC: _ClassVar[TimeHistoryAnalysisSettings.TimeStepForCalculation]
        TIME_STEP_FOR_CALCULATION_USER_DEFINED: _ClassVar[TimeHistoryAnalysisSettings.TimeStepForCalculation]
    TIME_STEP_FOR_CALCULATION_AUTOMATIC: TimeHistoryAnalysisSettings.TimeStepForCalculation
    TIME_STEP_FOR_CALCULATION_USER_DEFINED: TimeHistoryAnalysisSettings.TimeStepForCalculation
    ACTING_MASSES_ABOUT_AXIS_X_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ACTING_MASSES_ABOUT_AXIS_Y_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ACTING_MASSES_ABOUT_AXIS_Z_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ACTING_MASSES_IN_DIRECTION_X_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ACTING_MASSES_IN_DIRECTION_Y_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ACTING_MASSES_IN_DIRECTION_Z_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    CALCULATE_FROM_LEHRS_DAMPING_ENABLED_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    DAMPING_TYPE_FIELD_NUMBER: _ClassVar[int]
    LEHRS_DAMPING_CONSTANT_FIELD_NUMBER: _ClassVar[int]
    LEHRS_DAMPING_CONSTANT_1_FIELD_NUMBER: _ClassVar[int]
    LEHRS_DAMPING_CONSTANT_2_FIELD_NUMBER: _ClassVar[int]
    MASS_CONVERSION_TYPE_FIELD_NUMBER: _ClassVar[int]
    MASS_MATRIX_TYPE_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_TIME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NATURAL_FREQUENCY_1_FIELD_NUMBER: _ClassVar[int]
    NATURAL_FREQUENCY_2_FIELD_NUMBER: _ClassVar[int]
    NEGLECT_MASSES_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    RAYLEIGH_DAMPING_PARAMETER_ALPHA_FIELD_NUMBER: _ClassVar[int]
    RAYLEIGH_DAMPING_PARAMETER_BETA_FIELD_NUMBER: _ClassVar[int]
    SAVED_TIME_STEP_FIELD_NUMBER: _ClassVar[int]
    SPLIT_SAVED_TIME_STEPS_FIELD_NUMBER: _ClassVar[int]
    TIME_STEP_FOR_CALCULATION_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    acting_masses_about_axis_x_enabled: bool
    acting_masses_about_axis_y_enabled: bool
    acting_masses_about_axis_z_enabled: bool
    acting_masses_in_direction_x_enabled: bool
    acting_masses_in_direction_y_enabled: bool
    acting_masses_in_direction_z_enabled: bool
    analysis_type: TimeHistoryAnalysisSettings.AnalysisType
    assigned_to: str
    calculate_from_lehrs_damping_enabled: bool
    comment: str
    damping_type: TimeHistoryAnalysisSettings.DampingType
    lehrs_damping_constant: float
    lehrs_damping_constant_1: float
    lehrs_damping_constant_2: float
    mass_conversion_type: TimeHistoryAnalysisSettings.MassConversionType
    mass_matrix_type: TimeHistoryAnalysisSettings.MassMatrixType
    maximum_time: float
    name: str
    natural_frequency_1: float
    natural_frequency_2: float
    neglect_masses: TimeHistoryAnalysisSettings.NeglectMasses
    no: int
    rayleigh_damping_parameter_alpha: float
    rayleigh_damping_parameter_beta: float
    saved_time_step: float
    split_saved_time_steps: int
    time_step_for_calculation: TimeHistoryAnalysisSettings.TimeStepForCalculation
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, acting_masses_about_axis_x_enabled: bool = ..., acting_masses_about_axis_y_enabled: bool = ..., acting_masses_about_axis_z_enabled: bool = ..., acting_masses_in_direction_x_enabled: bool = ..., acting_masses_in_direction_y_enabled: bool = ..., acting_masses_in_direction_z_enabled: bool = ..., analysis_type: _Optional[_Union[TimeHistoryAnalysisSettings.AnalysisType, str]] = ..., assigned_to: _Optional[str] = ..., calculate_from_lehrs_damping_enabled: bool = ..., comment: _Optional[str] = ..., damping_type: _Optional[_Union[TimeHistoryAnalysisSettings.DampingType, str]] = ..., lehrs_damping_constant: _Optional[float] = ..., lehrs_damping_constant_1: _Optional[float] = ..., lehrs_damping_constant_2: _Optional[float] = ..., mass_conversion_type: _Optional[_Union[TimeHistoryAnalysisSettings.MassConversionType, str]] = ..., mass_matrix_type: _Optional[_Union[TimeHistoryAnalysisSettings.MassMatrixType, str]] = ..., maximum_time: _Optional[float] = ..., name: _Optional[str] = ..., natural_frequency_1: _Optional[float] = ..., natural_frequency_2: _Optional[float] = ..., neglect_masses: _Optional[_Union[TimeHistoryAnalysisSettings.NeglectMasses, str]] = ..., no: _Optional[int] = ..., rayleigh_damping_parameter_alpha: _Optional[float] = ..., rayleigh_damping_parameter_beta: _Optional[float] = ..., saved_time_step: _Optional[float] = ..., split_saved_time_steps: _Optional[int] = ..., time_step_for_calculation: _Optional[_Union[TimeHistoryAnalysisSettings.TimeStepForCalculation, str]] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
