from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NodalSupport(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "fictitious_column_enabled", "specific_direction_enabled", "specific_direction_type", "nodes", "spring", "spring_x", "spring_y", "spring_z", "rotational_restraint", "rotational_restraint_x", "rotational_restraint_y", "rotational_restraint_z", "spring_x_nonlinearity", "spring_y_nonlinearity", "spring_z_nonlinearity", "rotational_restraint_x_nonlinearity", "rotational_restraint_y_nonlinearity", "rotational_restraint_z_nonlinearity", "axes_sequence", "column_base_semi_rigid", "column_base_support_type", "column_head_support_type", "column_head_type", "column_height", "column_section_same_as_head", "column_material", "column_rotation", "column_rotational_restraint_x", "column_rotational_restraint_y", "column_section", "column_shear_stiffness", "column_spring_x", "column_spring_y", "column_spring_z", "column_support_type", "column_width_x", "column_width_y", "comment", "coordinate_system", "diagram_along_x_symmetric", "diagram_along_x_start", "diagram_along_x_end", "diagram_along_x_table", "diagram_along_x_is_sorted", "diagram_along_y_symmetric", "diagram_along_y_start", "diagram_along_y_end", "diagram_along_y_table", "diagram_along_y_is_sorted", "diagram_along_z_symmetric", "diagram_along_z_start", "diagram_along_z_end", "diagram_along_z_table", "diagram_along_z_is_sorted", "diagram_around_x_symmetric", "diagram_around_x_start", "diagram_around_x_end", "diagram_around_x_table", "diagram_around_x_is_sorted", "diagram_around_y_symmetric", "diagram_around_y_start", "diagram_around_y_end", "diagram_around_y_table", "diagram_around_y_is_sorted", "diagram_around_z_symmetric", "diagram_around_z_start", "diagram_around_z_end", "diagram_around_z_table", "diagram_around_z_is_sorted", "directed_to_node_direction_node", "directed_to_node_first_axis", "directed_to_node_plane_node", "directed_to_node_second_axis", "friction_coefficient_x", "friction_coefficient_xy", "friction_coefficient_xz", "friction_coefficient_y", "friction_coefficient_yx", "friction_coefficient_yz", "friction_coefficient_z", "friction_coefficient_zx", "friction_coefficient_zy", "parallel_to_line", "parallel_to_member", "parallel_to_two_nodes_first_axis", "parallel_to_two_nodes_first_node", "parallel_to_two_nodes_plane_node", "parallel_to_two_nodes_second_axis", "parallel_to_two_nodes_second_node", "partial_activity_along_x_negative_type", "partial_activity_along_x_negative_displacement", "partial_activity_along_x_negative_force", "partial_activity_along_x_negative_slippage", "partial_activity_along_x_positive_type", "partial_activity_along_x_positive_displacement", "partial_activity_along_x_positive_force", "partial_activity_along_x_positive_slippage", "partial_activity_along_y_negative_type", "partial_activity_along_y_negative_displacement", "partial_activity_along_y_negative_force", "partial_activity_along_y_negative_slippage", "partial_activity_along_y_positive_type", "partial_activity_along_y_positive_displacement", "partial_activity_along_y_positive_force", "partial_activity_along_y_positive_slippage", "partial_activity_along_z_negative_type", "partial_activity_along_z_negative_displacement", "partial_activity_along_z_negative_force", "partial_activity_along_z_negative_slippage", "partial_activity_along_z_positive_type", "partial_activity_along_z_positive_displacement", "partial_activity_along_z_positive_force", "partial_activity_along_z_positive_slippage", "partial_activity_around_x_negative_type", "partial_activity_around_x_negative_moment", "partial_activity_around_x_negative_rotation", "partial_activity_around_x_negative_slippage", "partial_activity_around_x_positive_type", "partial_activity_around_x_positive_moment", "partial_activity_around_x_positive_rotation", "partial_activity_around_x_positive_slippage", "partial_activity_around_y_negative_type", "partial_activity_around_y_negative_moment", "partial_activity_around_y_negative_rotation", "partial_activity_around_y_negative_slippage", "partial_activity_around_y_positive_type", "partial_activity_around_y_positive_moment", "partial_activity_around_y_positive_rotation", "partial_activity_around_y_positive_slippage", "partial_activity_around_z_negative_type", "partial_activity_around_z_negative_moment", "partial_activity_around_z_negative_rotation", "partial_activity_around_z_negative_slippage", "partial_activity_around_z_positive_type", "partial_activity_around_z_positive_moment", "partial_activity_around_z_positive_rotation", "partial_activity_around_z_positive_slippage", "rotated_about_angle_1", "rotated_about_angle_2", "rotated_about_angle_3", "rotated_about_angle_x", "rotated_about_angle_y", "rotated_about_angle_z", "stiffness_diagram_around_x_depends_on", "stiffness_diagram_around_x_end", "stiffness_diagram_around_x_is_sorted", "stiffness_diagram_around_x_start", "stiffness_diagram_around_x_symmetric", "stiffness_diagram_around_x_table", "stiffness_diagram_around_y_depends_on", "stiffness_diagram_around_y_end", "stiffness_diagram_around_y_is_sorted", "stiffness_diagram_around_y_start", "stiffness_diagram_around_y_symmetric", "stiffness_diagram_around_y_table", "stiffness_diagram_around_z_depends_on", "stiffness_diagram_around_z_end", "stiffness_diagram_around_z_is_sorted", "stiffness_diagram_around_z_start", "stiffness_diagram_around_z_symmetric", "stiffness_diagram_around_z_table", "support_dimension_diameter_x", "support_dimension_diameter_y", "support_dimension_diameter_z", "support_dimension_height_x", "support_dimension_height_y", "support_dimension_height_z", "support_dimension_type_on_x", "support_dimension_type_on_y", "support_dimension_type_on_z", "support_dimension_width_x", "support_dimension_width_y", "support_dimension_width_z", "support_dimensions_enabled", "diagram_along_x_ac_yield_minus", "diagram_along_y_ac_yield_minus", "diagram_along_z_ac_yield_minus", "diagram_around_x_ac_yield_minus", "diagram_around_y_ac_yield_minus", "diagram_around_z_ac_yield_minus", "diagram_along_x_ac_yield_plus", "diagram_along_y_ac_yield_plus", "diagram_along_z_ac_yield_plus", "diagram_around_x_ac_yield_plus", "diagram_around_y_ac_yield_plus", "diagram_around_z_ac_yield_plus", "diagram_along_x_acceptance_criteria_active", "diagram_along_y_acceptance_criteria_active", "diagram_along_z_acceptance_criteria_active", "diagram_around_x_acceptance_criteria_active", "diagram_around_y_acceptance_criteria_active", "diagram_around_z_acceptance_criteria_active", "diagram_along_x_minus_color_one", "diagram_along_y_minus_color_one", "diagram_along_z_minus_color_one", "diagram_around_x_minus_color_one", "diagram_around_y_minus_color_one", "diagram_around_z_minus_color_one", "diagram_along_x_minus_color_two", "diagram_along_y_minus_color_two", "diagram_along_z_minus_color_two", "diagram_around_x_minus_color_two", "diagram_around_y_minus_color_two", "diagram_around_z_minus_color_two", "diagram_along_x_plus_color_one", "diagram_along_y_plus_color_one", "diagram_along_z_plus_color_one", "diagram_around_x_plus_color_one", "diagram_around_y_plus_color_one", "diagram_around_z_plus_color_one", "diagram_along_x_plus_color_two", "diagram_along_y_plus_color_two", "diagram_along_z_plus_color_two", "diagram_around_x_plus_color_two", "diagram_around_y_plus_color_two", "diagram_around_z_plus_color_two", "diagram_along_x_color_table", "diagram_along_y_color_table", "diagram_along_z_color_table", "diagram_around_x_color_table", "diagram_around_y_color_table", "diagram_around_z_color_table", "generating_object_info", "is_generated", "id_for_export_import", "metadata_for_export_import")
    class SpecificDirectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SPECIFIC_DIRECTION_TYPE_ROTATED_VIA_3_ANGLES: _ClassVar[NodalSupport.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_DIRECTED_TO_NODE: _ClassVar[NodalSupport.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_LINE: _ClassVar[NodalSupport.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER: _ClassVar[NodalSupport.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_TWO_NODES: _ClassVar[NodalSupport.SpecificDirectionType]
    SPECIFIC_DIRECTION_TYPE_ROTATED_VIA_3_ANGLES: NodalSupport.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_DIRECTED_TO_NODE: NodalSupport.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_LINE: NodalSupport.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER: NodalSupport.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_TWO_NODES: NodalSupport.SpecificDirectionType
    class SpringXNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SPRING_X_NONLINEARITY_NONE: _ClassVar[NodalSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_DIAGRAM: _ClassVar[NodalSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[NodalSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[NodalSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[NodalSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[NodalSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[NodalSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[NodalSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[NodalSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[NodalSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[NodalSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[NodalSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_SCAFFOLDING_HINGE: _ClassVar[NodalSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[NodalSupport.SpringXNonlinearity]
    SPRING_X_NONLINEARITY_NONE: NodalSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_DIAGRAM: NodalSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: NodalSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: NodalSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FAILURE_IF_NEGATIVE: NodalSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FAILURE_IF_POSITIVE: NodalSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: NodalSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FRICTION_DIRECTION_1: NodalSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FRICTION_DIRECTION_1_2: NodalSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: NodalSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FRICTION_DIRECTION_2: NodalSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_PARTIAL_ACTIVITY: NodalSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_SCAFFOLDING_HINGE: NodalSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_STIFFNESS_DIAGRAM: NodalSupport.SpringXNonlinearity
    class SpringYNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SPRING_Y_NONLINEARITY_NONE: _ClassVar[NodalSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_DIAGRAM: _ClassVar[NodalSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[NodalSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[NodalSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[NodalSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[NodalSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[NodalSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[NodalSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[NodalSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[NodalSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[NodalSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[NodalSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_SCAFFOLDING_HINGE: _ClassVar[NodalSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[NodalSupport.SpringYNonlinearity]
    SPRING_Y_NONLINEARITY_NONE: NodalSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_DIAGRAM: NodalSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: NodalSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: NodalSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FAILURE_IF_NEGATIVE: NodalSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FAILURE_IF_POSITIVE: NodalSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FORCE_MOMENT_DIAGRAM: NodalSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_1: NodalSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_1_2: NodalSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: NodalSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_2: NodalSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_PARTIAL_ACTIVITY: NodalSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_SCAFFOLDING_HINGE: NodalSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_STIFFNESS_DIAGRAM: NodalSupport.SpringYNonlinearity
    class SpringZNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SPRING_Z_NONLINEARITY_NONE: _ClassVar[NodalSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_DIAGRAM: _ClassVar[NodalSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[NodalSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[NodalSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[NodalSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[NodalSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[NodalSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[NodalSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[NodalSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[NodalSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[NodalSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[NodalSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_SCAFFOLDING_HINGE: _ClassVar[NodalSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[NodalSupport.SpringZNonlinearity]
    SPRING_Z_NONLINEARITY_NONE: NodalSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_DIAGRAM: NodalSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: NodalSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: NodalSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FAILURE_IF_NEGATIVE: NodalSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FAILURE_IF_POSITIVE: NodalSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FORCE_MOMENT_DIAGRAM: NodalSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_1: NodalSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_1_2: NodalSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: NodalSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_2: NodalSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_PARTIAL_ACTIVITY: NodalSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_SCAFFOLDING_HINGE: NodalSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_STIFFNESS_DIAGRAM: NodalSupport.SpringZNonlinearity
    class RotationalRestraintXNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_NONE: _ClassVar[NodalSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_DIAGRAM: _ClassVar[NodalSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[NodalSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[NodalSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[NodalSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[NodalSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[NodalSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[NodalSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[NodalSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[NodalSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[NodalSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[NodalSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_SCAFFOLDING_HINGE: _ClassVar[NodalSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[NodalSupport.RotationalRestraintXNonlinearity]
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_NONE: NodalSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_DIAGRAM: NodalSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: NodalSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: NodalSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_IF_NEGATIVE: NodalSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_IF_POSITIVE: NodalSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: NodalSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_1: NodalSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_1_2: NodalSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: NodalSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_2: NodalSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_PARTIAL_ACTIVITY: NodalSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_SCAFFOLDING_HINGE: NodalSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_STIFFNESS_DIAGRAM: NodalSupport.RotationalRestraintXNonlinearity
    class RotationalRestraintYNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_NONE: _ClassVar[NodalSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_DIAGRAM: _ClassVar[NodalSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[NodalSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[NodalSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[NodalSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[NodalSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[NodalSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[NodalSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[NodalSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[NodalSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[NodalSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[NodalSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_SCAFFOLDING_HINGE: _ClassVar[NodalSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[NodalSupport.RotationalRestraintYNonlinearity]
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_NONE: NodalSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_DIAGRAM: NodalSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: NodalSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: NodalSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_IF_NEGATIVE: NodalSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_IF_POSITIVE: NodalSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FORCE_MOMENT_DIAGRAM: NodalSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_1: NodalSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_1_2: NodalSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: NodalSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_2: NodalSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_PARTIAL_ACTIVITY: NodalSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_SCAFFOLDING_HINGE: NodalSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_STIFFNESS_DIAGRAM: NodalSupport.RotationalRestraintYNonlinearity
    class RotationalRestraintZNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_NONE: _ClassVar[NodalSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_DIAGRAM: _ClassVar[NodalSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[NodalSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[NodalSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[NodalSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[NodalSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[NodalSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[NodalSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[NodalSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[NodalSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[NodalSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[NodalSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_SCAFFOLDING_HINGE: _ClassVar[NodalSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[NodalSupport.RotationalRestraintZNonlinearity]
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_NONE: NodalSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_DIAGRAM: NodalSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: NodalSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: NodalSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_IF_NEGATIVE: NodalSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_IF_POSITIVE: NodalSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FORCE_MOMENT_DIAGRAM: NodalSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_1: NodalSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_1_2: NodalSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: NodalSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_2: NodalSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_PARTIAL_ACTIVITY: NodalSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_SCAFFOLDING_HINGE: NodalSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_STIFFNESS_DIAGRAM: NodalSupport.RotationalRestraintZNonlinearity
    class AxesSequence(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXES_SEQUENCE_XYZ: _ClassVar[NodalSupport.AxesSequence]
        AXES_SEQUENCE_XZY: _ClassVar[NodalSupport.AxesSequence]
        AXES_SEQUENCE_YXZ: _ClassVar[NodalSupport.AxesSequence]
        AXES_SEQUENCE_YZX: _ClassVar[NodalSupport.AxesSequence]
        AXES_SEQUENCE_ZXY: _ClassVar[NodalSupport.AxesSequence]
        AXES_SEQUENCE_ZYX: _ClassVar[NodalSupport.AxesSequence]
    AXES_SEQUENCE_XYZ: NodalSupport.AxesSequence
    AXES_SEQUENCE_XZY: NodalSupport.AxesSequence
    AXES_SEQUENCE_YXZ: NodalSupport.AxesSequence
    AXES_SEQUENCE_YZX: NodalSupport.AxesSequence
    AXES_SEQUENCE_ZXY: NodalSupport.AxesSequence
    AXES_SEQUENCE_ZYX: NodalSupport.AxesSequence
    class ColumnBaseSupportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COLUMN_BASE_SUPPORT_TYPE_HINGED: _ClassVar[NodalSupport.ColumnBaseSupportType]
        COLUMN_BASE_SUPPORT_TYPE_RIGID: _ClassVar[NodalSupport.ColumnBaseSupportType]
        COLUMN_BASE_SUPPORT_TYPE_SEMI_RIGID: _ClassVar[NodalSupport.ColumnBaseSupportType]
    COLUMN_BASE_SUPPORT_TYPE_HINGED: NodalSupport.ColumnBaseSupportType
    COLUMN_BASE_SUPPORT_TYPE_RIGID: NodalSupport.ColumnBaseSupportType
    COLUMN_BASE_SUPPORT_TYPE_SEMI_RIGID: NodalSupport.ColumnBaseSupportType
    class ColumnHeadSupportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COLUMN_HEAD_SUPPORT_TYPE_HINGED: _ClassVar[NodalSupport.ColumnHeadSupportType]
        COLUMN_HEAD_SUPPORT_TYPE_RIGID: _ClassVar[NodalSupport.ColumnHeadSupportType]
    COLUMN_HEAD_SUPPORT_TYPE_HINGED: NodalSupport.ColumnHeadSupportType
    COLUMN_HEAD_SUPPORT_TYPE_RIGID: NodalSupport.ColumnHeadSupportType
    class ColumnHeadType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COLUMN_HEAD_TYPE_RECTANGULAR: _ClassVar[NodalSupport.ColumnHeadType]
        COLUMN_HEAD_TYPE_CIRCULAR: _ClassVar[NodalSupport.ColumnHeadType]
    COLUMN_HEAD_TYPE_RECTANGULAR: NodalSupport.ColumnHeadType
    COLUMN_HEAD_TYPE_CIRCULAR: NodalSupport.ColumnHeadType
    class ColumnSupportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COLUMN_SUPPORT_TYPE_ELASTIC_SURFACE_FOUNDATIONS: _ClassVar[NodalSupport.ColumnSupportType]
        COLUMN_SUPPORT_TYPE_ELASTIC_NODAL_SUPPORT: _ClassVar[NodalSupport.ColumnSupportType]
        COLUMN_SUPPORT_TYPE_WITH_ADAPTED_FE_MESH: _ClassVar[NodalSupport.ColumnSupportType]
    COLUMN_SUPPORT_TYPE_ELASTIC_SURFACE_FOUNDATIONS: NodalSupport.ColumnSupportType
    COLUMN_SUPPORT_TYPE_ELASTIC_NODAL_SUPPORT: NodalSupport.ColumnSupportType
    COLUMN_SUPPORT_TYPE_WITH_ADAPTED_FE_MESH: NodalSupport.ColumnSupportType
    class DiagramAlongXStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_X_START_FAILURE: _ClassVar[NodalSupport.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_CONTINUOUS: _ClassVar[NodalSupport.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_STOP: _ClassVar[NodalSupport.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_YIELDING: _ClassVar[NodalSupport.DiagramAlongXStart]
    DIAGRAM_ALONG_X_START_FAILURE: NodalSupport.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_CONTINUOUS: NodalSupport.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_STOP: NodalSupport.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_YIELDING: NodalSupport.DiagramAlongXStart
    class DiagramAlongXEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_X_END_FAILURE: _ClassVar[NodalSupport.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_CONTINUOUS: _ClassVar[NodalSupport.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_STOP: _ClassVar[NodalSupport.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_YIELDING: _ClassVar[NodalSupport.DiagramAlongXEnd]
    DIAGRAM_ALONG_X_END_FAILURE: NodalSupport.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_CONTINUOUS: NodalSupport.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_STOP: NodalSupport.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_YIELDING: NodalSupport.DiagramAlongXEnd
    class DiagramAlongYStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Y_START_FAILURE: _ClassVar[NodalSupport.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_CONTINUOUS: _ClassVar[NodalSupport.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_STOP: _ClassVar[NodalSupport.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_YIELDING: _ClassVar[NodalSupport.DiagramAlongYStart]
    DIAGRAM_ALONG_Y_START_FAILURE: NodalSupport.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_CONTINUOUS: NodalSupport.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_STOP: NodalSupport.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_YIELDING: NodalSupport.DiagramAlongYStart
    class DiagramAlongYEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Y_END_FAILURE: _ClassVar[NodalSupport.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_CONTINUOUS: _ClassVar[NodalSupport.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_STOP: _ClassVar[NodalSupport.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_YIELDING: _ClassVar[NodalSupport.DiagramAlongYEnd]
    DIAGRAM_ALONG_Y_END_FAILURE: NodalSupport.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_CONTINUOUS: NodalSupport.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_STOP: NodalSupport.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_YIELDING: NodalSupport.DiagramAlongYEnd
    class DiagramAlongZStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Z_START_FAILURE: _ClassVar[NodalSupport.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_CONTINUOUS: _ClassVar[NodalSupport.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_STOP: _ClassVar[NodalSupport.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_YIELDING: _ClassVar[NodalSupport.DiagramAlongZStart]
    DIAGRAM_ALONG_Z_START_FAILURE: NodalSupport.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_CONTINUOUS: NodalSupport.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_STOP: NodalSupport.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_YIELDING: NodalSupport.DiagramAlongZStart
    class DiagramAlongZEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Z_END_FAILURE: _ClassVar[NodalSupport.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_CONTINUOUS: _ClassVar[NodalSupport.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_STOP: _ClassVar[NodalSupport.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_YIELDING: _ClassVar[NodalSupport.DiagramAlongZEnd]
    DIAGRAM_ALONG_Z_END_FAILURE: NodalSupport.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_CONTINUOUS: NodalSupport.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_STOP: NodalSupport.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_YIELDING: NodalSupport.DiagramAlongZEnd
    class DiagramAroundXStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_X_START_FAILURE: _ClassVar[NodalSupport.DiagramAroundXStart]
        DIAGRAM_AROUND_X_START_CONTINUOUS: _ClassVar[NodalSupport.DiagramAroundXStart]
        DIAGRAM_AROUND_X_START_STOP: _ClassVar[NodalSupport.DiagramAroundXStart]
        DIAGRAM_AROUND_X_START_YIELDING: _ClassVar[NodalSupport.DiagramAroundXStart]
    DIAGRAM_AROUND_X_START_FAILURE: NodalSupport.DiagramAroundXStart
    DIAGRAM_AROUND_X_START_CONTINUOUS: NodalSupport.DiagramAroundXStart
    DIAGRAM_AROUND_X_START_STOP: NodalSupport.DiagramAroundXStart
    DIAGRAM_AROUND_X_START_YIELDING: NodalSupport.DiagramAroundXStart
    class DiagramAroundXEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_X_END_FAILURE: _ClassVar[NodalSupport.DiagramAroundXEnd]
        DIAGRAM_AROUND_X_END_CONTINUOUS: _ClassVar[NodalSupport.DiagramAroundXEnd]
        DIAGRAM_AROUND_X_END_STOP: _ClassVar[NodalSupport.DiagramAroundXEnd]
        DIAGRAM_AROUND_X_END_YIELDING: _ClassVar[NodalSupport.DiagramAroundXEnd]
    DIAGRAM_AROUND_X_END_FAILURE: NodalSupport.DiagramAroundXEnd
    DIAGRAM_AROUND_X_END_CONTINUOUS: NodalSupport.DiagramAroundXEnd
    DIAGRAM_AROUND_X_END_STOP: NodalSupport.DiagramAroundXEnd
    DIAGRAM_AROUND_X_END_YIELDING: NodalSupport.DiagramAroundXEnd
    class DiagramAroundYStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_Y_START_FAILURE: _ClassVar[NodalSupport.DiagramAroundYStart]
        DIAGRAM_AROUND_Y_START_CONTINUOUS: _ClassVar[NodalSupport.DiagramAroundYStart]
        DIAGRAM_AROUND_Y_START_STOP: _ClassVar[NodalSupport.DiagramAroundYStart]
        DIAGRAM_AROUND_Y_START_YIELDING: _ClassVar[NodalSupport.DiagramAroundYStart]
    DIAGRAM_AROUND_Y_START_FAILURE: NodalSupport.DiagramAroundYStart
    DIAGRAM_AROUND_Y_START_CONTINUOUS: NodalSupport.DiagramAroundYStart
    DIAGRAM_AROUND_Y_START_STOP: NodalSupport.DiagramAroundYStart
    DIAGRAM_AROUND_Y_START_YIELDING: NodalSupport.DiagramAroundYStart
    class DiagramAroundYEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_Y_END_FAILURE: _ClassVar[NodalSupport.DiagramAroundYEnd]
        DIAGRAM_AROUND_Y_END_CONTINUOUS: _ClassVar[NodalSupport.DiagramAroundYEnd]
        DIAGRAM_AROUND_Y_END_STOP: _ClassVar[NodalSupport.DiagramAroundYEnd]
        DIAGRAM_AROUND_Y_END_YIELDING: _ClassVar[NodalSupport.DiagramAroundYEnd]
    DIAGRAM_AROUND_Y_END_FAILURE: NodalSupport.DiagramAroundYEnd
    DIAGRAM_AROUND_Y_END_CONTINUOUS: NodalSupport.DiagramAroundYEnd
    DIAGRAM_AROUND_Y_END_STOP: NodalSupport.DiagramAroundYEnd
    DIAGRAM_AROUND_Y_END_YIELDING: NodalSupport.DiagramAroundYEnd
    class DiagramAroundZStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_Z_START_FAILURE: _ClassVar[NodalSupport.DiagramAroundZStart]
        DIAGRAM_AROUND_Z_START_CONTINUOUS: _ClassVar[NodalSupport.DiagramAroundZStart]
        DIAGRAM_AROUND_Z_START_STOP: _ClassVar[NodalSupport.DiagramAroundZStart]
        DIAGRAM_AROUND_Z_START_YIELDING: _ClassVar[NodalSupport.DiagramAroundZStart]
    DIAGRAM_AROUND_Z_START_FAILURE: NodalSupport.DiagramAroundZStart
    DIAGRAM_AROUND_Z_START_CONTINUOUS: NodalSupport.DiagramAroundZStart
    DIAGRAM_AROUND_Z_START_STOP: NodalSupport.DiagramAroundZStart
    DIAGRAM_AROUND_Z_START_YIELDING: NodalSupport.DiagramAroundZStart
    class DiagramAroundZEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_Z_END_FAILURE: _ClassVar[NodalSupport.DiagramAroundZEnd]
        DIAGRAM_AROUND_Z_END_CONTINUOUS: _ClassVar[NodalSupport.DiagramAroundZEnd]
        DIAGRAM_AROUND_Z_END_STOP: _ClassVar[NodalSupport.DiagramAroundZEnd]
        DIAGRAM_AROUND_Z_END_YIELDING: _ClassVar[NodalSupport.DiagramAroundZEnd]
    DIAGRAM_AROUND_Z_END_FAILURE: NodalSupport.DiagramAroundZEnd
    DIAGRAM_AROUND_Z_END_CONTINUOUS: NodalSupport.DiagramAroundZEnd
    DIAGRAM_AROUND_Z_END_STOP: NodalSupport.DiagramAroundZEnd
    DIAGRAM_AROUND_Z_END_YIELDING: NodalSupport.DiagramAroundZEnd
    class DirectedToNodeFirstAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIRECTED_TO_NODE_FIRST_AXIS_X: _ClassVar[NodalSupport.DirectedToNodeFirstAxis]
        DIRECTED_TO_NODE_FIRST_AXIS_Y: _ClassVar[NodalSupport.DirectedToNodeFirstAxis]
        DIRECTED_TO_NODE_FIRST_AXIS_Z: _ClassVar[NodalSupport.DirectedToNodeFirstAxis]
    DIRECTED_TO_NODE_FIRST_AXIS_X: NodalSupport.DirectedToNodeFirstAxis
    DIRECTED_TO_NODE_FIRST_AXIS_Y: NodalSupport.DirectedToNodeFirstAxis
    DIRECTED_TO_NODE_FIRST_AXIS_Z: NodalSupport.DirectedToNodeFirstAxis
    class DirectedToNodeSecondAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIRECTED_TO_NODE_SECOND_AXIS_X: _ClassVar[NodalSupport.DirectedToNodeSecondAxis]
        DIRECTED_TO_NODE_SECOND_AXIS_Y: _ClassVar[NodalSupport.DirectedToNodeSecondAxis]
        DIRECTED_TO_NODE_SECOND_AXIS_Z: _ClassVar[NodalSupport.DirectedToNodeSecondAxis]
    DIRECTED_TO_NODE_SECOND_AXIS_X: NodalSupport.DirectedToNodeSecondAxis
    DIRECTED_TO_NODE_SECOND_AXIS_Y: NodalSupport.DirectedToNodeSecondAxis
    DIRECTED_TO_NODE_SECOND_AXIS_Z: NodalSupport.DirectedToNodeSecondAxis
    class ParallelToTwoNodesFirstAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARALLEL_TO_TWO_NODES_FIRST_AXIS_X: _ClassVar[NodalSupport.ParallelToTwoNodesFirstAxis]
        PARALLEL_TO_TWO_NODES_FIRST_AXIS_Y: _ClassVar[NodalSupport.ParallelToTwoNodesFirstAxis]
        PARALLEL_TO_TWO_NODES_FIRST_AXIS_Z: _ClassVar[NodalSupport.ParallelToTwoNodesFirstAxis]
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_X: NodalSupport.ParallelToTwoNodesFirstAxis
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_Y: NodalSupport.ParallelToTwoNodesFirstAxis
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_Z: NodalSupport.ParallelToTwoNodesFirstAxis
    class ParallelToTwoNodesSecondAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARALLEL_TO_TWO_NODES_SECOND_AXIS_X: _ClassVar[NodalSupport.ParallelToTwoNodesSecondAxis]
        PARALLEL_TO_TWO_NODES_SECOND_AXIS_Y: _ClassVar[NodalSupport.ParallelToTwoNodesSecondAxis]
        PARALLEL_TO_TWO_NODES_SECOND_AXIS_Z: _ClassVar[NodalSupport.ParallelToTwoNodesSecondAxis]
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_X: NodalSupport.ParallelToTwoNodesSecondAxis
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_Y: NodalSupport.ParallelToTwoNodesSecondAxis
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_Z: NodalSupport.ParallelToTwoNodesSecondAxis
    class PartialActivityAlongXNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_COMPLETE: _ClassVar[NodalSupport.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE: _ClassVar[NodalSupport.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIXED: _ClassVar[NodalSupport.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAlongXNegativeType]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_COMPLETE: NodalSupport.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE: NodalSupport.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIXED: NodalSupport.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAlongXNegativeType
    class PartialActivityAlongXPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_COMPLETE: _ClassVar[NodalSupport.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE: _ClassVar[NodalSupport.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIXED: _ClassVar[NodalSupport.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAlongXPositiveType]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_COMPLETE: NodalSupport.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE: NodalSupport.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIXED: NodalSupport.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAlongXPositiveType
    class PartialActivityAlongYNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_COMPLETE: _ClassVar[NodalSupport.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE: _ClassVar[NodalSupport.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FIXED: _ClassVar[NodalSupport.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAlongYNegativeType]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_COMPLETE: NodalSupport.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE: NodalSupport.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FIXED: NodalSupport.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAlongYNegativeType
    class PartialActivityAlongYPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_COMPLETE: _ClassVar[NodalSupport.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE: _ClassVar[NodalSupport.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FIXED: _ClassVar[NodalSupport.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAlongYPositiveType]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_COMPLETE: NodalSupport.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE: NodalSupport.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FIXED: NodalSupport.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAlongYPositiveType
    class PartialActivityAlongZNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_COMPLETE: _ClassVar[NodalSupport.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE: _ClassVar[NodalSupport.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FIXED: _ClassVar[NodalSupport.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAlongZNegativeType]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_COMPLETE: NodalSupport.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE: NodalSupport.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FIXED: NodalSupport.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAlongZNegativeType
    class PartialActivityAlongZPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_COMPLETE: _ClassVar[NodalSupport.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE: _ClassVar[NodalSupport.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FIXED: _ClassVar[NodalSupport.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAlongZPositiveType]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_COMPLETE: NodalSupport.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE: NodalSupport.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FIXED: NodalSupport.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAlongZPositiveType
    class PartialActivityAroundXNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_COMPLETE: _ClassVar[NodalSupport.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE: _ClassVar[NodalSupport.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FIXED: _ClassVar[NodalSupport.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAroundXNegativeType]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_COMPLETE: NodalSupport.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE: NodalSupport.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FIXED: NodalSupport.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAroundXNegativeType
    class PartialActivityAroundXPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_COMPLETE: _ClassVar[NodalSupport.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE: _ClassVar[NodalSupport.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FIXED: _ClassVar[NodalSupport.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAroundXPositiveType]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_COMPLETE: NodalSupport.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE: NodalSupport.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FIXED: NodalSupport.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAroundXPositiveType
    class PartialActivityAroundYNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_COMPLETE: _ClassVar[NodalSupport.PartialActivityAroundYNegativeType]
        PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FAILURE: _ClassVar[NodalSupport.PartialActivityAroundYNegativeType]
        PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAroundYNegativeType]
        PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FIXED: _ClassVar[NodalSupport.PartialActivityAroundYNegativeType]
        PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAroundYNegativeType]
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_COMPLETE: NodalSupport.PartialActivityAroundYNegativeType
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FAILURE: NodalSupport.PartialActivityAroundYNegativeType
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAroundYNegativeType
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FIXED: NodalSupport.PartialActivityAroundYNegativeType
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAroundYNegativeType
    class PartialActivityAroundYPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_COMPLETE: _ClassVar[NodalSupport.PartialActivityAroundYPositiveType]
        PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FAILURE: _ClassVar[NodalSupport.PartialActivityAroundYPositiveType]
        PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAroundYPositiveType]
        PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FIXED: _ClassVar[NodalSupport.PartialActivityAroundYPositiveType]
        PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAroundYPositiveType]
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_COMPLETE: NodalSupport.PartialActivityAroundYPositiveType
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FAILURE: NodalSupport.PartialActivityAroundYPositiveType
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAroundYPositiveType
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FIXED: NodalSupport.PartialActivityAroundYPositiveType
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAroundYPositiveType
    class PartialActivityAroundZNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_COMPLETE: _ClassVar[NodalSupport.PartialActivityAroundZNegativeType]
        PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FAILURE: _ClassVar[NodalSupport.PartialActivityAroundZNegativeType]
        PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAroundZNegativeType]
        PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FIXED: _ClassVar[NodalSupport.PartialActivityAroundZNegativeType]
        PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAroundZNegativeType]
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_COMPLETE: NodalSupport.PartialActivityAroundZNegativeType
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FAILURE: NodalSupport.PartialActivityAroundZNegativeType
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAroundZNegativeType
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FIXED: NodalSupport.PartialActivityAroundZNegativeType
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAroundZNegativeType
    class PartialActivityAroundZPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_COMPLETE: _ClassVar[NodalSupport.PartialActivityAroundZPositiveType]
        PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FAILURE: _ClassVar[NodalSupport.PartialActivityAroundZPositiveType]
        PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAroundZPositiveType]
        PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FIXED: _ClassVar[NodalSupport.PartialActivityAroundZPositiveType]
        PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[NodalSupport.PartialActivityAroundZPositiveType]
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_COMPLETE: NodalSupport.PartialActivityAroundZPositiveType
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FAILURE: NodalSupport.PartialActivityAroundZPositiveType
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAroundZPositiveType
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FIXED: NodalSupport.PartialActivityAroundZPositiveType
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: NodalSupport.PartialActivityAroundZPositiveType
    class StiffnessDiagramAroundXDependsOn(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STIFFNESS_DIAGRAM_AROUND_X_DEPENDS_ON_PX: _ClassVar[NodalSupport.StiffnessDiagramAroundXDependsOn]
        STIFFNESS_DIAGRAM_AROUND_X_DEPENDS_ON_P: _ClassVar[NodalSupport.StiffnessDiagramAroundXDependsOn]
        STIFFNESS_DIAGRAM_AROUND_X_DEPENDS_ON_PY: _ClassVar[NodalSupport.StiffnessDiagramAroundXDependsOn]
        STIFFNESS_DIAGRAM_AROUND_X_DEPENDS_ON_PZ: _ClassVar[NodalSupport.StiffnessDiagramAroundXDependsOn]
    STIFFNESS_DIAGRAM_AROUND_X_DEPENDS_ON_PX: NodalSupport.StiffnessDiagramAroundXDependsOn
    STIFFNESS_DIAGRAM_AROUND_X_DEPENDS_ON_P: NodalSupport.StiffnessDiagramAroundXDependsOn
    STIFFNESS_DIAGRAM_AROUND_X_DEPENDS_ON_PY: NodalSupport.StiffnessDiagramAroundXDependsOn
    STIFFNESS_DIAGRAM_AROUND_X_DEPENDS_ON_PZ: NodalSupport.StiffnessDiagramAroundXDependsOn
    class StiffnessDiagramAroundXEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STIFFNESS_DIAGRAM_AROUND_X_END_FAILURE: _ClassVar[NodalSupport.StiffnessDiagramAroundXEnd]
        STIFFNESS_DIAGRAM_AROUND_X_END_CONTINUOUS: _ClassVar[NodalSupport.StiffnessDiagramAroundXEnd]
        STIFFNESS_DIAGRAM_AROUND_X_END_YIELDING: _ClassVar[NodalSupport.StiffnessDiagramAroundXEnd]
    STIFFNESS_DIAGRAM_AROUND_X_END_FAILURE: NodalSupport.StiffnessDiagramAroundXEnd
    STIFFNESS_DIAGRAM_AROUND_X_END_CONTINUOUS: NodalSupport.StiffnessDiagramAroundXEnd
    STIFFNESS_DIAGRAM_AROUND_X_END_YIELDING: NodalSupport.StiffnessDiagramAroundXEnd
    class StiffnessDiagramAroundXStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STIFFNESS_DIAGRAM_AROUND_X_START_FAILURE: _ClassVar[NodalSupport.StiffnessDiagramAroundXStart]
        STIFFNESS_DIAGRAM_AROUND_X_START_CONTINUOUS: _ClassVar[NodalSupport.StiffnessDiagramAroundXStart]
        STIFFNESS_DIAGRAM_AROUND_X_START_YIELDING: _ClassVar[NodalSupport.StiffnessDiagramAroundXStart]
    STIFFNESS_DIAGRAM_AROUND_X_START_FAILURE: NodalSupport.StiffnessDiagramAroundXStart
    STIFFNESS_DIAGRAM_AROUND_X_START_CONTINUOUS: NodalSupport.StiffnessDiagramAroundXStart
    STIFFNESS_DIAGRAM_AROUND_X_START_YIELDING: NodalSupport.StiffnessDiagramAroundXStart
    class StiffnessDiagramAroundYDependsOn(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STIFFNESS_DIAGRAM_AROUND_Y_DEPENDS_ON_PX: _ClassVar[NodalSupport.StiffnessDiagramAroundYDependsOn]
        STIFFNESS_DIAGRAM_AROUND_Y_DEPENDS_ON_P: _ClassVar[NodalSupport.StiffnessDiagramAroundYDependsOn]
        STIFFNESS_DIAGRAM_AROUND_Y_DEPENDS_ON_PY: _ClassVar[NodalSupport.StiffnessDiagramAroundYDependsOn]
        STIFFNESS_DIAGRAM_AROUND_Y_DEPENDS_ON_PZ: _ClassVar[NodalSupport.StiffnessDiagramAroundYDependsOn]
    STIFFNESS_DIAGRAM_AROUND_Y_DEPENDS_ON_PX: NodalSupport.StiffnessDiagramAroundYDependsOn
    STIFFNESS_DIAGRAM_AROUND_Y_DEPENDS_ON_P: NodalSupport.StiffnessDiagramAroundYDependsOn
    STIFFNESS_DIAGRAM_AROUND_Y_DEPENDS_ON_PY: NodalSupport.StiffnessDiagramAroundYDependsOn
    STIFFNESS_DIAGRAM_AROUND_Y_DEPENDS_ON_PZ: NodalSupport.StiffnessDiagramAroundYDependsOn
    class StiffnessDiagramAroundYEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STIFFNESS_DIAGRAM_AROUND_Y_END_FAILURE: _ClassVar[NodalSupport.StiffnessDiagramAroundYEnd]
        STIFFNESS_DIAGRAM_AROUND_Y_END_CONTINUOUS: _ClassVar[NodalSupport.StiffnessDiagramAroundYEnd]
        STIFFNESS_DIAGRAM_AROUND_Y_END_YIELDING: _ClassVar[NodalSupport.StiffnessDiagramAroundYEnd]
    STIFFNESS_DIAGRAM_AROUND_Y_END_FAILURE: NodalSupport.StiffnessDiagramAroundYEnd
    STIFFNESS_DIAGRAM_AROUND_Y_END_CONTINUOUS: NodalSupport.StiffnessDiagramAroundYEnd
    STIFFNESS_DIAGRAM_AROUND_Y_END_YIELDING: NodalSupport.StiffnessDiagramAroundYEnd
    class StiffnessDiagramAroundYStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STIFFNESS_DIAGRAM_AROUND_Y_START_FAILURE: _ClassVar[NodalSupport.StiffnessDiagramAroundYStart]
        STIFFNESS_DIAGRAM_AROUND_Y_START_CONTINUOUS: _ClassVar[NodalSupport.StiffnessDiagramAroundYStart]
        STIFFNESS_DIAGRAM_AROUND_Y_START_YIELDING: _ClassVar[NodalSupport.StiffnessDiagramAroundYStart]
    STIFFNESS_DIAGRAM_AROUND_Y_START_FAILURE: NodalSupport.StiffnessDiagramAroundYStart
    STIFFNESS_DIAGRAM_AROUND_Y_START_CONTINUOUS: NodalSupport.StiffnessDiagramAroundYStart
    STIFFNESS_DIAGRAM_AROUND_Y_START_YIELDING: NodalSupport.StiffnessDiagramAroundYStart
    class StiffnessDiagramAroundZDependsOn(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STIFFNESS_DIAGRAM_AROUND_Z_DEPENDS_ON_PX: _ClassVar[NodalSupport.StiffnessDiagramAroundZDependsOn]
        STIFFNESS_DIAGRAM_AROUND_Z_DEPENDS_ON_P: _ClassVar[NodalSupport.StiffnessDiagramAroundZDependsOn]
        STIFFNESS_DIAGRAM_AROUND_Z_DEPENDS_ON_PY: _ClassVar[NodalSupport.StiffnessDiagramAroundZDependsOn]
        STIFFNESS_DIAGRAM_AROUND_Z_DEPENDS_ON_PZ: _ClassVar[NodalSupport.StiffnessDiagramAroundZDependsOn]
    STIFFNESS_DIAGRAM_AROUND_Z_DEPENDS_ON_PX: NodalSupport.StiffnessDiagramAroundZDependsOn
    STIFFNESS_DIAGRAM_AROUND_Z_DEPENDS_ON_P: NodalSupport.StiffnessDiagramAroundZDependsOn
    STIFFNESS_DIAGRAM_AROUND_Z_DEPENDS_ON_PY: NodalSupport.StiffnessDiagramAroundZDependsOn
    STIFFNESS_DIAGRAM_AROUND_Z_DEPENDS_ON_PZ: NodalSupport.StiffnessDiagramAroundZDependsOn
    class StiffnessDiagramAroundZEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STIFFNESS_DIAGRAM_AROUND_Z_END_FAILURE: _ClassVar[NodalSupport.StiffnessDiagramAroundZEnd]
        STIFFNESS_DIAGRAM_AROUND_Z_END_CONTINUOUS: _ClassVar[NodalSupport.StiffnessDiagramAroundZEnd]
        STIFFNESS_DIAGRAM_AROUND_Z_END_YIELDING: _ClassVar[NodalSupport.StiffnessDiagramAroundZEnd]
    STIFFNESS_DIAGRAM_AROUND_Z_END_FAILURE: NodalSupport.StiffnessDiagramAroundZEnd
    STIFFNESS_DIAGRAM_AROUND_Z_END_CONTINUOUS: NodalSupport.StiffnessDiagramAroundZEnd
    STIFFNESS_DIAGRAM_AROUND_Z_END_YIELDING: NodalSupport.StiffnessDiagramAroundZEnd
    class StiffnessDiagramAroundZStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STIFFNESS_DIAGRAM_AROUND_Z_START_FAILURE: _ClassVar[NodalSupport.StiffnessDiagramAroundZStart]
        STIFFNESS_DIAGRAM_AROUND_Z_START_CONTINUOUS: _ClassVar[NodalSupport.StiffnessDiagramAroundZStart]
        STIFFNESS_DIAGRAM_AROUND_Z_START_YIELDING: _ClassVar[NodalSupport.StiffnessDiagramAroundZStart]
    STIFFNESS_DIAGRAM_AROUND_Z_START_FAILURE: NodalSupport.StiffnessDiagramAroundZStart
    STIFFNESS_DIAGRAM_AROUND_Z_START_CONTINUOUS: NodalSupport.StiffnessDiagramAroundZStart
    STIFFNESS_DIAGRAM_AROUND_Z_START_YIELDING: NodalSupport.StiffnessDiagramAroundZStart
    class SupportDimensionTypeOnX(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUPPORT_DIMENSION_TYPE_ON_X_RECTANGULAR: _ClassVar[NodalSupport.SupportDimensionTypeOnX]
        SUPPORT_DIMENSION_TYPE_ON_X_CIRCULAR: _ClassVar[NodalSupport.SupportDimensionTypeOnX]
        SUPPORT_DIMENSION_TYPE_ON_X_NONE: _ClassVar[NodalSupport.SupportDimensionTypeOnX]
    SUPPORT_DIMENSION_TYPE_ON_X_RECTANGULAR: NodalSupport.SupportDimensionTypeOnX
    SUPPORT_DIMENSION_TYPE_ON_X_CIRCULAR: NodalSupport.SupportDimensionTypeOnX
    SUPPORT_DIMENSION_TYPE_ON_X_NONE: NodalSupport.SupportDimensionTypeOnX
    class SupportDimensionTypeOnY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUPPORT_DIMENSION_TYPE_ON_Y_RECTANGULAR: _ClassVar[NodalSupport.SupportDimensionTypeOnY]
        SUPPORT_DIMENSION_TYPE_ON_Y_CIRCULAR: _ClassVar[NodalSupport.SupportDimensionTypeOnY]
        SUPPORT_DIMENSION_TYPE_ON_Y_NONE: _ClassVar[NodalSupport.SupportDimensionTypeOnY]
    SUPPORT_DIMENSION_TYPE_ON_Y_RECTANGULAR: NodalSupport.SupportDimensionTypeOnY
    SUPPORT_DIMENSION_TYPE_ON_Y_CIRCULAR: NodalSupport.SupportDimensionTypeOnY
    SUPPORT_DIMENSION_TYPE_ON_Y_NONE: NodalSupport.SupportDimensionTypeOnY
    class SupportDimensionTypeOnZ(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUPPORT_DIMENSION_TYPE_ON_Z_RECTANGULAR: _ClassVar[NodalSupport.SupportDimensionTypeOnZ]
        SUPPORT_DIMENSION_TYPE_ON_Z_CIRCULAR: _ClassVar[NodalSupport.SupportDimensionTypeOnZ]
        SUPPORT_DIMENSION_TYPE_ON_Z_NONE: _ClassVar[NodalSupport.SupportDimensionTypeOnZ]
    SUPPORT_DIMENSION_TYPE_ON_Z_RECTANGULAR: NodalSupport.SupportDimensionTypeOnZ
    SUPPORT_DIMENSION_TYPE_ON_Z_CIRCULAR: NodalSupport.SupportDimensionTypeOnZ
    SUPPORT_DIMENSION_TYPE_ON_Z_NONE: NodalSupport.SupportDimensionTypeOnZ
    class DiagramAlongXTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[NodalSupport.DiagramAlongXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[NodalSupport.DiagramAlongXTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAlongXTableRow(_message.Message):
        __slots__ = ("no", "description", "displacement", "force", "spring", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
        FORCE_FIELD_NUMBER: _ClassVar[int]
        SPRING_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        displacement: float
        force: float
        spring: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., displacement: _Optional[float] = ..., force: _Optional[float] = ..., spring: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    class DiagramAlongYTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[NodalSupport.DiagramAlongYTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[NodalSupport.DiagramAlongYTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAlongYTableRow(_message.Message):
        __slots__ = ("no", "description", "displacement", "force", "spring", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
        FORCE_FIELD_NUMBER: _ClassVar[int]
        SPRING_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        displacement: float
        force: float
        spring: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., displacement: _Optional[float] = ..., force: _Optional[float] = ..., spring: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    class DiagramAlongZTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[NodalSupport.DiagramAlongZTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[NodalSupport.DiagramAlongZTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAlongZTableRow(_message.Message):
        __slots__ = ("no", "description", "displacement", "force", "spring", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
        FORCE_FIELD_NUMBER: _ClassVar[int]
        SPRING_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        displacement: float
        force: float
        spring: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., displacement: _Optional[float] = ..., force: _Optional[float] = ..., spring: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    class DiagramAroundXTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[NodalSupport.DiagramAroundXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[NodalSupport.DiagramAroundXTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAroundXTableRow(_message.Message):
        __slots__ = ("no", "description", "rotation", "moment", "spring", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        ROTATION_FIELD_NUMBER: _ClassVar[int]
        MOMENT_FIELD_NUMBER: _ClassVar[int]
        SPRING_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        rotation: float
        moment: float
        spring: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., rotation: _Optional[float] = ..., moment: _Optional[float] = ..., spring: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    class DiagramAroundYTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[NodalSupport.DiagramAroundYTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[NodalSupport.DiagramAroundYTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAroundYTableRow(_message.Message):
        __slots__ = ("no", "description", "rotation", "moment", "spring", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        ROTATION_FIELD_NUMBER: _ClassVar[int]
        MOMENT_FIELD_NUMBER: _ClassVar[int]
        SPRING_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        rotation: float
        moment: float
        spring: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., rotation: _Optional[float] = ..., moment: _Optional[float] = ..., spring: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    class DiagramAroundZTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[NodalSupport.DiagramAroundZTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[NodalSupport.DiagramAroundZTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAroundZTableRow(_message.Message):
        __slots__ = ("no", "description", "rotation", "moment", "spring", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        ROTATION_FIELD_NUMBER: _ClassVar[int]
        MOMENT_FIELD_NUMBER: _ClassVar[int]
        SPRING_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        rotation: float
        moment: float
        spring: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., rotation: _Optional[float] = ..., moment: _Optional[float] = ..., spring: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    class StiffnessDiagramAroundXTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[NodalSupport.StiffnessDiagramAroundXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[NodalSupport.StiffnessDiagramAroundXTableRow, _Mapping]]] = ...) -> None: ...
    class StiffnessDiagramAroundXTableRow(_message.Message):
        __slots__ = ("no", "description", "force", "spring", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FORCE_FIELD_NUMBER: _ClassVar[int]
        SPRING_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        force: float
        spring: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., force: _Optional[float] = ..., spring: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    class StiffnessDiagramAroundYTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[NodalSupport.StiffnessDiagramAroundYTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[NodalSupport.StiffnessDiagramAroundYTableRow, _Mapping]]] = ...) -> None: ...
    class StiffnessDiagramAroundYTableRow(_message.Message):
        __slots__ = ("no", "description", "force", "spring", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FORCE_FIELD_NUMBER: _ClassVar[int]
        SPRING_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        force: float
        spring: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., force: _Optional[float] = ..., spring: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    class StiffnessDiagramAroundZTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[NodalSupport.StiffnessDiagramAroundZTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[NodalSupport.StiffnessDiagramAroundZTableRow, _Mapping]]] = ...) -> None: ...
    class StiffnessDiagramAroundZTableRow(_message.Message):
        __slots__ = ("no", "description", "force", "spring", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FORCE_FIELD_NUMBER: _ClassVar[int]
        SPRING_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        force: float
        spring: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., force: _Optional[float] = ..., spring: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    class DiagramAlongXColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[NodalSupport.DiagramAlongXColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[NodalSupport.DiagramAlongXColorTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAlongXColorTableRow(_message.Message):
        __slots__ = ("no", "description", "color")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        color: _common_pb2.Color
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., color: _Optional[_Union[_common_pb2.Color, _Mapping]] = ...) -> None: ...
    class DiagramAlongYColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[NodalSupport.DiagramAlongYColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[NodalSupport.DiagramAlongYColorTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAlongYColorTableRow(_message.Message):
        __slots__ = ("no", "description", "color")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        color: _common_pb2.Color
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., color: _Optional[_Union[_common_pb2.Color, _Mapping]] = ...) -> None: ...
    class DiagramAlongZColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[NodalSupport.DiagramAlongZColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[NodalSupport.DiagramAlongZColorTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAlongZColorTableRow(_message.Message):
        __slots__ = ("no", "description", "color")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        color: _common_pb2.Color
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., color: _Optional[_Union[_common_pb2.Color, _Mapping]] = ...) -> None: ...
    class DiagramAroundXColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[NodalSupport.DiagramAroundXColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[NodalSupport.DiagramAroundXColorTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAroundXColorTableRow(_message.Message):
        __slots__ = ("no", "description", "color")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        color: _common_pb2.Color
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., color: _Optional[_Union[_common_pb2.Color, _Mapping]] = ...) -> None: ...
    class DiagramAroundYColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[NodalSupport.DiagramAroundYColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[NodalSupport.DiagramAroundYColorTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAroundYColorTableRow(_message.Message):
        __slots__ = ("no", "description", "color")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        color: _common_pb2.Color
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., color: _Optional[_Union[_common_pb2.Color, _Mapping]] = ...) -> None: ...
    class DiagramAroundZColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[NodalSupport.DiagramAroundZColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[NodalSupport.DiagramAroundZColorTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAroundZColorTableRow(_message.Message):
        __slots__ = ("no", "description", "color")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        color: _common_pb2.Color
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., color: _Optional[_Union[_common_pb2.Color, _Mapping]] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FICTITIOUS_COLUMN_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SPECIFIC_DIRECTION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SPECIFIC_DIRECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    SPRING_FIELD_NUMBER: _ClassVar[int]
    SPRING_X_FIELD_NUMBER: _ClassVar[int]
    SPRING_Y_FIELD_NUMBER: _ClassVar[int]
    SPRING_Z_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RESTRAINT_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RESTRAINT_X_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RESTRAINT_Y_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RESTRAINT_Z_FIELD_NUMBER: _ClassVar[int]
    SPRING_X_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    SPRING_Y_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    SPRING_Z_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    AXES_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_BASE_SEMI_RIGID_FIELD_NUMBER: _ClassVar[int]
    COLUMN_BASE_SUPPORT_TYPE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_HEAD_SUPPORT_TYPE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_HEAD_TYPE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    COLUMN_SECTION_SAME_AS_HEAD_FIELD_NUMBER: _ClassVar[int]
    COLUMN_MATERIAL_FIELD_NUMBER: _ClassVar[int]
    COLUMN_ROTATION_FIELD_NUMBER: _ClassVar[int]
    COLUMN_ROTATIONAL_RESTRAINT_X_FIELD_NUMBER: _ClassVar[int]
    COLUMN_ROTATIONAL_RESTRAINT_Y_FIELD_NUMBER: _ClassVar[int]
    COLUMN_SECTION_FIELD_NUMBER: _ClassVar[int]
    COLUMN_SHEAR_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    COLUMN_SPRING_X_FIELD_NUMBER: _ClassVar[int]
    COLUMN_SPRING_Y_FIELD_NUMBER: _ClassVar[int]
    COLUMN_SPRING_Z_FIELD_NUMBER: _ClassVar[int]
    COLUMN_SUPPORT_TYPE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_WIDTH_X_FIELD_NUMBER: _ClassVar[int]
    COLUMN_WIDTH_Y_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_DIRECTION_NODE_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_FIRST_AXIS_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_PLANE_NODE_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_SECOND_AXIS_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_X_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_XY_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_XZ_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_Y_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_YX_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_YZ_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_Z_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_ZX_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_ZY_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_LINE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_MEMBER_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_FIRST_NODE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_PLANE_NODE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_SECOND_NODE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_1_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_2_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_3_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_X_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_Y_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_Z_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_X_DEPENDS_ON_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_X_END_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_X_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_X_START_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_X_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_X_TABLE_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_Y_DEPENDS_ON_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_Y_END_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_Y_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_Y_START_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_Y_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_Y_TABLE_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_Z_DEPENDS_ON_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_Z_END_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_Z_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_Z_START_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_Z_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_DIAGRAM_AROUND_Z_TABLE_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_DIMENSION_DIAMETER_X_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_DIMENSION_DIAMETER_Y_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_DIMENSION_DIAMETER_Z_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_DIMENSION_HEIGHT_X_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_DIMENSION_HEIGHT_Y_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_DIMENSION_HEIGHT_Z_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_DIMENSION_TYPE_ON_X_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_DIMENSION_TYPE_ON_Y_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_DIMENSION_TYPE_ON_Z_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_DIMENSION_WIDTH_X_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_DIMENSION_WIDTH_Y_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_DIMENSION_WIDTH_Z_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_DIMENSIONS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_AC_YIELD_MINUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_AC_YIELD_MINUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_AC_YIELD_MINUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_AC_YIELD_MINUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_AC_YIELD_MINUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_AC_YIELD_MINUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_AC_YIELD_PLUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_AC_YIELD_PLUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_AC_YIELD_PLUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_AC_YIELD_PLUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_AC_YIELD_PLUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_AC_YIELD_PLUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_ACCEPTANCE_CRITERIA_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_ACCEPTANCE_CRITERIA_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_ACCEPTANCE_CRITERIA_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_ACCEPTANCE_CRITERIA_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_ACCEPTANCE_CRITERIA_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_ACCEPTANCE_CRITERIA_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    fictitious_column_enabled: bool
    specific_direction_enabled: bool
    specific_direction_type: NodalSupport.SpecificDirectionType
    nodes: _containers.RepeatedScalarFieldContainer[int]
    spring: _common_pb2.Vector3d
    spring_x: float
    spring_y: float
    spring_z: float
    rotational_restraint: _common_pb2.Vector3d
    rotational_restraint_x: float
    rotational_restraint_y: float
    rotational_restraint_z: float
    spring_x_nonlinearity: NodalSupport.SpringXNonlinearity
    spring_y_nonlinearity: NodalSupport.SpringYNonlinearity
    spring_z_nonlinearity: NodalSupport.SpringZNonlinearity
    rotational_restraint_x_nonlinearity: NodalSupport.RotationalRestraintXNonlinearity
    rotational_restraint_y_nonlinearity: NodalSupport.RotationalRestraintYNonlinearity
    rotational_restraint_z_nonlinearity: NodalSupport.RotationalRestraintZNonlinearity
    axes_sequence: NodalSupport.AxesSequence
    column_base_semi_rigid: float
    column_base_support_type: NodalSupport.ColumnBaseSupportType
    column_head_support_type: NodalSupport.ColumnHeadSupportType
    column_head_type: NodalSupport.ColumnHeadType
    column_height: float
    column_section_same_as_head: bool
    column_material: int
    column_rotation: float
    column_rotational_restraint_x: float
    column_rotational_restraint_y: float
    column_section: int
    column_shear_stiffness: bool
    column_spring_x: float
    column_spring_y: float
    column_spring_z: float
    column_support_type: NodalSupport.ColumnSupportType
    column_width_x: float
    column_width_y: float
    comment: str
    coordinate_system: int
    diagram_along_x_symmetric: bool
    diagram_along_x_start: NodalSupport.DiagramAlongXStart
    diagram_along_x_end: NodalSupport.DiagramAlongXEnd
    diagram_along_x_table: NodalSupport.DiagramAlongXTable
    diagram_along_x_is_sorted: bool
    diagram_along_y_symmetric: bool
    diagram_along_y_start: NodalSupport.DiagramAlongYStart
    diagram_along_y_end: NodalSupport.DiagramAlongYEnd
    diagram_along_y_table: NodalSupport.DiagramAlongYTable
    diagram_along_y_is_sorted: bool
    diagram_along_z_symmetric: bool
    diagram_along_z_start: NodalSupport.DiagramAlongZStart
    diagram_along_z_end: NodalSupport.DiagramAlongZEnd
    diagram_along_z_table: NodalSupport.DiagramAlongZTable
    diagram_along_z_is_sorted: bool
    diagram_around_x_symmetric: bool
    diagram_around_x_start: NodalSupport.DiagramAroundXStart
    diagram_around_x_end: NodalSupport.DiagramAroundXEnd
    diagram_around_x_table: NodalSupport.DiagramAroundXTable
    diagram_around_x_is_sorted: bool
    diagram_around_y_symmetric: bool
    diagram_around_y_start: NodalSupport.DiagramAroundYStart
    diagram_around_y_end: NodalSupport.DiagramAroundYEnd
    diagram_around_y_table: NodalSupport.DiagramAroundYTable
    diagram_around_y_is_sorted: bool
    diagram_around_z_symmetric: bool
    diagram_around_z_start: NodalSupport.DiagramAroundZStart
    diagram_around_z_end: NodalSupport.DiagramAroundZEnd
    diagram_around_z_table: NodalSupport.DiagramAroundZTable
    diagram_around_z_is_sorted: bool
    directed_to_node_direction_node: int
    directed_to_node_first_axis: NodalSupport.DirectedToNodeFirstAxis
    directed_to_node_plane_node: int
    directed_to_node_second_axis: NodalSupport.DirectedToNodeSecondAxis
    friction_coefficient_x: float
    friction_coefficient_xy: float
    friction_coefficient_xz: float
    friction_coefficient_y: float
    friction_coefficient_yx: float
    friction_coefficient_yz: float
    friction_coefficient_z: float
    friction_coefficient_zx: float
    friction_coefficient_zy: float
    parallel_to_line: int
    parallel_to_member: int
    parallel_to_two_nodes_first_axis: NodalSupport.ParallelToTwoNodesFirstAxis
    parallel_to_two_nodes_first_node: int
    parallel_to_two_nodes_plane_node: int
    parallel_to_two_nodes_second_axis: NodalSupport.ParallelToTwoNodesSecondAxis
    parallel_to_two_nodes_second_node: int
    partial_activity_along_x_negative_type: NodalSupport.PartialActivityAlongXNegativeType
    partial_activity_along_x_negative_displacement: float
    partial_activity_along_x_negative_force: float
    partial_activity_along_x_negative_slippage: float
    partial_activity_along_x_positive_type: NodalSupport.PartialActivityAlongXPositiveType
    partial_activity_along_x_positive_displacement: float
    partial_activity_along_x_positive_force: float
    partial_activity_along_x_positive_slippage: float
    partial_activity_along_y_negative_type: NodalSupport.PartialActivityAlongYNegativeType
    partial_activity_along_y_negative_displacement: float
    partial_activity_along_y_negative_force: float
    partial_activity_along_y_negative_slippage: float
    partial_activity_along_y_positive_type: NodalSupport.PartialActivityAlongYPositiveType
    partial_activity_along_y_positive_displacement: float
    partial_activity_along_y_positive_force: float
    partial_activity_along_y_positive_slippage: float
    partial_activity_along_z_negative_type: NodalSupport.PartialActivityAlongZNegativeType
    partial_activity_along_z_negative_displacement: float
    partial_activity_along_z_negative_force: float
    partial_activity_along_z_negative_slippage: float
    partial_activity_along_z_positive_type: NodalSupport.PartialActivityAlongZPositiveType
    partial_activity_along_z_positive_displacement: float
    partial_activity_along_z_positive_force: float
    partial_activity_along_z_positive_slippage: float
    partial_activity_around_x_negative_type: NodalSupport.PartialActivityAroundXNegativeType
    partial_activity_around_x_negative_moment: float
    partial_activity_around_x_negative_rotation: float
    partial_activity_around_x_negative_slippage: float
    partial_activity_around_x_positive_type: NodalSupport.PartialActivityAroundXPositiveType
    partial_activity_around_x_positive_moment: float
    partial_activity_around_x_positive_rotation: float
    partial_activity_around_x_positive_slippage: float
    partial_activity_around_y_negative_type: NodalSupport.PartialActivityAroundYNegativeType
    partial_activity_around_y_negative_moment: float
    partial_activity_around_y_negative_rotation: float
    partial_activity_around_y_negative_slippage: float
    partial_activity_around_y_positive_type: NodalSupport.PartialActivityAroundYPositiveType
    partial_activity_around_y_positive_moment: float
    partial_activity_around_y_positive_rotation: float
    partial_activity_around_y_positive_slippage: float
    partial_activity_around_z_negative_type: NodalSupport.PartialActivityAroundZNegativeType
    partial_activity_around_z_negative_moment: float
    partial_activity_around_z_negative_rotation: float
    partial_activity_around_z_negative_slippage: float
    partial_activity_around_z_positive_type: NodalSupport.PartialActivityAroundZPositiveType
    partial_activity_around_z_positive_moment: float
    partial_activity_around_z_positive_rotation: float
    partial_activity_around_z_positive_slippage: float
    rotated_about_angle_1: float
    rotated_about_angle_2: float
    rotated_about_angle_3: float
    rotated_about_angle_x: float
    rotated_about_angle_y: float
    rotated_about_angle_z: float
    stiffness_diagram_around_x_depends_on: NodalSupport.StiffnessDiagramAroundXDependsOn
    stiffness_diagram_around_x_end: NodalSupport.StiffnessDiagramAroundXEnd
    stiffness_diagram_around_x_is_sorted: bool
    stiffness_diagram_around_x_start: NodalSupport.StiffnessDiagramAroundXStart
    stiffness_diagram_around_x_symmetric: bool
    stiffness_diagram_around_x_table: NodalSupport.StiffnessDiagramAroundXTable
    stiffness_diagram_around_y_depends_on: NodalSupport.StiffnessDiagramAroundYDependsOn
    stiffness_diagram_around_y_end: NodalSupport.StiffnessDiagramAroundYEnd
    stiffness_diagram_around_y_is_sorted: bool
    stiffness_diagram_around_y_start: NodalSupport.StiffnessDiagramAroundYStart
    stiffness_diagram_around_y_symmetric: bool
    stiffness_diagram_around_y_table: NodalSupport.StiffnessDiagramAroundYTable
    stiffness_diagram_around_z_depends_on: NodalSupport.StiffnessDiagramAroundZDependsOn
    stiffness_diagram_around_z_end: NodalSupport.StiffnessDiagramAroundZEnd
    stiffness_diagram_around_z_is_sorted: bool
    stiffness_diagram_around_z_start: NodalSupport.StiffnessDiagramAroundZStart
    stiffness_diagram_around_z_symmetric: bool
    stiffness_diagram_around_z_table: NodalSupport.StiffnessDiagramAroundZTable
    support_dimension_diameter_x: float
    support_dimension_diameter_y: float
    support_dimension_diameter_z: float
    support_dimension_height_x: float
    support_dimension_height_y: float
    support_dimension_height_z: float
    support_dimension_type_on_x: NodalSupport.SupportDimensionTypeOnX
    support_dimension_type_on_y: NodalSupport.SupportDimensionTypeOnY
    support_dimension_type_on_z: NodalSupport.SupportDimensionTypeOnZ
    support_dimension_width_x: float
    support_dimension_width_y: float
    support_dimension_width_z: float
    support_dimensions_enabled: bool
    diagram_along_x_ac_yield_minus: float
    diagram_along_y_ac_yield_minus: float
    diagram_along_z_ac_yield_minus: float
    diagram_around_x_ac_yield_minus: float
    diagram_around_y_ac_yield_minus: float
    diagram_around_z_ac_yield_minus: float
    diagram_along_x_ac_yield_plus: float
    diagram_along_y_ac_yield_plus: float
    diagram_along_z_ac_yield_plus: float
    diagram_around_x_ac_yield_plus: float
    diagram_around_y_ac_yield_plus: float
    diagram_around_z_ac_yield_plus: float
    diagram_along_x_acceptance_criteria_active: bool
    diagram_along_y_acceptance_criteria_active: bool
    diagram_along_z_acceptance_criteria_active: bool
    diagram_around_x_acceptance_criteria_active: bool
    diagram_around_y_acceptance_criteria_active: bool
    diagram_around_z_acceptance_criteria_active: bool
    diagram_along_x_minus_color_one: _common_pb2.Color
    diagram_along_y_minus_color_one: _common_pb2.Color
    diagram_along_z_minus_color_one: _common_pb2.Color
    diagram_around_x_minus_color_one: _common_pb2.Color
    diagram_around_y_minus_color_one: _common_pb2.Color
    diagram_around_z_minus_color_one: _common_pb2.Color
    diagram_along_x_minus_color_two: _common_pb2.Color
    diagram_along_y_minus_color_two: _common_pb2.Color
    diagram_along_z_minus_color_two: _common_pb2.Color
    diagram_around_x_minus_color_two: _common_pb2.Color
    diagram_around_y_minus_color_two: _common_pb2.Color
    diagram_around_z_minus_color_two: _common_pb2.Color
    diagram_along_x_plus_color_one: _common_pb2.Color
    diagram_along_y_plus_color_one: _common_pb2.Color
    diagram_along_z_plus_color_one: _common_pb2.Color
    diagram_around_x_plus_color_one: _common_pb2.Color
    diagram_around_y_plus_color_one: _common_pb2.Color
    diagram_around_z_plus_color_one: _common_pb2.Color
    diagram_along_x_plus_color_two: _common_pb2.Color
    diagram_along_y_plus_color_two: _common_pb2.Color
    diagram_along_z_plus_color_two: _common_pb2.Color
    diagram_around_x_plus_color_two: _common_pb2.Color
    diagram_around_y_plus_color_two: _common_pb2.Color
    diagram_around_z_plus_color_two: _common_pb2.Color
    diagram_along_x_color_table: NodalSupport.DiagramAlongXColorTable
    diagram_along_y_color_table: NodalSupport.DiagramAlongYColorTable
    diagram_along_z_color_table: NodalSupport.DiagramAlongZColorTable
    diagram_around_x_color_table: NodalSupport.DiagramAroundXColorTable
    diagram_around_y_color_table: NodalSupport.DiagramAroundYColorTable
    diagram_around_z_color_table: NodalSupport.DiagramAroundZColorTable
    generating_object_info: str
    is_generated: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., fictitious_column_enabled: bool = ..., specific_direction_enabled: bool = ..., specific_direction_type: _Optional[_Union[NodalSupport.SpecificDirectionType, str]] = ..., nodes: _Optional[_Iterable[int]] = ..., spring: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., spring_x: _Optional[float] = ..., spring_y: _Optional[float] = ..., spring_z: _Optional[float] = ..., rotational_restraint: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., rotational_restraint_x: _Optional[float] = ..., rotational_restraint_y: _Optional[float] = ..., rotational_restraint_z: _Optional[float] = ..., spring_x_nonlinearity: _Optional[_Union[NodalSupport.SpringXNonlinearity, str]] = ..., spring_y_nonlinearity: _Optional[_Union[NodalSupport.SpringYNonlinearity, str]] = ..., spring_z_nonlinearity: _Optional[_Union[NodalSupport.SpringZNonlinearity, str]] = ..., rotational_restraint_x_nonlinearity: _Optional[_Union[NodalSupport.RotationalRestraintXNonlinearity, str]] = ..., rotational_restraint_y_nonlinearity: _Optional[_Union[NodalSupport.RotationalRestraintYNonlinearity, str]] = ..., rotational_restraint_z_nonlinearity: _Optional[_Union[NodalSupport.RotationalRestraintZNonlinearity, str]] = ..., axes_sequence: _Optional[_Union[NodalSupport.AxesSequence, str]] = ..., column_base_semi_rigid: _Optional[float] = ..., column_base_support_type: _Optional[_Union[NodalSupport.ColumnBaseSupportType, str]] = ..., column_head_support_type: _Optional[_Union[NodalSupport.ColumnHeadSupportType, str]] = ..., column_head_type: _Optional[_Union[NodalSupport.ColumnHeadType, str]] = ..., column_height: _Optional[float] = ..., column_section_same_as_head: bool = ..., column_material: _Optional[int] = ..., column_rotation: _Optional[float] = ..., column_rotational_restraint_x: _Optional[float] = ..., column_rotational_restraint_y: _Optional[float] = ..., column_section: _Optional[int] = ..., column_shear_stiffness: bool = ..., column_spring_x: _Optional[float] = ..., column_spring_y: _Optional[float] = ..., column_spring_z: _Optional[float] = ..., column_support_type: _Optional[_Union[NodalSupport.ColumnSupportType, str]] = ..., column_width_x: _Optional[float] = ..., column_width_y: _Optional[float] = ..., comment: _Optional[str] = ..., coordinate_system: _Optional[int] = ..., diagram_along_x_symmetric: bool = ..., diagram_along_x_start: _Optional[_Union[NodalSupport.DiagramAlongXStart, str]] = ..., diagram_along_x_end: _Optional[_Union[NodalSupport.DiagramAlongXEnd, str]] = ..., diagram_along_x_table: _Optional[_Union[NodalSupport.DiagramAlongXTable, _Mapping]] = ..., diagram_along_x_is_sorted: bool = ..., diagram_along_y_symmetric: bool = ..., diagram_along_y_start: _Optional[_Union[NodalSupport.DiagramAlongYStart, str]] = ..., diagram_along_y_end: _Optional[_Union[NodalSupport.DiagramAlongYEnd, str]] = ..., diagram_along_y_table: _Optional[_Union[NodalSupport.DiagramAlongYTable, _Mapping]] = ..., diagram_along_y_is_sorted: bool = ..., diagram_along_z_symmetric: bool = ..., diagram_along_z_start: _Optional[_Union[NodalSupport.DiagramAlongZStart, str]] = ..., diagram_along_z_end: _Optional[_Union[NodalSupport.DiagramAlongZEnd, str]] = ..., diagram_along_z_table: _Optional[_Union[NodalSupport.DiagramAlongZTable, _Mapping]] = ..., diagram_along_z_is_sorted: bool = ..., diagram_around_x_symmetric: bool = ..., diagram_around_x_start: _Optional[_Union[NodalSupport.DiagramAroundXStart, str]] = ..., diagram_around_x_end: _Optional[_Union[NodalSupport.DiagramAroundXEnd, str]] = ..., diagram_around_x_table: _Optional[_Union[NodalSupport.DiagramAroundXTable, _Mapping]] = ..., diagram_around_x_is_sorted: bool = ..., diagram_around_y_symmetric: bool = ..., diagram_around_y_start: _Optional[_Union[NodalSupport.DiagramAroundYStart, str]] = ..., diagram_around_y_end: _Optional[_Union[NodalSupport.DiagramAroundYEnd, str]] = ..., diagram_around_y_table: _Optional[_Union[NodalSupport.DiagramAroundYTable, _Mapping]] = ..., diagram_around_y_is_sorted: bool = ..., diagram_around_z_symmetric: bool = ..., diagram_around_z_start: _Optional[_Union[NodalSupport.DiagramAroundZStart, str]] = ..., diagram_around_z_end: _Optional[_Union[NodalSupport.DiagramAroundZEnd, str]] = ..., diagram_around_z_table: _Optional[_Union[NodalSupport.DiagramAroundZTable, _Mapping]] = ..., diagram_around_z_is_sorted: bool = ..., directed_to_node_direction_node: _Optional[int] = ..., directed_to_node_first_axis: _Optional[_Union[NodalSupport.DirectedToNodeFirstAxis, str]] = ..., directed_to_node_plane_node: _Optional[int] = ..., directed_to_node_second_axis: _Optional[_Union[NodalSupport.DirectedToNodeSecondAxis, str]] = ..., friction_coefficient_x: _Optional[float] = ..., friction_coefficient_xy: _Optional[float] = ..., friction_coefficient_xz: _Optional[float] = ..., friction_coefficient_y: _Optional[float] = ..., friction_coefficient_yx: _Optional[float] = ..., friction_coefficient_yz: _Optional[float] = ..., friction_coefficient_z: _Optional[float] = ..., friction_coefficient_zx: _Optional[float] = ..., friction_coefficient_zy: _Optional[float] = ..., parallel_to_line: _Optional[int] = ..., parallel_to_member: _Optional[int] = ..., parallel_to_two_nodes_first_axis: _Optional[_Union[NodalSupport.ParallelToTwoNodesFirstAxis, str]] = ..., parallel_to_two_nodes_first_node: _Optional[int] = ..., parallel_to_two_nodes_plane_node: _Optional[int] = ..., parallel_to_two_nodes_second_axis: _Optional[_Union[NodalSupport.ParallelToTwoNodesSecondAxis, str]] = ..., parallel_to_two_nodes_second_node: _Optional[int] = ..., partial_activity_along_x_negative_type: _Optional[_Union[NodalSupport.PartialActivityAlongXNegativeType, str]] = ..., partial_activity_along_x_negative_displacement: _Optional[float] = ..., partial_activity_along_x_negative_force: _Optional[float] = ..., partial_activity_along_x_negative_slippage: _Optional[float] = ..., partial_activity_along_x_positive_type: _Optional[_Union[NodalSupport.PartialActivityAlongXPositiveType, str]] = ..., partial_activity_along_x_positive_displacement: _Optional[float] = ..., partial_activity_along_x_positive_force: _Optional[float] = ..., partial_activity_along_x_positive_slippage: _Optional[float] = ..., partial_activity_along_y_negative_type: _Optional[_Union[NodalSupport.PartialActivityAlongYNegativeType, str]] = ..., partial_activity_along_y_negative_displacement: _Optional[float] = ..., partial_activity_along_y_negative_force: _Optional[float] = ..., partial_activity_along_y_negative_slippage: _Optional[float] = ..., partial_activity_along_y_positive_type: _Optional[_Union[NodalSupport.PartialActivityAlongYPositiveType, str]] = ..., partial_activity_along_y_positive_displacement: _Optional[float] = ..., partial_activity_along_y_positive_force: _Optional[float] = ..., partial_activity_along_y_positive_slippage: _Optional[float] = ..., partial_activity_along_z_negative_type: _Optional[_Union[NodalSupport.PartialActivityAlongZNegativeType, str]] = ..., partial_activity_along_z_negative_displacement: _Optional[float] = ..., partial_activity_along_z_negative_force: _Optional[float] = ..., partial_activity_along_z_negative_slippage: _Optional[float] = ..., partial_activity_along_z_positive_type: _Optional[_Union[NodalSupport.PartialActivityAlongZPositiveType, str]] = ..., partial_activity_along_z_positive_displacement: _Optional[float] = ..., partial_activity_along_z_positive_force: _Optional[float] = ..., partial_activity_along_z_positive_slippage: _Optional[float] = ..., partial_activity_around_x_negative_type: _Optional[_Union[NodalSupport.PartialActivityAroundXNegativeType, str]] = ..., partial_activity_around_x_negative_moment: _Optional[float] = ..., partial_activity_around_x_negative_rotation: _Optional[float] = ..., partial_activity_around_x_negative_slippage: _Optional[float] = ..., partial_activity_around_x_positive_type: _Optional[_Union[NodalSupport.PartialActivityAroundXPositiveType, str]] = ..., partial_activity_around_x_positive_moment: _Optional[float] = ..., partial_activity_around_x_positive_rotation: _Optional[float] = ..., partial_activity_around_x_positive_slippage: _Optional[float] = ..., partial_activity_around_y_negative_type: _Optional[_Union[NodalSupport.PartialActivityAroundYNegativeType, str]] = ..., partial_activity_around_y_negative_moment: _Optional[float] = ..., partial_activity_around_y_negative_rotation: _Optional[float] = ..., partial_activity_around_y_negative_slippage: _Optional[float] = ..., partial_activity_around_y_positive_type: _Optional[_Union[NodalSupport.PartialActivityAroundYPositiveType, str]] = ..., partial_activity_around_y_positive_moment: _Optional[float] = ..., partial_activity_around_y_positive_rotation: _Optional[float] = ..., partial_activity_around_y_positive_slippage: _Optional[float] = ..., partial_activity_around_z_negative_type: _Optional[_Union[NodalSupport.PartialActivityAroundZNegativeType, str]] = ..., partial_activity_around_z_negative_moment: _Optional[float] = ..., partial_activity_around_z_negative_rotation: _Optional[float] = ..., partial_activity_around_z_negative_slippage: _Optional[float] = ..., partial_activity_around_z_positive_type: _Optional[_Union[NodalSupport.PartialActivityAroundZPositiveType, str]] = ..., partial_activity_around_z_positive_moment: _Optional[float] = ..., partial_activity_around_z_positive_rotation: _Optional[float] = ..., partial_activity_around_z_positive_slippage: _Optional[float] = ..., rotated_about_angle_1: _Optional[float] = ..., rotated_about_angle_2: _Optional[float] = ..., rotated_about_angle_3: _Optional[float] = ..., rotated_about_angle_x: _Optional[float] = ..., rotated_about_angle_y: _Optional[float] = ..., rotated_about_angle_z: _Optional[float] = ..., stiffness_diagram_around_x_depends_on: _Optional[_Union[NodalSupport.StiffnessDiagramAroundXDependsOn, str]] = ..., stiffness_diagram_around_x_end: _Optional[_Union[NodalSupport.StiffnessDiagramAroundXEnd, str]] = ..., stiffness_diagram_around_x_is_sorted: bool = ..., stiffness_diagram_around_x_start: _Optional[_Union[NodalSupport.StiffnessDiagramAroundXStart, str]] = ..., stiffness_diagram_around_x_symmetric: bool = ..., stiffness_diagram_around_x_table: _Optional[_Union[NodalSupport.StiffnessDiagramAroundXTable, _Mapping]] = ..., stiffness_diagram_around_y_depends_on: _Optional[_Union[NodalSupport.StiffnessDiagramAroundYDependsOn, str]] = ..., stiffness_diagram_around_y_end: _Optional[_Union[NodalSupport.StiffnessDiagramAroundYEnd, str]] = ..., stiffness_diagram_around_y_is_sorted: bool = ..., stiffness_diagram_around_y_start: _Optional[_Union[NodalSupport.StiffnessDiagramAroundYStart, str]] = ..., stiffness_diagram_around_y_symmetric: bool = ..., stiffness_diagram_around_y_table: _Optional[_Union[NodalSupport.StiffnessDiagramAroundYTable, _Mapping]] = ..., stiffness_diagram_around_z_depends_on: _Optional[_Union[NodalSupport.StiffnessDiagramAroundZDependsOn, str]] = ..., stiffness_diagram_around_z_end: _Optional[_Union[NodalSupport.StiffnessDiagramAroundZEnd, str]] = ..., stiffness_diagram_around_z_is_sorted: bool = ..., stiffness_diagram_around_z_start: _Optional[_Union[NodalSupport.StiffnessDiagramAroundZStart, str]] = ..., stiffness_diagram_around_z_symmetric: bool = ..., stiffness_diagram_around_z_table: _Optional[_Union[NodalSupport.StiffnessDiagramAroundZTable, _Mapping]] = ..., support_dimension_diameter_x: _Optional[float] = ..., support_dimension_diameter_y: _Optional[float] = ..., support_dimension_diameter_z: _Optional[float] = ..., support_dimension_height_x: _Optional[float] = ..., support_dimension_height_y: _Optional[float] = ..., support_dimension_height_z: _Optional[float] = ..., support_dimension_type_on_x: _Optional[_Union[NodalSupport.SupportDimensionTypeOnX, str]] = ..., support_dimension_type_on_y: _Optional[_Union[NodalSupport.SupportDimensionTypeOnY, str]] = ..., support_dimension_type_on_z: _Optional[_Union[NodalSupport.SupportDimensionTypeOnZ, str]] = ..., support_dimension_width_x: _Optional[float] = ..., support_dimension_width_y: _Optional[float] = ..., support_dimension_width_z: _Optional[float] = ..., support_dimensions_enabled: bool = ..., diagram_along_x_ac_yield_minus: _Optional[float] = ..., diagram_along_y_ac_yield_minus: _Optional[float] = ..., diagram_along_z_ac_yield_minus: _Optional[float] = ..., diagram_around_x_ac_yield_minus: _Optional[float] = ..., diagram_around_y_ac_yield_minus: _Optional[float] = ..., diagram_around_z_ac_yield_minus: _Optional[float] = ..., diagram_along_x_ac_yield_plus: _Optional[float] = ..., diagram_along_y_ac_yield_plus: _Optional[float] = ..., diagram_along_z_ac_yield_plus: _Optional[float] = ..., diagram_around_x_ac_yield_plus: _Optional[float] = ..., diagram_around_y_ac_yield_plus: _Optional[float] = ..., diagram_around_z_ac_yield_plus: _Optional[float] = ..., diagram_along_x_acceptance_criteria_active: bool = ..., diagram_along_y_acceptance_criteria_active: bool = ..., diagram_along_z_acceptance_criteria_active: bool = ..., diagram_around_x_acceptance_criteria_active: bool = ..., diagram_around_y_acceptance_criteria_active: bool = ..., diagram_around_z_acceptance_criteria_active: bool = ..., diagram_along_x_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_y_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_z_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_y_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_z_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_y_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_z_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_y_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_z_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_color_table: _Optional[_Union[NodalSupport.DiagramAlongXColorTable, _Mapping]] = ..., diagram_along_y_color_table: _Optional[_Union[NodalSupport.DiagramAlongYColorTable, _Mapping]] = ..., diagram_along_z_color_table: _Optional[_Union[NodalSupport.DiagramAlongZColorTable, _Mapping]] = ..., diagram_around_x_color_table: _Optional[_Union[NodalSupport.DiagramAroundXColorTable, _Mapping]] = ..., diagram_around_y_color_table: _Optional[_Union[NodalSupport.DiagramAroundYColorTable, _Mapping]] = ..., diagram_around_z_color_table: _Optional[_Union[NodalSupport.DiagramAroundZColorTable, _Mapping]] = ..., generating_object_info: _Optional[str] = ..., is_generated: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
