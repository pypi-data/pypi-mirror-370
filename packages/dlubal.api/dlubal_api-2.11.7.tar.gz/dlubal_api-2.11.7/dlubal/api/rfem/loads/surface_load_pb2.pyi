from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SurfaceLoad(_message.Message):
    __slots__ = ("no", "load_type", "surfaces", "load_case", "load_distribution", "coordinate_system", "load_direction", "uniform_magnitude", "magnitude_1", "magnitude_2", "magnitude_3", "uniform_magnitude_t_c", "magnitude_t_c_1", "magnitude_t_c_2", "magnitude_t_c_3", "uniform_magnitude_delta_t", "magnitude_delta_t_1", "magnitude_delta_t_2", "magnitude_delta_t_3", "magnitude_axial_strain_x", "magnitude_axial_strain_y", "magnitude_axial_strain_1x", "magnitude_axial_strain_1y", "magnitude_axial_strain_2x", "magnitude_axial_strain_2y", "magnitude_axial_strain_3x", "magnitude_axial_strain_3y", "angular_velocity", "angular_acceleration", "node_1", "node_2", "node_3", "axis_definition_type", "axis_definition_p1", "axis_definition_p1_x", "axis_definition_p1_y", "axis_definition_p1_z", "axis_definition_p2", "axis_definition_p2_x", "axis_definition_p2_y", "axis_definition_p2_z", "axis_definition_axis", "axis_definition_axis_orientation", "varying_load_parameters", "varying_load_parameters_sorted", "form_finding_definition", "magnitude_force_u", "magnitude_force_v", "magnitude_force_r", "magnitude_force_t", "magnitude_stress_u", "magnitude_stress_v", "magnitude_stress_r", "magnitude_stress_t", "magnitude_sag", "magnitude_force_scale_x", "magnitude_force_scale_y", "form_finding_calculation_method", "form_finding_sag_related_to_object", "form_finding_sag_related_to_surface", "individual_mass_components", "magnitude_mass_global", "magnitude_mass_y", "magnitude_mass_z", "magnitude_mass_x", "ponding_amount_precipitation", "ponding_magnitude_specific_weight", "ponding_magnitude_amount_precipitation", "comment", "is_generated", "generating_object_info", "magnitude_orthogonal_force_x", "magnitude_orthogonal_force_y", "magnitude_orthogonal_stress_x", "magnitude_orthogonal_stress_y", "magnitude_uniform_force_x", "magnitude_uniform_force_y", "magnitude_uniform_stress_x", "magnitude_uniform_stress_y", "id_for_export_import", "metadata_for_export_import")
    class LoadType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_TYPE_UNKNOWN: _ClassVar[SurfaceLoad.LoadType]
        LOAD_TYPE_AXIAL_STRAIN: _ClassVar[SurfaceLoad.LoadType]
        LOAD_TYPE_FORCE: _ClassVar[SurfaceLoad.LoadType]
        LOAD_TYPE_FORM_FINDING: _ClassVar[SurfaceLoad.LoadType]
        LOAD_TYPE_MASS: _ClassVar[SurfaceLoad.LoadType]
        LOAD_TYPE_PONDING: _ClassVar[SurfaceLoad.LoadType]
        LOAD_TYPE_PRECAMBER: _ClassVar[SurfaceLoad.LoadType]
        LOAD_TYPE_ROTARY_MOTION: _ClassVar[SurfaceLoad.LoadType]
        LOAD_TYPE_SNOW: _ClassVar[SurfaceLoad.LoadType]
        LOAD_TYPE_TEMPERATURE: _ClassVar[SurfaceLoad.LoadType]
    LOAD_TYPE_UNKNOWN: SurfaceLoad.LoadType
    LOAD_TYPE_AXIAL_STRAIN: SurfaceLoad.LoadType
    LOAD_TYPE_FORCE: SurfaceLoad.LoadType
    LOAD_TYPE_FORM_FINDING: SurfaceLoad.LoadType
    LOAD_TYPE_MASS: SurfaceLoad.LoadType
    LOAD_TYPE_PONDING: SurfaceLoad.LoadType
    LOAD_TYPE_PRECAMBER: SurfaceLoad.LoadType
    LOAD_TYPE_ROTARY_MOTION: SurfaceLoad.LoadType
    LOAD_TYPE_SNOW: SurfaceLoad.LoadType
    LOAD_TYPE_TEMPERATURE: SurfaceLoad.LoadType
    class LoadDistribution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DISTRIBUTION_UNIFORM: _ClassVar[SurfaceLoad.LoadDistribution]
        LOAD_DISTRIBUTION_LINEAR: _ClassVar[SurfaceLoad.LoadDistribution]
        LOAD_DISTRIBUTION_LINEAR_IN_X: _ClassVar[SurfaceLoad.LoadDistribution]
        LOAD_DISTRIBUTION_LINEAR_IN_Y: _ClassVar[SurfaceLoad.LoadDistribution]
        LOAD_DISTRIBUTION_LINEAR_IN_Z: _ClassVar[SurfaceLoad.LoadDistribution]
        LOAD_DISTRIBUTION_RADIAL: _ClassVar[SurfaceLoad.LoadDistribution]
        LOAD_DISTRIBUTION_VARYING_IN_Z: _ClassVar[SurfaceLoad.LoadDistribution]
    LOAD_DISTRIBUTION_UNIFORM: SurfaceLoad.LoadDistribution
    LOAD_DISTRIBUTION_LINEAR: SurfaceLoad.LoadDistribution
    LOAD_DISTRIBUTION_LINEAR_IN_X: SurfaceLoad.LoadDistribution
    LOAD_DISTRIBUTION_LINEAR_IN_Y: SurfaceLoad.LoadDistribution
    LOAD_DISTRIBUTION_LINEAR_IN_Z: SurfaceLoad.LoadDistribution
    LOAD_DISTRIBUTION_RADIAL: SurfaceLoad.LoadDistribution
    LOAD_DISTRIBUTION_VARYING_IN_Z: SurfaceLoad.LoadDistribution
    class LoadDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DIRECTION_LOCAL_X: _ClassVar[SurfaceLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED_LENGTH: _ClassVar[SurfaceLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: _ClassVar[SurfaceLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_PROJECTED_LENGTH: _ClassVar[SurfaceLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: _ClassVar[SurfaceLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_PROJECTED_LENGTH: _ClassVar[SurfaceLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: _ClassVar[SurfaceLoad.LoadDirection]
        LOAD_DIRECTION_LOCAL_Y: _ClassVar[SurfaceLoad.LoadDirection]
        LOAD_DIRECTION_LOCAL_Z: _ClassVar[SurfaceLoad.LoadDirection]
    LOAD_DIRECTION_LOCAL_X: SurfaceLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED_LENGTH: SurfaceLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: SurfaceLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_PROJECTED_LENGTH: SurfaceLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: SurfaceLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_PROJECTED_LENGTH: SurfaceLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: SurfaceLoad.LoadDirection
    LOAD_DIRECTION_LOCAL_Y: SurfaceLoad.LoadDirection
    LOAD_DIRECTION_LOCAL_Z: SurfaceLoad.LoadDirection
    class AxisDefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXIS_DEFINITION_TYPE_TWO_POINTS: _ClassVar[SurfaceLoad.AxisDefinitionType]
        AXIS_DEFINITION_TYPE_POINT_AND_AXIS: _ClassVar[SurfaceLoad.AxisDefinitionType]
    AXIS_DEFINITION_TYPE_TWO_POINTS: SurfaceLoad.AxisDefinitionType
    AXIS_DEFINITION_TYPE_POINT_AND_AXIS: SurfaceLoad.AxisDefinitionType
    class AxisDefinitionAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXIS_DEFINITION_AXIS_X: _ClassVar[SurfaceLoad.AxisDefinitionAxis]
        AXIS_DEFINITION_AXIS_Y: _ClassVar[SurfaceLoad.AxisDefinitionAxis]
        AXIS_DEFINITION_AXIS_Z: _ClassVar[SurfaceLoad.AxisDefinitionAxis]
    AXIS_DEFINITION_AXIS_X: SurfaceLoad.AxisDefinitionAxis
    AXIS_DEFINITION_AXIS_Y: SurfaceLoad.AxisDefinitionAxis
    AXIS_DEFINITION_AXIS_Z: SurfaceLoad.AxisDefinitionAxis
    class AxisDefinitionAxisOrientation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXIS_DEFINITION_AXIS_ORIENTATION_POSITIVE: _ClassVar[SurfaceLoad.AxisDefinitionAxisOrientation]
        AXIS_DEFINITION_AXIS_ORIENTATION_NEGATIVE: _ClassVar[SurfaceLoad.AxisDefinitionAxisOrientation]
    AXIS_DEFINITION_AXIS_ORIENTATION_POSITIVE: SurfaceLoad.AxisDefinitionAxisOrientation
    AXIS_DEFINITION_AXIS_ORIENTATION_NEGATIVE: SurfaceLoad.AxisDefinitionAxisOrientation
    class FormFindingDefinition(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FORM_FINDING_DEFINITION_FORCE: _ClassVar[SurfaceLoad.FormFindingDefinition]
        FORM_FINDING_DEFINITION_SAG: _ClassVar[SurfaceLoad.FormFindingDefinition]
        FORM_FINDING_DEFINITION_STRESS: _ClassVar[SurfaceLoad.FormFindingDefinition]
    FORM_FINDING_DEFINITION_FORCE: SurfaceLoad.FormFindingDefinition
    FORM_FINDING_DEFINITION_SAG: SurfaceLoad.FormFindingDefinition
    FORM_FINDING_DEFINITION_STRESS: SurfaceLoad.FormFindingDefinition
    class FormFindingCalculationMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FORM_FINDING_CALCULATION_METHOD_STANDARD: _ClassVar[SurfaceLoad.FormFindingCalculationMethod]
        FORM_FINDING_CALCULATION_METHOD_PROJECTION: _ClassVar[SurfaceLoad.FormFindingCalculationMethod]
    FORM_FINDING_CALCULATION_METHOD_STANDARD: SurfaceLoad.FormFindingCalculationMethod
    FORM_FINDING_CALCULATION_METHOD_PROJECTION: SurfaceLoad.FormFindingCalculationMethod
    class FormFindingSagRelatedToObject(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FORM_FINDING_SAG_RELATED_TO_OBJECT_BASE: _ClassVar[SurfaceLoad.FormFindingSagRelatedToObject]
        FORM_FINDING_SAG_RELATED_TO_OBJECT_CS: _ClassVar[SurfaceLoad.FormFindingSagRelatedToObject]
        FORM_FINDING_SAG_RELATED_TO_OBJECT_SURFACE: _ClassVar[SurfaceLoad.FormFindingSagRelatedToObject]
    FORM_FINDING_SAG_RELATED_TO_OBJECT_BASE: SurfaceLoad.FormFindingSagRelatedToObject
    FORM_FINDING_SAG_RELATED_TO_OBJECT_CS: SurfaceLoad.FormFindingSagRelatedToObject
    FORM_FINDING_SAG_RELATED_TO_OBJECT_SURFACE: SurfaceLoad.FormFindingSagRelatedToObject
    class VaryingLoadParametersTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[SurfaceLoad.VaryingLoadParametersRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[SurfaceLoad.VaryingLoadParametersRow, _Mapping]]] = ...) -> None: ...
    class VaryingLoadParametersRow(_message.Message):
        __slots__ = ("no", "description", "distance", "delta_distance", "magnitude", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        DISTANCE_FIELD_NUMBER: _ClassVar[int]
        DELTA_DISTANCE_FIELD_NUMBER: _ClassVar[int]
        MAGNITUDE_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        distance: float
        delta_distance: float
        magnitude: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., distance: _Optional[float] = ..., delta_distance: _Optional[float] = ..., magnitude: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    LOAD_TYPE_FIELD_NUMBER: _ClassVar[int]
    SURFACES_FIELD_NUMBER: _ClassVar[int]
    LOAD_CASE_FIELD_NUMBER: _ClassVar[int]
    LOAD_DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    LOAD_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    UNIFORM_MAGNITUDE_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_1_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_2_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_3_FIELD_NUMBER: _ClassVar[int]
    UNIFORM_MAGNITUDE_T_C_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_T_C_1_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_T_C_2_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_T_C_3_FIELD_NUMBER: _ClassVar[int]
    UNIFORM_MAGNITUDE_DELTA_T_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_DELTA_T_1_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_DELTA_T_2_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_DELTA_T_3_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_AXIAL_STRAIN_X_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_AXIAL_STRAIN_Y_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_AXIAL_STRAIN_1X_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_AXIAL_STRAIN_1Y_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_AXIAL_STRAIN_2X_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_AXIAL_STRAIN_2Y_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_AXIAL_STRAIN_3X_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_AXIAL_STRAIN_3Y_FIELD_NUMBER: _ClassVar[int]
    ANGULAR_VELOCITY_FIELD_NUMBER: _ClassVar[int]
    ANGULAR_ACCELERATION_FIELD_NUMBER: _ClassVar[int]
    NODE_1_FIELD_NUMBER: _ClassVar[int]
    NODE_2_FIELD_NUMBER: _ClassVar[int]
    NODE_3_FIELD_NUMBER: _ClassVar[int]
    AXIS_DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    AXIS_DEFINITION_P1_FIELD_NUMBER: _ClassVar[int]
    AXIS_DEFINITION_P1_X_FIELD_NUMBER: _ClassVar[int]
    AXIS_DEFINITION_P1_Y_FIELD_NUMBER: _ClassVar[int]
    AXIS_DEFINITION_P1_Z_FIELD_NUMBER: _ClassVar[int]
    AXIS_DEFINITION_P2_FIELD_NUMBER: _ClassVar[int]
    AXIS_DEFINITION_P2_X_FIELD_NUMBER: _ClassVar[int]
    AXIS_DEFINITION_P2_Y_FIELD_NUMBER: _ClassVar[int]
    AXIS_DEFINITION_P2_Z_FIELD_NUMBER: _ClassVar[int]
    AXIS_DEFINITION_AXIS_FIELD_NUMBER: _ClassVar[int]
    AXIS_DEFINITION_AXIS_ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    VARYING_LOAD_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    VARYING_LOAD_PARAMETERS_SORTED_FIELD_NUMBER: _ClassVar[int]
    FORM_FINDING_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_FORCE_U_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_FORCE_V_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_FORCE_R_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_FORCE_T_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_STRESS_U_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_STRESS_V_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_STRESS_R_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_STRESS_T_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_SAG_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_FORCE_SCALE_X_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_FORCE_SCALE_Y_FIELD_NUMBER: _ClassVar[int]
    FORM_FINDING_CALCULATION_METHOD_FIELD_NUMBER: _ClassVar[int]
    FORM_FINDING_SAG_RELATED_TO_OBJECT_FIELD_NUMBER: _ClassVar[int]
    FORM_FINDING_SAG_RELATED_TO_SURFACE_FIELD_NUMBER: _ClassVar[int]
    INDIVIDUAL_MASS_COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_MASS_GLOBAL_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_MASS_Y_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_MASS_Z_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_MASS_X_FIELD_NUMBER: _ClassVar[int]
    PONDING_AMOUNT_PRECIPITATION_FIELD_NUMBER: _ClassVar[int]
    PONDING_MAGNITUDE_SPECIFIC_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    PONDING_MAGNITUDE_AMOUNT_PRECIPITATION_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_ORTHOGONAL_FORCE_X_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_ORTHOGONAL_FORCE_Y_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_ORTHOGONAL_STRESS_X_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_ORTHOGONAL_STRESS_Y_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_UNIFORM_FORCE_X_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_UNIFORM_FORCE_Y_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_UNIFORM_STRESS_X_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_UNIFORM_STRESS_Y_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    load_type: SurfaceLoad.LoadType
    surfaces: _containers.RepeatedScalarFieldContainer[int]
    load_case: int
    load_distribution: SurfaceLoad.LoadDistribution
    coordinate_system: _common_pb2.CoordinateSystemRepresentation
    load_direction: SurfaceLoad.LoadDirection
    uniform_magnitude: float
    magnitude_1: float
    magnitude_2: float
    magnitude_3: float
    uniform_magnitude_t_c: float
    magnitude_t_c_1: float
    magnitude_t_c_2: float
    magnitude_t_c_3: float
    uniform_magnitude_delta_t: float
    magnitude_delta_t_1: float
    magnitude_delta_t_2: float
    magnitude_delta_t_3: float
    magnitude_axial_strain_x: float
    magnitude_axial_strain_y: float
    magnitude_axial_strain_1x: float
    magnitude_axial_strain_1y: float
    magnitude_axial_strain_2x: float
    magnitude_axial_strain_2y: float
    magnitude_axial_strain_3x: float
    magnitude_axial_strain_3y: float
    angular_velocity: float
    angular_acceleration: float
    node_1: int
    node_2: int
    node_3: int
    axis_definition_type: SurfaceLoad.AxisDefinitionType
    axis_definition_p1: _common_pb2.Vector3d
    axis_definition_p1_x: float
    axis_definition_p1_y: float
    axis_definition_p1_z: float
    axis_definition_p2: _common_pb2.Vector3d
    axis_definition_p2_x: float
    axis_definition_p2_y: float
    axis_definition_p2_z: float
    axis_definition_axis: SurfaceLoad.AxisDefinitionAxis
    axis_definition_axis_orientation: SurfaceLoad.AxisDefinitionAxisOrientation
    varying_load_parameters: SurfaceLoad.VaryingLoadParametersTable
    varying_load_parameters_sorted: bool
    form_finding_definition: SurfaceLoad.FormFindingDefinition
    magnitude_force_u: float
    magnitude_force_v: float
    magnitude_force_r: float
    magnitude_force_t: float
    magnitude_stress_u: float
    magnitude_stress_v: float
    magnitude_stress_r: float
    magnitude_stress_t: float
    magnitude_sag: float
    magnitude_force_scale_x: float
    magnitude_force_scale_y: float
    form_finding_calculation_method: SurfaceLoad.FormFindingCalculationMethod
    form_finding_sag_related_to_object: SurfaceLoad.FormFindingSagRelatedToObject
    form_finding_sag_related_to_surface: int
    individual_mass_components: bool
    magnitude_mass_global: float
    magnitude_mass_y: float
    magnitude_mass_z: float
    magnitude_mass_x: float
    ponding_amount_precipitation: bool
    ponding_magnitude_specific_weight: float
    ponding_magnitude_amount_precipitation: float
    comment: str
    is_generated: bool
    generating_object_info: str
    magnitude_orthogonal_force_x: float
    magnitude_orthogonal_force_y: float
    magnitude_orthogonal_stress_x: float
    magnitude_orthogonal_stress_y: float
    magnitude_uniform_force_x: float
    magnitude_uniform_force_y: float
    magnitude_uniform_stress_x: float
    magnitude_uniform_stress_y: float
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., load_type: _Optional[_Union[SurfaceLoad.LoadType, str]] = ..., surfaces: _Optional[_Iterable[int]] = ..., load_case: _Optional[int] = ..., load_distribution: _Optional[_Union[SurfaceLoad.LoadDistribution, str]] = ..., coordinate_system: _Optional[_Union[_common_pb2.CoordinateSystemRepresentation, _Mapping]] = ..., load_direction: _Optional[_Union[SurfaceLoad.LoadDirection, str]] = ..., uniform_magnitude: _Optional[float] = ..., magnitude_1: _Optional[float] = ..., magnitude_2: _Optional[float] = ..., magnitude_3: _Optional[float] = ..., uniform_magnitude_t_c: _Optional[float] = ..., magnitude_t_c_1: _Optional[float] = ..., magnitude_t_c_2: _Optional[float] = ..., magnitude_t_c_3: _Optional[float] = ..., uniform_magnitude_delta_t: _Optional[float] = ..., magnitude_delta_t_1: _Optional[float] = ..., magnitude_delta_t_2: _Optional[float] = ..., magnitude_delta_t_3: _Optional[float] = ..., magnitude_axial_strain_x: _Optional[float] = ..., magnitude_axial_strain_y: _Optional[float] = ..., magnitude_axial_strain_1x: _Optional[float] = ..., magnitude_axial_strain_1y: _Optional[float] = ..., magnitude_axial_strain_2x: _Optional[float] = ..., magnitude_axial_strain_2y: _Optional[float] = ..., magnitude_axial_strain_3x: _Optional[float] = ..., magnitude_axial_strain_3y: _Optional[float] = ..., angular_velocity: _Optional[float] = ..., angular_acceleration: _Optional[float] = ..., node_1: _Optional[int] = ..., node_2: _Optional[int] = ..., node_3: _Optional[int] = ..., axis_definition_type: _Optional[_Union[SurfaceLoad.AxisDefinitionType, str]] = ..., axis_definition_p1: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., axis_definition_p1_x: _Optional[float] = ..., axis_definition_p1_y: _Optional[float] = ..., axis_definition_p1_z: _Optional[float] = ..., axis_definition_p2: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., axis_definition_p2_x: _Optional[float] = ..., axis_definition_p2_y: _Optional[float] = ..., axis_definition_p2_z: _Optional[float] = ..., axis_definition_axis: _Optional[_Union[SurfaceLoad.AxisDefinitionAxis, str]] = ..., axis_definition_axis_orientation: _Optional[_Union[SurfaceLoad.AxisDefinitionAxisOrientation, str]] = ..., varying_load_parameters: _Optional[_Union[SurfaceLoad.VaryingLoadParametersTable, _Mapping]] = ..., varying_load_parameters_sorted: bool = ..., form_finding_definition: _Optional[_Union[SurfaceLoad.FormFindingDefinition, str]] = ..., magnitude_force_u: _Optional[float] = ..., magnitude_force_v: _Optional[float] = ..., magnitude_force_r: _Optional[float] = ..., magnitude_force_t: _Optional[float] = ..., magnitude_stress_u: _Optional[float] = ..., magnitude_stress_v: _Optional[float] = ..., magnitude_stress_r: _Optional[float] = ..., magnitude_stress_t: _Optional[float] = ..., magnitude_sag: _Optional[float] = ..., magnitude_force_scale_x: _Optional[float] = ..., magnitude_force_scale_y: _Optional[float] = ..., form_finding_calculation_method: _Optional[_Union[SurfaceLoad.FormFindingCalculationMethod, str]] = ..., form_finding_sag_related_to_object: _Optional[_Union[SurfaceLoad.FormFindingSagRelatedToObject, str]] = ..., form_finding_sag_related_to_surface: _Optional[int] = ..., individual_mass_components: bool = ..., magnitude_mass_global: _Optional[float] = ..., magnitude_mass_y: _Optional[float] = ..., magnitude_mass_z: _Optional[float] = ..., magnitude_mass_x: _Optional[float] = ..., ponding_amount_precipitation: bool = ..., ponding_magnitude_specific_weight: _Optional[float] = ..., ponding_magnitude_amount_precipitation: _Optional[float] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., magnitude_orthogonal_force_x: _Optional[float] = ..., magnitude_orthogonal_force_y: _Optional[float] = ..., magnitude_orthogonal_stress_x: _Optional[float] = ..., magnitude_orthogonal_stress_y: _Optional[float] = ..., magnitude_uniform_force_x: _Optional[float] = ..., magnitude_uniform_force_y: _Optional[float] = ..., magnitude_uniform_stress_x: _Optional[float] = ..., magnitude_uniform_stress_y: _Optional[float] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
