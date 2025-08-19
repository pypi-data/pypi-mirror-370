from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StaticAnalysisSettings(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "analysis_type", "iterative_method_for_nonlinear_analysis", "max_number_of_iterations", "number_of_load_increments", "standard_precision_and_tolerance_settings_enabled", "ignore_all_nonlinearities_enabled", "precision_of_convergence_criteria_for_nonlinear_calculation", "modify_loading_by_multiplier_factor", "loading_multiplier_factor", "divide_results_by_loading_factor", "consider_favorable_effect_due_to_tension_in_members", "displacements_due_to_bourdon_effect", "save_results_of_all_load_increments", "comment", "refer_internal_forces_to_deformed_structure", "refer_internal_forces_to_deformed_structure_for_normal_forces", "refer_internal_forces_to_deformed_structure_for_shear_forces", "refer_internal_forces_to_deformed_structure_for_moments", "mass_conversion_enabled", "mass_conversion_defined_as_acceleration", "mass_conversion_factor_in_direction_x", "mass_conversion_acceleration_in_direction_x", "mass_conversion_factor_in_direction_y", "mass_conversion_acceleration_in_direction_y", "mass_conversion_factor_in_direction_z", "mass_conversion_acceleration_in_direction_z", "deformation_of_failing_members_and_reactivation_enabled", "maximum_number_of_reactivations", "exceptional_handling_enabled", "assign_reduce_stiffness_enabled", "reduction_factor_of_stiffness", "id_for_export_import", "metadata_for_export_import")
    class AnalysisType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ANALYSIS_TYPE_GEOMETRICALLY_LINEAR: _ClassVar[StaticAnalysisSettings.AnalysisType]
        ANALYSIS_TYPE_LARGE_DEFORMATIONS: _ClassVar[StaticAnalysisSettings.AnalysisType]
        ANALYSIS_TYPE_SECOND_ORDER_P_DELTA: _ClassVar[StaticAnalysisSettings.AnalysisType]
    ANALYSIS_TYPE_GEOMETRICALLY_LINEAR: StaticAnalysisSettings.AnalysisType
    ANALYSIS_TYPE_LARGE_DEFORMATIONS: StaticAnalysisSettings.AnalysisType
    ANALYSIS_TYPE_SECOND_ORDER_P_DELTA: StaticAnalysisSettings.AnalysisType
    class IterativeMethodForNonlinearAnalysis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ITERATIVE_METHOD_FOR_NONLINEAR_ANALYSIS_NEWTON_RAPHSON: _ClassVar[StaticAnalysisSettings.IterativeMethodForNonlinearAnalysis]
        ITERATIVE_METHOD_FOR_NONLINEAR_ANALYSIS_DYNAMIC_RELAXATION: _ClassVar[StaticAnalysisSettings.IterativeMethodForNonlinearAnalysis]
        ITERATIVE_METHOD_FOR_NONLINEAR_ANALYSIS_NEWTON_RAPHSON_COMBINED_WITH_PICARD: _ClassVar[StaticAnalysisSettings.IterativeMethodForNonlinearAnalysis]
        ITERATIVE_METHOD_FOR_NONLINEAR_ANALYSIS_NEWTON_RAPHSON_WITH_CONSTANT_STIFFNESS: _ClassVar[StaticAnalysisSettings.IterativeMethodForNonlinearAnalysis]
        ITERATIVE_METHOD_FOR_NONLINEAR_ANALYSIS_NEWTON_RAPHSON_WITH_POSTCRITICAL_ANALYSIS: _ClassVar[StaticAnalysisSettings.IterativeMethodForNonlinearAnalysis]
        ITERATIVE_METHOD_FOR_NONLINEAR_ANALYSIS_PICARD: _ClassVar[StaticAnalysisSettings.IterativeMethodForNonlinearAnalysis]
    ITERATIVE_METHOD_FOR_NONLINEAR_ANALYSIS_NEWTON_RAPHSON: StaticAnalysisSettings.IterativeMethodForNonlinearAnalysis
    ITERATIVE_METHOD_FOR_NONLINEAR_ANALYSIS_DYNAMIC_RELAXATION: StaticAnalysisSettings.IterativeMethodForNonlinearAnalysis
    ITERATIVE_METHOD_FOR_NONLINEAR_ANALYSIS_NEWTON_RAPHSON_COMBINED_WITH_PICARD: StaticAnalysisSettings.IterativeMethodForNonlinearAnalysis
    ITERATIVE_METHOD_FOR_NONLINEAR_ANALYSIS_NEWTON_RAPHSON_WITH_CONSTANT_STIFFNESS: StaticAnalysisSettings.IterativeMethodForNonlinearAnalysis
    ITERATIVE_METHOD_FOR_NONLINEAR_ANALYSIS_NEWTON_RAPHSON_WITH_POSTCRITICAL_ANALYSIS: StaticAnalysisSettings.IterativeMethodForNonlinearAnalysis
    ITERATIVE_METHOD_FOR_NONLINEAR_ANALYSIS_PICARD: StaticAnalysisSettings.IterativeMethodForNonlinearAnalysis
    class AssignReduceStiffnessEnabled(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ASSIGN_REDUCE_STIFFNESS_ENABLED_FAIILING_MEMBERS_TO_BE_REMOVED_INDIVIDUALY_DURING_SUCCESSIVE_ITERATIONS: _ClassVar[StaticAnalysisSettings.AssignReduceStiffnessEnabled]
        ASSIGN_REDUCE_STIFFNESS_ENABLED_ASSIGN_REDUCED_STIFFNESS_TO_FAILING_MEMBERS: _ClassVar[StaticAnalysisSettings.AssignReduceStiffnessEnabled]
    ASSIGN_REDUCE_STIFFNESS_ENABLED_FAIILING_MEMBERS_TO_BE_REMOVED_INDIVIDUALY_DURING_SUCCESSIVE_ITERATIONS: StaticAnalysisSettings.AssignReduceStiffnessEnabled
    ASSIGN_REDUCE_STIFFNESS_ENABLED_ASSIGN_REDUCED_STIFFNESS_TO_FAILING_MEMBERS: StaticAnalysisSettings.AssignReduceStiffnessEnabled
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    ITERATIVE_METHOD_FOR_NONLINEAR_ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    MAX_NUMBER_OF_ITERATIONS_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_LOAD_INCREMENTS_FIELD_NUMBER: _ClassVar[int]
    STANDARD_PRECISION_AND_TOLERANCE_SETTINGS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    IGNORE_ALL_NONLINEARITIES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    PRECISION_OF_CONVERGENCE_CRITERIA_FOR_NONLINEAR_CALCULATION_FIELD_NUMBER: _ClassVar[int]
    MODIFY_LOADING_BY_MULTIPLIER_FACTOR_FIELD_NUMBER: _ClassVar[int]
    LOADING_MULTIPLIER_FACTOR_FIELD_NUMBER: _ClassVar[int]
    DIVIDE_RESULTS_BY_LOADING_FACTOR_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_FAVORABLE_EFFECT_DUE_TO_TENSION_IN_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    DISPLACEMENTS_DUE_TO_BOURDON_EFFECT_FIELD_NUMBER: _ClassVar[int]
    SAVE_RESULTS_OF_ALL_LOAD_INCREMENTS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    REFER_INTERNAL_FORCES_TO_DEFORMED_STRUCTURE_FIELD_NUMBER: _ClassVar[int]
    REFER_INTERNAL_FORCES_TO_DEFORMED_STRUCTURE_FOR_NORMAL_FORCES_FIELD_NUMBER: _ClassVar[int]
    REFER_INTERNAL_FORCES_TO_DEFORMED_STRUCTURE_FOR_SHEAR_FORCES_FIELD_NUMBER: _ClassVar[int]
    REFER_INTERNAL_FORCES_TO_DEFORMED_STRUCTURE_FOR_MOMENTS_FIELD_NUMBER: _ClassVar[int]
    MASS_CONVERSION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    MASS_CONVERSION_DEFINED_AS_ACCELERATION_FIELD_NUMBER: _ClassVar[int]
    MASS_CONVERSION_FACTOR_IN_DIRECTION_X_FIELD_NUMBER: _ClassVar[int]
    MASS_CONVERSION_ACCELERATION_IN_DIRECTION_X_FIELD_NUMBER: _ClassVar[int]
    MASS_CONVERSION_FACTOR_IN_DIRECTION_Y_FIELD_NUMBER: _ClassVar[int]
    MASS_CONVERSION_ACCELERATION_IN_DIRECTION_Y_FIELD_NUMBER: _ClassVar[int]
    MASS_CONVERSION_FACTOR_IN_DIRECTION_Z_FIELD_NUMBER: _ClassVar[int]
    MASS_CONVERSION_ACCELERATION_IN_DIRECTION_Z_FIELD_NUMBER: _ClassVar[int]
    DEFORMATION_OF_FAILING_MEMBERS_AND_REACTIVATION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_NUMBER_OF_REACTIVATIONS_FIELD_NUMBER: _ClassVar[int]
    EXCEPTIONAL_HANDLING_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ASSIGN_REDUCE_STIFFNESS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    REDUCTION_FACTOR_OF_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    analysis_type: StaticAnalysisSettings.AnalysisType
    iterative_method_for_nonlinear_analysis: StaticAnalysisSettings.IterativeMethodForNonlinearAnalysis
    max_number_of_iterations: int
    number_of_load_increments: int
    standard_precision_and_tolerance_settings_enabled: bool
    ignore_all_nonlinearities_enabled: bool
    precision_of_convergence_criteria_for_nonlinear_calculation: float
    modify_loading_by_multiplier_factor: bool
    loading_multiplier_factor: float
    divide_results_by_loading_factor: bool
    consider_favorable_effect_due_to_tension_in_members: bool
    displacements_due_to_bourdon_effect: bool
    save_results_of_all_load_increments: bool
    comment: str
    refer_internal_forces_to_deformed_structure: bool
    refer_internal_forces_to_deformed_structure_for_normal_forces: bool
    refer_internal_forces_to_deformed_structure_for_shear_forces: bool
    refer_internal_forces_to_deformed_structure_for_moments: bool
    mass_conversion_enabled: bool
    mass_conversion_defined_as_acceleration: bool
    mass_conversion_factor_in_direction_x: float
    mass_conversion_acceleration_in_direction_x: float
    mass_conversion_factor_in_direction_y: float
    mass_conversion_acceleration_in_direction_y: float
    mass_conversion_factor_in_direction_z: float
    mass_conversion_acceleration_in_direction_z: float
    deformation_of_failing_members_and_reactivation_enabled: bool
    maximum_number_of_reactivations: int
    exceptional_handling_enabled: bool
    assign_reduce_stiffness_enabled: StaticAnalysisSettings.AssignReduceStiffnessEnabled
    reduction_factor_of_stiffness: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., analysis_type: _Optional[_Union[StaticAnalysisSettings.AnalysisType, str]] = ..., iterative_method_for_nonlinear_analysis: _Optional[_Union[StaticAnalysisSettings.IterativeMethodForNonlinearAnalysis, str]] = ..., max_number_of_iterations: _Optional[int] = ..., number_of_load_increments: _Optional[int] = ..., standard_precision_and_tolerance_settings_enabled: bool = ..., ignore_all_nonlinearities_enabled: bool = ..., precision_of_convergence_criteria_for_nonlinear_calculation: _Optional[float] = ..., modify_loading_by_multiplier_factor: bool = ..., loading_multiplier_factor: _Optional[float] = ..., divide_results_by_loading_factor: bool = ..., consider_favorable_effect_due_to_tension_in_members: bool = ..., displacements_due_to_bourdon_effect: bool = ..., save_results_of_all_load_increments: bool = ..., comment: _Optional[str] = ..., refer_internal_forces_to_deformed_structure: bool = ..., refer_internal_forces_to_deformed_structure_for_normal_forces: bool = ..., refer_internal_forces_to_deformed_structure_for_shear_forces: bool = ..., refer_internal_forces_to_deformed_structure_for_moments: bool = ..., mass_conversion_enabled: bool = ..., mass_conversion_defined_as_acceleration: bool = ..., mass_conversion_factor_in_direction_x: _Optional[float] = ..., mass_conversion_acceleration_in_direction_x: _Optional[float] = ..., mass_conversion_factor_in_direction_y: _Optional[float] = ..., mass_conversion_acceleration_in_direction_y: _Optional[float] = ..., mass_conversion_factor_in_direction_z: _Optional[float] = ..., mass_conversion_acceleration_in_direction_z: _Optional[float] = ..., deformation_of_failing_members_and_reactivation_enabled: bool = ..., maximum_number_of_reactivations: _Optional[int] = ..., exceptional_handling_enabled: bool = ..., assign_reduce_stiffness_enabled: _Optional[_Union[StaticAnalysisSettings.AssignReduceStiffnessEnabled, str]] = ..., reduction_factor_of_stiffness: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
