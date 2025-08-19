from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberSetLoad(_message.Message):
    __slots__ = ("no", "load_type", "member_sets", "load_case", "coordinate_system", "load_distribution", "load_direction", "load_direction_orientation", "form_finding_definition_type", "magnitude", "magnitude_1", "magnitude_2", "magnitude_3", "magnitude_t_c", "magnitude_t_c_1", "magnitude_t_c_2", "magnitude_t_c_3", "magnitude_delta_t", "magnitude_delta_t_1", "magnitude_delta_t_2", "magnitude_delta_t_3", "magnitude_t_t", "magnitude_t_t_1", "magnitude_t_t_2", "magnitude_t_t_3", "magnitude_t_b", "magnitude_t_b_1", "magnitude_t_b_2", "magnitude_t_b_3", "mass_global", "mass_x", "mass_y", "mass_z", "distance_a_is_defined_as_relative", "distance_a_absolute", "distance_a_relative", "distance_b_is_defined_as_relative", "distance_b_absolute", "distance_b_relative", "distance_c_is_defined_as_relative", "distance_c_absolute", "distance_c_relative", "count_n", "varying_load_parameters_are_defined_as_relative", "varying_load_parameters", "varying_load_parameters_sorted", "angular_velocity", "angular_acceleration", "axis_definition_type", "axis_definition_p1", "axis_definition_p1_x", "axis_definition_p1_y", "axis_definition_p1_z", "axis_definition_p2", "axis_definition_p2_x", "axis_definition_p2_y", "axis_definition_p2_z", "axis_definition_axis", "axis_definition_axis_orientation", "filling_height", "distance_from_member_set_end", "load_is_over_total_length", "has_force_eccentricity", "eccentricity_horizontal_alignment", "eccentricity_vertical_alignment", "eccentricity_section_middle", "is_eccentricity_at_end_different_from_start", "eccentricity_y_at_start", "eccentricity_z_at_start", "eccentricity_y_at_end", "eccentricity_z_at_end", "form_finding_internal_force", "form_finding_geometry_definition", "form_finding_force_definition", "form_finding_magnitude_is_defined_as_relative", "form_finding_magnitude_absolute", "form_finding_magnitude_relative", "individual_mass_components", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class LoadType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_TYPE_UNKNOWN: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_AXIAL_DISPLACEMENT: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_AXIAL_STRAIN: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_COATING_CONTOUR: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_COATING_POLYGON: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_DISPLACEMENT: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_END_PRESTRESS: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_FORCE: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_FORM_FINDING: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_INITIAL_PRESTRESS: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_INTERNAL_PRESSURE: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_MASS: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_MOMENT: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_PIPE_CONTENT_FULL: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_PIPE_CONTENT_PARTIAL: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_PRECAMBER: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_PRESTRESS_TENDON: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_ROTARY_MOTION: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_ROTATION: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_TEMPERATURE: _ClassVar[MemberSetLoad.LoadType]
        LOAD_TYPE_TEMPERATURE_CHANGE: _ClassVar[MemberSetLoad.LoadType]
    LOAD_TYPE_UNKNOWN: MemberSetLoad.LoadType
    LOAD_TYPE_AXIAL_DISPLACEMENT: MemberSetLoad.LoadType
    LOAD_TYPE_AXIAL_STRAIN: MemberSetLoad.LoadType
    LOAD_TYPE_COATING_CONTOUR: MemberSetLoad.LoadType
    LOAD_TYPE_COATING_POLYGON: MemberSetLoad.LoadType
    LOAD_TYPE_DISPLACEMENT: MemberSetLoad.LoadType
    LOAD_TYPE_END_PRESTRESS: MemberSetLoad.LoadType
    LOAD_TYPE_FORCE: MemberSetLoad.LoadType
    LOAD_TYPE_FORM_FINDING: MemberSetLoad.LoadType
    LOAD_TYPE_INITIAL_PRESTRESS: MemberSetLoad.LoadType
    LOAD_TYPE_INTERNAL_PRESSURE: MemberSetLoad.LoadType
    LOAD_TYPE_MASS: MemberSetLoad.LoadType
    LOAD_TYPE_MOMENT: MemberSetLoad.LoadType
    LOAD_TYPE_PIPE_CONTENT_FULL: MemberSetLoad.LoadType
    LOAD_TYPE_PIPE_CONTENT_PARTIAL: MemberSetLoad.LoadType
    LOAD_TYPE_PRECAMBER: MemberSetLoad.LoadType
    LOAD_TYPE_PRESTRESS_TENDON: MemberSetLoad.LoadType
    LOAD_TYPE_ROTARY_MOTION: MemberSetLoad.LoadType
    LOAD_TYPE_ROTATION: MemberSetLoad.LoadType
    LOAD_TYPE_TEMPERATURE: MemberSetLoad.LoadType
    LOAD_TYPE_TEMPERATURE_CHANGE: MemberSetLoad.LoadType
    class LoadDistribution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DISTRIBUTION_UNIFORM: _ClassVar[MemberSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_CONCENTRATED_1: _ClassVar[MemberSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_CONCENTRATED_2: _ClassVar[MemberSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_CONCENTRATED_2_2: _ClassVar[MemberSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_CONCENTRATED_N: _ClassVar[MemberSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_CONCENTRATED_VARYING: _ClassVar[MemberSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_PARABOLIC: _ClassVar[MemberSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_TAPERED: _ClassVar[MemberSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_TRAPEZOIDAL: _ClassVar[MemberSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_UNIFORM_TOTAL: _ClassVar[MemberSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_VARYING: _ClassVar[MemberSetLoad.LoadDistribution]
        LOAD_DISTRIBUTION_VARYING_IN_Z: _ClassVar[MemberSetLoad.LoadDistribution]
    LOAD_DISTRIBUTION_UNIFORM: MemberSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_CONCENTRATED_1: MemberSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_CONCENTRATED_2: MemberSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_CONCENTRATED_2_2: MemberSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_CONCENTRATED_N: MemberSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_CONCENTRATED_VARYING: MemberSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_PARABOLIC: MemberSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_TAPERED: MemberSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_TRAPEZOIDAL: MemberSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_UNIFORM_TOTAL: MemberSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_VARYING: MemberSetLoad.LoadDistribution
    LOAD_DISTRIBUTION_VARYING_IN_Z: MemberSetLoad.LoadDistribution
    class LoadDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DIRECTION_LOCAL_X: _ClassVar[MemberSetLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED_LENGTH: _ClassVar[MemberSetLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: _ClassVar[MemberSetLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_PROJECTED_LENGTH: _ClassVar[MemberSetLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: _ClassVar[MemberSetLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_PROJECTED_LENGTH: _ClassVar[MemberSetLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: _ClassVar[MemberSetLoad.LoadDirection]
        LOAD_DIRECTION_LOCAL_Y: _ClassVar[MemberSetLoad.LoadDirection]
        LOAD_DIRECTION_LOCAL_Z: _ClassVar[MemberSetLoad.LoadDirection]
        LOAD_DIRECTION_PRINCIPAL_U: _ClassVar[MemberSetLoad.LoadDirection]
        LOAD_DIRECTION_PRINCIPAL_V: _ClassVar[MemberSetLoad.LoadDirection]
    LOAD_DIRECTION_LOCAL_X: MemberSetLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED_LENGTH: MemberSetLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: MemberSetLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_PROJECTED_LENGTH: MemberSetLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: MemberSetLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_PROJECTED_LENGTH: MemberSetLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: MemberSetLoad.LoadDirection
    LOAD_DIRECTION_LOCAL_Y: MemberSetLoad.LoadDirection
    LOAD_DIRECTION_LOCAL_Z: MemberSetLoad.LoadDirection
    LOAD_DIRECTION_PRINCIPAL_U: MemberSetLoad.LoadDirection
    LOAD_DIRECTION_PRINCIPAL_V: MemberSetLoad.LoadDirection
    class LoadDirectionOrientation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DIRECTION_ORIENTATION_LOAD_DIRECTION_FORWARD: _ClassVar[MemberSetLoad.LoadDirectionOrientation]
        LOAD_DIRECTION_ORIENTATION_LOAD_DIRECTION_REVERSED: _ClassVar[MemberSetLoad.LoadDirectionOrientation]
    LOAD_DIRECTION_ORIENTATION_LOAD_DIRECTION_FORWARD: MemberSetLoad.LoadDirectionOrientation
    LOAD_DIRECTION_ORIENTATION_LOAD_DIRECTION_REVERSED: MemberSetLoad.LoadDirectionOrientation
    class FormFindingDefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FORM_FINDING_DEFINITION_TYPE_GEOMETRIC: _ClassVar[MemberSetLoad.FormFindingDefinitionType]
        FORM_FINDING_DEFINITION_TYPE_FORCE: _ClassVar[MemberSetLoad.FormFindingDefinitionType]
    FORM_FINDING_DEFINITION_TYPE_GEOMETRIC: MemberSetLoad.FormFindingDefinitionType
    FORM_FINDING_DEFINITION_TYPE_FORCE: MemberSetLoad.FormFindingDefinitionType
    class AxisDefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXIS_DEFINITION_TYPE_TWO_POINTS: _ClassVar[MemberSetLoad.AxisDefinitionType]
        AXIS_DEFINITION_TYPE_POINT_AND_AXIS: _ClassVar[MemberSetLoad.AxisDefinitionType]
    AXIS_DEFINITION_TYPE_TWO_POINTS: MemberSetLoad.AxisDefinitionType
    AXIS_DEFINITION_TYPE_POINT_AND_AXIS: MemberSetLoad.AxisDefinitionType
    class AxisDefinitionAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXIS_DEFINITION_AXIS_X: _ClassVar[MemberSetLoad.AxisDefinitionAxis]
        AXIS_DEFINITION_AXIS_Y: _ClassVar[MemberSetLoad.AxisDefinitionAxis]
        AXIS_DEFINITION_AXIS_Z: _ClassVar[MemberSetLoad.AxisDefinitionAxis]
    AXIS_DEFINITION_AXIS_X: MemberSetLoad.AxisDefinitionAxis
    AXIS_DEFINITION_AXIS_Y: MemberSetLoad.AxisDefinitionAxis
    AXIS_DEFINITION_AXIS_Z: MemberSetLoad.AxisDefinitionAxis
    class AxisDefinitionAxisOrientation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXIS_DEFINITION_AXIS_ORIENTATION_POSITIVE: _ClassVar[MemberSetLoad.AxisDefinitionAxisOrientation]
        AXIS_DEFINITION_AXIS_ORIENTATION_NEGATIVE: _ClassVar[MemberSetLoad.AxisDefinitionAxisOrientation]
    AXIS_DEFINITION_AXIS_ORIENTATION_POSITIVE: MemberSetLoad.AxisDefinitionAxisOrientation
    AXIS_DEFINITION_AXIS_ORIENTATION_NEGATIVE: MemberSetLoad.AxisDefinitionAxisOrientation
    class EccentricityHorizontalAlignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ECCENTRICITY_HORIZONTAL_ALIGNMENT_LEFT: _ClassVar[MemberSetLoad.EccentricityHorizontalAlignment]
        ECCENTRICITY_HORIZONTAL_ALIGNMENT_CENTER: _ClassVar[MemberSetLoad.EccentricityHorizontalAlignment]
        ECCENTRICITY_HORIZONTAL_ALIGNMENT_NONE: _ClassVar[MemberSetLoad.EccentricityHorizontalAlignment]
        ECCENTRICITY_HORIZONTAL_ALIGNMENT_RIGHT: _ClassVar[MemberSetLoad.EccentricityHorizontalAlignment]
    ECCENTRICITY_HORIZONTAL_ALIGNMENT_LEFT: MemberSetLoad.EccentricityHorizontalAlignment
    ECCENTRICITY_HORIZONTAL_ALIGNMENT_CENTER: MemberSetLoad.EccentricityHorizontalAlignment
    ECCENTRICITY_HORIZONTAL_ALIGNMENT_NONE: MemberSetLoad.EccentricityHorizontalAlignment
    ECCENTRICITY_HORIZONTAL_ALIGNMENT_RIGHT: MemberSetLoad.EccentricityHorizontalAlignment
    class EccentricityVerticalAlignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ECCENTRICITY_VERTICAL_ALIGNMENT_TOP: _ClassVar[MemberSetLoad.EccentricityVerticalAlignment]
        ECCENTRICITY_VERTICAL_ALIGNMENT_BOTTOM: _ClassVar[MemberSetLoad.EccentricityVerticalAlignment]
        ECCENTRICITY_VERTICAL_ALIGNMENT_CENTER: _ClassVar[MemberSetLoad.EccentricityVerticalAlignment]
        ECCENTRICITY_VERTICAL_ALIGNMENT_NONE: _ClassVar[MemberSetLoad.EccentricityVerticalAlignment]
    ECCENTRICITY_VERTICAL_ALIGNMENT_TOP: MemberSetLoad.EccentricityVerticalAlignment
    ECCENTRICITY_VERTICAL_ALIGNMENT_BOTTOM: MemberSetLoad.EccentricityVerticalAlignment
    ECCENTRICITY_VERTICAL_ALIGNMENT_CENTER: MemberSetLoad.EccentricityVerticalAlignment
    ECCENTRICITY_VERTICAL_ALIGNMENT_NONE: MemberSetLoad.EccentricityVerticalAlignment
    class EccentricitySectionMiddle(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ECCENTRICITY_SECTION_MIDDLE_CENTER_OF_GRAVITY: _ClassVar[MemberSetLoad.EccentricitySectionMiddle]
        ECCENTRICITY_SECTION_MIDDLE_NONE: _ClassVar[MemberSetLoad.EccentricitySectionMiddle]
        ECCENTRICITY_SECTION_MIDDLE_SHEAR_CENTER: _ClassVar[MemberSetLoad.EccentricitySectionMiddle]
    ECCENTRICITY_SECTION_MIDDLE_CENTER_OF_GRAVITY: MemberSetLoad.EccentricitySectionMiddle
    ECCENTRICITY_SECTION_MIDDLE_NONE: MemberSetLoad.EccentricitySectionMiddle
    ECCENTRICITY_SECTION_MIDDLE_SHEAR_CENTER: MemberSetLoad.EccentricitySectionMiddle
    class FormFindingInternalForce(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FORM_FINDING_INTERNAL_FORCE_TENSION: _ClassVar[MemberSetLoad.FormFindingInternalForce]
        FORM_FINDING_INTERNAL_FORCE_COMPRESSION: _ClassVar[MemberSetLoad.FormFindingInternalForce]
    FORM_FINDING_INTERNAL_FORCE_TENSION: MemberSetLoad.FormFindingInternalForce
    FORM_FINDING_INTERNAL_FORCE_COMPRESSION: MemberSetLoad.FormFindingInternalForce
    class FormFindingGeometryDefinition(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FORM_FINDING_GEOMETRY_DEFINITION_LENGTH: _ClassVar[MemberSetLoad.FormFindingGeometryDefinition]
        FORM_FINDING_GEOMETRY_DEFINITION_LOW_POINT_VERTICAL_SAG: _ClassVar[MemberSetLoad.FormFindingGeometryDefinition]
        FORM_FINDING_GEOMETRY_DEFINITION_MAX_VERTICAL_SAG: _ClassVar[MemberSetLoad.FormFindingGeometryDefinition]
        FORM_FINDING_GEOMETRY_DEFINITION_SAG: _ClassVar[MemberSetLoad.FormFindingGeometryDefinition]
        FORM_FINDING_GEOMETRY_DEFINITION_UNSTRESSED_LENGTH: _ClassVar[MemberSetLoad.FormFindingGeometryDefinition]
    FORM_FINDING_GEOMETRY_DEFINITION_LENGTH: MemberSetLoad.FormFindingGeometryDefinition
    FORM_FINDING_GEOMETRY_DEFINITION_LOW_POINT_VERTICAL_SAG: MemberSetLoad.FormFindingGeometryDefinition
    FORM_FINDING_GEOMETRY_DEFINITION_MAX_VERTICAL_SAG: MemberSetLoad.FormFindingGeometryDefinition
    FORM_FINDING_GEOMETRY_DEFINITION_SAG: MemberSetLoad.FormFindingGeometryDefinition
    FORM_FINDING_GEOMETRY_DEFINITION_UNSTRESSED_LENGTH: MemberSetLoad.FormFindingGeometryDefinition
    class FormFindingForceDefinition(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FORM_FINDING_FORCE_DEFINITION_UNKNOWN: _ClassVar[MemberSetLoad.FormFindingForceDefinition]
        FORM_FINDING_FORCE_DEFINITION_AVERAGE: _ClassVar[MemberSetLoad.FormFindingForceDefinition]
        FORM_FINDING_FORCE_DEFINITION_DENSITY: _ClassVar[MemberSetLoad.FormFindingForceDefinition]
        FORM_FINDING_FORCE_DEFINITION_HORIZONTAL_TENSION_COMPONENT: _ClassVar[MemberSetLoad.FormFindingForceDefinition]
        FORM_FINDING_FORCE_DEFINITION_MAX_FORCE_MEMBER: _ClassVar[MemberSetLoad.FormFindingForceDefinition]
        FORM_FINDING_FORCE_DEFINITION_MINIMAL_TENSION_AT_IEND: _ClassVar[MemberSetLoad.FormFindingForceDefinition]
        FORM_FINDING_FORCE_DEFINITION_MINIMAL_TENSION_AT_JEND: _ClassVar[MemberSetLoad.FormFindingForceDefinition]
        FORM_FINDING_FORCE_DEFINITION_MIN_FORCE_MEMBER: _ClassVar[MemberSetLoad.FormFindingForceDefinition]
        FORM_FINDING_FORCE_DEFINITION_TENSION_AT_IEND: _ClassVar[MemberSetLoad.FormFindingForceDefinition]
        FORM_FINDING_FORCE_DEFINITION_TENSION_AT_JEND: _ClassVar[MemberSetLoad.FormFindingForceDefinition]
    FORM_FINDING_FORCE_DEFINITION_UNKNOWN: MemberSetLoad.FormFindingForceDefinition
    FORM_FINDING_FORCE_DEFINITION_AVERAGE: MemberSetLoad.FormFindingForceDefinition
    FORM_FINDING_FORCE_DEFINITION_DENSITY: MemberSetLoad.FormFindingForceDefinition
    FORM_FINDING_FORCE_DEFINITION_HORIZONTAL_TENSION_COMPONENT: MemberSetLoad.FormFindingForceDefinition
    FORM_FINDING_FORCE_DEFINITION_MAX_FORCE_MEMBER: MemberSetLoad.FormFindingForceDefinition
    FORM_FINDING_FORCE_DEFINITION_MINIMAL_TENSION_AT_IEND: MemberSetLoad.FormFindingForceDefinition
    FORM_FINDING_FORCE_DEFINITION_MINIMAL_TENSION_AT_JEND: MemberSetLoad.FormFindingForceDefinition
    FORM_FINDING_FORCE_DEFINITION_MIN_FORCE_MEMBER: MemberSetLoad.FormFindingForceDefinition
    FORM_FINDING_FORCE_DEFINITION_TENSION_AT_IEND: MemberSetLoad.FormFindingForceDefinition
    FORM_FINDING_FORCE_DEFINITION_TENSION_AT_JEND: MemberSetLoad.FormFindingForceDefinition
    class VaryingLoadParametersTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberSetLoad.VaryingLoadParametersRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberSetLoad.VaryingLoadParametersRow, _Mapping]]] = ...) -> None: ...
    class VaryingLoadParametersRow(_message.Message):
        __slots__ = ("no", "description", "distance", "delta_distance", "magnitude", "note", "magnitude_t_c", "magnitude_delta_t", "magnitude_t_t", "magnitude_t_b")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        DISTANCE_FIELD_NUMBER: _ClassVar[int]
        DELTA_DISTANCE_FIELD_NUMBER: _ClassVar[int]
        MAGNITUDE_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        MAGNITUDE_T_C_FIELD_NUMBER: _ClassVar[int]
        MAGNITUDE_DELTA_T_FIELD_NUMBER: _ClassVar[int]
        MAGNITUDE_T_T_FIELD_NUMBER: _ClassVar[int]
        MAGNITUDE_T_B_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        distance: float
        delta_distance: float
        magnitude: float
        note: str
        magnitude_t_c: float
        magnitude_delta_t: float
        magnitude_t_t: float
        magnitude_t_b: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., distance: _Optional[float] = ..., delta_distance: _Optional[float] = ..., magnitude: _Optional[float] = ..., note: _Optional[str] = ..., magnitude_t_c: _Optional[float] = ..., magnitude_delta_t: _Optional[float] = ..., magnitude_t_t: _Optional[float] = ..., magnitude_t_b: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    LOAD_TYPE_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    LOAD_CASE_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    LOAD_DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    LOAD_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    LOAD_DIRECTION_ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    FORM_FINDING_DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_1_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_2_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_3_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_T_C_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_T_C_1_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_T_C_2_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_T_C_3_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_DELTA_T_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_DELTA_T_1_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_DELTA_T_2_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_DELTA_T_3_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_T_T_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_T_T_1_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_T_T_2_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_T_T_3_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_T_B_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_T_B_1_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_T_B_2_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_T_B_3_FIELD_NUMBER: _ClassVar[int]
    MASS_GLOBAL_FIELD_NUMBER: _ClassVar[int]
    MASS_X_FIELD_NUMBER: _ClassVar[int]
    MASS_Y_FIELD_NUMBER: _ClassVar[int]
    MASS_Z_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_A_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_A_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_A_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_B_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_B_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_B_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_C_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_C_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_C_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_N_FIELD_NUMBER: _ClassVar[int]
    VARYING_LOAD_PARAMETERS_ARE_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    VARYING_LOAD_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    VARYING_LOAD_PARAMETERS_SORTED_FIELD_NUMBER: _ClassVar[int]
    ANGULAR_VELOCITY_FIELD_NUMBER: _ClassVar[int]
    ANGULAR_ACCELERATION_FIELD_NUMBER: _ClassVar[int]
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
    FILLING_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_MEMBER_SET_END_FIELD_NUMBER: _ClassVar[int]
    LOAD_IS_OVER_TOTAL_LENGTH_FIELD_NUMBER: _ClassVar[int]
    HAS_FORCE_ECCENTRICITY_FIELD_NUMBER: _ClassVar[int]
    ECCENTRICITY_HORIZONTAL_ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    ECCENTRICITY_VERTICAL_ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    ECCENTRICITY_SECTION_MIDDLE_FIELD_NUMBER: _ClassVar[int]
    IS_ECCENTRICITY_AT_END_DIFFERENT_FROM_START_FIELD_NUMBER: _ClassVar[int]
    ECCENTRICITY_Y_AT_START_FIELD_NUMBER: _ClassVar[int]
    ECCENTRICITY_Z_AT_START_FIELD_NUMBER: _ClassVar[int]
    ECCENTRICITY_Y_AT_END_FIELD_NUMBER: _ClassVar[int]
    ECCENTRICITY_Z_AT_END_FIELD_NUMBER: _ClassVar[int]
    FORM_FINDING_INTERNAL_FORCE_FIELD_NUMBER: _ClassVar[int]
    FORM_FINDING_GEOMETRY_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    FORM_FINDING_FORCE_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    FORM_FINDING_MAGNITUDE_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    FORM_FINDING_MAGNITUDE_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    FORM_FINDING_MAGNITUDE_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    INDIVIDUAL_MASS_COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    load_type: MemberSetLoad.LoadType
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    load_case: int
    coordinate_system: _common_pb2.CoordinateSystemRepresentation
    load_distribution: MemberSetLoad.LoadDistribution
    load_direction: MemberSetLoad.LoadDirection
    load_direction_orientation: MemberSetLoad.LoadDirectionOrientation
    form_finding_definition_type: MemberSetLoad.FormFindingDefinitionType
    magnitude: float
    magnitude_1: float
    magnitude_2: float
    magnitude_3: float
    magnitude_t_c: float
    magnitude_t_c_1: float
    magnitude_t_c_2: float
    magnitude_t_c_3: float
    magnitude_delta_t: float
    magnitude_delta_t_1: float
    magnitude_delta_t_2: float
    magnitude_delta_t_3: float
    magnitude_t_t: float
    magnitude_t_t_1: float
    magnitude_t_t_2: float
    magnitude_t_t_3: float
    magnitude_t_b: float
    magnitude_t_b_1: float
    magnitude_t_b_2: float
    magnitude_t_b_3: float
    mass_global: float
    mass_x: float
    mass_y: float
    mass_z: float
    distance_a_is_defined_as_relative: bool
    distance_a_absolute: float
    distance_a_relative: float
    distance_b_is_defined_as_relative: bool
    distance_b_absolute: float
    distance_b_relative: float
    distance_c_is_defined_as_relative: bool
    distance_c_absolute: float
    distance_c_relative: float
    count_n: int
    varying_load_parameters_are_defined_as_relative: bool
    varying_load_parameters: MemberSetLoad.VaryingLoadParametersTable
    varying_load_parameters_sorted: bool
    angular_velocity: float
    angular_acceleration: float
    axis_definition_type: MemberSetLoad.AxisDefinitionType
    axis_definition_p1: _common_pb2.Vector3d
    axis_definition_p1_x: float
    axis_definition_p1_y: float
    axis_definition_p1_z: float
    axis_definition_p2: _common_pb2.Vector3d
    axis_definition_p2_x: float
    axis_definition_p2_y: float
    axis_definition_p2_z: float
    axis_definition_axis: MemberSetLoad.AxisDefinitionAxis
    axis_definition_axis_orientation: MemberSetLoad.AxisDefinitionAxisOrientation
    filling_height: float
    distance_from_member_set_end: bool
    load_is_over_total_length: bool
    has_force_eccentricity: bool
    eccentricity_horizontal_alignment: MemberSetLoad.EccentricityHorizontalAlignment
    eccentricity_vertical_alignment: MemberSetLoad.EccentricityVerticalAlignment
    eccentricity_section_middle: MemberSetLoad.EccentricitySectionMiddle
    is_eccentricity_at_end_different_from_start: bool
    eccentricity_y_at_start: float
    eccentricity_z_at_start: float
    eccentricity_y_at_end: float
    eccentricity_z_at_end: float
    form_finding_internal_force: MemberSetLoad.FormFindingInternalForce
    form_finding_geometry_definition: MemberSetLoad.FormFindingGeometryDefinition
    form_finding_force_definition: MemberSetLoad.FormFindingForceDefinition
    form_finding_magnitude_is_defined_as_relative: bool
    form_finding_magnitude_absolute: float
    form_finding_magnitude_relative: float
    individual_mass_components: bool
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., load_type: _Optional[_Union[MemberSetLoad.LoadType, str]] = ..., member_sets: _Optional[_Iterable[int]] = ..., load_case: _Optional[int] = ..., coordinate_system: _Optional[_Union[_common_pb2.CoordinateSystemRepresentation, _Mapping]] = ..., load_distribution: _Optional[_Union[MemberSetLoad.LoadDistribution, str]] = ..., load_direction: _Optional[_Union[MemberSetLoad.LoadDirection, str]] = ..., load_direction_orientation: _Optional[_Union[MemberSetLoad.LoadDirectionOrientation, str]] = ..., form_finding_definition_type: _Optional[_Union[MemberSetLoad.FormFindingDefinitionType, str]] = ..., magnitude: _Optional[float] = ..., magnitude_1: _Optional[float] = ..., magnitude_2: _Optional[float] = ..., magnitude_3: _Optional[float] = ..., magnitude_t_c: _Optional[float] = ..., magnitude_t_c_1: _Optional[float] = ..., magnitude_t_c_2: _Optional[float] = ..., magnitude_t_c_3: _Optional[float] = ..., magnitude_delta_t: _Optional[float] = ..., magnitude_delta_t_1: _Optional[float] = ..., magnitude_delta_t_2: _Optional[float] = ..., magnitude_delta_t_3: _Optional[float] = ..., magnitude_t_t: _Optional[float] = ..., magnitude_t_t_1: _Optional[float] = ..., magnitude_t_t_2: _Optional[float] = ..., magnitude_t_t_3: _Optional[float] = ..., magnitude_t_b: _Optional[float] = ..., magnitude_t_b_1: _Optional[float] = ..., magnitude_t_b_2: _Optional[float] = ..., magnitude_t_b_3: _Optional[float] = ..., mass_global: _Optional[float] = ..., mass_x: _Optional[float] = ..., mass_y: _Optional[float] = ..., mass_z: _Optional[float] = ..., distance_a_is_defined_as_relative: bool = ..., distance_a_absolute: _Optional[float] = ..., distance_a_relative: _Optional[float] = ..., distance_b_is_defined_as_relative: bool = ..., distance_b_absolute: _Optional[float] = ..., distance_b_relative: _Optional[float] = ..., distance_c_is_defined_as_relative: bool = ..., distance_c_absolute: _Optional[float] = ..., distance_c_relative: _Optional[float] = ..., count_n: _Optional[int] = ..., varying_load_parameters_are_defined_as_relative: bool = ..., varying_load_parameters: _Optional[_Union[MemberSetLoad.VaryingLoadParametersTable, _Mapping]] = ..., varying_load_parameters_sorted: bool = ..., angular_velocity: _Optional[float] = ..., angular_acceleration: _Optional[float] = ..., axis_definition_type: _Optional[_Union[MemberSetLoad.AxisDefinitionType, str]] = ..., axis_definition_p1: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., axis_definition_p1_x: _Optional[float] = ..., axis_definition_p1_y: _Optional[float] = ..., axis_definition_p1_z: _Optional[float] = ..., axis_definition_p2: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., axis_definition_p2_x: _Optional[float] = ..., axis_definition_p2_y: _Optional[float] = ..., axis_definition_p2_z: _Optional[float] = ..., axis_definition_axis: _Optional[_Union[MemberSetLoad.AxisDefinitionAxis, str]] = ..., axis_definition_axis_orientation: _Optional[_Union[MemberSetLoad.AxisDefinitionAxisOrientation, str]] = ..., filling_height: _Optional[float] = ..., distance_from_member_set_end: bool = ..., load_is_over_total_length: bool = ..., has_force_eccentricity: bool = ..., eccentricity_horizontal_alignment: _Optional[_Union[MemberSetLoad.EccentricityHorizontalAlignment, str]] = ..., eccentricity_vertical_alignment: _Optional[_Union[MemberSetLoad.EccentricityVerticalAlignment, str]] = ..., eccentricity_section_middle: _Optional[_Union[MemberSetLoad.EccentricitySectionMiddle, str]] = ..., is_eccentricity_at_end_different_from_start: bool = ..., eccentricity_y_at_start: _Optional[float] = ..., eccentricity_z_at_start: _Optional[float] = ..., eccentricity_y_at_end: _Optional[float] = ..., eccentricity_z_at_end: _Optional[float] = ..., form_finding_internal_force: _Optional[_Union[MemberSetLoad.FormFindingInternalForce, str]] = ..., form_finding_geometry_definition: _Optional[_Union[MemberSetLoad.FormFindingGeometryDefinition, str]] = ..., form_finding_force_definition: _Optional[_Union[MemberSetLoad.FormFindingForceDefinition, str]] = ..., form_finding_magnitude_is_defined_as_relative: bool = ..., form_finding_magnitude_absolute: _Optional[float] = ..., form_finding_magnitude_relative: _Optional[float] = ..., individual_mass_components: bool = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
