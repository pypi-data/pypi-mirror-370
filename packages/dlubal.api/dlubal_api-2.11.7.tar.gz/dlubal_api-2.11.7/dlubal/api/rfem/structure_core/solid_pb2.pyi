from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Solid(_message.Message):
    __slots__ = ("no", "type", "analytical_center_of_gravity", "analytical_center_of_gravity_x", "analytical_center_of_gravity_y", "analytical_center_of_gravity_z", "analytical_mass", "analytical_surface_area", "analytical_volume", "boundary_surfaces", "center_of_gravity", "center_of_gravity_x", "center_of_gravity_y", "center_of_gravity_z", "gas", "is_deactivated_for_calculation", "mass", "material", "mesh_refinement", "solid_contact", "solid_contact_first_surface", "solid_contact_second_surface", "stress_analysis_configuration", "surface_area", "volume", "comment", "is_generated", "generating_object_info", "is_layered_mesh_enabled", "layered_mesh_first_surface", "layered_mesh_second_surface", "number_of_finite_element_layers_input_type", "number_of_finite_element_layers", "specific_direction_enabled", "coordinate_system", "specific_direction_type", "axes_sequence", "rotated_about_angle_x", "rotated_about_angle_y", "rotated_about_angle_z", "rotated_about_angle_1", "rotated_about_angle_2", "rotated_about_angle_3", "directed_to_node_direction_node", "directed_to_node_plane_node", "directed_to_node_first_axis", "directed_to_node_second_axis", "parallel_to_two_nodes_first_node", "parallel_to_two_nodes_second_node", "parallel_to_two_nodes_plane_node", "parallel_to_two_nodes_first_axis", "parallel_to_two_nodes_second_axis", "parallel_to_line", "parallel_to_member", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[Solid.Type]
        TYPE_CONTACT: _ClassVar[Solid.Type]
        TYPE_GAS: _ClassVar[Solid.Type]
        TYPE_HOLE: _ClassVar[Solid.Type]
        TYPE_INTERSECTION: _ClassVar[Solid.Type]
        TYPE_SOIL: _ClassVar[Solid.Type]
        TYPE_STANDARD: _ClassVar[Solid.Type]
    TYPE_UNKNOWN: Solid.Type
    TYPE_CONTACT: Solid.Type
    TYPE_GAS: Solid.Type
    TYPE_HOLE: Solid.Type
    TYPE_INTERSECTION: Solid.Type
    TYPE_SOIL: Solid.Type
    TYPE_STANDARD: Solid.Type
    class NumberOfFiniteElementLayersInputType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NUMBER_OF_FINITE_ELEMENT_LAYERS_INPUT_TYPE_USER_DEFINED: _ClassVar[Solid.NumberOfFiniteElementLayersInputType]
        NUMBER_OF_FINITE_ELEMENT_LAYERS_INPUT_TYPE_ACCORDING_TO_MESH_SETTINGS: _ClassVar[Solid.NumberOfFiniteElementLayersInputType]
    NUMBER_OF_FINITE_ELEMENT_LAYERS_INPUT_TYPE_USER_DEFINED: Solid.NumberOfFiniteElementLayersInputType
    NUMBER_OF_FINITE_ELEMENT_LAYERS_INPUT_TYPE_ACCORDING_TO_MESH_SETTINGS: Solid.NumberOfFiniteElementLayersInputType
    class SpecificDirectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SPECIFIC_DIRECTION_TYPE_ROTATED_VIA_3_ANGLES: _ClassVar[Solid.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_DIRECTED_TO_NODE: _ClassVar[Solid.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_BOUNDARY_SURFACE: _ClassVar[Solid.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_LINE: _ClassVar[Solid.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER: _ClassVar[Solid.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_TWO_NODES: _ClassVar[Solid.SpecificDirectionType]
    SPECIFIC_DIRECTION_TYPE_ROTATED_VIA_3_ANGLES: Solid.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_DIRECTED_TO_NODE: Solid.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_BOUNDARY_SURFACE: Solid.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_LINE: Solid.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER: Solid.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_TWO_NODES: Solid.SpecificDirectionType
    class AxesSequence(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXES_SEQUENCE_XYZ: _ClassVar[Solid.AxesSequence]
        AXES_SEQUENCE_XZY: _ClassVar[Solid.AxesSequence]
        AXES_SEQUENCE_YXZ: _ClassVar[Solid.AxesSequence]
        AXES_SEQUENCE_YZX: _ClassVar[Solid.AxesSequence]
        AXES_SEQUENCE_ZXY: _ClassVar[Solid.AxesSequence]
        AXES_SEQUENCE_ZYX: _ClassVar[Solid.AxesSequence]
    AXES_SEQUENCE_XYZ: Solid.AxesSequence
    AXES_SEQUENCE_XZY: Solid.AxesSequence
    AXES_SEQUENCE_YXZ: Solid.AxesSequence
    AXES_SEQUENCE_YZX: Solid.AxesSequence
    AXES_SEQUENCE_ZXY: Solid.AxesSequence
    AXES_SEQUENCE_ZYX: Solid.AxesSequence
    class DirectedToNodeFirstAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIRECTED_TO_NODE_FIRST_AXIS_X: _ClassVar[Solid.DirectedToNodeFirstAxis]
        DIRECTED_TO_NODE_FIRST_AXIS_Y: _ClassVar[Solid.DirectedToNodeFirstAxis]
        DIRECTED_TO_NODE_FIRST_AXIS_Z: _ClassVar[Solid.DirectedToNodeFirstAxis]
    DIRECTED_TO_NODE_FIRST_AXIS_X: Solid.DirectedToNodeFirstAxis
    DIRECTED_TO_NODE_FIRST_AXIS_Y: Solid.DirectedToNodeFirstAxis
    DIRECTED_TO_NODE_FIRST_AXIS_Z: Solid.DirectedToNodeFirstAxis
    class DirectedToNodeSecondAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIRECTED_TO_NODE_SECOND_AXIS_X: _ClassVar[Solid.DirectedToNodeSecondAxis]
        DIRECTED_TO_NODE_SECOND_AXIS_Y: _ClassVar[Solid.DirectedToNodeSecondAxis]
        DIRECTED_TO_NODE_SECOND_AXIS_Z: _ClassVar[Solid.DirectedToNodeSecondAxis]
    DIRECTED_TO_NODE_SECOND_AXIS_X: Solid.DirectedToNodeSecondAxis
    DIRECTED_TO_NODE_SECOND_AXIS_Y: Solid.DirectedToNodeSecondAxis
    DIRECTED_TO_NODE_SECOND_AXIS_Z: Solid.DirectedToNodeSecondAxis
    class ParallelToTwoNodesFirstAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARALLEL_TO_TWO_NODES_FIRST_AXIS_X: _ClassVar[Solid.ParallelToTwoNodesFirstAxis]
        PARALLEL_TO_TWO_NODES_FIRST_AXIS_Y: _ClassVar[Solid.ParallelToTwoNodesFirstAxis]
        PARALLEL_TO_TWO_NODES_FIRST_AXIS_Z: _ClassVar[Solid.ParallelToTwoNodesFirstAxis]
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_X: Solid.ParallelToTwoNodesFirstAxis
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_Y: Solid.ParallelToTwoNodesFirstAxis
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_Z: Solid.ParallelToTwoNodesFirstAxis
    class ParallelToTwoNodesSecondAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARALLEL_TO_TWO_NODES_SECOND_AXIS_X: _ClassVar[Solid.ParallelToTwoNodesSecondAxis]
        PARALLEL_TO_TWO_NODES_SECOND_AXIS_Y: _ClassVar[Solid.ParallelToTwoNodesSecondAxis]
        PARALLEL_TO_TWO_NODES_SECOND_AXIS_Z: _ClassVar[Solid.ParallelToTwoNodesSecondAxis]
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_X: Solid.ParallelToTwoNodesSecondAxis
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_Y: Solid.ParallelToTwoNodesSecondAxis
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_Z: Solid.ParallelToTwoNodesSecondAxis
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_CENTER_OF_GRAVITY_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_CENTER_OF_GRAVITY_X_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_CENTER_OF_GRAVITY_Z_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_MASS_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_SURFACE_AREA_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_VOLUME_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_SURFACES_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Z_FIELD_NUMBER: _ClassVar[int]
    GAS_FIELD_NUMBER: _ClassVar[int]
    IS_DEACTIVATED_FOR_CALCULATION_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_FIELD_NUMBER: _ClassVar[int]
    MESH_REFINEMENT_FIELD_NUMBER: _ClassVar[int]
    SOLID_CONTACT_FIELD_NUMBER: _ClassVar[int]
    SOLID_CONTACT_FIRST_SURFACE_FIELD_NUMBER: _ClassVar[int]
    SOLID_CONTACT_SECOND_SURFACE_FIELD_NUMBER: _ClassVar[int]
    STRESS_ANALYSIS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    SURFACE_AREA_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_LAYERED_MESH_ENABLED_FIELD_NUMBER: _ClassVar[int]
    LAYERED_MESH_FIRST_SURFACE_FIELD_NUMBER: _ClassVar[int]
    LAYERED_MESH_SECOND_SURFACE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_FINITE_ELEMENT_LAYERS_INPUT_TYPE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_FINITE_ELEMENT_LAYERS_FIELD_NUMBER: _ClassVar[int]
    SPECIFIC_DIRECTION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    SPECIFIC_DIRECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    AXES_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_X_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_Y_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_Z_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_1_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_2_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_3_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_DIRECTION_NODE_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_PLANE_NODE_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_FIRST_AXIS_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_SECOND_AXIS_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_FIRST_NODE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_SECOND_NODE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_PLANE_NODE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_LINE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_MEMBER_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: Solid.Type
    analytical_center_of_gravity: _common_pb2.Vector3d
    analytical_center_of_gravity_x: float
    analytical_center_of_gravity_y: float
    analytical_center_of_gravity_z: float
    analytical_mass: float
    analytical_surface_area: float
    analytical_volume: float
    boundary_surfaces: _containers.RepeatedScalarFieldContainer[int]
    center_of_gravity: _common_pb2.Vector3d
    center_of_gravity_x: float
    center_of_gravity_y: float
    center_of_gravity_z: float
    gas: int
    is_deactivated_for_calculation: bool
    mass: float
    material: int
    mesh_refinement: int
    solid_contact: int
    solid_contact_first_surface: int
    solid_contact_second_surface: int
    stress_analysis_configuration: int
    surface_area: float
    volume: float
    comment: str
    is_generated: bool
    generating_object_info: str
    is_layered_mesh_enabled: bool
    layered_mesh_first_surface: int
    layered_mesh_second_surface: int
    number_of_finite_element_layers_input_type: Solid.NumberOfFiniteElementLayersInputType
    number_of_finite_element_layers: int
    specific_direction_enabled: bool
    coordinate_system: int
    specific_direction_type: Solid.SpecificDirectionType
    axes_sequence: Solid.AxesSequence
    rotated_about_angle_x: float
    rotated_about_angle_y: float
    rotated_about_angle_z: float
    rotated_about_angle_1: float
    rotated_about_angle_2: float
    rotated_about_angle_3: float
    directed_to_node_direction_node: int
    directed_to_node_plane_node: int
    directed_to_node_first_axis: Solid.DirectedToNodeFirstAxis
    directed_to_node_second_axis: Solid.DirectedToNodeSecondAxis
    parallel_to_two_nodes_first_node: int
    parallel_to_two_nodes_second_node: int
    parallel_to_two_nodes_plane_node: int
    parallel_to_two_nodes_first_axis: Solid.ParallelToTwoNodesFirstAxis
    parallel_to_two_nodes_second_axis: Solid.ParallelToTwoNodesSecondAxis
    parallel_to_line: int
    parallel_to_member: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[Solid.Type, str]] = ..., analytical_center_of_gravity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., analytical_center_of_gravity_x: _Optional[float] = ..., analytical_center_of_gravity_y: _Optional[float] = ..., analytical_center_of_gravity_z: _Optional[float] = ..., analytical_mass: _Optional[float] = ..., analytical_surface_area: _Optional[float] = ..., analytical_volume: _Optional[float] = ..., boundary_surfaces: _Optional[_Iterable[int]] = ..., center_of_gravity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_of_gravity_x: _Optional[float] = ..., center_of_gravity_y: _Optional[float] = ..., center_of_gravity_z: _Optional[float] = ..., gas: _Optional[int] = ..., is_deactivated_for_calculation: bool = ..., mass: _Optional[float] = ..., material: _Optional[int] = ..., mesh_refinement: _Optional[int] = ..., solid_contact: _Optional[int] = ..., solid_contact_first_surface: _Optional[int] = ..., solid_contact_second_surface: _Optional[int] = ..., stress_analysis_configuration: _Optional[int] = ..., surface_area: _Optional[float] = ..., volume: _Optional[float] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., is_layered_mesh_enabled: bool = ..., layered_mesh_first_surface: _Optional[int] = ..., layered_mesh_second_surface: _Optional[int] = ..., number_of_finite_element_layers_input_type: _Optional[_Union[Solid.NumberOfFiniteElementLayersInputType, str]] = ..., number_of_finite_element_layers: _Optional[int] = ..., specific_direction_enabled: bool = ..., coordinate_system: _Optional[int] = ..., specific_direction_type: _Optional[_Union[Solid.SpecificDirectionType, str]] = ..., axes_sequence: _Optional[_Union[Solid.AxesSequence, str]] = ..., rotated_about_angle_x: _Optional[float] = ..., rotated_about_angle_y: _Optional[float] = ..., rotated_about_angle_z: _Optional[float] = ..., rotated_about_angle_1: _Optional[float] = ..., rotated_about_angle_2: _Optional[float] = ..., rotated_about_angle_3: _Optional[float] = ..., directed_to_node_direction_node: _Optional[int] = ..., directed_to_node_plane_node: _Optional[int] = ..., directed_to_node_first_axis: _Optional[_Union[Solid.DirectedToNodeFirstAxis, str]] = ..., directed_to_node_second_axis: _Optional[_Union[Solid.DirectedToNodeSecondAxis, str]] = ..., parallel_to_two_nodes_first_node: _Optional[int] = ..., parallel_to_two_nodes_second_node: _Optional[int] = ..., parallel_to_two_nodes_plane_node: _Optional[int] = ..., parallel_to_two_nodes_first_axis: _Optional[_Union[Solid.ParallelToTwoNodesFirstAxis, str]] = ..., parallel_to_two_nodes_second_axis: _Optional[_Union[Solid.ParallelToTwoNodesSecondAxis, str]] = ..., parallel_to_line: _Optional[int] = ..., parallel_to_member: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
