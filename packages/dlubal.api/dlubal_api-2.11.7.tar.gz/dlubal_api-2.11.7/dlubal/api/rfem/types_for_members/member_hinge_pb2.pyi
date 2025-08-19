from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberHinge(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "members", "coordinate_system", "axial_release_n", "axial_release_vy", "axial_release_vz", "moment_release_mt", "moment_release_my", "moment_release_mz", "axial_release_n_nonlinearity", "axial_release_vy_nonlinearity", "axial_release_vz_nonlinearity", "moment_release_mt_nonlinearity", "moment_release_my_nonlinearity", "moment_release_mz_nonlinearity", "partial_activity_along_x_negative_type", "partial_activity_along_x_positive_type", "partial_activity_along_y_negative_type", "partial_activity_along_y_positive_type", "partial_activity_along_z_negative_type", "partial_activity_along_z_positive_type", "partial_activity_around_x_negative_type", "partial_activity_around_x_positive_type", "partial_activity_around_y_negative_type", "partial_activity_around_y_positive_type", "partial_activity_around_z_negative_type", "partial_activity_around_z_positive_type", "partial_activity_along_x_negative_displacement", "partial_activity_along_x_positive_displacement", "partial_activity_along_y_negative_displacement", "partial_activity_along_y_positive_displacement", "partial_activity_along_z_negative_displacement", "partial_activity_along_z_positive_displacement", "partial_activity_around_x_negative_rotation", "partial_activity_around_x_positive_rotation", "partial_activity_around_y_negative_rotation", "partial_activity_around_y_positive_rotation", "partial_activity_around_z_negative_rotation", "partial_activity_around_z_positive_rotation", "partial_activity_along_x_negative_force", "partial_activity_along_x_positive_force", "partial_activity_along_y_negative_force", "partial_activity_along_y_positive_force", "partial_activity_along_z_negative_force", "partial_activity_along_z_positive_force", "partial_activity_around_x_negative_moment", "partial_activity_around_x_positive_moment", "partial_activity_around_y_negative_moment", "partial_activity_around_y_positive_moment", "partial_activity_around_z_negative_moment", "partial_activity_around_z_positive_moment", "partial_activity_along_x_negative_slippage", "partial_activity_along_x_positive_slippage", "partial_activity_along_y_negative_slippage", "partial_activity_along_y_positive_slippage", "partial_activity_along_z_negative_slippage", "partial_activity_along_z_positive_slippage", "partial_activity_around_x_negative_slippage", "partial_activity_around_x_positive_slippage", "partial_activity_around_y_negative_slippage", "partial_activity_around_y_positive_slippage", "partial_activity_around_z_negative_slippage", "partial_activity_around_z_positive_slippage", "diagram_along_x_symmetric", "diagram_along_y_symmetric", "diagram_along_z_symmetric", "diagram_around_x_symmetric", "diagram_around_y_symmetric", "diagram_around_z_symmetric", "diagram_along_x_is_sorted", "diagram_along_y_is_sorted", "diagram_along_z_is_sorted", "diagram_around_x_is_sorted", "diagram_around_y_is_sorted", "diagram_around_z_is_sorted", "diagram_along_x_start", "diagram_along_y_start", "diagram_along_z_start", "diagram_around_x_start", "diagram_around_y_start", "diagram_around_z_start", "diagram_along_x_end", "diagram_along_y_end", "diagram_along_z_end", "diagram_around_x_end", "diagram_around_y_end", "diagram_around_z_end", "diagram_along_x_table", "diagram_along_y_table", "diagram_along_z_table", "diagram_around_x_table", "diagram_around_y_table", "diagram_around_z_table", "diagram_along_x_ac_yield_minus", "diagram_along_y_ac_yield_minus", "diagram_along_z_ac_yield_minus", "diagram_around_x_ac_yield_minus", "diagram_around_y_ac_yield_minus", "diagram_around_z_ac_yield_minus", "diagram_along_x_ac_yield_plus", "diagram_along_y_ac_yield_plus", "diagram_along_z_ac_yield_plus", "diagram_around_x_ac_yield_plus", "diagram_around_y_ac_yield_plus", "diagram_around_z_ac_yield_plus", "diagram_along_x_acceptance_criteria_active", "diagram_along_y_acceptance_criteria_active", "diagram_along_z_acceptance_criteria_active", "diagram_around_x_acceptance_criteria_active", "diagram_around_y_acceptance_criteria_active", "diagram_around_z_acceptance_criteria_active", "diagram_along_x_minus_color_one", "diagram_along_y_minus_color_one", "diagram_along_z_minus_color_one", "diagram_around_x_minus_color_one", "diagram_around_y_minus_color_one", "diagram_around_z_minus_color_one", "diagram_along_x_minus_color_two", "diagram_along_y_minus_color_two", "diagram_along_z_minus_color_two", "diagram_around_x_minus_color_two", "diagram_around_y_minus_color_two", "diagram_around_z_minus_color_two", "diagram_along_x_plus_color_one", "diagram_along_y_plus_color_one", "diagram_along_z_plus_color_one", "diagram_around_x_plus_color_one", "diagram_around_y_plus_color_one", "diagram_around_z_plus_color_one", "diagram_along_x_plus_color_two", "diagram_along_y_plus_color_two", "diagram_along_z_plus_color_two", "diagram_around_x_plus_color_two", "diagram_around_y_plus_color_two", "diagram_around_z_plus_color_two", "diagram_along_x_color_table", "diagram_along_y_color_table", "diagram_along_z_color_table", "diagram_around_x_color_table", "diagram_around_y_color_table", "diagram_around_z_color_table", "plastic_diagram_along_x_table", "plastic_diagram_along_y_table", "plastic_diagram_along_z_table", "plastic_diagram_around_y_table", "plastic_diagram_around_z_table", "plastic_diagram_along_x_symmetric", "plastic_diagram_along_y_symmetric", "plastic_diagram_along_z_symmetric", "plastic_diagram_around_y_symmetric", "plastic_diagram_around_z_symmetric", "plastic_diagram_around_y_force_interaction", "plastic_diagram_around_z_force_interaction", "plastic_diagram_along_x_user_defined", "plastic_diagram_along_y_user_defined", "plastic_diagram_along_z_user_defined", "plastic_diagram_around_y_user_defined", "plastic_diagram_around_z_user_defined", "plastic_diagram_along_x_is_user_defined_member_length", "plastic_diagram_along_y_is_user_defined_member_length", "plastic_diagram_along_z_is_user_defined_member_length", "plastic_diagram_around_y_is_user_defined_member_length", "plastic_diagram_around_z_is_user_defined_member_length", "plastic_diagram_along_x_user_defined_member_length", "plastic_diagram_along_y_user_defined_member_length", "plastic_diagram_along_z_user_defined_member_length", "plastic_diagram_around_y_user_defined_member_length", "plastic_diagram_around_z_user_defined_member_length", "plastic_diagram_along_x_attached_members_min_max_length", "plastic_diagram_along_y_attached_members_min_max_length", "plastic_diagram_along_z_attached_members_min_max_length", "plastic_diagram_around_y_attached_members_min_max_length", "plastic_diagram_around_z_attached_members_min_max_length", "plastic_diagram_along_x_io_negative", "plastic_diagram_along_y_io_negative", "plastic_diagram_along_z_io_negative", "plastic_diagram_around_y_io_negative", "plastic_diagram_around_z_io_negative", "plastic_diagram_along_x_io_positive", "plastic_diagram_along_y_io_positive", "plastic_diagram_along_z_io_positive", "plastic_diagram_around_y_io_positive", "plastic_diagram_around_z_io_positive", "plastic_diagram_along_x_ls_negative", "plastic_diagram_along_y_ls_negative", "plastic_diagram_along_z_ls_negative", "plastic_diagram_around_y_ls_negative", "plastic_diagram_around_z_ls_negative", "plastic_diagram_along_x_ls_positive", "plastic_diagram_along_y_ls_positive", "plastic_diagram_along_z_ls_positive", "plastic_diagram_around_y_ls_positive", "plastic_diagram_around_z_ls_positive", "plastic_diagram_along_x_cp_negative", "plastic_diagram_along_y_cp_negative", "plastic_diagram_along_z_cp_negative", "plastic_diagram_around_y_cp_negative", "plastic_diagram_around_z_cp_negative", "plastic_diagram_along_x_cp_positive", "plastic_diagram_along_y_cp_positive", "plastic_diagram_along_z_cp_positive", "plastic_diagram_around_y_cp_positive", "plastic_diagram_around_z_cp_positive", "plastic_diagram_along_x_minus_color_one", "plastic_diagram_along_y_minus_color_one", "plastic_diagram_along_z_minus_color_one", "plastic_diagram_around_y_minus_color_one", "plastic_diagram_around_z_minus_color_one", "plastic_diagram_along_x_minus_color_two", "plastic_diagram_along_y_minus_color_two", "plastic_diagram_along_z_minus_color_two", "plastic_diagram_around_y_minus_color_two", "plastic_diagram_around_z_minus_color_two", "plastic_diagram_along_x_minus_color_three", "plastic_diagram_along_y_minus_color_three", "plastic_diagram_along_z_minus_color_three", "plastic_diagram_around_y_minus_color_three", "plastic_diagram_around_z_minus_color_three", "plastic_diagram_along_x_minus_color_four", "plastic_diagram_along_y_minus_color_four", "plastic_diagram_along_z_minus_color_four", "plastic_diagram_around_y_minus_color_four", "plastic_diagram_around_z_minus_color_four", "plastic_diagram_along_x_plus_color_one", "plastic_diagram_along_y_plus_color_one", "plastic_diagram_along_z_plus_color_one", "plastic_diagram_around_y_plus_color_one", "plastic_diagram_around_z_plus_color_one", "plastic_diagram_along_x_plus_color_two", "plastic_diagram_along_y_plus_color_two", "plastic_diagram_along_z_plus_color_two", "plastic_diagram_around_y_plus_color_two", "plastic_diagram_around_z_plus_color_two", "plastic_diagram_along_x_plus_color_three", "plastic_diagram_along_y_plus_color_three", "plastic_diagram_along_z_plus_color_three", "plastic_diagram_around_y_plus_color_three", "plastic_diagram_around_z_plus_color_three", "plastic_diagram_along_x_plus_color_four", "plastic_diagram_along_y_plus_color_four", "plastic_diagram_along_z_plus_color_four", "plastic_diagram_around_y_plus_color_four", "plastic_diagram_around_z_plus_color_four", "plastic_diagram_along_x_component_type", "plastic_diagram_along_y_component_type", "plastic_diagram_along_z_component_type", "plastic_diagram_around_y_component_type", "plastic_diagram_around_z_component_type", "plastic_diagram_along_x_color_table", "plastic_diagram_along_y_color_table", "plastic_diagram_along_z_color_table", "plastic_diagram_around_y_color_table", "plastic_diagram_around_z_color_table", "friction_coefficient_x", "friction_coefficient_xy", "friction_coefficient_xz", "friction_coefficient_y", "friction_coefficient_yx", "friction_coefficient_yz", "friction_coefficient_z", "friction_coefficient_zx", "friction_coefficient_zy", "friction_direction_independent_x", "friction_direction_independent_y", "friction_direction_independent_z", "comment", "is_generated", "generating_object_info", "special_type_of_hinge_direction_along_x", "special_type_of_hinge_direction_along_y", "special_type_of_hinge_direction_along_z", "special_type_of_hinge_direction_around_x", "special_type_of_hinge_direction_around_y", "special_type_of_hinge_direction_around_z", "special_type_of_hinge_enabled", "id_for_export_import", "metadata_for_export_import")
    class AxialReleaseNNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXIAL_RELEASE_N_NONLINEARITY_NONE: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_DIAGRAM: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_PLASTIC_BILINEAR: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_PLASTIC_DIAGRAM: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_PLASTIC_FEMA_356_ELASTIC: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_PLASTIC_FEMA_356_RIGID: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_SCAFFOLDING_DIAGRAM: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_SCAFFOLDING_N_PHI_YZ: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
        AXIAL_RELEASE_N_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[MemberHinge.AxialReleaseNNonlinearity]
    AXIAL_RELEASE_N_NONLINEARITY_NONE: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_DIAGRAM: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_FAILURE_IF_NEGATIVE: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_FAILURE_IF_POSITIVE: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_FORCE_MOMENT_DIAGRAM: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_FRICTION_DIRECTION_1: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_FRICTION_DIRECTION_1_2: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_FRICTION_DIRECTION_2: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_PARTIAL_ACTIVITY: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_PLASTIC_BILINEAR: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_PLASTIC_DIAGRAM: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_PLASTIC_FEMA_356_ELASTIC: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_PLASTIC_FEMA_356_RIGID: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_SCAFFOLDING_DIAGRAM: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_SCAFFOLDING_N_PHI_YZ: MemberHinge.AxialReleaseNNonlinearity
    AXIAL_RELEASE_N_NONLINEARITY_STIFFNESS_DIAGRAM: MemberHinge.AxialReleaseNNonlinearity
    class AxialReleaseVyNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXIAL_RELEASE_VY_NONLINEARITY_NONE: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_DIAGRAM: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_PLASTIC_BILINEAR: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_PLASTIC_DIAGRAM: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_PLASTIC_FEMA_356_ELASTIC: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_PLASTIC_FEMA_356_RIGID: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_SCAFFOLDING_DIAGRAM: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_SCAFFOLDING_N_PHI_YZ: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
        AXIAL_RELEASE_VY_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[MemberHinge.AxialReleaseVyNonlinearity]
    AXIAL_RELEASE_VY_NONLINEARITY_NONE: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_DIAGRAM: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_FAILURE_IF_NEGATIVE: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_FAILURE_IF_POSITIVE: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_FORCE_MOMENT_DIAGRAM: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_FRICTION_DIRECTION_1: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_FRICTION_DIRECTION_1_2: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_FRICTION_DIRECTION_2: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_PARTIAL_ACTIVITY: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_PLASTIC_BILINEAR: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_PLASTIC_DIAGRAM: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_PLASTIC_FEMA_356_ELASTIC: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_PLASTIC_FEMA_356_RIGID: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_SCAFFOLDING_DIAGRAM: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_SCAFFOLDING_N_PHI_YZ: MemberHinge.AxialReleaseVyNonlinearity
    AXIAL_RELEASE_VY_NONLINEARITY_STIFFNESS_DIAGRAM: MemberHinge.AxialReleaseVyNonlinearity
    class AxialReleaseVzNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXIAL_RELEASE_VZ_NONLINEARITY_NONE: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_DIAGRAM: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_PLASTIC_BILINEAR: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_PLASTIC_DIAGRAM: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_PLASTIC_FEMA_356_ELASTIC: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_PLASTIC_FEMA_356_RIGID: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_SCAFFOLDING_DIAGRAM: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_SCAFFOLDING_N_PHI_YZ: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
        AXIAL_RELEASE_VZ_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[MemberHinge.AxialReleaseVzNonlinearity]
    AXIAL_RELEASE_VZ_NONLINEARITY_NONE: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_DIAGRAM: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_FAILURE_IF_NEGATIVE: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_FAILURE_IF_POSITIVE: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_FORCE_MOMENT_DIAGRAM: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_FRICTION_DIRECTION_1: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_FRICTION_DIRECTION_1_2: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_FRICTION_DIRECTION_2: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_PARTIAL_ACTIVITY: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_PLASTIC_BILINEAR: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_PLASTIC_DIAGRAM: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_PLASTIC_FEMA_356_ELASTIC: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_PLASTIC_FEMA_356_RIGID: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_SCAFFOLDING_DIAGRAM: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_SCAFFOLDING_N_PHI_YZ: MemberHinge.AxialReleaseVzNonlinearity
    AXIAL_RELEASE_VZ_NONLINEARITY_STIFFNESS_DIAGRAM: MemberHinge.AxialReleaseVzNonlinearity
    class MomentReleaseMtNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MOMENT_RELEASE_MT_NONLINEARITY_NONE: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_DIAGRAM: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_PLASTIC_BILINEAR: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_PLASTIC_DIAGRAM: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_PLASTIC_FEMA_356_ELASTIC: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_PLASTIC_FEMA_356_RIGID: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_SCAFFOLDING_DIAGRAM: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_SCAFFOLDING_N_PHI_YZ: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
        MOMENT_RELEASE_MT_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[MemberHinge.MomentReleaseMtNonlinearity]
    MOMENT_RELEASE_MT_NONLINEARITY_NONE: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_DIAGRAM: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_FAILURE_IF_NEGATIVE: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_FAILURE_IF_POSITIVE: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_FORCE_MOMENT_DIAGRAM: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_FRICTION_DIRECTION_1: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_FRICTION_DIRECTION_1_2: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_FRICTION_DIRECTION_2: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_PARTIAL_ACTIVITY: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_PLASTIC_BILINEAR: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_PLASTIC_DIAGRAM: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_PLASTIC_FEMA_356_ELASTIC: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_PLASTIC_FEMA_356_RIGID: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_SCAFFOLDING_DIAGRAM: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_SCAFFOLDING_N_PHI_YZ: MemberHinge.MomentReleaseMtNonlinearity
    MOMENT_RELEASE_MT_NONLINEARITY_STIFFNESS_DIAGRAM: MemberHinge.MomentReleaseMtNonlinearity
    class MomentReleaseMyNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MOMENT_RELEASE_MY_NONLINEARITY_NONE: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_DIAGRAM: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_PLASTIC_BILINEAR: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_PLASTIC_DIAGRAM: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_PLASTIC_FEMA_356_ELASTIC: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_PLASTIC_FEMA_356_RIGID: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_SCAFFOLDING_DIAGRAM: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_SCAFFOLDING_N_PHI_YZ: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
        MOMENT_RELEASE_MY_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[MemberHinge.MomentReleaseMyNonlinearity]
    MOMENT_RELEASE_MY_NONLINEARITY_NONE: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_DIAGRAM: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_FAILURE_IF_NEGATIVE: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_FAILURE_IF_POSITIVE: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_FORCE_MOMENT_DIAGRAM: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_FRICTION_DIRECTION_1: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_FRICTION_DIRECTION_1_2: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_FRICTION_DIRECTION_2: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_PARTIAL_ACTIVITY: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_PLASTIC_BILINEAR: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_PLASTIC_DIAGRAM: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_PLASTIC_FEMA_356_ELASTIC: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_PLASTIC_FEMA_356_RIGID: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_SCAFFOLDING_DIAGRAM: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_SCAFFOLDING_N_PHI_YZ: MemberHinge.MomentReleaseMyNonlinearity
    MOMENT_RELEASE_MY_NONLINEARITY_STIFFNESS_DIAGRAM: MemberHinge.MomentReleaseMyNonlinearity
    class MomentReleaseMzNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MOMENT_RELEASE_MZ_NONLINEARITY_NONE: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_DIAGRAM: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_PLASTIC_BILINEAR: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_PLASTIC_DIAGRAM: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_PLASTIC_FEMA_356_ELASTIC: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_PLASTIC_FEMA_356_RIGID: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_SCAFFOLDING_DIAGRAM: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_SCAFFOLDING_N_PHI_YZ: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
        MOMENT_RELEASE_MZ_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[MemberHinge.MomentReleaseMzNonlinearity]
    MOMENT_RELEASE_MZ_NONLINEARITY_NONE: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_DIAGRAM: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_FAILURE_IF_NEGATIVE: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_FAILURE_IF_POSITIVE: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_FORCE_MOMENT_DIAGRAM: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_FRICTION_DIRECTION_1: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_FRICTION_DIRECTION_1_2: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_FRICTION_DIRECTION_2: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_PARTIAL_ACTIVITY: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_PLASTIC_BILINEAR: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_PLASTIC_DIAGRAM: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_PLASTIC_FEMA_356_ELASTIC: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_PLASTIC_FEMA_356_RIGID: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_SCAFFOLDING_DIAGRAM: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_SCAFFOLDING_N_PHI_YZ: MemberHinge.MomentReleaseMzNonlinearity
    MOMENT_RELEASE_MZ_NONLINEARITY_STIFFNESS_DIAGRAM: MemberHinge.MomentReleaseMzNonlinearity
    class PartialActivityAlongXNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_COMPLETE: _ClassVar[MemberHinge.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE: _ClassVar[MemberHinge.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIXED: _ClassVar[MemberHinge.PartialActivityAlongXNegativeType]
        PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAlongXNegativeType]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_COMPLETE: MemberHinge.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE: MemberHinge.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIXED: MemberHinge.PartialActivityAlongXNegativeType
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAlongXNegativeType
    class PartialActivityAlongXPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_COMPLETE: _ClassVar[MemberHinge.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE: _ClassVar[MemberHinge.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIXED: _ClassVar[MemberHinge.PartialActivityAlongXPositiveType]
        PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAlongXPositiveType]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_COMPLETE: MemberHinge.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE: MemberHinge.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIXED: MemberHinge.PartialActivityAlongXPositiveType
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAlongXPositiveType
    class PartialActivityAlongYNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_COMPLETE: _ClassVar[MemberHinge.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE: _ClassVar[MemberHinge.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FIXED: _ClassVar[MemberHinge.PartialActivityAlongYNegativeType]
        PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAlongYNegativeType]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_COMPLETE: MemberHinge.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE: MemberHinge.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FIXED: MemberHinge.PartialActivityAlongYNegativeType
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAlongYNegativeType
    class PartialActivityAlongYPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_COMPLETE: _ClassVar[MemberHinge.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE: _ClassVar[MemberHinge.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FIXED: _ClassVar[MemberHinge.PartialActivityAlongYPositiveType]
        PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAlongYPositiveType]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_COMPLETE: MemberHinge.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE: MemberHinge.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FIXED: MemberHinge.PartialActivityAlongYPositiveType
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAlongYPositiveType
    class PartialActivityAlongZNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_COMPLETE: _ClassVar[MemberHinge.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE: _ClassVar[MemberHinge.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FIXED: _ClassVar[MemberHinge.PartialActivityAlongZNegativeType]
        PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAlongZNegativeType]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_COMPLETE: MemberHinge.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE: MemberHinge.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FIXED: MemberHinge.PartialActivityAlongZNegativeType
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAlongZNegativeType
    class PartialActivityAlongZPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_COMPLETE: _ClassVar[MemberHinge.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE: _ClassVar[MemberHinge.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FIXED: _ClassVar[MemberHinge.PartialActivityAlongZPositiveType]
        PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAlongZPositiveType]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_COMPLETE: MemberHinge.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE: MemberHinge.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FIXED: MemberHinge.PartialActivityAlongZPositiveType
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAlongZPositiveType
    class PartialActivityAroundXNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_COMPLETE: _ClassVar[MemberHinge.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE: _ClassVar[MemberHinge.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FIXED: _ClassVar[MemberHinge.PartialActivityAroundXNegativeType]
        PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAroundXNegativeType]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_COMPLETE: MemberHinge.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE: MemberHinge.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FIXED: MemberHinge.PartialActivityAroundXNegativeType
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAroundXNegativeType
    class PartialActivityAroundXPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_COMPLETE: _ClassVar[MemberHinge.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE: _ClassVar[MemberHinge.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FIXED: _ClassVar[MemberHinge.PartialActivityAroundXPositiveType]
        PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAroundXPositiveType]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_COMPLETE: MemberHinge.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE: MemberHinge.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FIXED: MemberHinge.PartialActivityAroundXPositiveType
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAroundXPositiveType
    class PartialActivityAroundYNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_COMPLETE: _ClassVar[MemberHinge.PartialActivityAroundYNegativeType]
        PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FAILURE: _ClassVar[MemberHinge.PartialActivityAroundYNegativeType]
        PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAroundYNegativeType]
        PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FIXED: _ClassVar[MemberHinge.PartialActivityAroundYNegativeType]
        PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAroundYNegativeType]
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_COMPLETE: MemberHinge.PartialActivityAroundYNegativeType
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FAILURE: MemberHinge.PartialActivityAroundYNegativeType
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAroundYNegativeType
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FIXED: MemberHinge.PartialActivityAroundYNegativeType
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAroundYNegativeType
    class PartialActivityAroundYPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_COMPLETE: _ClassVar[MemberHinge.PartialActivityAroundYPositiveType]
        PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FAILURE: _ClassVar[MemberHinge.PartialActivityAroundYPositiveType]
        PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAroundYPositiveType]
        PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FIXED: _ClassVar[MemberHinge.PartialActivityAroundYPositiveType]
        PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAroundYPositiveType]
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_COMPLETE: MemberHinge.PartialActivityAroundYPositiveType
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FAILURE: MemberHinge.PartialActivityAroundYPositiveType
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAroundYPositiveType
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FIXED: MemberHinge.PartialActivityAroundYPositiveType
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAroundYPositiveType
    class PartialActivityAroundZNegativeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_COMPLETE: _ClassVar[MemberHinge.PartialActivityAroundZNegativeType]
        PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FAILURE: _ClassVar[MemberHinge.PartialActivityAroundZNegativeType]
        PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAroundZNegativeType]
        PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FIXED: _ClassVar[MemberHinge.PartialActivityAroundZNegativeType]
        PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAroundZNegativeType]
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_COMPLETE: MemberHinge.PartialActivityAroundZNegativeType
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FAILURE: MemberHinge.PartialActivityAroundZNegativeType
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAroundZNegativeType
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FIXED: MemberHinge.PartialActivityAroundZNegativeType
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAroundZNegativeType
    class PartialActivityAroundZPositiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_COMPLETE: _ClassVar[MemberHinge.PartialActivityAroundZPositiveType]
        PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FAILURE: _ClassVar[MemberHinge.PartialActivityAroundZPositiveType]
        PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAroundZPositiveType]
        PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FIXED: _ClassVar[MemberHinge.PartialActivityAroundZPositiveType]
        PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: _ClassVar[MemberHinge.PartialActivityAroundZPositiveType]
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_COMPLETE: MemberHinge.PartialActivityAroundZPositiveType
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FAILURE: MemberHinge.PartialActivityAroundZPositiveType
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FAILURE_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAroundZPositiveType
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FIXED: MemberHinge.PartialActivityAroundZPositiveType
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_YIELDING_FROM_FORCE_OR_MOMENT: MemberHinge.PartialActivityAroundZPositiveType
    class DiagramAlongXStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_X_START_FAILURE: _ClassVar[MemberHinge.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_CONTINUOUS: _ClassVar[MemberHinge.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_STOP: _ClassVar[MemberHinge.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_YIELDING: _ClassVar[MemberHinge.DiagramAlongXStart]
    DIAGRAM_ALONG_X_START_FAILURE: MemberHinge.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_CONTINUOUS: MemberHinge.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_STOP: MemberHinge.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_YIELDING: MemberHinge.DiagramAlongXStart
    class DiagramAlongYStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Y_START_FAILURE: _ClassVar[MemberHinge.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_CONTINUOUS: _ClassVar[MemberHinge.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_STOP: _ClassVar[MemberHinge.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_YIELDING: _ClassVar[MemberHinge.DiagramAlongYStart]
    DIAGRAM_ALONG_Y_START_FAILURE: MemberHinge.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_CONTINUOUS: MemberHinge.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_STOP: MemberHinge.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_YIELDING: MemberHinge.DiagramAlongYStart
    class DiagramAlongZStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Z_START_FAILURE: _ClassVar[MemberHinge.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_CONTINUOUS: _ClassVar[MemberHinge.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_STOP: _ClassVar[MemberHinge.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_YIELDING: _ClassVar[MemberHinge.DiagramAlongZStart]
    DIAGRAM_ALONG_Z_START_FAILURE: MemberHinge.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_CONTINUOUS: MemberHinge.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_STOP: MemberHinge.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_YIELDING: MemberHinge.DiagramAlongZStart
    class DiagramAroundXStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_X_START_FAILURE: _ClassVar[MemberHinge.DiagramAroundXStart]
        DIAGRAM_AROUND_X_START_CONTINUOUS: _ClassVar[MemberHinge.DiagramAroundXStart]
        DIAGRAM_AROUND_X_START_STOP: _ClassVar[MemberHinge.DiagramAroundXStart]
        DIAGRAM_AROUND_X_START_YIELDING: _ClassVar[MemberHinge.DiagramAroundXStart]
    DIAGRAM_AROUND_X_START_FAILURE: MemberHinge.DiagramAroundXStart
    DIAGRAM_AROUND_X_START_CONTINUOUS: MemberHinge.DiagramAroundXStart
    DIAGRAM_AROUND_X_START_STOP: MemberHinge.DiagramAroundXStart
    DIAGRAM_AROUND_X_START_YIELDING: MemberHinge.DiagramAroundXStart
    class DiagramAroundYStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_Y_START_FAILURE: _ClassVar[MemberHinge.DiagramAroundYStart]
        DIAGRAM_AROUND_Y_START_CONTINUOUS: _ClassVar[MemberHinge.DiagramAroundYStart]
        DIAGRAM_AROUND_Y_START_STOP: _ClassVar[MemberHinge.DiagramAroundYStart]
        DIAGRAM_AROUND_Y_START_YIELDING: _ClassVar[MemberHinge.DiagramAroundYStart]
    DIAGRAM_AROUND_Y_START_FAILURE: MemberHinge.DiagramAroundYStart
    DIAGRAM_AROUND_Y_START_CONTINUOUS: MemberHinge.DiagramAroundYStart
    DIAGRAM_AROUND_Y_START_STOP: MemberHinge.DiagramAroundYStart
    DIAGRAM_AROUND_Y_START_YIELDING: MemberHinge.DiagramAroundYStart
    class DiagramAroundZStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_Z_START_FAILURE: _ClassVar[MemberHinge.DiagramAroundZStart]
        DIAGRAM_AROUND_Z_START_CONTINUOUS: _ClassVar[MemberHinge.DiagramAroundZStart]
        DIAGRAM_AROUND_Z_START_STOP: _ClassVar[MemberHinge.DiagramAroundZStart]
        DIAGRAM_AROUND_Z_START_YIELDING: _ClassVar[MemberHinge.DiagramAroundZStart]
    DIAGRAM_AROUND_Z_START_FAILURE: MemberHinge.DiagramAroundZStart
    DIAGRAM_AROUND_Z_START_CONTINUOUS: MemberHinge.DiagramAroundZStart
    DIAGRAM_AROUND_Z_START_STOP: MemberHinge.DiagramAroundZStart
    DIAGRAM_AROUND_Z_START_YIELDING: MemberHinge.DiagramAroundZStart
    class DiagramAlongXEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_X_END_FAILURE: _ClassVar[MemberHinge.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_CONTINUOUS: _ClassVar[MemberHinge.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_STOP: _ClassVar[MemberHinge.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_YIELDING: _ClassVar[MemberHinge.DiagramAlongXEnd]
    DIAGRAM_ALONG_X_END_FAILURE: MemberHinge.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_CONTINUOUS: MemberHinge.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_STOP: MemberHinge.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_YIELDING: MemberHinge.DiagramAlongXEnd
    class DiagramAlongYEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Y_END_FAILURE: _ClassVar[MemberHinge.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_CONTINUOUS: _ClassVar[MemberHinge.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_STOP: _ClassVar[MemberHinge.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_YIELDING: _ClassVar[MemberHinge.DiagramAlongYEnd]
    DIAGRAM_ALONG_Y_END_FAILURE: MemberHinge.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_CONTINUOUS: MemberHinge.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_STOP: MemberHinge.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_YIELDING: MemberHinge.DiagramAlongYEnd
    class DiagramAlongZEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Z_END_FAILURE: _ClassVar[MemberHinge.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_CONTINUOUS: _ClassVar[MemberHinge.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_STOP: _ClassVar[MemberHinge.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_YIELDING: _ClassVar[MemberHinge.DiagramAlongZEnd]
    DIAGRAM_ALONG_Z_END_FAILURE: MemberHinge.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_CONTINUOUS: MemberHinge.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_STOP: MemberHinge.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_YIELDING: MemberHinge.DiagramAlongZEnd
    class DiagramAroundXEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_X_END_FAILURE: _ClassVar[MemberHinge.DiagramAroundXEnd]
        DIAGRAM_AROUND_X_END_CONTINUOUS: _ClassVar[MemberHinge.DiagramAroundXEnd]
        DIAGRAM_AROUND_X_END_STOP: _ClassVar[MemberHinge.DiagramAroundXEnd]
        DIAGRAM_AROUND_X_END_YIELDING: _ClassVar[MemberHinge.DiagramAroundXEnd]
    DIAGRAM_AROUND_X_END_FAILURE: MemberHinge.DiagramAroundXEnd
    DIAGRAM_AROUND_X_END_CONTINUOUS: MemberHinge.DiagramAroundXEnd
    DIAGRAM_AROUND_X_END_STOP: MemberHinge.DiagramAroundXEnd
    DIAGRAM_AROUND_X_END_YIELDING: MemberHinge.DiagramAroundXEnd
    class DiagramAroundYEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_Y_END_FAILURE: _ClassVar[MemberHinge.DiagramAroundYEnd]
        DIAGRAM_AROUND_Y_END_CONTINUOUS: _ClassVar[MemberHinge.DiagramAroundYEnd]
        DIAGRAM_AROUND_Y_END_STOP: _ClassVar[MemberHinge.DiagramAroundYEnd]
        DIAGRAM_AROUND_Y_END_YIELDING: _ClassVar[MemberHinge.DiagramAroundYEnd]
    DIAGRAM_AROUND_Y_END_FAILURE: MemberHinge.DiagramAroundYEnd
    DIAGRAM_AROUND_Y_END_CONTINUOUS: MemberHinge.DiagramAroundYEnd
    DIAGRAM_AROUND_Y_END_STOP: MemberHinge.DiagramAroundYEnd
    DIAGRAM_AROUND_Y_END_YIELDING: MemberHinge.DiagramAroundYEnd
    class DiagramAroundZEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_AROUND_Z_END_FAILURE: _ClassVar[MemberHinge.DiagramAroundZEnd]
        DIAGRAM_AROUND_Z_END_CONTINUOUS: _ClassVar[MemberHinge.DiagramAroundZEnd]
        DIAGRAM_AROUND_Z_END_STOP: _ClassVar[MemberHinge.DiagramAroundZEnd]
        DIAGRAM_AROUND_Z_END_YIELDING: _ClassVar[MemberHinge.DiagramAroundZEnd]
    DIAGRAM_AROUND_Z_END_FAILURE: MemberHinge.DiagramAroundZEnd
    DIAGRAM_AROUND_Z_END_CONTINUOUS: MemberHinge.DiagramAroundZEnd
    DIAGRAM_AROUND_Z_END_STOP: MemberHinge.DiagramAroundZEnd
    DIAGRAM_AROUND_Z_END_YIELDING: MemberHinge.DiagramAroundZEnd
    class PlasticDiagramAlongXComponentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PLASTIC_DIAGRAM_ALONG_X_COMPONENT_TYPE_PRIMARY: _ClassVar[MemberHinge.PlasticDiagramAlongXComponentType]
        PLASTIC_DIAGRAM_ALONG_X_COMPONENT_TYPE_SECONDARY: _ClassVar[MemberHinge.PlasticDiagramAlongXComponentType]
    PLASTIC_DIAGRAM_ALONG_X_COMPONENT_TYPE_PRIMARY: MemberHinge.PlasticDiagramAlongXComponentType
    PLASTIC_DIAGRAM_ALONG_X_COMPONENT_TYPE_SECONDARY: MemberHinge.PlasticDiagramAlongXComponentType
    class PlasticDiagramAlongYComponentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PLASTIC_DIAGRAM_ALONG_Y_COMPONENT_TYPE_PRIMARY: _ClassVar[MemberHinge.PlasticDiagramAlongYComponentType]
        PLASTIC_DIAGRAM_ALONG_Y_COMPONENT_TYPE_SECONDARY: _ClassVar[MemberHinge.PlasticDiagramAlongYComponentType]
    PLASTIC_DIAGRAM_ALONG_Y_COMPONENT_TYPE_PRIMARY: MemberHinge.PlasticDiagramAlongYComponentType
    PLASTIC_DIAGRAM_ALONG_Y_COMPONENT_TYPE_SECONDARY: MemberHinge.PlasticDiagramAlongYComponentType
    class PlasticDiagramAlongZComponentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PLASTIC_DIAGRAM_ALONG_Z_COMPONENT_TYPE_PRIMARY: _ClassVar[MemberHinge.PlasticDiagramAlongZComponentType]
        PLASTIC_DIAGRAM_ALONG_Z_COMPONENT_TYPE_SECONDARY: _ClassVar[MemberHinge.PlasticDiagramAlongZComponentType]
    PLASTIC_DIAGRAM_ALONG_Z_COMPONENT_TYPE_PRIMARY: MemberHinge.PlasticDiagramAlongZComponentType
    PLASTIC_DIAGRAM_ALONG_Z_COMPONENT_TYPE_SECONDARY: MemberHinge.PlasticDiagramAlongZComponentType
    class PlasticDiagramAroundYComponentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PLASTIC_DIAGRAM_AROUND_Y_COMPONENT_TYPE_PRIMARY: _ClassVar[MemberHinge.PlasticDiagramAroundYComponentType]
        PLASTIC_DIAGRAM_AROUND_Y_COMPONENT_TYPE_SECONDARY: _ClassVar[MemberHinge.PlasticDiagramAroundYComponentType]
    PLASTIC_DIAGRAM_AROUND_Y_COMPONENT_TYPE_PRIMARY: MemberHinge.PlasticDiagramAroundYComponentType
    PLASTIC_DIAGRAM_AROUND_Y_COMPONENT_TYPE_SECONDARY: MemberHinge.PlasticDiagramAroundYComponentType
    class PlasticDiagramAroundZComponentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PLASTIC_DIAGRAM_AROUND_Z_COMPONENT_TYPE_PRIMARY: _ClassVar[MemberHinge.PlasticDiagramAroundZComponentType]
        PLASTIC_DIAGRAM_AROUND_Z_COMPONENT_TYPE_SECONDARY: _ClassVar[MemberHinge.PlasticDiagramAroundZComponentType]
    PLASTIC_DIAGRAM_AROUND_Z_COMPONENT_TYPE_PRIMARY: MemberHinge.PlasticDiagramAroundZComponentType
    PLASTIC_DIAGRAM_AROUND_Z_COMPONENT_TYPE_SECONDARY: MemberHinge.PlasticDiagramAroundZComponentType
    class DiagramAlongXTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.DiagramAlongXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.DiagramAlongXTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.DiagramAlongYTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.DiagramAlongYTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.DiagramAlongZTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.DiagramAlongZTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.DiagramAroundXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.DiagramAroundXTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.DiagramAroundYTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.DiagramAroundYTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.DiagramAroundZTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.DiagramAroundZTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.DiagramAlongXColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.DiagramAlongXColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.DiagramAlongYColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.DiagramAlongYColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.DiagramAlongZColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.DiagramAlongZColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.DiagramAroundXColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.DiagramAroundXColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.DiagramAroundYColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.DiagramAroundYColorTableRow, _Mapping]]] = ...) -> None: ...
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
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.DiagramAroundZColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.DiagramAroundZColorTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAroundZColorTableRow(_message.Message):
        __slots__ = ("no", "description", "color")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        color: _common_pb2.Color
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., color: _Optional[_Union[_common_pb2.Color, _Mapping]] = ...) -> None: ...
    class PlasticDiagramAlongXTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.PlasticDiagramAlongXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.PlasticDiagramAlongXTableRow, _Mapping]]] = ...) -> None: ...
    class PlasticDiagramAlongXTableRow(_message.Message):
        __slots__ = ("no", "description", "force_ratio", "deflection_ratio")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FORCE_RATIO_FIELD_NUMBER: _ClassVar[int]
        DEFLECTION_RATIO_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        force_ratio: float
        deflection_ratio: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., force_ratio: _Optional[float] = ..., deflection_ratio: _Optional[float] = ...) -> None: ...
    class PlasticDiagramAlongYTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.PlasticDiagramAlongYTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.PlasticDiagramAlongYTableRow, _Mapping]]] = ...) -> None: ...
    class PlasticDiagramAlongYTableRow(_message.Message):
        __slots__ = ("no", "description", "force_ratio", "deflection_ratio")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FORCE_RATIO_FIELD_NUMBER: _ClassVar[int]
        DEFLECTION_RATIO_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        force_ratio: float
        deflection_ratio: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., force_ratio: _Optional[float] = ..., deflection_ratio: _Optional[float] = ...) -> None: ...
    class PlasticDiagramAlongZTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.PlasticDiagramAlongZTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.PlasticDiagramAlongZTableRow, _Mapping]]] = ...) -> None: ...
    class PlasticDiagramAlongZTableRow(_message.Message):
        __slots__ = ("no", "description", "force_ratio", "deflection_ratio")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FORCE_RATIO_FIELD_NUMBER: _ClassVar[int]
        DEFLECTION_RATIO_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        force_ratio: float
        deflection_ratio: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., force_ratio: _Optional[float] = ..., deflection_ratio: _Optional[float] = ...) -> None: ...
    class PlasticDiagramAroundYTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.PlasticDiagramAroundYTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.PlasticDiagramAroundYTableRow, _Mapping]]] = ...) -> None: ...
    class PlasticDiagramAroundYTableRow(_message.Message):
        __slots__ = ("no", "description", "force_ratio", "deflection_ratio")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FORCE_RATIO_FIELD_NUMBER: _ClassVar[int]
        DEFLECTION_RATIO_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        force_ratio: float
        deflection_ratio: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., force_ratio: _Optional[float] = ..., deflection_ratio: _Optional[float] = ...) -> None: ...
    class PlasticDiagramAroundZTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.PlasticDiagramAroundZTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.PlasticDiagramAroundZTableRow, _Mapping]]] = ...) -> None: ...
    class PlasticDiagramAroundZTableRow(_message.Message):
        __slots__ = ("no", "description", "force_ratio", "deflection_ratio")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        FORCE_RATIO_FIELD_NUMBER: _ClassVar[int]
        DEFLECTION_RATIO_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        force_ratio: float
        deflection_ratio: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., force_ratio: _Optional[float] = ..., deflection_ratio: _Optional[float] = ...) -> None: ...
    class PlasticDiagramAlongXColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.PlasticDiagramAlongXColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.PlasticDiagramAlongXColorTableRow, _Mapping]]] = ...) -> None: ...
    class PlasticDiagramAlongXColorTableRow(_message.Message):
        __slots__ = ("no", "description", "color")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        color: _common_pb2.Color
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., color: _Optional[_Union[_common_pb2.Color, _Mapping]] = ...) -> None: ...
    class PlasticDiagramAlongYColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.PlasticDiagramAlongYColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.PlasticDiagramAlongYColorTableRow, _Mapping]]] = ...) -> None: ...
    class PlasticDiagramAlongYColorTableRow(_message.Message):
        __slots__ = ("no", "description", "color")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        color: _common_pb2.Color
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., color: _Optional[_Union[_common_pb2.Color, _Mapping]] = ...) -> None: ...
    class PlasticDiagramAlongZColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.PlasticDiagramAlongZColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.PlasticDiagramAlongZColorTableRow, _Mapping]]] = ...) -> None: ...
    class PlasticDiagramAlongZColorTableRow(_message.Message):
        __slots__ = ("no", "description", "color")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        color: _common_pb2.Color
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., color: _Optional[_Union[_common_pb2.Color, _Mapping]] = ...) -> None: ...
    class PlasticDiagramAroundYColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.PlasticDiagramAroundYColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.PlasticDiagramAroundYColorTableRow, _Mapping]]] = ...) -> None: ...
    class PlasticDiagramAroundYColorTableRow(_message.Message):
        __slots__ = ("no", "description", "color")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        color: _common_pb2.Color
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., color: _Optional[_Union[_common_pb2.Color, _Mapping]] = ...) -> None: ...
    class PlasticDiagramAroundZColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[MemberHinge.PlasticDiagramAroundZColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[MemberHinge.PlasticDiagramAroundZColorTableRow, _Mapping]]] = ...) -> None: ...
    class PlasticDiagramAroundZColorTableRow(_message.Message):
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
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    AXIAL_RELEASE_N_FIELD_NUMBER: _ClassVar[int]
    AXIAL_RELEASE_VY_FIELD_NUMBER: _ClassVar[int]
    AXIAL_RELEASE_VZ_FIELD_NUMBER: _ClassVar[int]
    MOMENT_RELEASE_MT_FIELD_NUMBER: _ClassVar[int]
    MOMENT_RELEASE_MY_FIELD_NUMBER: _ClassVar[int]
    MOMENT_RELEASE_MZ_FIELD_NUMBER: _ClassVar[int]
    AXIAL_RELEASE_N_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    AXIAL_RELEASE_VY_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    AXIAL_RELEASE_VZ_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    MOMENT_RELEASE_MT_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    MOMENT_RELEASE_MY_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    MOMENT_RELEASE_MZ_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_ROTATION_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_FORCE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_MOMENT_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_X_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Y_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_ALONG_Z_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_X_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Y_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_NEGATIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_ACTIVITY_AROUND_Z_POSITIVE_SLIPPAGE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Z_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_X_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_AROUND_Y_TABLE_FIELD_NUMBER: _ClassVar[int]
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
    PLASTIC_DIAGRAM_ALONG_X_TABLE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_TABLE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_TABLE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_TABLE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_TABLE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_FORCE_INTERACTION_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_FORCE_INTERACTION_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_USER_DEFINED_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_USER_DEFINED_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_USER_DEFINED_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_USER_DEFINED_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_USER_DEFINED_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_IS_USER_DEFINED_MEMBER_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_IS_USER_DEFINED_MEMBER_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_IS_USER_DEFINED_MEMBER_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_IS_USER_DEFINED_MEMBER_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_IS_USER_DEFINED_MEMBER_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_USER_DEFINED_MEMBER_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_USER_DEFINED_MEMBER_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_USER_DEFINED_MEMBER_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_USER_DEFINED_MEMBER_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_USER_DEFINED_MEMBER_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_ATTACHED_MEMBERS_MIN_MAX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_ATTACHED_MEMBERS_MIN_MAX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_ATTACHED_MEMBERS_MIN_MAX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_ATTACHED_MEMBERS_MIN_MAX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_ATTACHED_MEMBERS_MIN_MAX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_IO_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_IO_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_IO_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_IO_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_IO_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_IO_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_IO_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_IO_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_IO_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_IO_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_LS_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_LS_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_LS_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_LS_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_LS_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_LS_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_LS_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_LS_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_LS_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_LS_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_CP_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_CP_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_CP_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_CP_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_CP_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_CP_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_CP_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_CP_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_CP_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_CP_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_MINUS_COLOR_THREE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_MINUS_COLOR_THREE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_MINUS_COLOR_THREE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_MINUS_COLOR_THREE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_MINUS_COLOR_THREE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_MINUS_COLOR_FOUR_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_MINUS_COLOR_FOUR_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_MINUS_COLOR_FOUR_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_MINUS_COLOR_FOUR_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_MINUS_COLOR_FOUR_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_PLUS_COLOR_THREE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_PLUS_COLOR_THREE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_PLUS_COLOR_THREE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_PLUS_COLOR_THREE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_PLUS_COLOR_THREE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_PLUS_COLOR_FOUR_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_PLUS_COLOR_FOUR_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_PLUS_COLOR_FOUR_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_PLUS_COLOR_FOUR_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_PLUS_COLOR_FOUR_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_COMPONENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_COMPONENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_COMPONENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_COMPONENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_COMPONENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_X_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Y_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_ALONG_Z_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Y_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_DIAGRAM_AROUND_Z_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
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
    SPECIAL_TYPE_OF_HINGE_DIRECTION_ALONG_X_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_TYPE_OF_HINGE_DIRECTION_ALONG_Y_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_TYPE_OF_HINGE_DIRECTION_ALONG_Z_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_TYPE_OF_HINGE_DIRECTION_AROUND_X_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_TYPE_OF_HINGE_DIRECTION_AROUND_Y_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_TYPE_OF_HINGE_DIRECTION_AROUND_Z_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_TYPE_OF_HINGE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    members: str
    coordinate_system: _common_pb2.CoordinateSystemRepresentation
    axial_release_n: float
    axial_release_vy: float
    axial_release_vz: float
    moment_release_mt: float
    moment_release_my: float
    moment_release_mz: float
    axial_release_n_nonlinearity: MemberHinge.AxialReleaseNNonlinearity
    axial_release_vy_nonlinearity: MemberHinge.AxialReleaseVyNonlinearity
    axial_release_vz_nonlinearity: MemberHinge.AxialReleaseVzNonlinearity
    moment_release_mt_nonlinearity: MemberHinge.MomentReleaseMtNonlinearity
    moment_release_my_nonlinearity: MemberHinge.MomentReleaseMyNonlinearity
    moment_release_mz_nonlinearity: MemberHinge.MomentReleaseMzNonlinearity
    partial_activity_along_x_negative_type: MemberHinge.PartialActivityAlongXNegativeType
    partial_activity_along_x_positive_type: MemberHinge.PartialActivityAlongXPositiveType
    partial_activity_along_y_negative_type: MemberHinge.PartialActivityAlongYNegativeType
    partial_activity_along_y_positive_type: MemberHinge.PartialActivityAlongYPositiveType
    partial_activity_along_z_negative_type: MemberHinge.PartialActivityAlongZNegativeType
    partial_activity_along_z_positive_type: MemberHinge.PartialActivityAlongZPositiveType
    partial_activity_around_x_negative_type: MemberHinge.PartialActivityAroundXNegativeType
    partial_activity_around_x_positive_type: MemberHinge.PartialActivityAroundXPositiveType
    partial_activity_around_y_negative_type: MemberHinge.PartialActivityAroundYNegativeType
    partial_activity_around_y_positive_type: MemberHinge.PartialActivityAroundYPositiveType
    partial_activity_around_z_negative_type: MemberHinge.PartialActivityAroundZNegativeType
    partial_activity_around_z_positive_type: MemberHinge.PartialActivityAroundZPositiveType
    partial_activity_along_x_negative_displacement: float
    partial_activity_along_x_positive_displacement: float
    partial_activity_along_y_negative_displacement: float
    partial_activity_along_y_positive_displacement: float
    partial_activity_along_z_negative_displacement: float
    partial_activity_along_z_positive_displacement: float
    partial_activity_around_x_negative_rotation: float
    partial_activity_around_x_positive_rotation: float
    partial_activity_around_y_negative_rotation: float
    partial_activity_around_y_positive_rotation: float
    partial_activity_around_z_negative_rotation: float
    partial_activity_around_z_positive_rotation: float
    partial_activity_along_x_negative_force: float
    partial_activity_along_x_positive_force: float
    partial_activity_along_y_negative_force: float
    partial_activity_along_y_positive_force: float
    partial_activity_along_z_negative_force: float
    partial_activity_along_z_positive_force: float
    partial_activity_around_x_negative_moment: float
    partial_activity_around_x_positive_moment: float
    partial_activity_around_y_negative_moment: float
    partial_activity_around_y_positive_moment: float
    partial_activity_around_z_negative_moment: float
    partial_activity_around_z_positive_moment: float
    partial_activity_along_x_negative_slippage: float
    partial_activity_along_x_positive_slippage: float
    partial_activity_along_y_negative_slippage: float
    partial_activity_along_y_positive_slippage: float
    partial_activity_along_z_negative_slippage: float
    partial_activity_along_z_positive_slippage: float
    partial_activity_around_x_negative_slippage: float
    partial_activity_around_x_positive_slippage: float
    partial_activity_around_y_negative_slippage: float
    partial_activity_around_y_positive_slippage: float
    partial_activity_around_z_negative_slippage: float
    partial_activity_around_z_positive_slippage: float
    diagram_along_x_symmetric: bool
    diagram_along_y_symmetric: bool
    diagram_along_z_symmetric: bool
    diagram_around_x_symmetric: bool
    diagram_around_y_symmetric: bool
    diagram_around_z_symmetric: bool
    diagram_along_x_is_sorted: bool
    diagram_along_y_is_sorted: bool
    diagram_along_z_is_sorted: bool
    diagram_around_x_is_sorted: bool
    diagram_around_y_is_sorted: bool
    diagram_around_z_is_sorted: bool
    diagram_along_x_start: MemberHinge.DiagramAlongXStart
    diagram_along_y_start: MemberHinge.DiagramAlongYStart
    diagram_along_z_start: MemberHinge.DiagramAlongZStart
    diagram_around_x_start: MemberHinge.DiagramAroundXStart
    diagram_around_y_start: MemberHinge.DiagramAroundYStart
    diagram_around_z_start: MemberHinge.DiagramAroundZStart
    diagram_along_x_end: MemberHinge.DiagramAlongXEnd
    diagram_along_y_end: MemberHinge.DiagramAlongYEnd
    diagram_along_z_end: MemberHinge.DiagramAlongZEnd
    diagram_around_x_end: MemberHinge.DiagramAroundXEnd
    diagram_around_y_end: MemberHinge.DiagramAroundYEnd
    diagram_around_z_end: MemberHinge.DiagramAroundZEnd
    diagram_along_x_table: MemberHinge.DiagramAlongXTable
    diagram_along_y_table: MemberHinge.DiagramAlongYTable
    diagram_along_z_table: MemberHinge.DiagramAlongZTable
    diagram_around_x_table: MemberHinge.DiagramAroundXTable
    diagram_around_y_table: MemberHinge.DiagramAroundYTable
    diagram_around_z_table: MemberHinge.DiagramAroundZTable
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
    diagram_along_x_color_table: MemberHinge.DiagramAlongXColorTable
    diagram_along_y_color_table: MemberHinge.DiagramAlongYColorTable
    diagram_along_z_color_table: MemberHinge.DiagramAlongZColorTable
    diagram_around_x_color_table: MemberHinge.DiagramAroundXColorTable
    diagram_around_y_color_table: MemberHinge.DiagramAroundYColorTable
    diagram_around_z_color_table: MemberHinge.DiagramAroundZColorTable
    plastic_diagram_along_x_table: MemberHinge.PlasticDiagramAlongXTable
    plastic_diagram_along_y_table: MemberHinge.PlasticDiagramAlongYTable
    plastic_diagram_along_z_table: MemberHinge.PlasticDiagramAlongZTable
    plastic_diagram_around_y_table: MemberHinge.PlasticDiagramAroundYTable
    plastic_diagram_around_z_table: MemberHinge.PlasticDiagramAroundZTable
    plastic_diagram_along_x_symmetric: bool
    plastic_diagram_along_y_symmetric: bool
    plastic_diagram_along_z_symmetric: bool
    plastic_diagram_around_y_symmetric: bool
    plastic_diagram_around_z_symmetric: bool
    plastic_diagram_around_y_force_interaction: bool
    plastic_diagram_around_z_force_interaction: bool
    plastic_diagram_along_x_user_defined: bool
    plastic_diagram_along_y_user_defined: bool
    plastic_diagram_along_z_user_defined: bool
    plastic_diagram_around_y_user_defined: bool
    plastic_diagram_around_z_user_defined: bool
    plastic_diagram_along_x_is_user_defined_member_length: bool
    plastic_diagram_along_y_is_user_defined_member_length: bool
    plastic_diagram_along_z_is_user_defined_member_length: bool
    plastic_diagram_around_y_is_user_defined_member_length: bool
    plastic_diagram_around_z_is_user_defined_member_length: bool
    plastic_diagram_along_x_user_defined_member_length: float
    plastic_diagram_along_y_user_defined_member_length: float
    plastic_diagram_along_z_user_defined_member_length: float
    plastic_diagram_around_y_user_defined_member_length: float
    plastic_diagram_around_z_user_defined_member_length: float
    plastic_diagram_along_x_attached_members_min_max_length: str
    plastic_diagram_along_y_attached_members_min_max_length: str
    plastic_diagram_along_z_attached_members_min_max_length: str
    plastic_diagram_around_y_attached_members_min_max_length: str
    plastic_diagram_around_z_attached_members_min_max_length: str
    plastic_diagram_along_x_io_negative: float
    plastic_diagram_along_y_io_negative: float
    plastic_diagram_along_z_io_negative: float
    plastic_diagram_around_y_io_negative: float
    plastic_diagram_around_z_io_negative: float
    plastic_diagram_along_x_io_positive: float
    plastic_diagram_along_y_io_positive: float
    plastic_diagram_along_z_io_positive: float
    plastic_diagram_around_y_io_positive: float
    plastic_diagram_around_z_io_positive: float
    plastic_diagram_along_x_ls_negative: float
    plastic_diagram_along_y_ls_negative: float
    plastic_diagram_along_z_ls_negative: float
    plastic_diagram_around_y_ls_negative: float
    plastic_diagram_around_z_ls_negative: float
    plastic_diagram_along_x_ls_positive: float
    plastic_diagram_along_y_ls_positive: float
    plastic_diagram_along_z_ls_positive: float
    plastic_diagram_around_y_ls_positive: float
    plastic_diagram_around_z_ls_positive: float
    plastic_diagram_along_x_cp_negative: float
    plastic_diagram_along_y_cp_negative: float
    plastic_diagram_along_z_cp_negative: float
    plastic_diagram_around_y_cp_negative: float
    plastic_diagram_around_z_cp_negative: float
    plastic_diagram_along_x_cp_positive: float
    plastic_diagram_along_y_cp_positive: float
    plastic_diagram_along_z_cp_positive: float
    plastic_diagram_around_y_cp_positive: float
    plastic_diagram_around_z_cp_positive: float
    plastic_diagram_along_x_minus_color_one: _common_pb2.Color
    plastic_diagram_along_y_minus_color_one: _common_pb2.Color
    plastic_diagram_along_z_minus_color_one: _common_pb2.Color
    plastic_diagram_around_y_minus_color_one: _common_pb2.Color
    plastic_diagram_around_z_minus_color_one: _common_pb2.Color
    plastic_diagram_along_x_minus_color_two: _common_pb2.Color
    plastic_diagram_along_y_minus_color_two: _common_pb2.Color
    plastic_diagram_along_z_minus_color_two: _common_pb2.Color
    plastic_diagram_around_y_minus_color_two: _common_pb2.Color
    plastic_diagram_around_z_minus_color_two: _common_pb2.Color
    plastic_diagram_along_x_minus_color_three: _common_pb2.Color
    plastic_diagram_along_y_minus_color_three: _common_pb2.Color
    plastic_diagram_along_z_minus_color_three: _common_pb2.Color
    plastic_diagram_around_y_minus_color_three: _common_pb2.Color
    plastic_diagram_around_z_minus_color_three: _common_pb2.Color
    plastic_diagram_along_x_minus_color_four: _common_pb2.Color
    plastic_diagram_along_y_minus_color_four: _common_pb2.Color
    plastic_diagram_along_z_minus_color_four: _common_pb2.Color
    plastic_diagram_around_y_minus_color_four: _common_pb2.Color
    plastic_diagram_around_z_minus_color_four: _common_pb2.Color
    plastic_diagram_along_x_plus_color_one: _common_pb2.Color
    plastic_diagram_along_y_plus_color_one: _common_pb2.Color
    plastic_diagram_along_z_plus_color_one: _common_pb2.Color
    plastic_diagram_around_y_plus_color_one: _common_pb2.Color
    plastic_diagram_around_z_plus_color_one: _common_pb2.Color
    plastic_diagram_along_x_plus_color_two: _common_pb2.Color
    plastic_diagram_along_y_plus_color_two: _common_pb2.Color
    plastic_diagram_along_z_plus_color_two: _common_pb2.Color
    plastic_diagram_around_y_plus_color_two: _common_pb2.Color
    plastic_diagram_around_z_plus_color_two: _common_pb2.Color
    plastic_diagram_along_x_plus_color_three: _common_pb2.Color
    plastic_diagram_along_y_plus_color_three: _common_pb2.Color
    plastic_diagram_along_z_plus_color_three: _common_pb2.Color
    plastic_diagram_around_y_plus_color_three: _common_pb2.Color
    plastic_diagram_around_z_plus_color_three: _common_pb2.Color
    plastic_diagram_along_x_plus_color_four: _common_pb2.Color
    plastic_diagram_along_y_plus_color_four: _common_pb2.Color
    plastic_diagram_along_z_plus_color_four: _common_pb2.Color
    plastic_diagram_around_y_plus_color_four: _common_pb2.Color
    plastic_diagram_around_z_plus_color_four: _common_pb2.Color
    plastic_diagram_along_x_component_type: MemberHinge.PlasticDiagramAlongXComponentType
    plastic_diagram_along_y_component_type: MemberHinge.PlasticDiagramAlongYComponentType
    plastic_diagram_along_z_component_type: MemberHinge.PlasticDiagramAlongZComponentType
    plastic_diagram_around_y_component_type: MemberHinge.PlasticDiagramAroundYComponentType
    plastic_diagram_around_z_component_type: MemberHinge.PlasticDiagramAroundZComponentType
    plastic_diagram_along_x_color_table: MemberHinge.PlasticDiagramAlongXColorTable
    plastic_diagram_along_y_color_table: MemberHinge.PlasticDiagramAlongYColorTable
    plastic_diagram_along_z_color_table: MemberHinge.PlasticDiagramAlongZColorTable
    plastic_diagram_around_y_color_table: MemberHinge.PlasticDiagramAroundYColorTable
    plastic_diagram_around_z_color_table: MemberHinge.PlasticDiagramAroundZColorTable
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
    special_type_of_hinge_direction_along_x: bool
    special_type_of_hinge_direction_along_y: bool
    special_type_of_hinge_direction_along_z: bool
    special_type_of_hinge_direction_around_x: bool
    special_type_of_hinge_direction_around_y: bool
    special_type_of_hinge_direction_around_z: bool
    special_type_of_hinge_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., members: _Optional[str] = ..., coordinate_system: _Optional[_Union[_common_pb2.CoordinateSystemRepresentation, _Mapping]] = ..., axial_release_n: _Optional[float] = ..., axial_release_vy: _Optional[float] = ..., axial_release_vz: _Optional[float] = ..., moment_release_mt: _Optional[float] = ..., moment_release_my: _Optional[float] = ..., moment_release_mz: _Optional[float] = ..., axial_release_n_nonlinearity: _Optional[_Union[MemberHinge.AxialReleaseNNonlinearity, str]] = ..., axial_release_vy_nonlinearity: _Optional[_Union[MemberHinge.AxialReleaseVyNonlinearity, str]] = ..., axial_release_vz_nonlinearity: _Optional[_Union[MemberHinge.AxialReleaseVzNonlinearity, str]] = ..., moment_release_mt_nonlinearity: _Optional[_Union[MemberHinge.MomentReleaseMtNonlinearity, str]] = ..., moment_release_my_nonlinearity: _Optional[_Union[MemberHinge.MomentReleaseMyNonlinearity, str]] = ..., moment_release_mz_nonlinearity: _Optional[_Union[MemberHinge.MomentReleaseMzNonlinearity, str]] = ..., partial_activity_along_x_negative_type: _Optional[_Union[MemberHinge.PartialActivityAlongXNegativeType, str]] = ..., partial_activity_along_x_positive_type: _Optional[_Union[MemberHinge.PartialActivityAlongXPositiveType, str]] = ..., partial_activity_along_y_negative_type: _Optional[_Union[MemberHinge.PartialActivityAlongYNegativeType, str]] = ..., partial_activity_along_y_positive_type: _Optional[_Union[MemberHinge.PartialActivityAlongYPositiveType, str]] = ..., partial_activity_along_z_negative_type: _Optional[_Union[MemberHinge.PartialActivityAlongZNegativeType, str]] = ..., partial_activity_along_z_positive_type: _Optional[_Union[MemberHinge.PartialActivityAlongZPositiveType, str]] = ..., partial_activity_around_x_negative_type: _Optional[_Union[MemberHinge.PartialActivityAroundXNegativeType, str]] = ..., partial_activity_around_x_positive_type: _Optional[_Union[MemberHinge.PartialActivityAroundXPositiveType, str]] = ..., partial_activity_around_y_negative_type: _Optional[_Union[MemberHinge.PartialActivityAroundYNegativeType, str]] = ..., partial_activity_around_y_positive_type: _Optional[_Union[MemberHinge.PartialActivityAroundYPositiveType, str]] = ..., partial_activity_around_z_negative_type: _Optional[_Union[MemberHinge.PartialActivityAroundZNegativeType, str]] = ..., partial_activity_around_z_positive_type: _Optional[_Union[MemberHinge.PartialActivityAroundZPositiveType, str]] = ..., partial_activity_along_x_negative_displacement: _Optional[float] = ..., partial_activity_along_x_positive_displacement: _Optional[float] = ..., partial_activity_along_y_negative_displacement: _Optional[float] = ..., partial_activity_along_y_positive_displacement: _Optional[float] = ..., partial_activity_along_z_negative_displacement: _Optional[float] = ..., partial_activity_along_z_positive_displacement: _Optional[float] = ..., partial_activity_around_x_negative_rotation: _Optional[float] = ..., partial_activity_around_x_positive_rotation: _Optional[float] = ..., partial_activity_around_y_negative_rotation: _Optional[float] = ..., partial_activity_around_y_positive_rotation: _Optional[float] = ..., partial_activity_around_z_negative_rotation: _Optional[float] = ..., partial_activity_around_z_positive_rotation: _Optional[float] = ..., partial_activity_along_x_negative_force: _Optional[float] = ..., partial_activity_along_x_positive_force: _Optional[float] = ..., partial_activity_along_y_negative_force: _Optional[float] = ..., partial_activity_along_y_positive_force: _Optional[float] = ..., partial_activity_along_z_negative_force: _Optional[float] = ..., partial_activity_along_z_positive_force: _Optional[float] = ..., partial_activity_around_x_negative_moment: _Optional[float] = ..., partial_activity_around_x_positive_moment: _Optional[float] = ..., partial_activity_around_y_negative_moment: _Optional[float] = ..., partial_activity_around_y_positive_moment: _Optional[float] = ..., partial_activity_around_z_negative_moment: _Optional[float] = ..., partial_activity_around_z_positive_moment: _Optional[float] = ..., partial_activity_along_x_negative_slippage: _Optional[float] = ..., partial_activity_along_x_positive_slippage: _Optional[float] = ..., partial_activity_along_y_negative_slippage: _Optional[float] = ..., partial_activity_along_y_positive_slippage: _Optional[float] = ..., partial_activity_along_z_negative_slippage: _Optional[float] = ..., partial_activity_along_z_positive_slippage: _Optional[float] = ..., partial_activity_around_x_negative_slippage: _Optional[float] = ..., partial_activity_around_x_positive_slippage: _Optional[float] = ..., partial_activity_around_y_negative_slippage: _Optional[float] = ..., partial_activity_around_y_positive_slippage: _Optional[float] = ..., partial_activity_around_z_negative_slippage: _Optional[float] = ..., partial_activity_around_z_positive_slippage: _Optional[float] = ..., diagram_along_x_symmetric: bool = ..., diagram_along_y_symmetric: bool = ..., diagram_along_z_symmetric: bool = ..., diagram_around_x_symmetric: bool = ..., diagram_around_y_symmetric: bool = ..., diagram_around_z_symmetric: bool = ..., diagram_along_x_is_sorted: bool = ..., diagram_along_y_is_sorted: bool = ..., diagram_along_z_is_sorted: bool = ..., diagram_around_x_is_sorted: bool = ..., diagram_around_y_is_sorted: bool = ..., diagram_around_z_is_sorted: bool = ..., diagram_along_x_start: _Optional[_Union[MemberHinge.DiagramAlongXStart, str]] = ..., diagram_along_y_start: _Optional[_Union[MemberHinge.DiagramAlongYStart, str]] = ..., diagram_along_z_start: _Optional[_Union[MemberHinge.DiagramAlongZStart, str]] = ..., diagram_around_x_start: _Optional[_Union[MemberHinge.DiagramAroundXStart, str]] = ..., diagram_around_y_start: _Optional[_Union[MemberHinge.DiagramAroundYStart, str]] = ..., diagram_around_z_start: _Optional[_Union[MemberHinge.DiagramAroundZStart, str]] = ..., diagram_along_x_end: _Optional[_Union[MemberHinge.DiagramAlongXEnd, str]] = ..., diagram_along_y_end: _Optional[_Union[MemberHinge.DiagramAlongYEnd, str]] = ..., diagram_along_z_end: _Optional[_Union[MemberHinge.DiagramAlongZEnd, str]] = ..., diagram_around_x_end: _Optional[_Union[MemberHinge.DiagramAroundXEnd, str]] = ..., diagram_around_y_end: _Optional[_Union[MemberHinge.DiagramAroundYEnd, str]] = ..., diagram_around_z_end: _Optional[_Union[MemberHinge.DiagramAroundZEnd, str]] = ..., diagram_along_x_table: _Optional[_Union[MemberHinge.DiagramAlongXTable, _Mapping]] = ..., diagram_along_y_table: _Optional[_Union[MemberHinge.DiagramAlongYTable, _Mapping]] = ..., diagram_along_z_table: _Optional[_Union[MemberHinge.DiagramAlongZTable, _Mapping]] = ..., diagram_around_x_table: _Optional[_Union[MemberHinge.DiagramAroundXTable, _Mapping]] = ..., diagram_around_y_table: _Optional[_Union[MemberHinge.DiagramAroundYTable, _Mapping]] = ..., diagram_around_z_table: _Optional[_Union[MemberHinge.DiagramAroundZTable, _Mapping]] = ..., diagram_along_x_ac_yield_minus: _Optional[float] = ..., diagram_along_y_ac_yield_minus: _Optional[float] = ..., diagram_along_z_ac_yield_minus: _Optional[float] = ..., diagram_around_x_ac_yield_minus: _Optional[float] = ..., diagram_around_y_ac_yield_minus: _Optional[float] = ..., diagram_around_z_ac_yield_minus: _Optional[float] = ..., diagram_along_x_ac_yield_plus: _Optional[float] = ..., diagram_along_y_ac_yield_plus: _Optional[float] = ..., diagram_along_z_ac_yield_plus: _Optional[float] = ..., diagram_around_x_ac_yield_plus: _Optional[float] = ..., diagram_around_y_ac_yield_plus: _Optional[float] = ..., diagram_around_z_ac_yield_plus: _Optional[float] = ..., diagram_along_x_acceptance_criteria_active: bool = ..., diagram_along_y_acceptance_criteria_active: bool = ..., diagram_along_z_acceptance_criteria_active: bool = ..., diagram_around_x_acceptance_criteria_active: bool = ..., diagram_around_y_acceptance_criteria_active: bool = ..., diagram_around_z_acceptance_criteria_active: bool = ..., diagram_along_x_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_y_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_z_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_y_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_z_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_y_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_z_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_x_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_y_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_around_z_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_color_table: _Optional[_Union[MemberHinge.DiagramAlongXColorTable, _Mapping]] = ..., diagram_along_y_color_table: _Optional[_Union[MemberHinge.DiagramAlongYColorTable, _Mapping]] = ..., diagram_along_z_color_table: _Optional[_Union[MemberHinge.DiagramAlongZColorTable, _Mapping]] = ..., diagram_around_x_color_table: _Optional[_Union[MemberHinge.DiagramAroundXColorTable, _Mapping]] = ..., diagram_around_y_color_table: _Optional[_Union[MemberHinge.DiagramAroundYColorTable, _Mapping]] = ..., diagram_around_z_color_table: _Optional[_Union[MemberHinge.DiagramAroundZColorTable, _Mapping]] = ..., plastic_diagram_along_x_table: _Optional[_Union[MemberHinge.PlasticDiagramAlongXTable, _Mapping]] = ..., plastic_diagram_along_y_table: _Optional[_Union[MemberHinge.PlasticDiagramAlongYTable, _Mapping]] = ..., plastic_diagram_along_z_table: _Optional[_Union[MemberHinge.PlasticDiagramAlongZTable, _Mapping]] = ..., plastic_diagram_around_y_table: _Optional[_Union[MemberHinge.PlasticDiagramAroundYTable, _Mapping]] = ..., plastic_diagram_around_z_table: _Optional[_Union[MemberHinge.PlasticDiagramAroundZTable, _Mapping]] = ..., plastic_diagram_along_x_symmetric: bool = ..., plastic_diagram_along_y_symmetric: bool = ..., plastic_diagram_along_z_symmetric: bool = ..., plastic_diagram_around_y_symmetric: bool = ..., plastic_diagram_around_z_symmetric: bool = ..., plastic_diagram_around_y_force_interaction: bool = ..., plastic_diagram_around_z_force_interaction: bool = ..., plastic_diagram_along_x_user_defined: bool = ..., plastic_diagram_along_y_user_defined: bool = ..., plastic_diagram_along_z_user_defined: bool = ..., plastic_diagram_around_y_user_defined: bool = ..., plastic_diagram_around_z_user_defined: bool = ..., plastic_diagram_along_x_is_user_defined_member_length: bool = ..., plastic_diagram_along_y_is_user_defined_member_length: bool = ..., plastic_diagram_along_z_is_user_defined_member_length: bool = ..., plastic_diagram_around_y_is_user_defined_member_length: bool = ..., plastic_diagram_around_z_is_user_defined_member_length: bool = ..., plastic_diagram_along_x_user_defined_member_length: _Optional[float] = ..., plastic_diagram_along_y_user_defined_member_length: _Optional[float] = ..., plastic_diagram_along_z_user_defined_member_length: _Optional[float] = ..., plastic_diagram_around_y_user_defined_member_length: _Optional[float] = ..., plastic_diagram_around_z_user_defined_member_length: _Optional[float] = ..., plastic_diagram_along_x_attached_members_min_max_length: _Optional[str] = ..., plastic_diagram_along_y_attached_members_min_max_length: _Optional[str] = ..., plastic_diagram_along_z_attached_members_min_max_length: _Optional[str] = ..., plastic_diagram_around_y_attached_members_min_max_length: _Optional[str] = ..., plastic_diagram_around_z_attached_members_min_max_length: _Optional[str] = ..., plastic_diagram_along_x_io_negative: _Optional[float] = ..., plastic_diagram_along_y_io_negative: _Optional[float] = ..., plastic_diagram_along_z_io_negative: _Optional[float] = ..., plastic_diagram_around_y_io_negative: _Optional[float] = ..., plastic_diagram_around_z_io_negative: _Optional[float] = ..., plastic_diagram_along_x_io_positive: _Optional[float] = ..., plastic_diagram_along_y_io_positive: _Optional[float] = ..., plastic_diagram_along_z_io_positive: _Optional[float] = ..., plastic_diagram_around_y_io_positive: _Optional[float] = ..., plastic_diagram_around_z_io_positive: _Optional[float] = ..., plastic_diagram_along_x_ls_negative: _Optional[float] = ..., plastic_diagram_along_y_ls_negative: _Optional[float] = ..., plastic_diagram_along_z_ls_negative: _Optional[float] = ..., plastic_diagram_around_y_ls_negative: _Optional[float] = ..., plastic_diagram_around_z_ls_negative: _Optional[float] = ..., plastic_diagram_along_x_ls_positive: _Optional[float] = ..., plastic_diagram_along_y_ls_positive: _Optional[float] = ..., plastic_diagram_along_z_ls_positive: _Optional[float] = ..., plastic_diagram_around_y_ls_positive: _Optional[float] = ..., plastic_diagram_around_z_ls_positive: _Optional[float] = ..., plastic_diagram_along_x_cp_negative: _Optional[float] = ..., plastic_diagram_along_y_cp_negative: _Optional[float] = ..., plastic_diagram_along_z_cp_negative: _Optional[float] = ..., plastic_diagram_around_y_cp_negative: _Optional[float] = ..., plastic_diagram_around_z_cp_negative: _Optional[float] = ..., plastic_diagram_along_x_cp_positive: _Optional[float] = ..., plastic_diagram_along_y_cp_positive: _Optional[float] = ..., plastic_diagram_along_z_cp_positive: _Optional[float] = ..., plastic_diagram_around_y_cp_positive: _Optional[float] = ..., plastic_diagram_around_z_cp_positive: _Optional[float] = ..., plastic_diagram_along_x_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_y_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_z_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_y_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_z_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_x_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_y_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_z_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_y_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_z_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_x_minus_color_three: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_y_minus_color_three: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_z_minus_color_three: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_y_minus_color_three: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_z_minus_color_three: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_x_minus_color_four: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_y_minus_color_four: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_z_minus_color_four: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_y_minus_color_four: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_z_minus_color_four: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_x_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_y_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_z_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_y_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_z_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_x_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_y_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_z_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_y_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_z_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_x_plus_color_three: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_y_plus_color_three: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_z_plus_color_three: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_y_plus_color_three: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_z_plus_color_three: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_x_plus_color_four: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_y_plus_color_four: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_z_plus_color_four: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_y_plus_color_four: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_around_z_plus_color_four: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., plastic_diagram_along_x_component_type: _Optional[_Union[MemberHinge.PlasticDiagramAlongXComponentType, str]] = ..., plastic_diagram_along_y_component_type: _Optional[_Union[MemberHinge.PlasticDiagramAlongYComponentType, str]] = ..., plastic_diagram_along_z_component_type: _Optional[_Union[MemberHinge.PlasticDiagramAlongZComponentType, str]] = ..., plastic_diagram_around_y_component_type: _Optional[_Union[MemberHinge.PlasticDiagramAroundYComponentType, str]] = ..., plastic_diagram_around_z_component_type: _Optional[_Union[MemberHinge.PlasticDiagramAroundZComponentType, str]] = ..., plastic_diagram_along_x_color_table: _Optional[_Union[MemberHinge.PlasticDiagramAlongXColorTable, _Mapping]] = ..., plastic_diagram_along_y_color_table: _Optional[_Union[MemberHinge.PlasticDiagramAlongYColorTable, _Mapping]] = ..., plastic_diagram_along_z_color_table: _Optional[_Union[MemberHinge.PlasticDiagramAlongZColorTable, _Mapping]] = ..., plastic_diagram_around_y_color_table: _Optional[_Union[MemberHinge.PlasticDiagramAroundYColorTable, _Mapping]] = ..., plastic_diagram_around_z_color_table: _Optional[_Union[MemberHinge.PlasticDiagramAroundZColorTable, _Mapping]] = ..., friction_coefficient_x: _Optional[float] = ..., friction_coefficient_xy: _Optional[float] = ..., friction_coefficient_xz: _Optional[float] = ..., friction_coefficient_y: _Optional[float] = ..., friction_coefficient_yx: _Optional[float] = ..., friction_coefficient_yz: _Optional[float] = ..., friction_coefficient_z: _Optional[float] = ..., friction_coefficient_zx: _Optional[float] = ..., friction_coefficient_zy: _Optional[float] = ..., friction_direction_independent_x: bool = ..., friction_direction_independent_y: bool = ..., friction_direction_independent_z: bool = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., special_type_of_hinge_direction_along_x: bool = ..., special_type_of_hinge_direction_along_y: bool = ..., special_type_of_hinge_direction_along_z: bool = ..., special_type_of_hinge_direction_around_x: bool = ..., special_type_of_hinge_direction_around_y: bool = ..., special_type_of_hinge_direction_around_z: bool = ..., special_type_of_hinge_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
