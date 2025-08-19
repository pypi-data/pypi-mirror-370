from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StabilityAnalysisSettings(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "comment", "assigned_to", "analysis_type", "number_of_lowest_eigenvalues", "considered_favored_effect", "eigenvalue_method", "find_eigenvectors_beyond_critical_load_factor", "critical_load_factor", "calculate_without_loading_for_instability", "activate_minimum_initial_prestress", "minimum_initial_strain", "display_local_torsional_rotations", "local_torsional_rotations", "matrix_type", "initial_load_factor", "load_factor_increment", "refinement_of_the_last_load_increment", "maximum_number_of_load_increments", "activate_stopping_of_load_increasing", "stopping_of_load_increasing_result", "stopping_of_load_increasing_limit_result_displacement", "stopping_of_load_increasing_limit_result_rotation", "stopping_of_load_increasing_limit_node", "save_results_of_all_increments", "id_for_export_import", "metadata_for_export_import")
    class AnalysisType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ANALYSIS_TYPE_EIGENVALUE_METHOD: _ClassVar[StabilityAnalysisSettings.AnalysisType]
        ANALYSIS_TYPE_INCREMENTALY_METHOD_WITHOUT_EIGENVALUE: _ClassVar[StabilityAnalysisSettings.AnalysisType]
        ANALYSIS_TYPE_INCREMENTALY_METHOD_WITH_EIGENVALUE: _ClassVar[StabilityAnalysisSettings.AnalysisType]
        ANALYSIS_TYPE_INCREMENTAL_METHOD_MATERIAL_PARAMETERS_REDUCTION: _ClassVar[StabilityAnalysisSettings.AnalysisType]
    ANALYSIS_TYPE_EIGENVALUE_METHOD: StabilityAnalysisSettings.AnalysisType
    ANALYSIS_TYPE_INCREMENTALY_METHOD_WITHOUT_EIGENVALUE: StabilityAnalysisSettings.AnalysisType
    ANALYSIS_TYPE_INCREMENTALY_METHOD_WITH_EIGENVALUE: StabilityAnalysisSettings.AnalysisType
    ANALYSIS_TYPE_INCREMENTAL_METHOD_MATERIAL_PARAMETERS_REDUCTION: StabilityAnalysisSettings.AnalysisType
    class EigenvalueMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        EIGENVALUE_METHOD_LANCZOS: _ClassVar[StabilityAnalysisSettings.EigenvalueMethod]
        EIGENVALUE_METHOD_ICG_ITERATION: _ClassVar[StabilityAnalysisSettings.EigenvalueMethod]
        EIGENVALUE_METHOD_ROOTS_OF_CHARACTERISTIC_POLYNOMIAL: _ClassVar[StabilityAnalysisSettings.EigenvalueMethod]
        EIGENVALUE_METHOD_SHIFTED_INVERSE_POWER_METHOD: _ClassVar[StabilityAnalysisSettings.EigenvalueMethod]
        EIGENVALUE_METHOD_SUBSPACE_ITERATION: _ClassVar[StabilityAnalysisSettings.EigenvalueMethod]
    EIGENVALUE_METHOD_LANCZOS: StabilityAnalysisSettings.EigenvalueMethod
    EIGENVALUE_METHOD_ICG_ITERATION: StabilityAnalysisSettings.EigenvalueMethod
    EIGENVALUE_METHOD_ROOTS_OF_CHARACTERISTIC_POLYNOMIAL: StabilityAnalysisSettings.EigenvalueMethod
    EIGENVALUE_METHOD_SHIFTED_INVERSE_POWER_METHOD: StabilityAnalysisSettings.EigenvalueMethod
    EIGENVALUE_METHOD_SUBSPACE_ITERATION: StabilityAnalysisSettings.EigenvalueMethod
    class MatrixType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MATRIX_TYPE_STANDARD: _ClassVar[StabilityAnalysisSettings.MatrixType]
        MATRIX_TYPE_UNIT: _ClassVar[StabilityAnalysisSettings.MatrixType]
    MATRIX_TYPE_STANDARD: StabilityAnalysisSettings.MatrixType
    MATRIX_TYPE_UNIT: StabilityAnalysisSettings.MatrixType
    class StoppingOfLoadIncreasingResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STOPPING_OF_LOAD_INCREASING_RESULT_DISPLACEMENT_U: _ClassVar[StabilityAnalysisSettings.StoppingOfLoadIncreasingResult]
        STOPPING_OF_LOAD_INCREASING_RESULT_DISPLACEMENT_U_X: _ClassVar[StabilityAnalysisSettings.StoppingOfLoadIncreasingResult]
        STOPPING_OF_LOAD_INCREASING_RESULT_DISPLACEMENT_U_Y: _ClassVar[StabilityAnalysisSettings.StoppingOfLoadIncreasingResult]
        STOPPING_OF_LOAD_INCREASING_RESULT_DISPLACEMENT_U_Z: _ClassVar[StabilityAnalysisSettings.StoppingOfLoadIncreasingResult]
        STOPPING_OF_LOAD_INCREASING_RESULT_ROTATION_PHI: _ClassVar[StabilityAnalysisSettings.StoppingOfLoadIncreasingResult]
        STOPPING_OF_LOAD_INCREASING_RESULT_ROTATION_PHI_X: _ClassVar[StabilityAnalysisSettings.StoppingOfLoadIncreasingResult]
        STOPPING_OF_LOAD_INCREASING_RESULT_ROTATION_PHI_Y: _ClassVar[StabilityAnalysisSettings.StoppingOfLoadIncreasingResult]
        STOPPING_OF_LOAD_INCREASING_RESULT_ROTATION_PHI_Z: _ClassVar[StabilityAnalysisSettings.StoppingOfLoadIncreasingResult]
    STOPPING_OF_LOAD_INCREASING_RESULT_DISPLACEMENT_U: StabilityAnalysisSettings.StoppingOfLoadIncreasingResult
    STOPPING_OF_LOAD_INCREASING_RESULT_DISPLACEMENT_U_X: StabilityAnalysisSettings.StoppingOfLoadIncreasingResult
    STOPPING_OF_LOAD_INCREASING_RESULT_DISPLACEMENT_U_Y: StabilityAnalysisSettings.StoppingOfLoadIncreasingResult
    STOPPING_OF_LOAD_INCREASING_RESULT_DISPLACEMENT_U_Z: StabilityAnalysisSettings.StoppingOfLoadIncreasingResult
    STOPPING_OF_LOAD_INCREASING_RESULT_ROTATION_PHI: StabilityAnalysisSettings.StoppingOfLoadIncreasingResult
    STOPPING_OF_LOAD_INCREASING_RESULT_ROTATION_PHI_X: StabilityAnalysisSettings.StoppingOfLoadIncreasingResult
    STOPPING_OF_LOAD_INCREASING_RESULT_ROTATION_PHI_Y: StabilityAnalysisSettings.StoppingOfLoadIncreasingResult
    STOPPING_OF_LOAD_INCREASING_RESULT_ROTATION_PHI_Z: StabilityAnalysisSettings.StoppingOfLoadIncreasingResult
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_LOWEST_EIGENVALUES_FIELD_NUMBER: _ClassVar[int]
    CONSIDERED_FAVORED_EFFECT_FIELD_NUMBER: _ClassVar[int]
    EIGENVALUE_METHOD_FIELD_NUMBER: _ClassVar[int]
    FIND_EIGENVECTORS_BEYOND_CRITICAL_LOAD_FACTOR_FIELD_NUMBER: _ClassVar[int]
    CRITICAL_LOAD_FACTOR_FIELD_NUMBER: _ClassVar[int]
    CALCULATE_WITHOUT_LOADING_FOR_INSTABILITY_FIELD_NUMBER: _ClassVar[int]
    ACTIVATE_MINIMUM_INITIAL_PRESTRESS_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_INITIAL_STRAIN_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_LOCAL_TORSIONAL_ROTATIONS_FIELD_NUMBER: _ClassVar[int]
    LOCAL_TORSIONAL_ROTATIONS_FIELD_NUMBER: _ClassVar[int]
    MATRIX_TYPE_FIELD_NUMBER: _ClassVar[int]
    INITIAL_LOAD_FACTOR_FIELD_NUMBER: _ClassVar[int]
    LOAD_FACTOR_INCREMENT_FIELD_NUMBER: _ClassVar[int]
    REFINEMENT_OF_THE_LAST_LOAD_INCREMENT_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_NUMBER_OF_LOAD_INCREMENTS_FIELD_NUMBER: _ClassVar[int]
    ACTIVATE_STOPPING_OF_LOAD_INCREASING_FIELD_NUMBER: _ClassVar[int]
    STOPPING_OF_LOAD_INCREASING_RESULT_FIELD_NUMBER: _ClassVar[int]
    STOPPING_OF_LOAD_INCREASING_LIMIT_RESULT_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    STOPPING_OF_LOAD_INCREASING_LIMIT_RESULT_ROTATION_FIELD_NUMBER: _ClassVar[int]
    STOPPING_OF_LOAD_INCREASING_LIMIT_NODE_FIELD_NUMBER: _ClassVar[int]
    SAVE_RESULTS_OF_ALL_INCREMENTS_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    comment: str
    assigned_to: str
    analysis_type: StabilityAnalysisSettings.AnalysisType
    number_of_lowest_eigenvalues: int
    considered_favored_effect: bool
    eigenvalue_method: StabilityAnalysisSettings.EigenvalueMethod
    find_eigenvectors_beyond_critical_load_factor: bool
    critical_load_factor: float
    calculate_without_loading_for_instability: bool
    activate_minimum_initial_prestress: bool
    minimum_initial_strain: float
    display_local_torsional_rotations: bool
    local_torsional_rotations: float
    matrix_type: StabilityAnalysisSettings.MatrixType
    initial_load_factor: float
    load_factor_increment: float
    refinement_of_the_last_load_increment: int
    maximum_number_of_load_increments: int
    activate_stopping_of_load_increasing: bool
    stopping_of_load_increasing_result: StabilityAnalysisSettings.StoppingOfLoadIncreasingResult
    stopping_of_load_increasing_limit_result_displacement: float
    stopping_of_load_increasing_limit_result_rotation: float
    stopping_of_load_increasing_limit_node: int
    save_results_of_all_increments: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., comment: _Optional[str] = ..., assigned_to: _Optional[str] = ..., analysis_type: _Optional[_Union[StabilityAnalysisSettings.AnalysisType, str]] = ..., number_of_lowest_eigenvalues: _Optional[int] = ..., considered_favored_effect: bool = ..., eigenvalue_method: _Optional[_Union[StabilityAnalysisSettings.EigenvalueMethod, str]] = ..., find_eigenvectors_beyond_critical_load_factor: bool = ..., critical_load_factor: _Optional[float] = ..., calculate_without_loading_for_instability: bool = ..., activate_minimum_initial_prestress: bool = ..., minimum_initial_strain: _Optional[float] = ..., display_local_torsional_rotations: bool = ..., local_torsional_rotations: _Optional[float] = ..., matrix_type: _Optional[_Union[StabilityAnalysisSettings.MatrixType, str]] = ..., initial_load_factor: _Optional[float] = ..., load_factor_increment: _Optional[float] = ..., refinement_of_the_last_load_increment: _Optional[int] = ..., maximum_number_of_load_increments: _Optional[int] = ..., activate_stopping_of_load_increasing: bool = ..., stopping_of_load_increasing_result: _Optional[_Union[StabilityAnalysisSettings.StoppingOfLoadIncreasingResult, str]] = ..., stopping_of_load_increasing_limit_result_displacement: _Optional[float] = ..., stopping_of_load_increasing_limit_result_rotation: _Optional[float] = ..., stopping_of_load_increasing_limit_node: _Optional[int] = ..., save_results_of_all_increments: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
