from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LineSupport(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "lines", "coordinate_system", "x_axis_rotation", "spring", "rotational_restraint", "spring_x", "spring_y", "spring_z", "rotational_restraint_x", "rotational_restraint_y", "rotational_restraint_z", "spring_x_nonlinearity", "spring_y_nonlinearity", "spring_z_nonlinearity", "rotational_restraint_x_nonlinearity", "rotational_restraint_y_nonlinearity", "rotational_restraint_z_nonlinearity", "comment", "diagram_along_x_end", "diagram_along_x_is_sorted", "diagram_along_x_symmetric", "diagram_along_x_start", "diagram_along_x_table", "diagram_along_y_end", "diagram_along_y_is_sorted", "diagram_along_y_symmetric", "diagram_along_y_start", "diagram_along_y_table", "diagram_along_z_end", "diagram_along_z_is_sorted", "diagram_along_z_symmetric", "diagram_along_z_start", "diagram_along_z_table", "diagram_around_x_end", "diagram_around_x_is_sorted", "diagram_around_x_symmetric", "diagram_around_x_start", "diagram_around_x_table", "diagram_around_y_end", "diagram_around_y_is_sorted", "diagram_around_y_symmetric", "diagram_around_y_start", "diagram_around_y_table", "diagram_around_z_end", "diagram_around_z_is_sorted", "diagram_around_z_symmetric", "diagram_around_z_start", "diagram_around_z_table", "diagram_along_x_ac_yield_minus", "diagram_along_y_ac_yield_minus", "diagram_along_z_ac_yield_minus", "diagram_around_x_ac_yield_minus", "diagram_around_y_ac_yield_minus", "diagram_around_z_ac_yield_minus", "diagram_along_x_ac_yield_plus", "diagram_along_y_ac_yield_plus", "diagram_along_z_ac_yield_plus", "diagram_around_x_ac_yield_plus", "diagram_around_y_ac_yield_plus", "diagram_around_z_ac_yield_plus", "diagram_along_x_acceptance_criteria_active", "diagram_along_y_acceptance_criteria_active", "diagram_along_z_acceptance_criteria_active", "diagram_around_x_acceptance_criteria_active", "diagram_around_y_acceptance_criteria_active", "diagram_around_z_acceptance_criteria_active", "diagram_along_x_minus_color_one", "diagram_along_y_minus_color_one", "diagram_along_z_minus_color_one", "diagram_around_x_minus_color_one", "diagram_around_y_minus_color_one", "diagram_around_z_minus_color_one", "diagram_along_x_minus_color_two", "diagram_along_y_minus_color_two", "diagram_along_z_minus_color_two", "diagram_around_x_minus_color_two", "diagram_around_y_minus_color_two", "diagram_around_z_minus_color_two", "diagram_along_x_plus_color_one", "diagram_along_y_plus_color_one", "diagram_along_z_plus_color_one", "diagram_around_x_plus_color_one", "diagram_around_y_plus_color_one", "diagram_around_z_plus_color_one", "diagram_along_x_plus_color_two", "diagram_along_y_plus_color_two", "diagram_along_z_plus_color_two", "diagram_around_x_plus_color_two", "diagram_around_y_plus_color_two", "diagram_around_z_plus_color_two", "diagram_along_x_color_table", "diagram_along_y_color_table", "diagram_along_z_color_table", "diagram_around_x_color_table", "diagram_around_y_color_table", "diagram_around_z_color_table", "friction_coefficient_x", "friction_coefficient_y", "friction_coefficient_z", "friction_direction_independent_x", "friction_direction_independent_y", "friction_direction_independent_z", "partial_activity_along_x_negative_displacement", "partial_activity_along_x_negative_force", "partial_activity_along_x_negative_slippage", "partial_activity_along_x_negative_type", "partial_activity_along_x_positive_displacement", "partial_activity_along_x_positive_force", "partial_activity_along_x_positive_slippage", "partial_activity_along_x_positive_type", "partial_activity_along_y_negative_displacement", "partial_activity_along_y_negative_force", "partial_activity_along_y_negative_slippage", "partial_activity_along_y_negative_type", "partial_activity_along_y_positive_displacement", "partial_activity_along_y_positive_force", "partial_activity_along_y_positive_slippage", "partial_activity_along_y_positive_type", "partial_activity_along_z_negative_displacement", "partial_activity_along_z_negative_force", "partial_activity_along_z_negative_slippage", "partial_activity_along_z_negative_type", "partial_activity_along_z_positive_displacement", "partial_activity_along_z_positive_force", "partial_activity_along_z_positive_slippage", "partial_activity_along_z_positive_type", "partial_activity_around_x_negative_moment", "partial_activity_around_x_negative_rotation", "partial_activity_around_x_negative_slippage", "partial_activity_around_x_negative_type", "partial_activity_around_x_positive_moment", "partial_activity_around_x_positive_rotation", "partial_activity_around_x_positive_slippage", "partial_activity_around_x_positive_type", "partial_activity_around_y_negative_moment", "partial_activity_around_y_negative_rotation", "partial_activity_around_y_negative_slippage", "partial_activity_around_y_negative_type", "partial_activity_around_y_positive_moment", "partial_activity_around_y_positive_rotation", "partial_activity_around_y_positive_slippage", "partial_activity_around_y_positive_type", "partial_activity_around_z_negative_moment", "partial_activity_around_z_negative_rotation", "partial_activity_around_z_negative_slippage", "partial_activity_around_z_negative_type", "partial_activity_around_z_positive_moment", "partial_activity_around_z_positive_rotation", "partial_activity_around_z_positive_slippage", "partial_activity_around_z_positive_type", "is_generated", "generating_object_info", "fictitious_wall_enabled", "fictitious_wall_width", "fictitious_wall_height", "fictitious_wall_head_support_type", "fictitious_wall_base_support_type", "fictitious_wall_base_elastic", "fictitious_wall_shear_stiffness", "fictitious_wall_material", "fictitious_wall_spring_x", "fictitious_wall_spring_y", "fictitious_wall_spring_z", "fictitious_wall_rotational_restraint_about_line_axis", "id_for_export_import", "metadata_for_export_import")
    class CoordinateSystem(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COORDINATE_SYSTEM_LOCAL: _ClassVar[LineSupport.CoordinateSystem]
        COORDINATE_SYSTEM_GLOBAL: _ClassVar[LineSupport.CoordinateSystem]
    COORDINATE_SYSTEM_LOCAL: LineSupport.CoordinateSystem
    COORDINATE_SYSTEM_GLOBAL: LineSupport.CoordinateSystem
    class SpringXNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SPRING_X_NONLINEARITY_NONE: _ClassVar[LineSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_DIAGRAM: _ClassVar[LineSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[LineSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[LineSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[LineSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[LineSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[LineSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[LineSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[LineSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[LineSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[LineSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[LineSupport.SpringXNonlinearity]
        SPRING_X_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[LineSupport.SpringXNonlinearity]
    SPRING_X_NONLINEARITY_NONE: LineSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_DIAGRAM: LineSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: LineSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: LineSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FAILURE_IF_NEGATIVE: LineSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FAILURE_IF_POSITIVE: LineSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: LineSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FRICTION_DIRECTION_1: LineSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FRICTION_DIRECTION_1_2: LineSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: LineSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_FRICTION_DIRECTION_2: LineSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_PARTIAL_ACTIVITY: LineSupport.SpringXNonlinearity
    SPRING_X_NONLINEARITY_STIFFNESS_DIAGRAM: LineSupport.SpringXNonlinearity
    class SpringYNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SPRING_Y_NONLINEARITY_NONE: _ClassVar[LineSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_DIAGRAM: _ClassVar[LineSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[LineSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[LineSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[LineSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[LineSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[LineSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[LineSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[LineSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[LineSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[LineSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[LineSupport.SpringYNonlinearity]
        SPRING_Y_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[LineSupport.SpringYNonlinearity]
    SPRING_Y_NONLINEARITY_NONE: LineSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_DIAGRAM: LineSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: LineSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: LineSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FAILURE_IF_NEGATIVE: LineSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FAILURE_IF_POSITIVE: LineSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FORCE_MOMENT_DIAGRAM: LineSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_1: LineSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_1_2: LineSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: LineSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_FRICTION_DIRECTION_2: LineSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_PARTIAL_ACTIVITY: LineSupport.SpringYNonlinearity
    SPRING_Y_NONLINEARITY_STIFFNESS_DIAGRAM: LineSupport.SpringYNonlinearity
    class SpringZNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SPRING_Z_NONLINEARITY_NONE: _ClassVar[LineSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_DIAGRAM: _ClassVar[LineSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[LineSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[LineSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[LineSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[LineSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[LineSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[LineSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[LineSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[LineSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[LineSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[LineSupport.SpringZNonlinearity]
        SPRING_Z_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[LineSupport.SpringZNonlinearity]
    SPRING_Z_NONLINEARITY_NONE: LineSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_DIAGRAM: LineSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: LineSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: LineSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FAILURE_IF_NEGATIVE: LineSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FAILURE_IF_POSITIVE: LineSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FORCE_MOMENT_DIAGRAM: LineSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_1: LineSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_1_2: LineSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: LineSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_FRICTION_DIRECTION_2: LineSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_PARTIAL_ACTIVITY: LineSupport.SpringZNonlinearity
    SPRING_Z_NONLINEARITY_STIFFNESS_DIAGRAM: LineSupport.SpringZNonlinearity
    class RotationalRestraintXNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_NONE: _ClassVar[LineSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_DIAGRAM: _ClassVar[LineSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[LineSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[LineSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[LineSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[LineSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[LineSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[LineSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[LineSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[LineSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[LineSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[LineSupport.RotationalRestraintXNonlinearity]
        ROTATIONAL_RESTRAINT_X_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[LineSupport.RotationalRestraintXNonlinearity]
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_NONE: LineSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_DIAGRAM: LineSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: LineSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: LineSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_IF_NEGATIVE: LineSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FAILURE_IF_POSITIVE: LineSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: LineSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_1: LineSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_1_2: LineSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: LineSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FRICTION_DIRECTION_2: LineSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_PARTIAL_ACTIVITY: LineSupport.RotationalRestraintXNonlinearity
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_STIFFNESS_DIAGRAM: LineSupport.RotationalRestraintXNonlinearity
    class RotationalRestraintYNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_NONE: _ClassVar[LineSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_DIAGRAM: _ClassVar[LineSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[LineSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[LineSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[LineSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[LineSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[LineSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[LineSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[LineSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[LineSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[LineSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[LineSupport.RotationalRestraintYNonlinearity]
        ROTATIONAL_RESTRAINT_Y_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[LineSupport.RotationalRestraintYNonlinearity]
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_NONE: LineSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_DIAGRAM: LineSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: LineSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: LineSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_IF_NEGATIVE: LineSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FAILURE_IF_POSITIVE: LineSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FORCE_MOMENT_DIAGRAM: LineSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_1: LineSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_1_2: LineSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: LineSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FRICTION_DIRECTION_2: LineSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_PARTIAL_ACTIVITY: LineSupport.RotationalRestraintYNonlinearity
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_STIFFNESS_DIAGRAM: LineSupport.RotationalRestraintYNonlinearity
    class RotationalRestraintZNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_NONE: _ClassVar[LineSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_DIAGRAM: _ClassVar[LineSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[LineSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[LineSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[LineSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[LineSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[LineSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[LineSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[LineSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[LineSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[LineSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[LineSupport.RotationalRestraintZNonlinearity]
        ROTATIONAL_RESTRAINT_Z_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[LineSupport.RotationalRestraintZNonlinearity]
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_NONE: LineSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_DIAGRAM: LineSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: LineSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: LineSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_IF_NEGATIVE: LineSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FAILURE_IF_POSITIVE: LineSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FORCE_MOMENT_DIAGRAM: LineSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_1: LineSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_1_2: LineSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: LineSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FRICTION_DIRECTION_2: LineSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_PARTIAL_ACTIVITY: LineSupport.RotationalRestraintZNonlinearity
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_STIFFNESS_DIAGRAM: LineSupport.RotationalRestraintZNonlinearity
    class DiagramAlongXEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_X_END_FAILURE: _ClassVar[LineSupport.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_CONTINUOUS: _ClassVar[LineSupport.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_STOP: _ClassVar[LineSupport.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_YIELDING: _ClassVar[LineSupport.DiagramAlongXEnd]
    DIAGRAM_ALONG_X_END_FAILURE: LineSupport.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_CONTINUOUS: LineSupport.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_STOP: LineSupport.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_YIELDING: LineSupport.DiagramAlongXEnd
    class DiagramAlongXStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_X_START_FAILURE: _ClassVar[LineSupport.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_CONTINUOUS: _ClassVar[LineSupport.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_STOP: _ClassVar[LineSupport.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_YIELDING: _ClassVar[LineSupport.DiagramAlongXStart]
    DIAGRAM_ALONG_X_START_FAILURE: LineSupport.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_CONTINUOUS: LineSupport.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_STOP: LineSupport.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_YIELDING: LineSupport.DiagramAlongXStart
    class DiagramAlongYEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Y_END_FAILURE: _ClassVar[LineSupport.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_CONTINUOUS: _ClassVar[LineSupport.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_STOP: _ClassVar[LineSupport.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_YIELDING: _ClassVar[LineSupport.DiagramAlongYEnd]
    DIAGRAM_ALONG_Y_END_FAILURE: LineSupport.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_CONTINUOUS: LineSupport.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_STOP: LineSupport.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_YIELDING: LineSupport.DiagramAlongYEnd
    class DiagramAlongYStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Y_START_FAILURE: _ClassVar[LineSupport.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_CONTINUOUS: _ClassVar[LineSupport.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_STOP: _ClassVar[LineSupport.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_YIELDING: _ClassVar[LineSupport.DiagramAlongYStart]
    DIAGRAM_ALONG_Y_START_FAILURE: LineSupport.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_CONTINUOUS: LineSupport.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_STOP: LineSupport.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_YIELDING: LineSupport.DiagramAlongYStart
    class DiagramAlongZEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Z_END_FAILURE: _ClassVar[LineSupport.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_CONTINUOUS: _ClassVar[LineSupport.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_STOP: _ClassVar[LineSupport.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_YIELDING: _ClassVar[LineSupport.DiagramAlongZEnd]
    DIAGRAM_ALONG_Z_END_FAILURE: LineSupport.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_CONTINUOUS: LineSupport.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_STOP: LineSupport.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_YIELDING: LineSupport.DiagramAlongZEnd
    class DiagramAlongZStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Z_START_FAILURE: _ClassVar[LineSupport.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_CONTINUOUS: _ClassVar[LineSupport.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_STOP: _ClassVar[LineSupport.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_YIELDING: _ClassVar[LineSupport.DiagramAlongZStart]
    DIAGRAM_ALONG_Z_START_FAILURE: LineSupport.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_CONTINUOUS: LineSupport.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_STOP: LineSupport.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_YIELDING: LineSupport.DiagramAlongZStart
    class DiagramAroundXEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_X_END_FAILURE: _ClassVar[LineSupport.DiagramAroundXEnd]
        DIAGRAM_AROUND_X_END_CONTINUOUS: _ClassVar[LineSupport.DiagramAroundXEnd]
        DIAGRAM_AROUND_X_END_STOP: _ClassVar[LineSupport.DiagramAroundXEnd]
        DIAGRAM_AROUND_X_END_YIELDING: _ClassVar[LineSupport.DiagramAroundXEnd]
    DIAGRAM_AROUND_X_END_FAILURE: LineSupport.DiagramAroundXEnd
    DIAGRAM_AROUND_X_END_CONTINUOUS: LineSupport.DiagramAroundXEnd
    DIAGRAM_AROUND_X_END_STOP: LineSupport.DiagramAroundXEnd
    DIAGRAM_AROUND_X_END_YIELDING: LineSupport.DiagramAroundXEnd
    class DiagramAroundXStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_X_START_FAILURE: _ClassVar[LineSupport.DiagramAroundXStart]
        DIAGRAM_AROUND_X_START_CONTINUOUS: _ClassVar[LineSupport.DiagramAroundXStart]
        DIAGRAM_AROUND_X_START_STOP: _ClassVar[LineSupport.DiagramAroundXStart]
        DIAGRAM_AROUND_X_START_YIELDING: _ClassVar[LineSupport.DiagramAroundXStart]
    DIAGRAM_AROUND_X_START_FAILURE: LineSupport.DiagramAroundXStart
    DIAGRAM_AROUND_X_START_CONTINUOUS: LineSupport.DiagramAroundXStart
    DIAGRAM_AROUND_X_START_STOP: LineSupport.DiagramAroundXStart
    DIAGRAM_AROUND_X_START_YIELDING: LineSupport.DiagramAroundXStart
    class DiagramAroundYEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_Y_END_FAILURE: _ClassVar[LineSupport.DiagramAroundYEnd]
        DIAGRAM_AROUND_Y_END_CONTINUOUS: _ClassVar[LineSupport.DiagramAroundYEnd]
        DIAGRAM_AROUND_Y_END_STOP: _ClassVar[LineSupport.DiagramAroundYEnd]
        DIAGRAM_AROUND_Y_END_YIELDING: _ClassVar[LineSupport.DiagramAroundYEnd]
    DIAGRAM_AROUND_Y_END_FAILURE: LineSupport.DiagramAroundYEnd
    DIAGRAM_AROUND_Y_END_CONTINUOUS: LineSupport.DiagramAroundYEnd
    DIAGRAM_AROUND_Y_END_STOP: LineSupport.DiagramAroundYEnd
    DIAGRAM_AROUND_Y_END_YIELDING: LineSupport.DiagramAroundYEnd
    class DiagramAroundYStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_Y_START_FAILURE: _ClassVar[LineSupport.DiagramAroundYStart]
        DIAGRAM_AROUND_Y_START_CONTINUOUS: _ClassVar[LineSupport.DiagramAroundYStart]
        DIAGRAM_AROUND_Y_START_STOP: _ClassVar[LineSupport.DiagramAroundYStart]
        DIAGRAM_AROUND_Y_START_YIELDING: _ClassVar[LineSupport.DiagramAroundYStart]
    DIAGRAM_AROUND_Y_START_FAILURE: LineSupport.DiagramAroundYStart
    DIAGRAM_AROUND_Y_START_CONTINUOUS: LineSupport.DiagramAroundYStart
    DIAGRAM_AROUND_Y_START_STOP: LineSupport.DiagramAroundYStart
    DIAGRAM_AROUND_Y_START_YIELDING: LineSupport.DiagramAroundYStart
    class DiagramAroundZEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_Z_END_FAILURE: _ClassVar[LineSupport.DiagramAroundZEnd]
        DIAGRAM_AROUND_Z_END_CONTINUOUS: _ClassVar[LineSupport.DiagramAroundZEnd]
        DIAGRAM_AROUND_Z_END_STOP: _ClassVar[LineSupport.DiagramAroundZEnd]
        DIAGRAM_AROUND_Z_END_YIELDING: _ClassVar[LineSupport.DiagramAroundZEnd]
    DIAGRAM_AROUND_Z_END_FAILURE: LineSupport.DiagramAroundZEnd
    DIAGRAM_AROUND_Z_END_CONTINUOUS: LineSupport.DiagramAroundZEnd
    DIAGRAM_AROUND_Z_END_STOP: LineSupport.DiagramAroundZEnd
    DIAGRAM_AROUND_Z_END_YIELDING: LineSupport.DiagramAroundZEnd
    class DiagramAroundZStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_Z_START_FAILURE: _ClassVar[LineSupport.DiagramAroundZStart]
        DIAGRAM_AROUND_Z_START_CONTINUOUS: _ClassVar[LineSupport.DiagramAroundZStart]
        DIAGRAM_AROUND_Z_START_STOP: _ClassVar[LineSupport.DiagramAroundZStart]
        DIAGRAM_AROUND_Z_START_YIELDING: _ClassVar[LineSupport.DiagramAroundZStart]
    DIAGRAM_AROUND_Z_START_FAILURE: LineSupport.DiagramAroundZStart
    DIAGRAM_AROUND_Z_START_CONTINUOUS: LineSupport.DiagramAroundZStart
    DIAGRAM_AROUND_Z_START_STOP: LineSupport.DiagramAroundZStart
    DIAGRAM_AROUND_Z_START_YIELDING: LineSupport.DiagramAroundZStart
    class PartialActivityAlongXNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_COMPLETE: _ClassVar[LineSupport.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE: _ClassVar[LineSupport.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIXED: _ClassVar[LineSupport.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAlongXNegativeType]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_COMPLETE: LineSupport.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE: LineSupport.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIXED: LineSupport.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAlongXNegativeType
    class PartialActivityAlongXPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_COMPLETE: _ClassVar[LineSupport.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE: _ClassVar[LineSupport.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIXED: _ClassVar[LineSupport.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAlongXPositiveType]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_COMPLETE: LineSupport.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE: LineSupport.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIXED: LineSupport.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAlongXPositiveType
    class PartialActivityAlongYNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_COMPLETE: _ClassVar[LineSupport.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE: _ClassVar[LineSupport.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FIXED: _ClassVar[LineSupport.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAlongYNegativeType]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_COMPLETE: LineSupport.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE: LineSupport.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FIXED: LineSupport.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAlongYNegativeType
    class PartialActivityAlongYPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_COMPLETE: _ClassVar[LineSupport.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE: _ClassVar[LineSupport.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FIXED: _ClassVar[LineSupport.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAlongYPositiveType]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_COMPLETE: LineSupport.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE: LineSupport.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FIXED: LineSupport.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAlongYPositiveType
    class PartialActivityAlongZNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_COMPLETE: _ClassVar[LineSupport.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE: _ClassVar[LineSupport.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FIXED: _ClassVar[LineSupport.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAlongZNegativeType]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_COMPLETE: LineSupport.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE: LineSupport.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FIXED: LineSupport.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAlongZNegativeType
    class PartialActivityAlongZPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_COMPLETE: _ClassVar[LineSupport.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE: _ClassVar[LineSupport.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FIXED: _ClassVar[LineSupport.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAlongZPositiveType]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_COMPLETE: LineSupport.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE: LineSupport.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FIXED: LineSupport.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAlongZPositiveType
    class PartialActivityAroundXNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_COMPLETE: _ClassVar[LineSupport.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE: _ClassVar[LineSupport.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FIXED: _ClassVar[LineSupport.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAroundXNegativeType]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_COMPLETE: LineSupport.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE: LineSupport.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FIXED: LineSupport.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAroundXNegativeType
    class PartialActivityAroundXPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_COMPLETE: _ClassVar[LineSupport.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE: _ClassVar[LineSupport.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FIXED: _ClassVar[LineSupport.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAroundXPositiveType]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_COMPLETE: LineSupport.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE: LineSupport.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FIXED: LineSupport.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAroundXPositiveType
    class PartialActivityAroundYNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_COMPLETE: _ClassVar[LineSupport.PartialActivityAroundYNegativeType]
        PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FAILURE: _ClassVar[LineSupport.PartialActivityAroundYNegativeType]
        PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAroundYNegativeType]
        PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FIXED: _ClassVar[LineSupport.PartialActivityAroundYNegativeType]
        PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAroundYNegativeType]
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_COMPLETE: LineSupport.PartialActivityAroundYNegativeType
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FAILURE: LineSupport.PartialActivityAroundYNegativeType
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAroundYNegativeType
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FIXED: LineSupport.PartialActivityAroundYNegativeType
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAroundYNegativeType
    class PartialActivityAroundYPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_COMPLETE: _ClassVar[LineSupport.PartialActivityAroundYPositiveType]
        PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FAILURE: _ClassVar[LineSupport.PartialActivityAroundYPositiveType]
        PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAroundYPositiveType]
        PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FIXED: _ClassVar[LineSupport.PartialActivityAroundYPositiveType]
        PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAroundYPositiveType]
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_COMPLETE: LineSupport.PartialActivityAroundYPositiveType
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FAILURE: LineSupport.PartialActivityAroundYPositiveType
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAroundYPositiveType
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FIXED: LineSupport.PartialActivityAroundYPositiveType
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAroundYPositiveType
    class PartialActivityAroundZNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_COMPLETE: _ClassVar[LineSupport.PartialActivityAroundZNegativeType]
        PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FAILURE: _ClassVar[LineSupport.PartialActivityAroundZNegativeType]
        PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAroundZNegativeType]
        PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FIXED: _ClassVar[LineSupport.PartialActivityAroundZNegativeType]
        PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAroundZNegativeType]
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_COMPLETE: LineSupport.PartialActivityAroundZNegativeType
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FAILURE: LineSupport.PartialActivityAroundZNegativeType
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAroundZNegativeType
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FIXED: LineSupport.PartialActivityAroundZNegativeType
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAroundZNegativeType
    class PartialActivityAroundZPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_COMPLETE: _ClassVar[LineSupport.PartialActivityAroundZPositiveType]
        PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FAILURE: _ClassVar[LineSupport.PartialActivityAroundZPositiveType]
        PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAroundZPositiveType]
        PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FIXED: _ClassVar[LineSupport.PartialActivityAroundZPositiveType]
        PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineSupport.PartialActivityAroundZPositiveType]
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_COMPLETE: LineSupport.PartialActivityAroundZPositiveType
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FAILURE: LineSupport.PartialActivityAroundZPositiveType
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAroundZPositiveType
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FIXED: LineSupport.PartialActivityAroundZPositiveType
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineSupport.PartialActivityAroundZPositiveType
    class FictitiousWallHeadSupportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FICTITIOUS_WALL_HEAD_SUPPORT_TYPE_HINGED: _ClassVar[LineSupport.FictitiousWallHeadSupportType]
        FICTITIOUS_WALL_HEAD_SUPPORT_TYPE_RIGID: _ClassVar[LineSupport.FictitiousWallHeadSupportType]
    FICTITIOUS_WALL_HEAD_SUPPORT_TYPE_HINGED: LineSupport.FictitiousWallHeadSupportType
    FICTITIOUS_WALL_HEAD_SUPPORT_TYPE_RIGID: LineSupport.FictitiousWallHeadSupportType
    class FictitiousWallBaseSupportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FICTITIOUS_WALL_BASE_SUPPORT_TYPE_HINGED: _ClassVar[LineSupport.FictitiousWallBaseSupportType]
        FICTITIOUS_WALL_BASE_SUPPORT_TYPE_ELASTIC: _ClassVar[LineSupport.FictitiousWallBaseSupportType]
        FICTITIOUS_WALL_BASE_SUPPORT_TYPE_RIGID: _ClassVar[LineSupport.FictitiousWallBaseSupportType]
    FICTITIOUS_WALL_BASE_SUPPORT_TYPE_HINGED: LineSupport.FictitiousWallBaseSupportType
    FICTITIOUS_WALL_BASE_SUPPORT_TYPE_ELASTIC: LineSupport.FictitiousWallBaseSupportType
    FICTITIOUS_WALL_BASE_SUPPORT_TYPE_RIGID: LineSupport.FictitiousWallBaseSupportType
    class DiagramAlongXTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[LineSupport.DiagramAlongXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineSupport.DiagramAlongXTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineSupport.DiagramAlongYTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineSupport.DiagramAlongYTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineSupport.DiagramAlongZTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineSupport.DiagramAlongZTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineSupport.DiagramAroundXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineSupport.DiagramAroundXTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineSupport.DiagramAroundYTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineSupport.DiagramAroundYTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineSupport.DiagramAroundZTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineSupport.DiagramAroundZTableRow, _Mapping]]] = ...) -> None: ...
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
    class DiagramAlongXColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[LineSupport.DiagramAlongXColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineSupport.DiagramAlongXColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineSupport.DiagramAlongYColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineSupport.DiagramAlongYColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineSupport.DiagramAlongZColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineSupport.DiagramAlongZColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineSupport.DiagramAroundXColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineSupport.DiagramAroundXColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineSupport.DiagramAroundYColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineSupport.DiagramAroundYColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineSupport.DiagramAroundZColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineSupport.DiagramAroundZColorTableRow, _Mapping]]] = ...) -> None: ...
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
    LINES_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    X_AXIS_ROTATION_FIELD_NUMBER: _ClassVar[int]
    SPRING_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RESTRAINT_FIELD_NUMBER: _ClassVar[int]
    SPRING_X_FIELD_NUMBER: _ClassVar[int]
    SPRING_Y_FIELD_NUMBER: _ClassVar[int]
    SPRING_Z_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RESTRAINT_X_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RESTRAINT_Y_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RESTRAINT_Z_FIELD_NUMBER: _ClassVar[int]
    SPRING_X_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    SPRING_Y_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    SPRING_Z_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RESTRAINT_X_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RESTRAINT_Y_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RESTRAINT_Z_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_TABLE_FIELD_NUMBER: _ClassVar[int]
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
    FRICTION_COEFFICIENT_X_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_Y_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_Z_FIELD_NUMBER: _ClassVar[int]
    FRICTION_DIRECTION_INDEPENDENT_X_FIELD_NUMBER: _ClassVar[int]
    FRICTION_DIRECTION_INDEPENDENT_Y_FIELD_NUMBER: _ClassVar[int]
    FRICTION_DIRECTION_INDEPENDENT_Z_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    FICTITIOUS_WALL_ENABLED_FIELD_NUMBER: _ClassVar[int]
    FICTITIOUS_WALL_WIDTH_FIELD_NUMBER: _ClassVar[int]
    FICTITIOUS_WALL_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FICTITIOUS_WALL_HEAD_SUPPORT_TYPE_FIELD_NUMBER: _ClassVar[int]
    FICTITIOUS_WALL_BASE_SUPPORT_TYPE_FIELD_NUMBER: _ClassVar[int]
    FICTITIOUS_WALL_BASE_ELASTIC_FIELD_NUMBER: _ClassVar[int]
    FICTITIOUS_WALL_SHEAR_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    FICTITIOUS_WALL_MATERIAL_FIELD_NUMBER: _ClassVar[int]
    FICTITIOUS_WALL_SPRING_X_FIELD_NUMBER: _ClassVar[int]
    FICTITIOUS_WALL_SPRING_Y_FIELD_NUMBER: _ClassVar[int]
    FICTITIOUS_WALL_SPRING_Z_FIELD_NUMBER: _ClassVar[int]
    FICTITIOUS_WALL_ROTATIONAL_RESTRAINT_ABOUT_LINE_AXIS_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    lines: _containers.RepeatedScalarFieldContainer[int]
    coordinate_system: LineSupport.CoordinateSystem
    x_axis_rotation: float
    spring: _common_pb2.Vector3d
    rotational_restraint: _common_pb2.Vector3d
    spring_x: float
    spring_y: float
    spring_z: float
    rotational_restraint_x: float
    rotational_restraint_y: float
    rotational_restraint_z: float
    spring_x_nonlinearity: LineSupport.SpringXNonlinearity
    spring_y_nonlinearity: LineSupport.SpringYNonlinearity
    spring_z_nonlinearity: LineSupport.SpringZNonlinearity
    rotational_restraint_x_nonlinearity: LineSupport.RotationalRestraintXNonlinearity
    rotational_restraint_y_nonlinearity: LineSupport.RotationalRestraintYNonlinearity
    rotational_restraint_z_nonlinearity: LineSupport.RotationalRestraintZNonlinearity
    comment: str
    diagram_along_x_end: LineSupport.DiagramAlongXEnd
    diagram_along_x_is_sorted: bool
    diagram_along_x_symmetric: bool
    diagram_along_x_start: LineSupport.DiagramAlongXStart
    diagram_along_x_table: LineSupport.DiagramAlongXTable
    diagram_along_y_end: LineSupport.DiagramAlongYEnd
    diagram_along_y_is_sorted: bool
    diagram_along_y_symmetric: bool
    diagram_along_y_start: LineSupport.DiagramAlongYStart
    diagram_along_y_table: LineSupport.DiagramAlongYTable
    diagram_along_z_end: LineSupport.DiagramAlongZEnd
    diagram_along_z_is_sorted: bool
    diagram_along_z_symmetric: bool
    diagram_along_z_start: LineSupport.DiagramAlongZStart
    diagram_along_z_table: LineSupport.DiagramAlongZTable
    diagram_around_x_end: LineSupport.DiagramAroundXEnd
    diagram_around_x_is_sorted: bool
    diagram_around_x_symmetric: bool
    diagram_around_x_start: LineSupport.DiagramAroundXStart
    diagram_around_x_table: LineSupport.DiagramAroundXTable
    diagram_around_y_end: LineSupport.DiagramAroundYEnd
    diagram_around_y_is_sorted: bool
    diagram_around_y_symmetric: bool
    diagram_around_y_start: LineSupport.DiagramAroundYStart
    diagram_around_y_table: LineSupport.DiagramAroundYTable
    diagram_around_z_end: LineSupport.DiagramAroundZEnd
    diagram_around_z_is_sorted: bool
    diagram_around_z_symmetric: bool
    diagram_around_z_start: LineSupport.DiagramAroundZStart
    diagram_around_z_table: LineSupport.DiagramAroundZTable
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
    diagram_along_x_color_table: LineSupport.DiagramAlongXColorTable
    diagram_along_y_color_table: LineSupport.DiagramAlongYColorTable
    diagram_along_z_color_table: LineSupport.DiagramAlongZColorTable
    diagram_around_x_color_table: LineSupport.DiagramAroundXColorTable
    diagram_around_y_color_table: LineSupport.DiagramAroundYColorTable
    diagram_around_z_color_table: LineSupport.DiagramAroundZColorTable
    friction_coefficient_x: float
    friction_coefficient_y: float
    friction_coefficient_z: float
    friction_direction_independent_x: bool
    friction_direction_independent_y: bool
    friction_direction_independent_z: bool
    partial_activity_along_x_negative_displacement: float
    partial_activity_along_x_negative_force: float
    partial_activity_along_x_negative_slippage: float
    partial_activity_along_x_negative_type: LineSupport.PartialActivityAlongXNegativeType
    partial_activity_along_x_positive_displacement: float
    partial_activity_along_x_positive_force: float
    partial_activity_along_x_positive_slippage: float
    partial_activity_along_x_positive_type: LineSupport.PartialActivityAlongXPositiveType
    partial_activity_along_y_negative_displacement: float
    partial_activity_along_y_negative_force: float
    partial_activity_along_y_negative_slippage: float
    partial_activity_along_y_negative_type: LineSupport.PartialActivityAlongYNegativeType
    partial_activity_along_y_positive_displacement: float
    partial_activity_along_y_positive_force: float
    partial_activity_along_y_positive_slippage: float
    partial_activity_along_y_positive_type: LineSupport.PartialActivityAlongYPositiveType
    partial_activity_along_z_negative_displacement: float
    partial_activity_along_z_negative_force: float
    partial_activity_along_z_negative_slippage: float
    partial_activity_along_z_negative_type: LineSupport.PartialActivityAlongZNegativeType
    partial_activity_along_z_positive_displacement: float
    partial_activity_along_z_positive_force: float
    partial_activity_along_z_positive_slippage: float
    partial_activity_along_z_positive_type: LineSupport.PartialActivityAlongZPositiveType
    partial_activity_around_x_negative_moment: float
    partial_activity_around_x_negative_rotation: float
    partial_activity_around_x_negative_slippage: float
    partial_activity_around_x_negative_type: LineSupport.PartialActivityAroundXNegativeType
    partial_activity_around_x_positive_moment: float
    partial_activity_around_x_positive_rotation: float
    partial_activity_around_x_positive_slippage: float
    partial_activity_around_x_positive_type: LineSupport.PartialActivityAroundXPositiveType
    partial_activity_around_y_negative_moment: float
    partial_activity_around_y_negative_rotation: float
    partial_activity_around_y_negative_slippage: float
    partial_activity_around_y_negative_type: LineSupport.PartialActivityAroundYNegativeType
    partial_activity_around_y_positive_moment: float
    partial_activity_around_y_positive_rotation: float
    partial_activity_around_y_positive_slippage: float
    partial_activity_around_y_positive_type: LineSupport.PartialActivityAroundYPositiveType
    partial_activity_around_z_negative_moment: float
    partial_activity_around_z_negative_rotation: float
    partial_activity_around_z_negative_slippage: float
    partial_activity_around_z_negative_type: LineSupport.PartialActivityAroundZNegativeType
    partial_activity_around_z_positive_moment: float
    partial_activity_around_z_positive_rotation: float
    partial_activity_around_z_positive_slippage: float
    partial_activity_around_z_positive_type: LineSupport.PartialActivityAroundZPositiveType
    is_generated: bool
    generating_object_info: str
    fictitious_wall_enabled: bool
    fictitious_wall_width: float
    fictitious_wall_height: float
    fictitious_wall_head_support_type: LineSupport.FictitiousWallHeadSupportType
    fictitious_wall_base_support_type: LineSupport.FictitiousWallBaseSupportType
    fictitious_wall_base_elastic: float
    fictitious_wall_shear_stiffness: bool
    fictitious_wall_material: int
    fictitious_wall_spring_x: float
    fictitious_wall_spring_y: float
    fictitious_wall_spring_z: float
    fictitious_wall_rotational_restraint_about_line_axis: float
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., lines: _Optional[_Iterable[int]] = ..., coordinate_system: _Optional[_Union[LineSupport.CoordinateSystem, str]] = ..., x_axis_rotation: _Optional[float] = ..., spring: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., rotational_restraint: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., spring_x: _Optional[float] = ..., spring_y: _Optional[float] = ..., spring_z: _Optional[float] = ..., rotational_restraint_x: _Optional[float] = ..., rotational_restraint_y: _Optional[float] = ..., rotational_restraint_z: _Optional[float] = ..., spring_x_nonlinearity: _Optional[_Union[LineSupport.SpringXNonlinearity, str]] = ..., spring_y_nonlinearity: _Optional[_Union[LineSupport.SpringYNonlinearity, str]] = ..., spring_z_nonlinearity: _Optional[_Union[LineSupport.SpringZNonlinearity, str]] = ..., rotational_restraint_x_nonlinearity: _Optional[_Union[LineSupport.RotationalRestraintXNonlinearity, str]] = ..., rotational_restraint_y_nonlinearity: _Optional[_Union[LineSupport.RotationalRestraintYNonlinearity, str]] = ..., rotational_restraint_z_nonlinearity: _Optional[_Union[LineSupport.RotationalRestraintZNonlinearity, str]] = ..., comment: _Optional[str] = ..., diagram_along_x_end: _Optional[_Union[LineSupport.DiagramAlongXEnd, str]] = ..., diagram_along_x_is_sorted: bool = ..., diagram_along_x_symmetric: bool = ..., diagram_along_x_start: _Optional[_Union[LineSupport.DiagramAlongXStart, str]] = ..., diagram_along_x_table: _Optional[_Union[LineSupport.DiagramAlongXTable, _Mapping]] = ..., diagram_along_y_end: _Optional[_Union[LineSupport.DiagramAlongYEnd, str]] = ..., diagram_along_y_is_sorted: bool = ..., diagram_along_y_symmetric: bool = ..., diagram_along_y_start: _Optional[_Union[LineSupport.DiagramAlongYStart, str]] = ..., diagram_along_y_table: _Optional[_Union[LineSupport.DiagramAlongYTable, _Mapping]] = ..., diagram_along_z_end: _Optional[_Union[LineSupport.DiagramAlongZEnd, str]] = ..., diagram_along_z_is_sorted: bool = ..., diagram_along_z_symmetric: bool = ..., diagram_along_z_start: _Optional[_Union[LineSupport.DiagramAlongZStart, str]] = ..., diagram_along_z_table: _Optional[_Union[LineSupport.DiagramAlongZTable, _Mapping]] = ..., diagram_around_x_end: _Optional[_Union[LineSupport.DiagramAroundXEnd, str]] = ..., diagram_around_x_is_sorted: bool = ..., diagram_around_x_symmetric: bool = ..., diagram_around_x_start: _Optional[_Union[LineSupport.DiagramAroundXStart, str]] = ..., diagram_around_x_table: _Optional[_Union[LineSupport.DiagramAroundXTable, _Mapping]] = ..., diagram_around_y_end: _Optional[_Union[LineSupport.DiagramAroundYEnd, str]] = ..., diagram_around_y_is_sorted: bool = ..., diagram_around_y_symmetric: bool = ..., diagram_around_y_start: _Optional[_Union[LineSupport.DiagramAroundYStart, str]] = ..., diagram_around_y_table: _Optional[_Union[LineSupport.DiagramAroundYTable, _Mapping]] = ..., diagram_around_z_end: _Optional[_Union[LineSupport.DiagramAroundZEnd, str]] = ..., diagram_around_z_is_sorted: bool = ..., diagram_around_z_symmetric: bool = ..., diagram_around_z_start: _Optional[_Union[LineSupport.DiagramAroundZStart, str]] = ..., diagram_around_z_table: _Optional[_Union[LineSupport.DiagramAroundZTable, _Mapping]] = ..., diagram_along_x_ac_yield_minus: _Optional[float] = ..., diagram_along_y_ac_yield_minus: _Optional[float] = ..., diagram_along_z_ac_yield_minus: _Optional[float] = ..., diagram_around_x_ac_yield_minus: _Optional[float] = ..., diagram_around_y_ac_yield_minus: _Optional[float] = ..., diagram_around_z_ac_yield_minus: _Optional[float] = ..., diagram_along_x_ac_yield_plus: _Optional[float] = ..., diagram_along_y_ac_yield_plus: _Optional[float] = ..., diagram_along_z_ac_yield_plus: _Optional[float] = ..., diagram_around_x_ac_yield_plus: _Optional[float] = ..., diagram_around_y_ac_yield_plus: _Optional[float] = ..., diagram_around_z_ac_yield_plus: _Optional[float] = ..., diagram_along_x_acceptance_criteria_active: bool = ..., diagram_along_y_acceptance_criteria_active: bool = ..., diagram_along_z_acceptance_criteria_active: bool = ..., diagram_around_x_acceptance_criteria_active: bool = ..., diagram_around_y_acceptance_criteria_active: bool = ..., diagram_around_z_acceptance_criteria_active: bool = ..., diagram_along_x_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_y_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_z_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_y_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_z_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_y_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_z_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_y_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_z_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_color_table: _Optional[_Union[LineSupport.DiagramAlongXColorTable, _Mapping]] = ..., diagram_along_y_color_table: _Optional[_Union[LineSupport.DiagramAlongYColorTable, _Mapping]] = ..., diagram_along_z_color_table: _Optional[_Union[LineSupport.DiagramAlongZColorTable, _Mapping]] = ..., diagram_around_x_color_table: _Optional[_Union[LineSupport.DiagramAroundXColorTable, _Mapping]] = ..., diagram_around_y_color_table: _Optional[_Union[LineSupport.DiagramAroundYColorTable, _Mapping]] = ..., diagram_around_z_color_table: _Optional[_Union[LineSupport.DiagramAroundZColorTable, _Mapping]] = ..., friction_coefficient_x: _Optional[float] = ..., friction_coefficient_y: _Optional[float] = ..., friction_coefficient_z: _Optional[float] = ..., friction_direction_independent_x: bool = ..., friction_direction_independent_y: bool = ..., friction_direction_independent_z: bool = ..., partial_activity_along_x_negative_displacement: _Optional[float] = ..., partial_activity_along_x_negative_force: _Optional[float] = ..., partial_activity_along_x_negative_slippage: _Optional[float] = ..., partial_activity_along_x_negative_type: _Optional[_Union[LineSupport.PartialActivityAlongXNegativeType, str]] = ..., partial_activity_along_x_positive_displacement: _Optional[float] = ..., partial_activity_along_x_positive_force: _Optional[float] = ..., partial_activity_along_x_positive_slippage: _Optional[float] = ..., partial_activity_along_x_positive_type: _Optional[_Union[LineSupport.PartialActivityAlongXPositiveType, str]] = ..., partial_activity_along_y_negative_displacement: _Optional[float] = ..., partial_activity_along_y_negative_force: _Optional[float] = ..., partial_activity_along_y_negative_slippage: _Optional[float] = ..., partial_activity_along_y_negative_type: _Optional[_Union[LineSupport.PartialActivityAlongYNegativeType, str]] = ..., partial_activity_along_y_positive_displacement: _Optional[float] = ..., partial_activity_along_y_positive_force: _Optional[float] = ..., partial_activity_along_y_positive_slippage: _Optional[float] = ..., partial_activity_along_y_positive_type: _Optional[_Union[LineSupport.PartialActivityAlongYPositiveType, str]] = ..., partial_activity_along_z_negative_displacement: _Optional[float] = ..., partial_activity_along_z_negative_force: _Optional[float] = ..., partial_activity_along_z_negative_slippage: _Optional[float] = ..., partial_activity_along_z_negative_type: _Optional[_Union[LineSupport.PartialActivityAlongZNegativeType, str]] = ..., partial_activity_along_z_positive_displacement: _Optional[float] = ..., partial_activity_along_z_positive_force: _Optional[float] = ..., partial_activity_along_z_positive_slippage: _Optional[float] = ..., partial_activity_along_z_positive_type: _Optional[_Union[LineSupport.PartialActivityAlongZPositiveType, str]] = ..., partial_activity_around_x_negative_moment: _Optional[float] = ..., partial_activity_around_x_negative_rotation: _Optional[float] = ..., partial_activity_around_x_negative_slippage: _Optional[float] = ..., partial_activity_around_x_negative_type: _Optional[_Union[LineSupport.PartialActivityAroundXNegativeType, str]] = ..., partial_activity_around_x_positive_moment: _Optional[float] = ..., partial_activity_around_x_positive_rotation: _Optional[float] = ..., partial_activity_around_x_positive_slippage: _Optional[float] = ..., partial_activity_around_x_positive_type: _Optional[_Union[LineSupport.PartialActivityAroundXPositiveType, str]] = ..., partial_activity_around_y_negative_moment: _Optional[float] = ..., partial_activity_around_y_negative_rotation: _Optional[float] = ..., partial_activity_around_y_negative_slippage: _Optional[float] = ..., partial_activity_around_y_negative_type: _Optional[_Union[LineSupport.PartialActivityAroundYNegativeType, str]] = ..., partial_activity_around_y_positive_moment: _Optional[float] = ..., partial_activity_around_y_positive_rotation: _Optional[float] = ..., partial_activity_around_y_positive_slippage: _Optional[float] = ..., partial_activity_around_y_positive_type: _Optional[_Union[LineSupport.PartialActivityAroundYPositiveType, str]] = ..., partial_activity_around_z_negative_moment: _Optional[float] = ..., partial_activity_around_z_negative_rotation: _Optional[float] = ..., partial_activity_around_z_negative_slippage: _Optional[float] = ..., partial_activity_around_z_negative_type: _Optional[_Union[LineSupport.PartialActivityAroundZNegativeType, str]] = ..., partial_activity_around_z_positive_moment: _Optional[float] = ..., partial_activity_around_z_positive_rotation: _Optional[float] = ..., partial_activity_around_z_positive_slippage: _Optional[float] = ..., partial_activity_around_z_positive_type: _Optional[_Union[LineSupport.PartialActivityAroundZPositiveType, str]] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., fictitious_wall_enabled: bool = ..., fictitious_wall_width: _Optional[float] = ..., fictitious_wall_height: _Optional[float] = ..., fictitious_wall_head_support_type: _Optional[_Union[LineSupport.FictitiousWallHeadSupportType, str]] = ..., fictitious_wall_base_support_type: _Optional[_Union[LineSupport.FictitiousWallBaseSupportType, str]] = ..., fictitious_wall_base_elastic: _Optional[float] = ..., fictitious_wall_shear_stiffness: bool = ..., fictitious_wall_material: _Optional[int] = ..., fictitious_wall_spring_x: _Optional[float] = ..., fictitious_wall_spring_y: _Optional[float] = ..., fictitious_wall_spring_z: _Optional[float] = ..., fictitious_wall_rotational_restraint_about_line_axis: _Optional[float] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
