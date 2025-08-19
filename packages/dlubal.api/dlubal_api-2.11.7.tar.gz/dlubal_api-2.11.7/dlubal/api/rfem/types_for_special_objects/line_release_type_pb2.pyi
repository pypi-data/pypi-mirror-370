from dlubal.api.common import common_pb2 as _common_pb2
from dlubal.api.rfem import object_id_pb2 as _object_id_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LineReleaseType(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "line_releases", "translational_release_u_x", "translational_release_u_y", "translational_release_u_z", "rotational_release_phi_x", "translational_release_u_x_nonlinearity", "translational_release_u_y_nonlinearity", "translational_release_u_z_nonlinearity", "rotational_release_phi_x_nonlinearity", "partial_activity_along_x_negative_type", "partial_activity_along_x_positive_type", "partial_activity_along_y_negative_type", "partial_activity_along_y_positive_type", "partial_activity_along_z_negative_type", "partial_activity_along_z_positive_type", "partial_activity_around_x_negative_type", "partial_activity_around_x_positive_type", "partial_activity_along_x_negative_displacement", "partial_activity_along_x_positive_displacement", "partial_activity_along_y_negative_displacement", "partial_activity_along_y_positive_displacement", "partial_activity_along_z_negative_displacement", "partial_activity_along_z_positive_displacement", "partial_activity_around_x_negative_moment", "partial_activity_around_x_positive_moment", "partial_activity_along_x_negative_force", "partial_activity_along_x_positive_force", "partial_activity_along_y_negative_force", "partial_activity_along_y_positive_force", "partial_activity_along_z_negative_force", "partial_activity_along_z_positive_force", "partial_activity_around_x_negative_rotation", "partial_activity_around_x_positive_rotation", "partial_activity_along_x_negative_slippage", "partial_activity_along_x_positive_slippage", "partial_activity_along_y_negative_slippage", "partial_activity_along_y_positive_slippage", "partial_activity_along_z_negative_slippage", "partial_activity_along_z_positive_slippage", "partial_activity_around_x_negative_slippage", "partial_activity_around_x_positive_slippage", "diagram_along_x_symmetric", "diagram_along_y_symmetric", "diagram_along_z_symmetric", "diagram_around_x_symmetric", "diagram_along_x_is_sorted", "diagram_along_y_is_sorted", "diagram_along_z_is_sorted", "diagram_around_x_is_sorted", "diagram_along_x_table", "diagram_along_y_table", "diagram_along_z_table", "diagram_around_x_table", "diagram_along_x_start", "diagram_along_y_start", "diagram_along_z_start", "diagram_around_x_start", "diagram_along_x_end", "diagram_along_y_end", "diagram_along_z_end", "diagram_around_x_end", "diagram_along_x_ac_yield_minus", "diagram_along_y_ac_yield_minus", "diagram_along_z_ac_yield_minus", "diagram_around_x_ac_yield_minus", "diagram_along_x_ac_yield_plus", "diagram_along_y_ac_yield_plus", "diagram_along_z_ac_yield_plus", "diagram_around_x_ac_yield_plus", "diagram_along_x_acceptance_criteria_active", "diagram_along_y_acceptance_criteria_active", "diagram_along_z_acceptance_criteria_active", "diagram_around_x_acceptance_criteria_active", "diagram_along_x_minus_color_one", "diagram_along_y_minus_color_one", "diagram_along_z_minus_color_one", "diagram_around_x_minus_color_one", "diagram_along_x_minus_color_two", "diagram_along_y_minus_color_two", "diagram_along_z_minus_color_two", "diagram_around_x_minus_color_two", "diagram_along_x_plus_color_one", "diagram_along_y_plus_color_one", "diagram_along_z_plus_color_one", "diagram_around_x_plus_color_one", "diagram_along_x_plus_color_two", "diagram_along_y_plus_color_two", "diagram_along_z_plus_color_two", "diagram_around_x_plus_color_two", "diagram_along_x_color_table", "diagram_along_y_color_table", "diagram_along_z_color_table", "diagram_around_x_color_table", "force_moment_diagram_around_x_table", "force_moment_diagram_around_x_symmetric", "force_moment_diagram_around_x_is_sorted", "force_moment_diagram_around_x_start", "force_moment_diagram_around_x_end", "force_moment_diagram_around_x_depends_on", "friction_spring_x", "friction_spring_y", "friction_spring_z", "friction_coefficient_x", "friction_coefficient_xy", "friction_coefficient_xz", "friction_coefficient_y", "friction_coefficient_yx", "friction_coefficient_yz", "friction_coefficient_z", "friction_coefficient_zx", "friction_coefficient_zy", "friction_direction_independent_x", "friction_direction_independent_y", "friction_direction_independent_z", "comment", "is_generated", "generating_object_info", "local_axis_system_object_type", "local_axis_system_object_in_plane", "local_axis_system_reference_object", "rotation_angle", "id_for_export_import", "metadata_for_export_import")
    class TranslationalReleaseUXNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_NONE: _ClassVar[LineReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_COUPLED_DIAGRAM_PERMANENT_RELEASE: _ClassVar[LineReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_DIAGRAM: _ClassVar[LineReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[LineReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[LineReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[LineReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[LineReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[LineReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[LineReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[LineReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[LineReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[LineReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[LineReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[LineReleaseType.TranslationalReleaseUXNonlinearity]
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_NONE: LineReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_COUPLED_DIAGRAM_PERMANENT_RELEASE: LineReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_DIAGRAM: LineReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: LineReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: LineReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_IF_NEGATIVE: LineReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_IF_POSITIVE: LineReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: LineReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1: LineReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1_2: LineReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: LineReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_2: LineReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_PARTIAL_ACTIVITY: LineReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_STIFFNESS_DIAGRAM: LineReleaseType.TranslationalReleaseUXNonlinearity
    class TranslationalReleaseUYNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_NONE: _ClassVar[LineReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_COUPLED_DIAGRAM_PERMANENT_RELEASE: _ClassVar[LineReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_DIAGRAM: _ClassVar[LineReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[LineReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[LineReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[LineReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[LineReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[LineReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[LineReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[LineReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[LineReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[LineReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[LineReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[LineReleaseType.TranslationalReleaseUYNonlinearity]
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_NONE: LineReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_COUPLED_DIAGRAM_PERMANENT_RELEASE: LineReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_DIAGRAM: LineReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: LineReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: LineReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_IF_NEGATIVE: LineReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_IF_POSITIVE: LineReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FORCE_MOMENT_DIAGRAM: LineReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1: LineReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1_2: LineReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: LineReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_2: LineReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_PARTIAL_ACTIVITY: LineReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_STIFFNESS_DIAGRAM: LineReleaseType.TranslationalReleaseUYNonlinearity
    class TranslationalReleaseUZNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_NONE: _ClassVar[LineReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_COUPLED_DIAGRAM_PERMANENT_RELEASE: _ClassVar[LineReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_DIAGRAM: _ClassVar[LineReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[LineReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[LineReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[LineReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[LineReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[LineReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[LineReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[LineReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[LineReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[LineReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[LineReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[LineReleaseType.TranslationalReleaseUZNonlinearity]
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_NONE: LineReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_COUPLED_DIAGRAM_PERMANENT_RELEASE: LineReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_DIAGRAM: LineReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: LineReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: LineReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_IF_NEGATIVE: LineReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_IF_POSITIVE: LineReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FORCE_MOMENT_DIAGRAM: LineReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1: LineReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1_2: LineReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: LineReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_2: LineReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_PARTIAL_ACTIVITY: LineReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_STIFFNESS_DIAGRAM: LineReleaseType.TranslationalReleaseUZNonlinearity
    class RotationalReleasePhiXNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_NONE: _ClassVar[LineReleaseType.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_COUPLED_DIAGRAM_PERMANENT_RELEASE: _ClassVar[LineReleaseType.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_DIAGRAM: _ClassVar[LineReleaseType.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[LineReleaseType.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[LineReleaseType.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[LineReleaseType.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[LineReleaseType.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[LineReleaseType.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[LineReleaseType.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[LineReleaseType.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[LineReleaseType.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[LineReleaseType.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[LineReleaseType.RotationalReleasePhiXNonlinearity]
        ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[LineReleaseType.RotationalReleasePhiXNonlinearity]
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_NONE: LineReleaseType.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_COUPLED_DIAGRAM_PERMANENT_RELEASE: LineReleaseType.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_DIAGRAM: LineReleaseType.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: LineReleaseType.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: LineReleaseType.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_IF_NEGATIVE: LineReleaseType.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FAILURE_IF_POSITIVE: LineReleaseType.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: LineReleaseType.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_1: LineReleaseType.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_1_2: LineReleaseType.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: LineReleaseType.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_FRICTION_DIRECTION_2: LineReleaseType.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_PARTIAL_ACTIVITY: LineReleaseType.RotationalReleasePhiXNonlinearity
    ROTATIONAL_RELEASE_PHI_X_NONLINEARITY_STIFFNESS_DIAGRAM: LineReleaseType.RotationalReleasePhiXNonlinearity
    class PartialActivityAlongXNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_COMPLETE: _ClassVar[LineReleaseType.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE: _ClassVar[LineReleaseType.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIXED: _ClassVar[LineReleaseType.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAlongXNegativeType]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_COMPLETE: LineReleaseType.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE: LineReleaseType.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIXED: LineReleaseType.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAlongXNegativeType
    class PartialActivityAlongXPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_COMPLETE: _ClassVar[LineReleaseType.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE: _ClassVar[LineReleaseType.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIXED: _ClassVar[LineReleaseType.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAlongXPositiveType]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_COMPLETE: LineReleaseType.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE: LineReleaseType.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIXED: LineReleaseType.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAlongXPositiveType
    class PartialActivityAlongYNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_COMPLETE: _ClassVar[LineReleaseType.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE: _ClassVar[LineReleaseType.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FIXED: _ClassVar[LineReleaseType.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAlongYNegativeType]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_COMPLETE: LineReleaseType.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE: LineReleaseType.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FIXED: LineReleaseType.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAlongYNegativeType
    class PartialActivityAlongYPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_COMPLETE: _ClassVar[LineReleaseType.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE: _ClassVar[LineReleaseType.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FIXED: _ClassVar[LineReleaseType.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAlongYPositiveType]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_COMPLETE: LineReleaseType.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE: LineReleaseType.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FIXED: LineReleaseType.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAlongYPositiveType
    class PartialActivityAlongZNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_COMPLETE: _ClassVar[LineReleaseType.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE: _ClassVar[LineReleaseType.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FIXED: _ClassVar[LineReleaseType.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAlongZNegativeType]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_COMPLETE: LineReleaseType.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE: LineReleaseType.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FIXED: LineReleaseType.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAlongZNegativeType
    class PartialActivityAlongZPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_COMPLETE: _ClassVar[LineReleaseType.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE: _ClassVar[LineReleaseType.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FIXED: _ClassVar[LineReleaseType.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAlongZPositiveType]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_COMPLETE: LineReleaseType.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE: LineReleaseType.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FIXED: LineReleaseType.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAlongZPositiveType
    class PartialActivityAroundXNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_COMPLETE: _ClassVar[LineReleaseType.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE: _ClassVar[LineReleaseType.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FIXED: _ClassVar[LineReleaseType.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAroundXNegativeType]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_COMPLETE: LineReleaseType.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE: LineReleaseType.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FIXED: LineReleaseType.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAroundXNegativeType
    class PartialActivityAroundXPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_COMPLETE: _ClassVar[LineReleaseType.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE: _ClassVar[LineReleaseType.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FIXED: _ClassVar[LineReleaseType.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[LineReleaseType.PartialActivityAroundXPositiveType]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_COMPLETE: LineReleaseType.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE: LineReleaseType.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FIXED: LineReleaseType.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: LineReleaseType.PartialActivityAroundXPositiveType
    class DiagramAlongXStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_X_START_FAILURE: _ClassVar[LineReleaseType.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_CONTINUOUS: _ClassVar[LineReleaseType.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_STOP: _ClassVar[LineReleaseType.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_YIELDING: _ClassVar[LineReleaseType.DiagramAlongXStart]
    DIAGRAM_ALONG_X_START_FAILURE: LineReleaseType.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_CONTINUOUS: LineReleaseType.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_STOP: LineReleaseType.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_YIELDING: LineReleaseType.DiagramAlongXStart
    class DiagramAlongYStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Y_START_FAILURE: _ClassVar[LineReleaseType.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_CONTINUOUS: _ClassVar[LineReleaseType.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_STOP: _ClassVar[LineReleaseType.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_YIELDING: _ClassVar[LineReleaseType.DiagramAlongYStart]
    DIAGRAM_ALONG_Y_START_FAILURE: LineReleaseType.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_CONTINUOUS: LineReleaseType.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_STOP: LineReleaseType.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_YIELDING: LineReleaseType.DiagramAlongYStart
    class DiagramAlongZStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Z_START_FAILURE: _ClassVar[LineReleaseType.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_CONTINUOUS: _ClassVar[LineReleaseType.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_STOP: _ClassVar[LineReleaseType.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_YIELDING: _ClassVar[LineReleaseType.DiagramAlongZStart]
    DIAGRAM_ALONG_Z_START_FAILURE: LineReleaseType.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_CONTINUOUS: LineReleaseType.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_STOP: LineReleaseType.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_YIELDING: LineReleaseType.DiagramAlongZStart
    class DiagramAroundXStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_X_START_FAILURE: _ClassVar[LineReleaseType.DiagramAroundXStart]
        DIAGRAM_AROUND_X_START_CONTINUOUS: _ClassVar[LineReleaseType.DiagramAroundXStart]
        DIAGRAM_AROUND_X_START_STOP: _ClassVar[LineReleaseType.DiagramAroundXStart]
        DIAGRAM_AROUND_X_START_YIELDING: _ClassVar[LineReleaseType.DiagramAroundXStart]
    DIAGRAM_AROUND_X_START_FAILURE: LineReleaseType.DiagramAroundXStart
    DIAGRAM_AROUND_X_START_CONTINUOUS: LineReleaseType.DiagramAroundXStart
    DIAGRAM_AROUND_X_START_STOP: LineReleaseType.DiagramAroundXStart
    DIAGRAM_AROUND_X_START_YIELDING: LineReleaseType.DiagramAroundXStart
    class DiagramAlongXEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_X_END_FAILURE: _ClassVar[LineReleaseType.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_CONTINUOUS: _ClassVar[LineReleaseType.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_STOP: _ClassVar[LineReleaseType.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_YIELDING: _ClassVar[LineReleaseType.DiagramAlongXEnd]
    DIAGRAM_ALONG_X_END_FAILURE: LineReleaseType.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_CONTINUOUS: LineReleaseType.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_STOP: LineReleaseType.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_YIELDING: LineReleaseType.DiagramAlongXEnd
    class DiagramAlongYEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Y_END_FAILURE: _ClassVar[LineReleaseType.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_CONTINUOUS: _ClassVar[LineReleaseType.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_STOP: _ClassVar[LineReleaseType.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_YIELDING: _ClassVar[LineReleaseType.DiagramAlongYEnd]
    DIAGRAM_ALONG_Y_END_FAILURE: LineReleaseType.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_CONTINUOUS: LineReleaseType.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_STOP: LineReleaseType.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_YIELDING: LineReleaseType.DiagramAlongYEnd
    class DiagramAlongZEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Z_END_FAILURE: _ClassVar[LineReleaseType.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_CONTINUOUS: _ClassVar[LineReleaseType.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_STOP: _ClassVar[LineReleaseType.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_YIELDING: _ClassVar[LineReleaseType.DiagramAlongZEnd]
    DIAGRAM_ALONG_Z_END_FAILURE: LineReleaseType.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_CONTINUOUS: LineReleaseType.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_STOP: LineReleaseType.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_YIELDING: LineReleaseType.DiagramAlongZEnd
    class DiagramAroundXEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_X_END_FAILURE: _ClassVar[LineReleaseType.DiagramAroundXEnd]
        DIAGRAM_AROUND_X_END_CONTINUOUS: _ClassVar[LineReleaseType.DiagramAroundXEnd]
        DIAGRAM_AROUND_X_END_STOP: _ClassVar[LineReleaseType.DiagramAroundXEnd]
        DIAGRAM_AROUND_X_END_YIELDING: _ClassVar[LineReleaseType.DiagramAroundXEnd]
    DIAGRAM_AROUND_X_END_FAILURE: LineReleaseType.DiagramAroundXEnd
    DIAGRAM_AROUND_X_END_CONTINUOUS: LineReleaseType.DiagramAroundXEnd
    DIAGRAM_AROUND_X_END_STOP: LineReleaseType.DiagramAroundXEnd
    DIAGRAM_AROUND_X_END_YIELDING: LineReleaseType.DiagramAroundXEnd
    class ForceMomentDiagramAroundXStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FORCE_MOMENT_DIAGRAM_AROUND_X_START_FAILURE: _ClassVar[LineReleaseType.ForceMomentDiagramAroundXStart]
        FORCE_MOMENT_DIAGRAM_AROUND_X_START_CONTINUOUS: _ClassVar[LineReleaseType.ForceMomentDiagramAroundXStart]
        FORCE_MOMENT_DIAGRAM_AROUND_X_START_YIELDING: _ClassVar[LineReleaseType.ForceMomentDiagramAroundXStart]
    FORCE_MOMENT_DIAGRAM_AROUND_X_START_FAILURE: LineReleaseType.ForceMomentDiagramAroundXStart
    FORCE_MOMENT_DIAGRAM_AROUND_X_START_CONTINUOUS: LineReleaseType.ForceMomentDiagramAroundXStart
    FORCE_MOMENT_DIAGRAM_AROUND_X_START_YIELDING: LineReleaseType.ForceMomentDiagramAroundXStart
    class ForceMomentDiagramAroundXEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FORCE_MOMENT_DIAGRAM_AROUND_X_END_FAILURE: _ClassVar[LineReleaseType.ForceMomentDiagramAroundXEnd]
        FORCE_MOMENT_DIAGRAM_AROUND_X_END_CONTINUOUS: _ClassVar[LineReleaseType.ForceMomentDiagramAroundXEnd]
        FORCE_MOMENT_DIAGRAM_AROUND_X_END_YIELDING: _ClassVar[LineReleaseType.ForceMomentDiagramAroundXEnd]
    FORCE_MOMENT_DIAGRAM_AROUND_X_END_FAILURE: LineReleaseType.ForceMomentDiagramAroundXEnd
    FORCE_MOMENT_DIAGRAM_AROUND_X_END_CONTINUOUS: LineReleaseType.ForceMomentDiagramAroundXEnd
    FORCE_MOMENT_DIAGRAM_AROUND_X_END_YIELDING: LineReleaseType.ForceMomentDiagramAroundXEnd
    class ForceMomentDiagramAroundXDependsOn(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FORCE_MOMENT_DIAGRAM_AROUND_X_DEPENDS_ON_N: _ClassVar[LineReleaseType.ForceMomentDiagramAroundXDependsOn]
        FORCE_MOMENT_DIAGRAM_AROUND_X_DEPENDS_ON_VY: _ClassVar[LineReleaseType.ForceMomentDiagramAroundXDependsOn]
        FORCE_MOMENT_DIAGRAM_AROUND_X_DEPENDS_ON_VZ: _ClassVar[LineReleaseType.ForceMomentDiagramAroundXDependsOn]
    FORCE_MOMENT_DIAGRAM_AROUND_X_DEPENDS_ON_N: LineReleaseType.ForceMomentDiagramAroundXDependsOn
    FORCE_MOMENT_DIAGRAM_AROUND_X_DEPENDS_ON_VY: LineReleaseType.ForceMomentDiagramAroundXDependsOn
    FORCE_MOMENT_DIAGRAM_AROUND_X_DEPENDS_ON_VZ: LineReleaseType.ForceMomentDiagramAroundXDependsOn
    class LocalAxisSystemObjectType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOCAL_AXIS_SYSTEM_OBJECT_TYPE_ORIGINAL_LINE: _ClassVar[LineReleaseType.LocalAxisSystemObjectType]
        LOCAL_AXIS_SYSTEM_OBJECT_TYPE_HELP_NODE: _ClassVar[LineReleaseType.LocalAxisSystemObjectType]
        LOCAL_AXIS_SYSTEM_OBJECT_TYPE_MEMBER_ON_ORIGINAL_LINE: _ClassVar[LineReleaseType.LocalAxisSystemObjectType]
        LOCAL_AXIS_SYSTEM_OBJECT_TYPE_Z_AXIS_PERPENDICULAR_TO_SURFACE: _ClassVar[LineReleaseType.LocalAxisSystemObjectType]
    LOCAL_AXIS_SYSTEM_OBJECT_TYPE_ORIGINAL_LINE: LineReleaseType.LocalAxisSystemObjectType
    LOCAL_AXIS_SYSTEM_OBJECT_TYPE_HELP_NODE: LineReleaseType.LocalAxisSystemObjectType
    LOCAL_AXIS_SYSTEM_OBJECT_TYPE_MEMBER_ON_ORIGINAL_LINE: LineReleaseType.LocalAxisSystemObjectType
    LOCAL_AXIS_SYSTEM_OBJECT_TYPE_Z_AXIS_PERPENDICULAR_TO_SURFACE: LineReleaseType.LocalAxisSystemObjectType
    class LocalAxisSystemObjectInPlane(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOCAL_AXIS_SYSTEM_OBJECT_IN_PLANE_XY: _ClassVar[LineReleaseType.LocalAxisSystemObjectInPlane]
        LOCAL_AXIS_SYSTEM_OBJECT_IN_PLANE_XZ: _ClassVar[LineReleaseType.LocalAxisSystemObjectInPlane]
    LOCAL_AXIS_SYSTEM_OBJECT_IN_PLANE_XY: LineReleaseType.LocalAxisSystemObjectInPlane
    LOCAL_AXIS_SYSTEM_OBJECT_IN_PLANE_XZ: LineReleaseType.LocalAxisSystemObjectInPlane
    class DiagramAlongXTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[LineReleaseType.DiagramAlongXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineReleaseType.DiagramAlongXTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineReleaseType.DiagramAlongYTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineReleaseType.DiagramAlongYTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineReleaseType.DiagramAlongZTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineReleaseType.DiagramAlongZTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineReleaseType.DiagramAroundXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineReleaseType.DiagramAroundXTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineReleaseType.DiagramAlongXColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineReleaseType.DiagramAlongXColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineReleaseType.DiagramAlongYColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineReleaseType.DiagramAlongYColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineReleaseType.DiagramAlongZColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineReleaseType.DiagramAlongZColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineReleaseType.DiagramAroundXColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineReleaseType.DiagramAroundXColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[LineReleaseType.ForceMomentDiagramAroundXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineReleaseType.ForceMomentDiagramAroundXTableRow, _Mapping]]] = ...) -> None: ...
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
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LINE_RELEASES_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_X_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_Y_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_Z_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_RELEASE_PHI_X_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
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
    FRICTION_SPRING_X_FIELD_NUMBER: _ClassVar[int]
    FRICTION_SPRING_Y_FIELD_NUMBER: _ClassVar[int]
    FRICTION_SPRING_Z_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_X_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_XY_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_XZ_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_Y_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_YX_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_YZ_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_Z_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_ZX_FIELD_NUMBER: _ClassVar[int]
    FRICTION_COEFFICIENT_ZY_FIELD_NUMBER: _ClassVar[int]
    FRICTION_DIRECTION_INDEPENDENT_X_FIELD_NUMBER: _ClassVar[int]
    FRICTION_DIRECTION_INDEPENDENT_Y_FIELD_NUMBER: _ClassVar[int]
    FRICTION_DIRECTION_INDEPENDENT_Z_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    LOCAL_AXIS_SYSTEM_OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    LOCAL_AXIS_SYSTEM_OBJECT_IN_PLANE_FIELD_NUMBER: _ClassVar[int]
    LOCAL_AXIS_SYSTEM_REFERENCE_OBJECT_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLE_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    line_releases: _containers.RepeatedScalarFieldContainer[int]
    translational_release_u_x: float
    translational_release_u_y: float
    translational_release_u_z: float
    rotational_release_phi_x: float
    translational_release_u_x_nonlinearity: LineReleaseType.TranslationalReleaseUXNonlinearity
    translational_release_u_y_nonlinearity: LineReleaseType.TranslationalReleaseUYNonlinearity
    translational_release_u_z_nonlinearity: LineReleaseType.TranslationalReleaseUZNonlinearity
    rotational_release_phi_x_nonlinearity: LineReleaseType.RotationalReleasePhiXNonlinearity
    partial_activity_along_x_negative_type: LineReleaseType.PartialActivityAlongXNegativeType
    partial_activity_along_x_positive_type: LineReleaseType.PartialActivityAlongXPositiveType
    partial_activity_along_y_negative_type: LineReleaseType.PartialActivityAlongYNegativeType
    partial_activity_along_y_positive_type: LineReleaseType.PartialActivityAlongYPositiveType
    partial_activity_along_z_negative_type: LineReleaseType.PartialActivityAlongZNegativeType
    partial_activity_along_z_positive_type: LineReleaseType.PartialActivityAlongZPositiveType
    partial_activity_around_x_negative_type: LineReleaseType.PartialActivityAroundXNegativeType
    partial_activity_around_x_positive_type: LineReleaseType.PartialActivityAroundXPositiveType
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
    diagram_along_x_table: LineReleaseType.DiagramAlongXTable
    diagram_along_y_table: LineReleaseType.DiagramAlongYTable
    diagram_along_z_table: LineReleaseType.DiagramAlongZTable
    diagram_around_x_table: LineReleaseType.DiagramAroundXTable
    diagram_along_x_start: LineReleaseType.DiagramAlongXStart
    diagram_along_y_start: LineReleaseType.DiagramAlongYStart
    diagram_along_z_start: LineReleaseType.DiagramAlongZStart
    diagram_around_x_start: LineReleaseType.DiagramAroundXStart
    diagram_along_x_end: LineReleaseType.DiagramAlongXEnd
    diagram_along_y_end: LineReleaseType.DiagramAlongYEnd
    diagram_along_z_end: LineReleaseType.DiagramAlongZEnd
    diagram_around_x_end: LineReleaseType.DiagramAroundXEnd
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
    diagram_along_x_color_table: LineReleaseType.DiagramAlongXColorTable
    diagram_along_y_color_table: LineReleaseType.DiagramAlongYColorTable
    diagram_along_z_color_table: LineReleaseType.DiagramAlongZColorTable
    diagram_around_x_color_table: LineReleaseType.DiagramAroundXColorTable
    force_moment_diagram_around_x_table: LineReleaseType.ForceMomentDiagramAroundXTable
    force_moment_diagram_around_x_symmetric: bool
    force_moment_diagram_around_x_is_sorted: bool
    force_moment_diagram_around_x_start: LineReleaseType.ForceMomentDiagramAroundXStart
    force_moment_diagram_around_x_end: LineReleaseType.ForceMomentDiagramAroundXEnd
    force_moment_diagram_around_x_depends_on: LineReleaseType.ForceMomentDiagramAroundXDependsOn
    friction_spring_x: float
    friction_spring_y: float
    friction_spring_z: float
    friction_coefficient_x: float
    friction_coefficient_xy: float
    friction_coefficient_xz: float
    friction_coefficient_y: float
    friction_coefficient_yx: float
    friction_coefficient_yz: float
    friction_coefficient_z: float
    friction_coefficient_zx: float
    friction_coefficient_zy: float
    friction_direction_independent_x: bool
    friction_direction_independent_y: bool
    friction_direction_independent_z: bool
    comment: str
    is_generated: bool
    generating_object_info: str
    local_axis_system_object_type: LineReleaseType.LocalAxisSystemObjectType
    local_axis_system_object_in_plane: LineReleaseType.LocalAxisSystemObjectInPlane
    local_axis_system_reference_object: _object_id_pb2.ObjectId
    rotation_angle: float
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., line_releases: _Optional[_Iterable[int]] = ..., translational_release_u_x: _Optional[float] = ..., translational_release_u_y: _Optional[float] = ..., translational_release_u_z: _Optional[float] = ..., rotational_release_phi_x: _Optional[float] = ..., translational_release_u_x_nonlinearity: _Optional[_Union[LineReleaseType.TranslationalReleaseUXNonlinearity, str]] = ..., translational_release_u_y_nonlinearity: _Optional[_Union[LineReleaseType.TranslationalReleaseUYNonlinearity, str]] = ..., translational_release_u_z_nonlinearity: _Optional[_Union[LineReleaseType.TranslationalReleaseUZNonlinearity, str]] = ..., rotational_release_phi_x_nonlinearity: _Optional[_Union[LineReleaseType.RotationalReleasePhiXNonlinearity, str]] = ..., partial_activity_along_x_negative_type: _Optional[_Union[LineReleaseType.PartialActivityAlongXNegativeType, str]] = ..., partial_activity_along_x_positive_type: _Optional[_Union[LineReleaseType.PartialActivityAlongXPositiveType, str]] = ..., partial_activity_along_y_negative_type: _Optional[_Union[LineReleaseType.PartialActivityAlongYNegativeType, str]] = ..., partial_activity_along_y_positive_type: _Optional[_Union[LineReleaseType.PartialActivityAlongYPositiveType, str]] = ..., partial_activity_along_z_negative_type: _Optional[_Union[LineReleaseType.PartialActivityAlongZNegativeType, str]] = ..., partial_activity_along_z_positive_type: _Optional[_Union[LineReleaseType.PartialActivityAlongZPositiveType, str]] = ..., partial_activity_around_x_negative_type: _Optional[_Union[LineReleaseType.PartialActivityAroundXNegativeType, str]] = ..., partial_activity_around_x_positive_type: _Optional[_Union[LineReleaseType.PartialActivityAroundXPositiveType, str]] = ..., partial_activity_along_x_negative_displacement: _Optional[float] = ..., partial_activity_along_x_positive_displacement: _Optional[float] = ..., partial_activity_along_y_negative_displacement: _Optional[float] = ..., partial_activity_along_y_positive_displacement: _Optional[float] = ..., partial_activity_along_z_negative_displacement: _Optional[float] = ..., partial_activity_along_z_positive_displacement: _Optional[float] = ..., partial_activity_around_x_negative_moment: _Optional[float] = ..., partial_activity_around_x_positive_moment: _Optional[float] = ..., partial_activity_along_x_negative_force: _Optional[float] = ..., partial_activity_along_x_positive_force: _Optional[float] = ..., partial_activity_along_y_negative_force: _Optional[float] = ..., partial_activity_along_y_positive_force: _Optional[float] = ..., partial_activity_along_z_negative_force: _Optional[float] = ..., partial_activity_along_z_positive_force: _Optional[float] = ..., partial_activity_around_x_negative_rotation: _Optional[float] = ..., partial_activity_around_x_positive_rotation: _Optional[float] = ..., partial_activity_along_x_negative_slippage: _Optional[float] = ..., partial_activity_along_x_positive_slippage: _Optional[float] = ..., partial_activity_along_y_negative_slippage: _Optional[float] = ..., partial_activity_along_y_positive_slippage: _Optional[float] = ..., partial_activity_along_z_negative_slippage: _Optional[float] = ..., partial_activity_along_z_positive_slippage: _Optional[float] = ..., partial_activity_around_x_negative_slippage: _Optional[float] = ..., partial_activity_around_x_positive_slippage: _Optional[float] = ..., diagram_along_x_symmetric: bool = ..., diagram_along_y_symmetric: bool = ..., diagram_along_z_symmetric: bool = ..., diagram_around_x_symmetric: bool = ..., diagram_along_x_is_sorted: bool = ..., diagram_along_y_is_sorted: bool = ..., diagram_along_z_is_sorted: bool = ..., diagram_around_x_is_sorted: bool = ..., diagram_along_x_table: _Optional[_Union[LineReleaseType.DiagramAlongXTable, _Mapping]] = ..., diagram_along_y_table: _Optional[_Union[LineReleaseType.DiagramAlongYTable, _Mapping]] = ..., diagram_along_z_table: _Optional[_Union[LineReleaseType.DiagramAlongZTable, _Mapping]] = ..., diagram_around_x_table: _Optional[_Union[LineReleaseType.DiagramAroundXTable, _Mapping]] = ..., diagram_along_x_start: _Optional[_Union[LineReleaseType.DiagramAlongXStart, str]] = ..., diagram_along_y_start: _Optional[_Union[LineReleaseType.DiagramAlongYStart, str]] = ..., diagram_along_z_start: _Optional[_Union[LineReleaseType.DiagramAlongZStart, str]] = ..., diagram_around_x_start: _Optional[_Union[LineReleaseType.DiagramAroundXStart, str]] = ..., diagram_along_x_end: _Optional[_Union[LineReleaseType.DiagramAlongXEnd, str]] = ..., diagram_along_y_end: _Optional[_Union[LineReleaseType.DiagramAlongYEnd, str]] = ..., diagram_along_z_end: _Optional[_Union[LineReleaseType.DiagramAlongZEnd, str]] = ..., diagram_around_x_end: _Optional[_Union[LineReleaseType.DiagramAroundXEnd, str]] = ..., diagram_along_x_ac_yield_minus: _Optional[float] = ..., diagram_along_y_ac_yield_minus: _Optional[float] = ..., diagram_along_z_ac_yield_minus: _Optional[float] = ..., diagram_around_x_ac_yield_minus: _Optional[float] = ..., diagram_along_x_ac_yield_plus: _Optional[float] = ..., diagram_along_y_ac_yield_plus: _Optional[float] = ..., diagram_along_z_ac_yield_plus: _Optional[float] = ..., diagram_around_x_ac_yield_plus: _Optional[float] = ..., diagram_along_x_acceptance_criteria_active: bool = ..., diagram_along_y_acceptance_criteria_active: bool = ..., diagram_along_z_acceptance_criteria_active: bool = ..., diagram_around_x_acceptance_criteria_active: bool = ..., diagram_along_x_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_color_table: _Optional[_Union[LineReleaseType.DiagramAlongXColorTable, _Mapping]] = ..., diagram_along_y_color_table: _Optional[_Union[LineReleaseType.DiagramAlongYColorTable, _Mapping]] = ..., diagram_along_z_color_table: _Optional[_Union[LineReleaseType.DiagramAlongZColorTable, _Mapping]] = ..., diagram_around_x_color_table: _Optional[_Union[LineReleaseType.DiagramAroundXColorTable, _Mapping]] = ..., force_moment_diagram_around_x_table: _Optional[_Union[LineReleaseType.ForceMomentDiagramAroundXTable, _Mapping]] = ..., force_moment_diagram_around_x_symmetric: bool = ..., force_moment_diagram_around_x_is_sorted: bool = ..., force_moment_diagram_around_x_start: _Optional[_Union[LineReleaseType.ForceMomentDiagramAroundXStart, str]] = ..., force_moment_diagram_around_x_end: _Optional[_Union[LineReleaseType.ForceMomentDiagramAroundXEnd, str]] = ..., force_moment_diagram_around_x_depends_on: _Optional[_Union[LineReleaseType.ForceMomentDiagramAroundXDependsOn, str]] = ..., friction_spring_x: _Optional[float] = ..., friction_spring_y: _Optional[float] = ..., friction_spring_z: _Optional[float] = ..., friction_coefficient_x: _Optional[float] = ..., friction_coefficient_xy: _Optional[float] = ..., friction_coefficient_xz: _Optional[float] = ..., friction_coefficient_y: _Optional[float] = ..., friction_coefficient_yx: _Optional[float] = ..., friction_coefficient_yz: _Optional[float] = ..., friction_coefficient_z: _Optional[float] = ..., friction_coefficient_zx: _Optional[float] = ..., friction_coefficient_zy: _Optional[float] = ..., friction_direction_independent_x: bool = ..., friction_direction_independent_y: bool = ..., friction_direction_independent_z: bool = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., local_axis_system_object_type: _Optional[_Union[LineReleaseType.LocalAxisSystemObjectType, str]] = ..., local_axis_system_object_in_plane: _Optional[_Union[LineReleaseType.LocalAxisSystemObjectInPlane, str]] = ..., local_axis_system_reference_object: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., rotation_angle: _Optional[float] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
