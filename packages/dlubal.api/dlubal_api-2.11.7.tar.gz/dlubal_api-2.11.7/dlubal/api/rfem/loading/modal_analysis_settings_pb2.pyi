from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModalAnalysisSettings(_message.Message):
    __slots__ = ("no", "acting_masses_about_axis_x_enabled", "acting_masses_about_axis_y_enabled", "acting_masses_about_axis_z_enabled", "acting_masses_in_direction_x_enabled", "acting_masses_in_direction_y_enabled", "acting_masses_in_direction_z_enabled", "activate_minimum_initial_prestress", "minimum_initial_strain", "assigned_to", "comment", "solution_method", "find_eigenvectors_beyond_frequency", "frequency", "mass_conversion_type", "mass_matrix_type", "number_of_modes_method", "maxmimum_natural_frequency", "effective_modal_mass_factor", "number_of_modes", "user_defined_name_enabled", "name", "neglect_masses", "id_for_export_import", "metadata_for_export_import")
    class SolutionMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SOLUTION_METHOD_LANCZOS: _ClassVar[ModalAnalysisSettings.SolutionMethod]
        SOLUTION_METHOD_ROOT_OF_CHARACTERISTIC_POLYNOMIAL: _ClassVar[ModalAnalysisSettings.SolutionMethod]
        SOLUTION_METHOD_SHIFTED_INVERSE_POWER_METHOD: _ClassVar[ModalAnalysisSettings.SolutionMethod]
        SOLUTION_METHOD_SUBSPACE_ITERATION: _ClassVar[ModalAnalysisSettings.SolutionMethod]
    SOLUTION_METHOD_LANCZOS: ModalAnalysisSettings.SolutionMethod
    SOLUTION_METHOD_ROOT_OF_CHARACTERISTIC_POLYNOMIAL: ModalAnalysisSettings.SolutionMethod
    SOLUTION_METHOD_SHIFTED_INVERSE_POWER_METHOD: ModalAnalysisSettings.SolutionMethod
    SOLUTION_METHOD_SUBSPACE_ITERATION: ModalAnalysisSettings.SolutionMethod
    class MassConversionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MASS_CONVERSION_TYPE_Z_COMPONENTS_OF_LOADS: _ClassVar[ModalAnalysisSettings.MassConversionType]
        MASS_CONVERSION_TYPE_FULL_LOADS_AS_MASS: _ClassVar[ModalAnalysisSettings.MassConversionType]
        MASS_CONVERSION_TYPE_Z_COMPONENTS_OF_LOADS_IN_DIRECTION_OF_GRAVITY: _ClassVar[ModalAnalysisSettings.MassConversionType]
    MASS_CONVERSION_TYPE_Z_COMPONENTS_OF_LOADS: ModalAnalysisSettings.MassConversionType
    MASS_CONVERSION_TYPE_FULL_LOADS_AS_MASS: ModalAnalysisSettings.MassConversionType
    MASS_CONVERSION_TYPE_Z_COMPONENTS_OF_LOADS_IN_DIRECTION_OF_GRAVITY: ModalAnalysisSettings.MassConversionType
    class MassMatrixType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MASS_MATRIX_TYPE_DIAGONAL: _ClassVar[ModalAnalysisSettings.MassMatrixType]
        MASS_MATRIX_TYPE_CONSISTENT: _ClassVar[ModalAnalysisSettings.MassMatrixType]
        MASS_MATRIX_TYPE_DIAGONAL_TRANSLATIONAL_AND_ROTATIONAL_DOFS: _ClassVar[ModalAnalysisSettings.MassMatrixType]
        MASS_MATRIX_TYPE_UNIT: _ClassVar[ModalAnalysisSettings.MassMatrixType]
    MASS_MATRIX_TYPE_DIAGONAL: ModalAnalysisSettings.MassMatrixType
    MASS_MATRIX_TYPE_CONSISTENT: ModalAnalysisSettings.MassMatrixType
    MASS_MATRIX_TYPE_DIAGONAL_TRANSLATIONAL_AND_ROTATIONAL_DOFS: ModalAnalysisSettings.MassMatrixType
    MASS_MATRIX_TYPE_UNIT: ModalAnalysisSettings.MassMatrixType
    class NumberOfModesMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NUMBER_OF_MODES_METHOD_USER_DEFINED: _ClassVar[ModalAnalysisSettings.NumberOfModesMethod]
        NUMBER_OF_MODES_METHOD_EFFECTIVE_MASS_FACTORS: _ClassVar[ModalAnalysisSettings.NumberOfModesMethod]
        NUMBER_OF_MODES_METHOD_MAXIMUM_FREQUENCY: _ClassVar[ModalAnalysisSettings.NumberOfModesMethod]
    NUMBER_OF_MODES_METHOD_USER_DEFINED: ModalAnalysisSettings.NumberOfModesMethod
    NUMBER_OF_MODES_METHOD_EFFECTIVE_MASS_FACTORS: ModalAnalysisSettings.NumberOfModesMethod
    NUMBER_OF_MODES_METHOD_MAXIMUM_FREQUENCY: ModalAnalysisSettings.NumberOfModesMethod
    class NeglectMasses(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NEGLECT_MASSES_IN_ALL_FIXED_SUPPORTS: _ClassVar[ModalAnalysisSettings.NeglectMasses]
        NEGLECT_MASSES_NO_NEGLECTION: _ClassVar[ModalAnalysisSettings.NeglectMasses]
        NEGLECT_MASSES_USER_DEFINED: _ClassVar[ModalAnalysisSettings.NeglectMasses]
    NEGLECT_MASSES_IN_ALL_FIXED_SUPPORTS: ModalAnalysisSettings.NeglectMasses
    NEGLECT_MASSES_NO_NEGLECTION: ModalAnalysisSettings.NeglectMasses
    NEGLECT_MASSES_USER_DEFINED: ModalAnalysisSettings.NeglectMasses
    NO_FIELD_NUMBER: _ClassVar[int]
    ACTING_MASSES_ABOUT_AXIS_X_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ACTING_MASSES_ABOUT_AXIS_Y_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ACTING_MASSES_ABOUT_AXIS_Z_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ACTING_MASSES_IN_DIRECTION_X_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ACTING_MASSES_IN_DIRECTION_Y_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ACTING_MASSES_IN_DIRECTION_Z_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ACTIVATE_MINIMUM_INITIAL_PRESTRESS_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_INITIAL_STRAIN_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    SOLUTION_METHOD_FIELD_NUMBER: _ClassVar[int]
    FIND_EIGENVECTORS_BEYOND_FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    MASS_CONVERSION_TYPE_FIELD_NUMBER: _ClassVar[int]
    MASS_MATRIX_TYPE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_MODES_METHOD_FIELD_NUMBER: _ClassVar[int]
    MAXMIMUM_NATURAL_FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_MODAL_MASS_FACTOR_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_MODES_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NEGLECT_MASSES_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    acting_masses_about_axis_x_enabled: bool
    acting_masses_about_axis_y_enabled: bool
    acting_masses_about_axis_z_enabled: bool
    acting_masses_in_direction_x_enabled: bool
    acting_masses_in_direction_y_enabled: bool
    acting_masses_in_direction_z_enabled: bool
    activate_minimum_initial_prestress: bool
    minimum_initial_strain: float
    assigned_to: str
    comment: str
    solution_method: ModalAnalysisSettings.SolutionMethod
    find_eigenvectors_beyond_frequency: bool
    frequency: float
    mass_conversion_type: ModalAnalysisSettings.MassConversionType
    mass_matrix_type: ModalAnalysisSettings.MassMatrixType
    number_of_modes_method: ModalAnalysisSettings.NumberOfModesMethod
    maxmimum_natural_frequency: float
    effective_modal_mass_factor: float
    number_of_modes: int
    user_defined_name_enabled: bool
    name: str
    neglect_masses: ModalAnalysisSettings.NeglectMasses
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., acting_masses_about_axis_x_enabled: bool = ..., acting_masses_about_axis_y_enabled: bool = ..., acting_masses_about_axis_z_enabled: bool = ..., acting_masses_in_direction_x_enabled: bool = ..., acting_masses_in_direction_y_enabled: bool = ..., acting_masses_in_direction_z_enabled: bool = ..., activate_minimum_initial_prestress: bool = ..., minimum_initial_strain: _Optional[float] = ..., assigned_to: _Optional[str] = ..., comment: _Optional[str] = ..., solution_method: _Optional[_Union[ModalAnalysisSettings.SolutionMethod, str]] = ..., find_eigenvectors_beyond_frequency: bool = ..., frequency: _Optional[float] = ..., mass_conversion_type: _Optional[_Union[ModalAnalysisSettings.MassConversionType, str]] = ..., mass_matrix_type: _Optional[_Union[ModalAnalysisSettings.MassMatrixType, str]] = ..., number_of_modes_method: _Optional[_Union[ModalAnalysisSettings.NumberOfModesMethod, str]] = ..., maxmimum_natural_frequency: _Optional[float] = ..., effective_modal_mass_factor: _Optional[float] = ..., number_of_modes: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., neglect_masses: _Optional[_Union[ModalAnalysisSettings.NeglectMasses, str]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
