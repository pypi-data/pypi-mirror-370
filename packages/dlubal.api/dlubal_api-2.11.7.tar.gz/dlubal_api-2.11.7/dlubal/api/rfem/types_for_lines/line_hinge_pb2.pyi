from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LineHinge(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "assigned_to", "translational_release_u_x", "translational_release_u_x_nonlinearity", "translational_release_u_y", "translational_release_u_y_nonlinearity", "translational_release_u_z", "translational_release_u_z_nonlinearity", "rotational_release_phi_x", "rotational_release_phi_x_nonlinearity", "partial_activity_along_x_negative_type", "partial_activity_along_x_positive_type", "partial_activity_along_y_negative_type", "partial_activity_along_y_positive_type", "partial_activity_along_z_negative_type", "partial_activity_along_z_positive_type", "partial_activity_around_x_negative_type", "partial_activity_around_x_positive_type", "partial_activity_along_x_negative_displacement", "partial_activity_along_x_positive_displacement", "partial_activity_along_y_negative_displacement", "partial_activity_along_y_positive_displacement", "partial_activity_along_z_negative_displacement", "partial_activity_along_z_positive_displacement", "partial_activity_around_x_negative_moment", "partial_activity_around_x_positive_moment", "partial_activity_along_x_negative_force", "partial_activity_along_x_positive_force", "partial_activity_along_y_negative_force", "partial_activity_along_y_positive_force", "partial_activity_along_z_negative_force", "partial_activity_along_z_positive_force", "partial_activity_around_x_negative_rotation", "partial_activity_around_x_positive_rotation", "partial_activity_along_x_negative_slippage", "partial_activity_along_x_positive_slippage", "partial_activity_along_y_negative_slippage", "partial_activity_along_y_positive_slippage", "partial_activity_along_z_negative_slippage", "partial_activity_along_z_positive_slippage", "partial_activity_around_x_negative_slippage", "partial_activity_around_x_positive_slippage", "diagram_along_x_symmetric", "diagram_along_y_symmetric", "diagram_along_z_symmetric", "diagram_around_x_symmetric", "diagram_along_x_is_sorted", "diagram_along_y_is_sorted", "diagram_along_z_is_sorted", "diagram_around_x_is_sorted", "diagram_along_x_table", "diagram_along_y_table", "diagram_along_z_table", "diagram_around_x_table", "diagram_along_x_start", "diagram_along_y_start", "diagram_along_z_start", "diagram_around_x_start", "diagram_along_x_end", "diagram_along_y_end", "diagram_along_z_end", "diagram_around_x_end", "diagram_along_x_ac_yield_minus", "diagram_along_y_ac_yield_minus", "diagram_along_z_ac_yield_minus", "diagram_around_x_ac_yield_minus", "diagram_along_x_ac_yield_plus", "diagram_along_y_ac_yield_plus", "diagram_along_z_ac_yield_plus", "diagram_around_x_ac_yield_plus", "diagram_along_x_acceptance_criteria_active", "diagram_along_y_acceptance_criteria_active", "diagram_along_z_acceptance_criteria_active", "diagram_around_x_acceptance_criteria_active", "diagram_along_x_minus_color_one", "diagram_along_y_minus_color_one", "diagram_along_z_minus_color_one", "diagram_around_x_minus_color_one", "diagram_along_x_minus_color_two", "diagram_along_y_minus_color_two", "diagram_along_z_minus_color_two", "diagram_around_x_minus_color_two", "diagram_along_x_plus_color_one", "diagram_along_y_plus_color_one", "diagram_along_z_plus_color_one", "diagram_around_x_plus_color_one", "diagram_along_x_plus_color_two", "diagram_along_y_plus_color_two", "diagram_along_z_plus_color_two", "diagram_around_x_plus_color_two", "diagram_along_x_color_table", "diagram_along_y_color_table", "diagram_along_z_color_table", "diagram_around_x_color_table", "force_moment_diagram_around_x_table", "force_moment_diagram_around_x_symmetric", "force_moment_diagram_around_x_is_sorted", "force_moment_diagram_around_x_start", "force_moment_diagram_around_x_end", "force_moment_diagram_around_x_depends_on", "slab_wall_connection", "slab_wall_connection_offset", "slab_wall_with_slab_edge_block", "slab_edge_block_width", "generated_line_hinges", "has_released_rotations_perpendicular_to_axis", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class TranslationalReleaseUXNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_NONE: _ClassVar[LineHinge.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_DIAGRAM: _ClassVar[LineHinge.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[LineHinge.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[LineHinge.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[LineHinge.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[LineHinge.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[LineHinge.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[LineHinge.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[LineHinge.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[LineHinge.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[LineHinge.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[LineHinge.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[LineHinge.TranslationalReleaseUXNonlinearity]
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_NONE: LineHinge.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_DIAGRAM: LineHinge.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: LineHinge.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: LineHinge.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_IF_NEGATIVE: LineHinge.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_IF_POSITIVE: LineHinge.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: LineHinge.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1: LineHinge.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1_2: LineHinge.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: LineHinge.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_2: LineHinge.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_PARTIAL_ACTIVITY: LineHinge.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_STIFFNESS_DIAGRAM: LineHinge.TranslationalReleaseUXNonlinearity
    class TranslationalReleaseUYNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_NONE: _ClassVar[LineHinge.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_DIAGRAM: _ClassVar[LineHinge.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[LineHinge.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[LineHinge.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[LineHinge.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[LineHinge.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[LineHinge.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[LineHinge.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[LineHinge.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[LineHinge.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[LineHinge.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[LineHinge.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[LineHinge.TranslationalReleaseUYNonlinearity]
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_NONE: LineHinge.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_DIAGRAM: LineHinge.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: LineHinge.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: LineHinge.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_IF_NEGATIVE: LineHinge.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_IF_POSITIVE: LineHinge.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FORCE_MOMENT_DIAGRAM: LineHinge.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1: LineHinge.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1_2: LineHinge.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: LineHinge.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_2: LineHinge.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_PARTIAL_ACTIVITY: LineHinge.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_STIFFNESS_DIAGRAM: LineHinge.TranslationalReleaseUYNonlinearity
    class TranslationalReleaseUZNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_NONE: _ClassVar[LineHinge.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_DIAGRAM: _ClassVar[LineHinge.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[LineHinge.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[LineHinge.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[LineHinge.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[LineHinge.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[LineHinge.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[LineHinge.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[LineHinge.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[LineHinge.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[LineHinge.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[LineHinge.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[LineHinge.TranslationalReleaseUZNonlinearity]
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_NONE: LineHinge.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_DIAGRAM: LineHinge.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: LineHinge.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: LineHinge.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_IF_NEGATIVE: LineHinge.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_IF_POSITIVE: LineHinge.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FORCE_MOMENT_DIAGRAM: LineHinge.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1: LineHinge.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1_2: LineHinge.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: LineHinge.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_2: LineHinge.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_PARTIAL_ACTIVITY: LineHinge.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_STIFFNESS_DIAGRAM: LineHinge.TranslationalReleaseUZNonlinearity
    class RotationalReleasePhiXNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_NONE: _ClassVar[LineHinge.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_DIAGRAM: _ClassVar[LineHinge.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[LineHinge.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[LineHinge.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[LineHinge.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[LineHinge.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[LineHinge.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[LineHinge.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[LineHinge.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[LineHinge.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[LineHinge.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[LineHinge.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[LineHinge.RotationalReleasePhiXNonlinearity]
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_NONE: LineHinge.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_DIAGRAM: LineHinge.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: LineHinge.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: LineHinge.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_IF_NEGATIVE: LineHinge.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_IF_POSITIVE: LineHinge.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: LineHinge.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_1: LineHinge.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_1_2: LineHinge.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: LineHinge.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_2: LineHinge.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_PARTIAL_ACTIVITY: LineHinge.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_STIFFNESS_DIAGRAM: LineHinge.RotationalReleasePhiXNonlinearity
    class PartialActivityAlongXNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_COMPLETE: _ClassVar[LineHinge.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE: _ClassVar[LineHinge.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIXED: _ClassVar[LineHinge.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAlongXNegativeType]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_COMPLETE: LineHinge.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE: LineHinge.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIXED: LineHinge.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAlongXNegativeType
    class PartialActivityAlongXPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_COMPLETE: _ClassVar[LineHinge.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE: _ClassVar[LineHinge.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIXED: _ClassVar[LineHinge.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAlongXPositiveType]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_COMPLETE: LineHinge.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE: LineHinge.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIXED: LineHinge.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAlongXPositiveType
    class PartialActivityAlongYNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_COMPLETE: _ClassVar[LineHinge.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE: _ClassVar[LineHinge.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FIXED: _ClassVar[LineHinge.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAlongYNegativeType]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_COMPLETE: LineHinge.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE: LineHinge.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FIXED: LineHinge.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAlongYNegativeType
    class PartialActivityAlongYPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_COMPLETE: _ClassVar[LineHinge.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE: _ClassVar[LineHinge.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FIXED: _ClassVar[LineHinge.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAlongYPositiveType]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_COMPLETE: LineHinge.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE: LineHinge.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FIXED: LineHinge.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAlongYPositiveType
    class PartialActivityAlongZNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_COMPLETE: _ClassVar[LineHinge.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE: _ClassVar[LineHinge.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FIXED: _ClassVar[LineHinge.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAlongZNegativeType]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_COMPLETE: LineHinge.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE: LineHinge.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FIXED: LineHinge.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAlongZNegativeType
    class PartialActivityAlongZPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_COMPLETE: _ClassVar[LineHinge.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE: _ClassVar[LineHinge.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FIXED: _ClassVar[LineHinge.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAlongZPositiveType]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_COMPLETE: LineHinge.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE: LineHinge.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FIXED: LineHinge.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAlongZPositiveType
    class PartialActivityAroundXNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_COMPLETE: _ClassVar[LineHinge.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE: _ClassVar[LineHinge.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FIXED: _ClassVar[LineHinge.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAroundXNegativeType]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_COMPLETE: LineHinge.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE: LineHinge.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FIXED: LineHinge.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAroundXNegativeType
    class PartialActivityAroundXPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_COMPLETE: _ClassVar[LineHinge.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE: _ClassVar[LineHinge.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FIXED: _ClassVar[LineHinge.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineHinge.PartialActivityAroundXPositiveType]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_COMPLETE: LineHinge.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE: LineHinge.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FIXED: LineHinge.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineHinge.PartialActivityAroundXPositiveType
    class DiagramAlongXStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_X_START_FAILURE: _ClassVar[LineHinge.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_CONTINUOUS: _ClassVar[LineHinge.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_STOP: _ClassVar[LineHinge.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_YIELDING: _ClassVar[LineHinge.DiagramAlongXStart]
    DIAGRAM_ALONG_X_START_FAILURE: LineHinge.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_CONTINUOUS: LineHinge.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_STOP: LineHinge.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_YIELDING: LineHinge.DiagramAlongXStart
    class DiagramAlongYStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Y_START_FAILURE: _ClassVar[LineHinge.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_CONTINUOUS: _ClassVar[LineHinge.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_STOP: _ClassVar[LineHinge.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_YIELDING: _ClassVar[LineHinge.DiagramAlongYStart]
    DIAGRAM_ALONG_Y_START_FAILURE: LineHinge.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_CONTINUOUS: LineHinge.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_STOP: LineHinge.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_YIELDING: LineHinge.DiagramAlongYStart
    class DiagramAlongZStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Z_START_FAILURE: _ClassVar[LineHinge.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_CONTINUOUS: _ClassVar[LineHinge.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_STOP: _ClassVar[LineHinge.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_YIELDING: _ClassVar[LineHinge.DiagramAlongZStart]
    DIAGRAM_ALONG_Z_START_FAILURE: LineHinge.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_CONTINUOUS: LineHinge.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_STOP: LineHinge.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_YIELDING: LineHinge.DiagramAlongZStart
    class DiagramAroundXStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_X_START_FAILURE: _ClassVar[LineHinge.DiagramAroundXStart]
        DIAGRAM_AROUND_X_START_CONTINUOUS: _ClassVar[LineHinge.DiagramAroundXStart]
        DIAGRAM_AROUND_X_START_STOP: _ClassVar[LineHinge.DiagramAroundXStart]
        DIAGRAM_AROUND_X_START_YIELDING: _ClassVar[LineHinge.DiagramAroundXStart]
    DIAGRAM_AROUND_X_START_FAILURE: LineHinge.DiagramAroundXStart
    DIAGRAM_AROUND_X_START_CONTINUOUS: LineHinge.DiagramAroundXStart
    DIAGRAM_AROUND_X_START_STOP: LineHinge.DiagramAroundXStart
    DIAGRAM_AROUND_X_START_YIELDING: LineHinge.DiagramAroundXStart
    class DiagramAlongXEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_X_END_FAILURE: _ClassVar[LineHinge.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_CONTINUOUS: _ClassVar[LineHinge.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_STOP: _ClassVar[LineHinge.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_YIELDING: _ClassVar[LineHinge.DiagramAlongXEnd]
    DIAGRAM_ALONG_X_END_FAILURE: LineHinge.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_CONTINUOUS: LineHinge.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_STOP: LineHinge.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_YIELDING: LineHinge.DiagramAlongXEnd
    class DiagramAlongYEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Y_END_FAILURE: _ClassVar[LineHinge.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_CONTINUOUS: _ClassVar[LineHinge.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_STOP: _ClassVar[LineHinge.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_YIELDING: _ClassVar[LineHinge.DiagramAlongYEnd]
    DIAGRAM_ALONG_Y_END_FAILURE: LineHinge.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_CONTINUOUS: LineHinge.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_STOP: LineHinge.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_YIELDING: LineHinge.DiagramAlongYEnd
    class DiagramAlongZEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Z_END_FAILURE: _ClassVar[LineHinge.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_CONTINUOUS: _ClassVar[LineHinge.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_STOP: _ClassVar[LineHinge.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_YIELDING: _ClassVar[LineHinge.DiagramAlongZEnd]
    DIAGRAM_ALONG_Z_END_FAILURE: LineHinge.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_CONTINUOUS: LineHinge.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_STOP: LineHinge.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_YIELDING: LineHinge.DiagramAlongZEnd
    class DiagramAroundXEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_X_END_FAILURE: _ClassVar[LineHinge.DiagramAroundXEnd]
        DIAGRAM_AROUND_X_END_CONTINUOUS: _ClassVar[LineHinge.DiagramAroundXEnd]
        DIAGRAM_AROUND_X_END_STOP: _ClassVar[LineHinge.DiagramAroundXEnd]
        DIAGRAM_AROUND_X_END_YIELDING: _ClassVar[LineHinge.DiagramAroundXEnd]
    DIAGRAM_AROUND_X_END_FAILURE: LineHinge.DiagramAroundXEnd
    DIAGRAM_AROUND_X_END_CONTINUOUS: LineHinge.DiagramAroundXEnd
    DIAGRAM_AROUND_X_END_STOP: LineHinge.DiagramAroundXEnd
    DIAGRAM_AROUND_X_END_YIELDING: LineHinge.DiagramAroundXEnd
    class ForceMomentDiagramAroundXStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FORCE_MOMENT_DIAGRAM_AROUND_X_START_FAILURE: _ClassVar[LineHinge.ForceMomentDiagramAroundXStart]
        FORCE_MOMENT_DIAGRAM_AROUND_X_START_CONTINUOUS: _ClassVar[LineHinge.ForceMomentDiagramAroundXStart]
        FORCE_MOMENT_DIAGRAM_AROUND_X_START_YIELDING: _ClassVar[LineHinge.ForceMomentDiagramAroundXStart]
    FORCE_MOMENT_DIAGRAM_AROUND_X_START_FAILURE: LineHinge.ForceMomentDiagramAroundXStart
    FORCE_MOMENT_DIAGRAM_AROUND_X_START_CONTINUOUS: LineHinge.ForceMomentDiagramAroundXStart
    FORCE_MOMENT_DIAGRAM_AROUND_X_START_YIELDING: LineHinge.ForceMomentDiagramAroundXStart
    class ForceMomentDiagramAroundXEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FORCE_MOMENT_DIAGRAM_AROUND_X_END_FAILURE: _ClassVar[LineHinge.ForceMomentDiagramAroundXEnd]
        FORCE_MOMENT_DIAGRAM_AROUND_X_END_CONTINUOUS: _ClassVar[LineHinge.ForceMomentDiagramAroundXEnd]
        FORCE_MOMENT_DIAGRAM_AROUND_X_END_YIELDING: _ClassVar[LineHinge.ForceMomentDiagramAroundXEnd]
    FORCE_MOMENT_DIAGRAM_AROUND_X_END_FAILURE: LineHinge.ForceMomentDiagramAroundXEnd
    FORCE_MOMENT_DIAGRAM_AROUND_X_END_CONTINUOUS: LineHinge.ForceMomentDiagramAroundXEnd
    FORCE_MOMENT_DIAGRAM_AROUND_X_END_YIELDING: LineHinge.ForceMomentDiagramAroundXEnd
    class ForceMomentDiagramAroundXDependsOn(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FORCE_MOMENT_DIAGRAM_AROUND_X_DEPENDS_ON_N: _ClassVar[LineHinge.ForceMomentDiagramAroundXDependsOn]
        FORCE_MOMENT_DIAGRAM_AROUND_X_DEPENDS_ON_VY: _ClassVar[LineHinge.ForceMomentDiagramAroundXDependsOn]
        FORCE_MOMENT_DIAGRAM_AROUND_X_DEPENDS_ON_VZ: _ClassVar[LineHinge.ForceMomentDiagramAroundXDependsOn]
    FORCE_MOMENT_DIAGRAM_AROUND_X_DEPENDS_ON_N: LineHinge.ForceMomentDiagramAroundXDependsOn
    FORCE_MOMENT_DIAGRAM_AROUND_X_DEPENDS_ON_VY: LineHinge.ForceMomentDiagramAroundXDependsOn
    FORCE_MOMENT_DIAGRAM_AROUND_X_DEPENDS_ON_VZ: LineHinge.ForceMomentDiagramAroundXDependsOn
    class DiagramAlongXTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[LineHinge.DiagramAlongXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineHinge.DiagramAlongXTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineHinge.DiagramAlongYTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineHinge.DiagramAlongYTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineHinge.DiagramAlongZTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineHinge.DiagramAlongZTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineHinge.DiagramAroundXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineHinge.DiagramAroundXTableRow, _Mapping]]] = ...) -> None: ...
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
    class DiagramAlongXColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[LineHinge.DiagramAlongXColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineHinge.DiagramAlongXColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineHinge.DiagramAlongYColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineHinge.DiagramAlongYColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineHinge.DiagramAlongZColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineHinge.DiagramAlongZColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineHinge.DiagramAroundXColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineHinge.DiagramAroundXColorTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAroundXColorTableRow(_message.Message):
        __slots__ = ("no", "description", "color")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        color: _common_pb2.Color
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., color: _Optional[_Union[_common_pb2.Color, _Mapping]] = ...) -> None: ...
    class ForceMomentDiagramAroundXTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[LineHinge.ForceMomentDiagramAroundXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineHinge.ForceMomentDiagramAroundXTableRow, _Mapping]]] = ...) -> None: ...
    class ForceMomentDiagramAroundXTableRow(_message.Message):
        __slots__ = ("no", "description", "force", "max_moment", "min_moment", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FORCE_FIELD_NUMBER: _ClassVar[int]
        MAX_MOMENT_FIELD_NUMBER: _ClassVar[int]
        MIN_MOMENT_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        force: float
        max_moment: float
        min_moment: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., force: _Optional[float] = ..., max_moment: _Optional[float] = ..., min_moment: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    class GeneratedLineHingesTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[LineHinge.GeneratedLineHingesRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineHinge.GeneratedLineHingesRow, _Mapping]]] = ...) -> None: ...
    class GeneratedLineHingesRow(_message.Message):
        __slots__ = ("no", "description", "generated_by", "generated_line_hinge")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        GENERATED_BY_FIELD_NUMBER: _ClassVar[int]
        GENERATED_LINE_HINGE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        generated_by: int
        generated_line_hinge: int
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., generated_by: _Optional[int] = ..., generated_line_hinge: _Optional[int] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_X_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_Y_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_Z_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RELEASE_PHI_X_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_AC_YIELD_MINUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_AC_YIELD_MINUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_AC_YIELD_MINUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_AC_YIELD_MINUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_AC_YIELD_PLUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_AC_YIELD_PLUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_AC_YIELD_PLUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_AC_YIELD_PLUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_ACCEPTANCE_CRITERIA_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_ACCEPTANCE_CRITERIA_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_ACCEPTANCE_CRITERIA_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_ACCEPTANCE_CRITERIA_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    FORCE_MOMENT_DIAGRAM_AROUND_X_TABLE_FIELD_NUMBER: _ClassVar[int]
    FORCE_MOMENT_DIAGRAM_AROUND_X_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    FORCE_MOMENT_DIAGRAM_AROUND_X_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    FORCE_MOMENT_DIAGRAM_AROUND_X_START_FIELD_NUMBER: _ClassVar[int]
    FORCE_MOMENT_DIAGRAM_AROUND_X_END_FIELD_NUMBER: _ClassVar[int]
    FORCE_MOMENT_DIAGRAM_AROUND_X_DEPENDS_ON_FIELD_NUMBER: _ClassVar[int]
    SLAB_WALL_CONNECTION_FIELD_NUMBER: _ClassVar[int]
    SLAB_WALL_CONNECTION_OFFSET_FIELD_NUMBER: _ClassVar[int]
    SLAB_WALL_WITH_SLAB_EDGE_BLOCK_FIELD_NUMBER: _ClassVar[int]
    SLAB_EDGE_BLOCK_WIDTH_FIELD_NUMBER: _ClassVar[int]
    GENERATED_LINE_HINGES_FIELD_NUMBER: _ClassVar[int]
    HAS_RELEASED_ROTATIONS_PERPENDICULAR_TO_AXIS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    assigned_to: str
    translational_release_u_x: float
    translational_release_u_x_nonlinearity: LineHinge.TranslationalReleaseUXNonlinearity
    translational_release_u_y: float
    translational_release_u_y_nonlinearity: LineHinge.TranslationalReleaseUYNonlinearity
    translational_release_u_z: float
    translational_release_u_z_nonlinearity: LineHinge.TranslationalReleaseUZNonlinearity
    rotational_release_phi_x: float
    rotational_release_phi_x_nonlinearity: LineHinge.RotationalReleasePhiXNonlinearity
    partial_activity_along_x_negative_type: LineHinge.PartialActivityAlongXNegativeType
    partial_activity_along_x_positive_type: LineHinge.PartialActivityAlongXPositiveType
    partial_activity_along_y_negative_type: LineHinge.PartialActivityAlongYNegativeType
    partial_activity_along_y_positive_type: LineHinge.PartialActivityAlongYPositiveType
    partial_activity_along_z_negative_type: LineHinge.PartialActivityAlongZNegativeType
    partial_activity_along_z_positive_type: LineHinge.PartialActivityAlongZPositiveType
    partial_activity_around_x_negative_type: LineHinge.PartialActivityAroundXNegativeType
    partial_activity_around_x_positive_type: LineHinge.PartialActivityAroundXPositiveType
    partial_activity_along_x_negative_displacement: float
    partial_activity_along_x_positive_displacement: float
    partial_activity_along_y_negative_displacement: float
    partial_activity_along_y_positive_displacement: float
    partial_activity_along_z_negative_displacement: float
    partial_activity_along_z_positive_displacement: float
    partial_activity_around_x_negative_moment: float
    partial_activity_around_x_positive_moment: float
    partial_activity_along_x_negative_force: float
    partial_activity_along_x_positive_force: float
    partial_activity_along_y_negative_force: float
    partial_activity_along_y_positive_force: float
    partial_activity_along_z_negative_force: float
    partial_activity_along_z_positive_force: float
    partial_activity_around_x_negative_rotation: float
    partial_activity_around_x_positive_rotation: float
    partial_activity_along_x_negative_slippage: float
    partial_activity_along_x_positive_slippage: float
    partial_activity_along_y_negative_slippage: float
    partial_activity_along_y_positive_slippage: float
    partial_activity_along_z_negative_slippage: float
    partial_activity_along_z_positive_slippage: float
    partial_activity_around_x_negative_slippage: float
    partial_activity_around_x_positive_slippage: float
    diagram_along_x_symmetric: bool
    diagram_along_y_symmetric: bool
    diagram_along_z_symmetric: bool
    diagram_around_x_symmetric: bool
    diagram_along_x_is_sorted: bool
    diagram_along_y_is_sorted: bool
    diagram_along_z_is_sorted: bool
    diagram_around_x_is_sorted: bool
    diagram_along_x_table: LineHinge.DiagramAlongXTable
    diagram_along_y_table: LineHinge.DiagramAlongYTable
    diagram_along_z_table: LineHinge.DiagramAlongZTable
    diagram_around_x_table: LineHinge.DiagramAroundXTable
    diagram_along_x_start: LineHinge.DiagramAlongXStart
    diagram_along_y_start: LineHinge.DiagramAlongYStart
    diagram_along_z_start: LineHinge.DiagramAlongZStart
    diagram_around_x_start: LineHinge.DiagramAroundXStart
    diagram_along_x_end: LineHinge.DiagramAlongXEnd
    diagram_along_y_end: LineHinge.DiagramAlongYEnd
    diagram_along_z_end: LineHinge.DiagramAlongZEnd
    diagram_around_x_end: LineHinge.DiagramAroundXEnd
    diagram_along_x_ac_yield_minus: float
    diagram_along_y_ac_yield_minus: float
    diagram_along_z_ac_yield_minus: float
    diagram_around_x_ac_yield_minus: float
    diagram_along_x_ac_yield_plus: float
    diagram_along_y_ac_yield_plus: float
    diagram_along_z_ac_yield_plus: float
    diagram_around_x_ac_yield_plus: float
    diagram_along_x_acceptance_criteria_active: bool
    diagram_along_y_acceptance_criteria_active: bool
    diagram_along_z_acceptance_criteria_active: bool
    diagram_around_x_acceptance_criteria_active: bool
    diagram_along_x_minus_color_one: _common_pb2.Color
    diagram_along_y_minus_color_one: _common_pb2.Color
    diagram_along_z_minus_color_one: _common_pb2.Color
    diagram_around_x_minus_color_one: _common_pb2.Color
    diagram_along_x_minus_color_two: _common_pb2.Color
    diagram_along_y_minus_color_two: _common_pb2.Color
    diagram_along_z_minus_color_two: _common_pb2.Color
    diagram_around_x_minus_color_two: _common_pb2.Color
    diagram_along_x_plus_color_one: _common_pb2.Color
    diagram_along_y_plus_color_one: _common_pb2.Color
    diagram_along_z_plus_color_one: _common_pb2.Color
    diagram_around_x_plus_color_one: _common_pb2.Color
    diagram_along_x_plus_color_two: _common_pb2.Color
    diagram_along_y_plus_color_two: _common_pb2.Color
    diagram_along_z_plus_color_two: _common_pb2.Color
    diagram_around_x_plus_color_two: _common_pb2.Color
    diagram_along_x_color_table: LineHinge.DiagramAlongXColorTable
    diagram_along_y_color_table: LineHinge.DiagramAlongYColorTable
    diagram_along_z_color_table: LineHinge.DiagramAlongZColorTable
    diagram_around_x_color_table: LineHinge.DiagramAroundXColorTable
    force_moment_diagram_around_x_table: LineHinge.ForceMomentDiagramAroundXTable
    force_moment_diagram_around_x_symmetric: bool
    force_moment_diagram_around_x_is_sorted: bool
    force_moment_diagram_around_x_start: LineHinge.ForceMomentDiagramAroundXStart
    force_moment_diagram_around_x_end: LineHinge.ForceMomentDiagramAroundXEnd
    force_moment_diagram_around_x_depends_on: LineHinge.ForceMomentDiagramAroundXDependsOn
    slab_wall_connection: bool
    slab_wall_connection_offset: float
    slab_wall_with_slab_edge_block: bool
    slab_edge_block_width: float
    generated_line_hinges: LineHinge.GeneratedLineHingesTable
    has_released_rotations_perpendicular_to_axis: bool
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., assigned_to: _Optional[str] = ..., translational_release_u_x: _Optional[float] = ..., translational_release_u_x_nonlinearity: _Optional[_Union[LineHinge.TranslationalReleaseUXNonlinearity, str]] = ..., translational_release_u_y: _Optional[float] = ..., translational_release_u_y_nonlinearity: _Optional[_Union[LineHinge.TranslationalReleaseUYNonlinearity, str]] = ..., translational_release_u_z: _Optional[float] = ..., translational_release_u_z_nonlinearity: _Optional[_Union[LineHinge.TranslationalReleaseUZNonlinearity, str]] = ..., rotational_release_phi_x: _Optional[float] = ..., rotational_release_phi_x_nonlinearity: _Optional[_Union[LineHinge.RotationalReleasePhiXNonlinearity, str]] = ..., partial_activity_along_x_negative_type: _Optional[_Union[LineHinge.PartialActivityAlongXNegativeType, str]] = ..., partial_activity_along_x_positive_type: _Optional[_Union[LineHinge.PartialActivityAlongXPositiveType, str]] = ..., partial_activity_along_y_negative_type: _Optional[_Union[LineHinge.PartialActivityAlongYNegativeType, str]] = ..., partial_activity_along_y_positive_type: _Optional[_Union[LineHinge.PartialActivityAlongYPositiveType, str]] = ..., partial_activity_along_z_negative_type: _Optional[_Union[LineHinge.PartialActivityAlongZNegativeType, str]] = ..., partial_activity_along_z_positive_type: _Optional[_Union[LineHinge.PartialActivityAlongZPositiveType, str]] = ..., partial_activity_around_x_negative_type: _Optional[_Union[LineHinge.PartialActivityAroundXNegativeType, str]] = ..., partial_activity_around_x_positive_type: _Optional[_Union[LineHinge.PartialActivityAroundXPositiveType, str]] = ..., partial_activity_along_x_negative_displacement: _Optional[float] = ..., partial_activity_along_x_positive_displacement: _Optional[float] = ..., partial_activity_along_y_negative_displacement: _Optional[float] = ..., partial_activity_along_y_positive_displacement: _Optional[float] = ..., partial_activity_along_z_negative_displacement: _Optional[float] = ..., partial_activity_along_z_positive_displacement: _Optional[float] = ..., partial_activity_around_x_negative_moment: _Optional[float] = ..., partial_activity_around_x_positive_moment: _Optional[float] = ..., partial_activity_along_x_negative_force: _Optional[float] = ..., partial_activity_along_x_positive_force: _Optional[float] = ..., partial_activity_along_y_negative_force: _Optional[float] = ..., partial_activity_along_y_positive_force: _Optional[float] = ..., partial_activity_along_z_negative_force: _Optional[float] = ..., partial_activity_along_z_positive_force: _Optional[float] = ..., partial_activity_around_x_negative_rotation: _Optional[float] = ..., partial_activity_around_x_positive_rotation: _Optional[float] = ..., partial_activity_along_x_negative_slippage: _Optional[float] = ..., partial_activity_along_x_positive_slippage: _Optional[float] = ..., partial_activity_along_y_negative_slippage: _Optional[float] = ..., partial_activity_along_y_positive_slippage: _Optional[float] = ..., partial_activity_along_z_negative_slippage: _Optional[float] = ..., partial_activity_along_z_positive_slippage: _Optional[float] = ..., partial_activity_around_x_negative_slippage: _Optional[float] = ..., partial_activity_around_x_positive_slippage: _Optional[float] = ..., diagram_along_x_symmetric: bool = ..., diagram_along_y_symmetric: bool = ..., diagram_along_z_symmetric: bool = ..., diagram_around_x_symmetric: bool = ..., diagram_along_x_is_sorted: bool = ..., diagram_along_y_is_sorted: bool = ..., diagram_along_z_is_sorted: bool = ..., diagram_around_x_is_sorted: bool = ..., diagram_along_x_table: _Optional[_Union[LineHinge.DiagramAlongXTable, _Mapping]] = ..., diagram_along_y_table: _Optional[_Union[LineHinge.DiagramAlongYTable, _Mapping]] = ..., diagram_along_z_table: _Optional[_Union[LineHinge.DiagramAlongZTable, _Mapping]] = ..., diagram_around_x_table: _Optional[_Union[LineHinge.DiagramAroundXTable, _Mapping]] = ..., diagram_along_x_start: _Optional[_Union[LineHinge.DiagramAlongXStart, str]] = ..., diagram_along_y_start: _Optional[_Union[LineHinge.DiagramAlongYStart, str]] = ..., diagram_along_z_start: _Optional[_Union[LineHinge.DiagramAlongZStart, str]] = ..., diagram_around_x_start: _Optional[_Union[LineHinge.DiagramAroundXStart, str]] = ..., diagram_along_x_end: _Optional[_Union[LineHinge.DiagramAlongXEnd, str]] = ..., diagram_along_y_end: _Optional[_Union[LineHinge.DiagramAlongYEnd, str]] = ..., diagram_along_z_end: _Optional[_Union[LineHinge.DiagramAlongZEnd, str]] = ..., diagram_around_x_end: _Optional[_Union[LineHinge.DiagramAroundXEnd, str]] = ..., diagram_along_x_ac_yield_minus: _Optional[float] = ..., diagram_along_y_ac_yield_minus: _Optional[float] = ..., diagram_along_z_ac_yield_minus: _Optional[float] = ..., diagram_around_x_ac_yield_minus: _Optional[float] = ..., diagram_along_x_ac_yield_plus: _Optional[float] = ..., diagram_along_y_ac_yield_plus: _Optional[float] = ..., diagram_along_z_ac_yield_plus: _Optional[float] = ..., diagram_around_x_ac_yield_plus: _Optional[float] = ..., diagram_along_x_acceptance_criteria_active: bool = ..., diagram_along_y_acceptance_criteria_active: bool = ..., diagram_along_z_acceptance_criteria_active: bool = ..., diagram_around_x_acceptance_criteria_active: bool = ..., diagram_along_x_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_color_table: _Optional[_Union[LineHinge.DiagramAlongXColorTable, _Mapping]] = ..., diagram_along_y_color_table: _Optional[_Union[LineHinge.DiagramAlongYColorTable, _Mapping]] = ..., diagram_along_z_color_table: _Optional[_Union[LineHinge.DiagramAlongZColorTable, _Mapping]] = ..., diagram_around_x_color_table: _Optional[_Union[LineHinge.DiagramAroundXColorTable, _Mapping]] = ..., force_moment_diagram_around_x_table: _Optional[_Union[LineHinge.ForceMomentDiagramAroundXTable, _Mapping]] = ..., force_moment_diagram_around_x_symmetric: bool = ..., force_moment_diagram_around_x_is_sorted: bool = ..., force_moment_diagram_around_x_start: _Optional[_Union[LineHinge.ForceMomentDiagramAroundXStart, str]] = ..., force_moment_diagram_around_x_end: _Optional[_Union[LineHinge.ForceMomentDiagramAroundXEnd, str]] = ..., force_moment_diagram_around_x_depends_on: _Optional[_Union[LineHinge.ForceMomentDiagramAroundXDependsOn, str]] = ..., slab_wall_connection: bool = ..., slab_wall_connection_offset: _Optional[float] = ..., slab_wall_with_slab_edge_block: bool = ..., slab_edge_block_width: _Optional[float] = ..., generated_line_hinges: _Optional[_Union[LineHinge.GeneratedLineHingesTable, _Mapping]] = ..., has_released_rotations_perpendicular_to_axis: bool = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
