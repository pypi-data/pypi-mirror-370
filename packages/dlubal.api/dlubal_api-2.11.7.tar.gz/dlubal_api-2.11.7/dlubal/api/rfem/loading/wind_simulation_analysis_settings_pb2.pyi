from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WindSimulationAnalysisSettings(_message.Message):
    __slots__ = ("no", "simulation_type", "user_defined_name_enabled", "name", "comment", "assigned_to", "kinematic_viscosity", "numerical_solver", "finite_volume_mesh_density", "maximum_number_of_iterations", "mesh_refinement_type", "snap_to_model_edges", "boundary_layers_checked", "boundary_layers_value", "consider_turbulence", "slip_boundary_condition_on_bottom_boundary", "use_second_order_numerical_scheme", "user_defined_dimensions_of_wind_tunnel", "member_load_distribution", "turbulence_model_type", "sand_grain_roughness_height", "roughness_constant", "user_defined_simulation_time", "velocity_field", "velocity_x_component", "velocity_y_component", "velocity_z_component", "specific_turbulent_dissipation_rate", "start_time_for_saving_transient_results", "steady_flow_from_solver", "turbulence_model_type_for_initial_condition", "turbulent_dissipation_rate", "turbulence_intermittency", "turbulent_kinetic_energy", "turbulent_kinetic_energy_residue_monitors", "turbulence_kinetic_viscosity", "save_solver_data_to_continue_calculation", "simulation_time", "pressure_field", "residual_pressure", "momentum_thickness_reynolds_number", "data_compression_error_tolerance", "consider_surface_roughness", "use_potential_flow_solver_for_initial_condition", "intermediate_transient_master_time_step", "intermediate_transient_results_for_all_time_steps", "intermediate_transient_results_number_of_time_layers", "intermediate_transient_results_time_steps", "id_for_export_import", "metadata_for_export_import")
    class SimulationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SIMULATION_TYPE_STEADY_FLOW: _ClassVar[WindSimulationAnalysisSettings.SimulationType]
        SIMULATION_TYPE_TRANSIENT_FLOW: _ClassVar[WindSimulationAnalysisSettings.SimulationType]
    SIMULATION_TYPE_STEADY_FLOW: WindSimulationAnalysisSettings.SimulationType
    SIMULATION_TYPE_TRANSIENT_FLOW: WindSimulationAnalysisSettings.SimulationType
    class NumericalSolver(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NUMERICAL_SOLVER_OPENFOAM: _ClassVar[WindSimulationAnalysisSettings.NumericalSolver]
    NUMERICAL_SOLVER_OPENFOAM: WindSimulationAnalysisSettings.NumericalSolver
    class MeshRefinementType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MESH_REFINEMENT_TYPE_DISTANCE_FROM_SURFACE: _ClassVar[WindSimulationAnalysisSettings.MeshRefinementType]
        MESH_REFINEMENT_TYPE_SURFACE_CURVATURE: _ClassVar[WindSimulationAnalysisSettings.MeshRefinementType]
    MESH_REFINEMENT_TYPE_DISTANCE_FROM_SURFACE: WindSimulationAnalysisSettings.MeshRefinementType
    MESH_REFINEMENT_TYPE_SURFACE_CURVATURE: WindSimulationAnalysisSettings.MeshRefinementType
    class MemberLoadDistribution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MEMBER_LOAD_DISTRIBUTION_UNIFORM: _ClassVar[WindSimulationAnalysisSettings.MemberLoadDistribution]
        MEMBER_LOAD_DISTRIBUTION_CONCENTRATED: _ClassVar[WindSimulationAnalysisSettings.MemberLoadDistribution]
        MEMBER_LOAD_DISTRIBUTION_TRAPEZOIDAL: _ClassVar[WindSimulationAnalysisSettings.MemberLoadDistribution]
    MEMBER_LOAD_DISTRIBUTION_UNIFORM: WindSimulationAnalysisSettings.MemberLoadDistribution
    MEMBER_LOAD_DISTRIBUTION_CONCENTRATED: WindSimulationAnalysisSettings.MemberLoadDistribution
    MEMBER_LOAD_DISTRIBUTION_TRAPEZOIDAL: WindSimulationAnalysisSettings.MemberLoadDistribution
    class TurbulenceModelType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TURBULENCE_MODEL_TYPE_OMEGA: _ClassVar[WindSimulationAnalysisSettings.TurbulenceModelType]
        TURBULENCE_MODEL_TYPE_EPSILON: _ClassVar[WindSimulationAnalysisSettings.TurbulenceModelType]
        TURBULENCE_MODEL_TYPE_LES: _ClassVar[WindSimulationAnalysisSettings.TurbulenceModelType]
    TURBULENCE_MODEL_TYPE_OMEGA: WindSimulationAnalysisSettings.TurbulenceModelType
    TURBULENCE_MODEL_TYPE_EPSILON: WindSimulationAnalysisSettings.TurbulenceModelType
    TURBULENCE_MODEL_TYPE_LES: WindSimulationAnalysisSettings.TurbulenceModelType
    class TurbulenceModelTypeForInitialCondition(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TURBULENCE_MODEL_TYPE_FOR_INITIAL_CONDITION_OMEGA: _ClassVar[WindSimulationAnalysisSettings.TurbulenceModelTypeForInitialCondition]
        TURBULENCE_MODEL_TYPE_FOR_INITIAL_CONDITION_EPSILON: _ClassVar[WindSimulationAnalysisSettings.TurbulenceModelTypeForInitialCondition]
        TURBULENCE_MODEL_TYPE_FOR_INITIAL_CONDITION_LES: _ClassVar[WindSimulationAnalysisSettings.TurbulenceModelTypeForInitialCondition]
    TURBULENCE_MODEL_TYPE_FOR_INITIAL_CONDITION_OMEGA: WindSimulationAnalysisSettings.TurbulenceModelTypeForInitialCondition
    TURBULENCE_MODEL_TYPE_FOR_INITIAL_CONDITION_EPSILON: WindSimulationAnalysisSettings.TurbulenceModelTypeForInitialCondition
    TURBULENCE_MODEL_TYPE_FOR_INITIAL_CONDITION_LES: WindSimulationAnalysisSettings.TurbulenceModelTypeForInitialCondition
    NO_FIELD_NUMBER: _ClassVar[int]
    SIMULATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    KINEMATIC_VISCOSITY_FIELD_NUMBER: _ClassVar[int]
    NUMERICAL_SOLVER_FIELD_NUMBER: _ClassVar[int]
    FINITE_VOLUME_MESH_DENSITY_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_NUMBER_OF_ITERATIONS_FIELD_NUMBER: _ClassVar[int]
    MESH_REFINEMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SNAP_TO_MODEL_EDGES_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_LAYERS_CHECKED_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_LAYERS_VALUE_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_TURBULENCE_FIELD_NUMBER: _ClassVar[int]
    SLIP_BOUNDARY_CONDITION_ON_BOTTOM_BOUNDARY_FIELD_NUMBER: _ClassVar[int]
    USE_SECOND_ORDER_NUMERICAL_SCHEME_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_DIMENSIONS_OF_WIND_TUNNEL_FIELD_NUMBER: _ClassVar[int]
    MEMBER_LOAD_DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    TURBULENCE_MODEL_TYPE_FIELD_NUMBER: _ClassVar[int]
    SAND_GRAIN_ROUGHNESS_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    ROUGHNESS_CONSTANT_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_SIMULATION_TIME_FIELD_NUMBER: _ClassVar[int]
    VELOCITY_FIELD_FIELD_NUMBER: _ClassVar[int]
    VELOCITY_X_COMPONENT_FIELD_NUMBER: _ClassVar[int]
    VELOCITY_Y_COMPONENT_FIELD_NUMBER: _ClassVar[int]
    VELOCITY_Z_COMPONENT_FIELD_NUMBER: _ClassVar[int]
    SPECIFIC_TURBULENT_DISSIPATION_RATE_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FOR_SAVING_TRANSIENT_RESULTS_FIELD_NUMBER: _ClassVar[int]
    STEADY_FLOW_FROM_SOLVER_FIELD_NUMBER: _ClassVar[int]
    TURBULENCE_MODEL_TYPE_FOR_INITIAL_CONDITION_FIELD_NUMBER: _ClassVar[int]
    TURBULENT_DISSIPATION_RATE_FIELD_NUMBER: _ClassVar[int]
    TURBULENCE_INTERMITTENCY_FIELD_NUMBER: _ClassVar[int]
    TURBULENT_KINETIC_ENERGY_FIELD_NUMBER: _ClassVar[int]
    TURBULENT_KINETIC_ENERGY_RESIDUE_MONITORS_FIELD_NUMBER: _ClassVar[int]
    TURBULENCE_KINETIC_VISCOSITY_FIELD_NUMBER: _ClassVar[int]
    SAVE_SOLVER_DATA_TO_CONTINUE_CALCULATION_FIELD_NUMBER: _ClassVar[int]
    SIMULATION_TIME_FIELD_NUMBER: _ClassVar[int]
    PRESSURE_FIELD_FIELD_NUMBER: _ClassVar[int]
    RESIDUAL_PRESSURE_FIELD_NUMBER: _ClassVar[int]
    MOMENTUM_THICKNESS_REYNOLDS_NUMBER_FIELD_NUMBER: _ClassVar[int]
    DATA_COMPRESSION_ERROR_TOLERANCE_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_SURFACE_ROUGHNESS_FIELD_NUMBER: _ClassVar[int]
    USE_POTENTIAL_FLOW_SOLVER_FOR_INITIAL_CONDITION_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIATE_TRANSIENT_MASTER_TIME_STEP_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIATE_TRANSIENT_RESULTS_FOR_ALL_TIME_STEPS_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIATE_TRANSIENT_RESULTS_NUMBER_OF_TIME_LAYERS_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIATE_TRANSIENT_RESULTS_TIME_STEPS_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    simulation_type: WindSimulationAnalysisSettings.SimulationType
    user_defined_name_enabled: bool
    name: str
    comment: str
    assigned_to: str
    kinematic_viscosity: float
    numerical_solver: WindSimulationAnalysisSettings.NumericalSolver
    finite_volume_mesh_density: float
    maximum_number_of_iterations: int
    mesh_refinement_type: WindSimulationAnalysisSettings.MeshRefinementType
    snap_to_model_edges: bool
    boundary_layers_checked: bool
    boundary_layers_value: int
    consider_turbulence: bool
    slip_boundary_condition_on_bottom_boundary: bool
    use_second_order_numerical_scheme: bool
    user_defined_dimensions_of_wind_tunnel: bool
    member_load_distribution: WindSimulationAnalysisSettings.MemberLoadDistribution
    turbulence_model_type: WindSimulationAnalysisSettings.TurbulenceModelType
    sand_grain_roughness_height: float
    roughness_constant: float
    user_defined_simulation_time: bool
    velocity_field: float
    velocity_x_component: float
    velocity_y_component: float
    velocity_z_component: float
    specific_turbulent_dissipation_rate: float
    start_time_for_saving_transient_results: float
    steady_flow_from_solver: bool
    turbulence_model_type_for_initial_condition: WindSimulationAnalysisSettings.TurbulenceModelTypeForInitialCondition
    turbulent_dissipation_rate: float
    turbulence_intermittency: float
    turbulent_kinetic_energy: float
    turbulent_kinetic_energy_residue_monitors: float
    turbulence_kinetic_viscosity: float
    save_solver_data_to_continue_calculation: bool
    simulation_time: float
    pressure_field: float
    residual_pressure: float
    momentum_thickness_reynolds_number: float
    data_compression_error_tolerance: float
    consider_surface_roughness: bool
    use_potential_flow_solver_for_initial_condition: bool
    intermediate_transient_master_time_step: int
    intermediate_transient_results_for_all_time_steps: bool
    intermediate_transient_results_number_of_time_layers: int
    intermediate_transient_results_time_steps: float
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., simulation_type: _Optional[_Union[WindSimulationAnalysisSettings.SimulationType, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., comment: _Optional[str] = ..., assigned_to: _Optional[str] = ..., kinematic_viscosity: _Optional[float] = ..., numerical_solver: _Optional[_Union[WindSimulationAnalysisSettings.NumericalSolver, str]] = ..., finite_volume_mesh_density: _Optional[float] = ..., maximum_number_of_iterations: _Optional[int] = ..., mesh_refinement_type: _Optional[_Union[WindSimulationAnalysisSettings.MeshRefinementType, str]] = ..., snap_to_model_edges: bool = ..., boundary_layers_checked: bool = ..., boundary_layers_value: _Optional[int] = ..., consider_turbulence: bool = ..., slip_boundary_condition_on_bottom_boundary: bool = ..., use_second_order_numerical_scheme: bool = ..., user_defined_dimensions_of_wind_tunnel: bool = ..., member_load_distribution: _Optional[_Union[WindSimulationAnalysisSettings.MemberLoadDistribution, str]] = ..., turbulence_model_type: _Optional[_Union[WindSimulationAnalysisSettings.TurbulenceModelType, str]] = ..., sand_grain_roughness_height: _Optional[float] = ..., roughness_constant: _Optional[float] = ..., user_defined_simulation_time: bool = ..., velocity_field: _Optional[float] = ..., velocity_x_component: _Optional[float] = ..., velocity_y_component: _Optional[float] = ..., velocity_z_component: _Optional[float] = ..., specific_turbulent_dissipation_rate: _Optional[float] = ..., start_time_for_saving_transient_results: _Optional[float] = ..., steady_flow_from_solver: bool = ..., turbulence_model_type_for_initial_condition: _Optional[_Union[WindSimulationAnalysisSettings.TurbulenceModelTypeForInitialCondition, str]] = ..., turbulent_dissipation_rate: _Optional[float] = ..., turbulence_intermittency: _Optional[float] = ..., turbulent_kinetic_energy: _Optional[float] = ..., turbulent_kinetic_energy_residue_monitors: _Optional[float] = ..., turbulence_kinetic_viscosity: _Optional[float] = ..., save_solver_data_to_continue_calculation: bool = ..., simulation_time: _Optional[float] = ..., pressure_field: _Optional[float] = ..., residual_pressure: _Optional[float] = ..., momentum_thickness_reynolds_number: _Optional[float] = ..., data_compression_error_tolerance: _Optional[float] = ..., consider_surface_roughness: bool = ..., use_potential_flow_solver_for_initial_condition: bool = ..., intermediate_transient_master_time_step: _Optional[int] = ..., intermediate_transient_results_for_all_time_steps: bool = ..., intermediate_transient_results_number_of_time_layers: _Optional[int] = ..., intermediate_transient_results_time_steps: _Optional[float] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
