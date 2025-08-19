from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NodalLoad(_message.Message):
    __slots__ = ("no", "load_type", "nodes", "force_eccentricity", "force_eccentricity_x", "force_eccentricity_y", "force_eccentricity_z", "coordinate_system", "has_specific_direction", "specific_direction_type", "axes_sequence", "rotated_about_angle_x", "rotated_about_angle_y", "rotated_about_angle_z", "rotated_about_angle_1", "rotated_about_angle_2", "rotated_about_angle_3", "directed_to_node_direction_node", "parallel_to_two_nodes_first_node", "parallel_to_two_nodes_second_node", "parallel_to_line", "parallel_to_member", "components_force", "components_force_x", "components_force_y", "components_force_z", "components_moment", "components_moment_x", "components_moment_y", "components_moment_z", "force_magnitude", "load_direction", "moment_magnitude", "individual_mass_components", "mass_global", "mass", "mass_x", "mass_y", "mass_z", "mass_moment_of_inertia", "mass_moment_of_inertia_x", "mass_moment_of_inertia_y", "mass_moment_of_inertia_z", "mass_has_rotational_mass", "mass_rotational_mass", "mass_angular_velocity", "mass_angular_acceleration", "mass_radius", "mass_axis_of_rotation", "mass_angle", "has_shifted_display", "offset", "offset_x", "offset_y", "offset_z", "size_or_distance", "comment", "load_case", "is_generated", "generating_object_info", "has_load_graphic_position_below", "id_for_export_import", "metadata_for_export_import")
    class LoadType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_TYPE_UNKNOWN: _ClassVar[NodalLoad.LoadType]
        LOAD_TYPE_COMPONENTS: _ClassVar[NodalLoad.LoadType]
        LOAD_TYPE_FORCE: _ClassVar[NodalLoad.LoadType]
        LOAD_TYPE_MASS: _ClassVar[NodalLoad.LoadType]
        LOAD_TYPE_MOMENT: _ClassVar[NodalLoad.LoadType]
    LOAD_TYPE_UNKNOWN: NodalLoad.LoadType
    LOAD_TYPE_COMPONENTS: NodalLoad.LoadType
    LOAD_TYPE_FORCE: NodalLoad.LoadType
    LOAD_TYPE_MASS: NodalLoad.LoadType
    LOAD_TYPE_MOMENT: NodalLoad.LoadType
    class SpecificDirectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SPECIFIC_DIRECTION_TYPE_ROTATED_VIA_3_ANGLES: _ClassVar[NodalLoad.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_DIRECTED_TO_NODE: _ClassVar[NodalLoad.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_LINE: _ClassVar[NodalLoad.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER: _ClassVar[NodalLoad.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_TWO_NODES: _ClassVar[NodalLoad.SpecificDirectionType]
    SPECIFIC_DIRECTION_TYPE_ROTATED_VIA_3_ANGLES: NodalLoad.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_DIRECTED_TO_NODE: NodalLoad.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_LINE: NodalLoad.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER: NodalLoad.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_TWO_NODES: NodalLoad.SpecificDirectionType
    class AxesSequence(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXES_SEQUENCE_XYZ: _ClassVar[NodalLoad.AxesSequence]
        AXES_SEQUENCE_XZY: _ClassVar[NodalLoad.AxesSequence]
        AXES_SEQUENCE_YXZ: _ClassVar[NodalLoad.AxesSequence]
        AXES_SEQUENCE_YZX: _ClassVar[NodalLoad.AxesSequence]
        AXES_SEQUENCE_ZXY: _ClassVar[NodalLoad.AxesSequence]
        AXES_SEQUENCE_ZYX: _ClassVar[NodalLoad.AxesSequence]
    AXES_SEQUENCE_XYZ: NodalLoad.AxesSequence
    AXES_SEQUENCE_XZY: NodalLoad.AxesSequence
    AXES_SEQUENCE_YXZ: NodalLoad.AxesSequence
    AXES_SEQUENCE_YZX: NodalLoad.AxesSequence
    AXES_SEQUENCE_ZXY: NodalLoad.AxesSequence
    AXES_SEQUENCE_ZYX: NodalLoad.AxesSequence
    class LoadDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DIRECTION_LOCAL_X: _ClassVar[NodalLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: _ClassVar[NodalLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: _ClassVar[NodalLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: _ClassVar[NodalLoad.LoadDirection]
        LOAD_DIRECTION_LOCAL_Y: _ClassVar[NodalLoad.LoadDirection]
        LOAD_DIRECTION_LOCAL_Z: _ClassVar[NodalLoad.LoadDirection]
    LOAD_DIRECTION_LOCAL_X: NodalLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: NodalLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: NodalLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: NodalLoad.LoadDirection
    LOAD_DIRECTION_LOCAL_Y: NodalLoad.LoadDirection
    LOAD_DIRECTION_LOCAL_Z: NodalLoad.LoadDirection
    class MassAxisOfRotation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MASS_AXIS_OF_ROTATION_X_POSITIVE: _ClassVar[NodalLoad.MassAxisOfRotation]
        MASS_AXIS_OF_ROTATION_X_NEGATIVE: _ClassVar[NodalLoad.MassAxisOfRotation]
        MASS_AXIS_OF_ROTATION_Y_NEGATIVE: _ClassVar[NodalLoad.MassAxisOfRotation]
        MASS_AXIS_OF_ROTATION_Y_POSITIVE: _ClassVar[NodalLoad.MassAxisOfRotation]
        MASS_AXIS_OF_ROTATION_Z_NEGATIVE: _ClassVar[NodalLoad.MassAxisOfRotation]
        MASS_AXIS_OF_ROTATION_Z_POSITIVE: _ClassVar[NodalLoad.MassAxisOfRotation]
    MASS_AXIS_OF_ROTATION_X_POSITIVE: NodalLoad.MassAxisOfRotation
    MASS_AXIS_OF_ROTATION_X_NEGATIVE: NodalLoad.MassAxisOfRotation
    MASS_AXIS_OF_ROTATION_Y_NEGATIVE: NodalLoad.MassAxisOfRotation
    MASS_AXIS_OF_ROTATION_Y_POSITIVE: NodalLoad.MassAxisOfRotation
    MASS_AXIS_OF_ROTATION_Z_NEGATIVE: NodalLoad.MassAxisOfRotation
    MASS_AXIS_OF_ROTATION_Z_POSITIVE: NodalLoad.MassAxisOfRotation
    NO_FIELD_NUMBER: _ClassVar[int]
    LOAD_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    FORCE_ECCENTRICITY_FIELD_NUMBER: _ClassVar[int]
    FORCE_ECCENTRICITY_X_FIELD_NUMBER: _ClassVar[int]
    FORCE_ECCENTRICITY_Y_FIELD_NUMBER: _ClassVar[int]
    FORCE_ECCENTRICITY_Z_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    HAS_SPECIFIC_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    SPECIFIC_DIRECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    AXES_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_X_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_Y_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_Z_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_1_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_2_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_3_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_DIRECTION_NODE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_FIRST_NODE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_SECOND_NODE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_LINE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_MEMBER_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FORCE_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FORCE_X_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FORCE_Y_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FORCE_Z_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_MOMENT_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_MOMENT_X_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_MOMENT_Y_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_MOMENT_Z_FIELD_NUMBER: _ClassVar[int]
    FORCE_MAGNITUDE_FIELD_NUMBER: _ClassVar[int]
    LOAD_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    MOMENT_MAGNITUDE_FIELD_NUMBER: _ClassVar[int]
    INDIVIDUAL_MASS_COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    MASS_GLOBAL_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    MASS_X_FIELD_NUMBER: _ClassVar[int]
    MASS_Y_FIELD_NUMBER: _ClassVar[int]
    MASS_Z_FIELD_NUMBER: _ClassVar[int]
    MASS_MOMENT_OF_INERTIA_FIELD_NUMBER: _ClassVar[int]
    MASS_MOMENT_OF_INERTIA_X_FIELD_NUMBER: _ClassVar[int]
    MASS_MOMENT_OF_INERTIA_Y_FIELD_NUMBER: _ClassVar[int]
    MASS_MOMENT_OF_INERTIA_Z_FIELD_NUMBER: _ClassVar[int]
    MASS_HAS_ROTATIONAL_MASS_FIELD_NUMBER: _ClassVar[int]
    MASS_ROTATIONAL_MASS_FIELD_NUMBER: _ClassVar[int]
    MASS_ANGULAR_VELOCITY_FIELD_NUMBER: _ClassVar[int]
    MASS_ANGULAR_ACCELERATION_FIELD_NUMBER: _ClassVar[int]
    MASS_RADIUS_FIELD_NUMBER: _ClassVar[int]
    MASS_AXIS_OF_ROTATION_FIELD_NUMBER: _ClassVar[int]
    MASS_ANGLE_FIELD_NUMBER: _ClassVar[int]
    HAS_SHIFTED_DISPLAY_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    OFFSET_X_FIELD_NUMBER: _ClassVar[int]
    OFFSET_Y_FIELD_NUMBER: _ClassVar[int]
    OFFSET_Z_FIELD_NUMBER: _ClassVar[int]
    SIZE_OR_DISTANCE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    LOAD_CASE_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    HAS_LOAD_GRAPHIC_POSITION_BELOW_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    load_type: NodalLoad.LoadType
    nodes: _containers.RepeatedScalarFieldContainer[int]
    force_eccentricity: _common_pb2.Vector3d
    force_eccentricity_x: float
    force_eccentricity_y: float
    force_eccentricity_z: float
    coordinate_system: int
    has_specific_direction: bool
    specific_direction_type: NodalLoad.SpecificDirectionType
    axes_sequence: NodalLoad.AxesSequence
    rotated_about_angle_x: float
    rotated_about_angle_y: float
    rotated_about_angle_z: float
    rotated_about_angle_1: float
    rotated_about_angle_2: float
    rotated_about_angle_3: float
    directed_to_node_direction_node: int
    parallel_to_two_nodes_first_node: int
    parallel_to_two_nodes_second_node: int
    parallel_to_line: int
    parallel_to_member: int
    components_force: _common_pb2.Vector3d
    components_force_x: float
    components_force_y: float
    components_force_z: float
    components_moment: _common_pb2.Vector3d
    components_moment_x: float
    components_moment_y: float
    components_moment_z: float
    force_magnitude: float
    load_direction: NodalLoad.LoadDirection
    moment_magnitude: float
    individual_mass_components: bool
    mass_global: float
    mass: _common_pb2.Vector3d
    mass_x: float
    mass_y: float
    mass_z: float
    mass_moment_of_inertia: _common_pb2.Vector3d
    mass_moment_of_inertia_x: float
    mass_moment_of_inertia_y: float
    mass_moment_of_inertia_z: float
    mass_has_rotational_mass: bool
    mass_rotational_mass: float
    mass_angular_velocity: float
    mass_angular_acceleration: float
    mass_radius: float
    mass_axis_of_rotation: NodalLoad.MassAxisOfRotation
    mass_angle: float
    has_shifted_display: bool
    offset: _common_pb2.Vector3d
    offset_x: float
    offset_y: float
    offset_z: float
    size_or_distance: float
    comment: str
    load_case: int
    is_generated: bool
    generating_object_info: str
    has_load_graphic_position_below: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., load_type: _Optional[_Union[NodalLoad.LoadType, str]] = ..., nodes: _Optional[_Iterable[int]] = ..., force_eccentricity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., force_eccentricity_x: _Optional[float] = ..., force_eccentricity_y: _Optional[float] = ..., force_eccentricity_z: _Optional[float] = ..., coordinate_system: _Optional[int] = ..., has_specific_direction: bool = ..., specific_direction_type: _Optional[_Union[NodalLoad.SpecificDirectionType, str]] = ..., axes_sequence: _Optional[_Union[NodalLoad.AxesSequence, str]] = ..., rotated_about_angle_x: _Optional[float] = ..., rotated_about_angle_y: _Optional[float] = ..., rotated_about_angle_z: _Optional[float] = ..., rotated_about_angle_1: _Optional[float] = ..., rotated_about_angle_2: _Optional[float] = ..., rotated_about_angle_3: _Optional[float] = ..., directed_to_node_direction_node: _Optional[int] = ..., parallel_to_two_nodes_first_node: _Optional[int] = ..., parallel_to_two_nodes_second_node: _Optional[int] = ..., parallel_to_line: _Optional[int] = ..., parallel_to_member: _Optional[int] = ..., components_force: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., components_force_x: _Optional[float] = ..., components_force_y: _Optional[float] = ..., components_force_z: _Optional[float] = ..., components_moment: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., components_moment_x: _Optional[float] = ..., components_moment_y: _Optional[float] = ..., components_moment_z: _Optional[float] = ..., force_magnitude: _Optional[float] = ..., load_direction: _Optional[_Union[NodalLoad.LoadDirection, str]] = ..., moment_magnitude: _Optional[float] = ..., individual_mass_components: bool = ..., mass_global: _Optional[float] = ..., mass: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., mass_x: _Optional[float] = ..., mass_y: _Optional[float] = ..., mass_z: _Optional[float] = ..., mass_moment_of_inertia: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., mass_moment_of_inertia_x: _Optional[float] = ..., mass_moment_of_inertia_y: _Optional[float] = ..., mass_moment_of_inertia_z: _Optional[float] = ..., mass_has_rotational_mass: bool = ..., mass_rotational_mass: _Optional[float] = ..., mass_angular_velocity: _Optional[float] = ..., mass_angular_acceleration: _Optional[float] = ..., mass_radius: _Optional[float] = ..., mass_axis_of_rotation: _Optional[_Union[NodalLoad.MassAxisOfRotation, str]] = ..., mass_angle: _Optional[float] = ..., has_shifted_display: bool = ..., offset: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., offset_x: _Optional[float] = ..., offset_y: _Optional[float] = ..., offset_z: _Optional[float] = ..., size_or_distance: _Optional[float] = ..., comment: _Optional[str] = ..., load_case: _Optional[int] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., has_load_graphic_position_below: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
