from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Block(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "coordinate_system", "insert_node_id", "is_insert_point_position_defined_by_node", "insert_point_position_node", "insert_point_position_coordinates", "insert_point_position_coordinate_x", "insert_point_position_coordinate_y", "insert_point_position_coordinate_z", "rotation_coordinate_system", "specific_direction_type", "rotated_about_angle_x", "rotated_about_angle_y", "rotated_about_angle_z", "rotated_about_angle_1", "rotated_about_angle_2", "rotated_about_angle_3", "axes_sequence", "directed_to_node_direction_node", "directed_to_node_plane_node", "directed_to_node_first_axis", "directed_to_node_second_axis", "parallel_to_two_nodes_first_node", "parallel_to_two_nodes_second_node", "parallel_to_two_nodes_plane_node", "parallel_to_two_nodes_first_axis", "parallel_to_two_nodes_second_axis", "parallel_to_member", "loads_enabled", "numbering_enabled", "has_javascript", "block_id", "block_name", "model_type", "block_object_type", "model_category1", "model_subcategory1", "model_category2", "model_subcategory2", "reference_block_enabled", "reference_block", "comment", "script", "parameters", "explode_enabled", "id_for_export_import", "metadata_for_export_import")
    class IsInsertPointPositionDefinedByNode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        IS_INSERT_POINT_POSITION_DEFINED_BY_NODE_INSERT_POINT_SPECIFICATION_TYPE_NODE: _ClassVar[Block.IsInsertPointPositionDefinedByNode]
        IS_INSERT_POINT_POSITION_DEFINED_BY_NODE_INSERT_POINT_SPECIFICATION_TYPE_COORDINATES: _ClassVar[Block.IsInsertPointPositionDefinedByNode]
    IS_INSERT_POINT_POSITION_DEFINED_BY_NODE_INSERT_POINT_SPECIFICATION_TYPE_NODE: Block.IsInsertPointPositionDefinedByNode
    IS_INSERT_POINT_POSITION_DEFINED_BY_NODE_INSERT_POINT_SPECIFICATION_TYPE_COORDINATES: Block.IsInsertPointPositionDefinedByNode
    class SpecificDirectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SPECIFIC_DIRECTION_TYPE_ROTATED_VIA_3_ANGLES: _ClassVar[Block.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_DIRECTED_TO_NODE: _ClassVar[Block.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER: _ClassVar[Block.SpecificDirectionType]
        SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_TWO_NODES: _ClassVar[Block.SpecificDirectionType]
    SPECIFIC_DIRECTION_TYPE_ROTATED_VIA_3_ANGLES: Block.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_DIRECTED_TO_NODE: Block.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER: Block.SpecificDirectionType
    SPECIFIC_DIRECTION_TYPE_PARALLEL_TO_TWO_NODES: Block.SpecificDirectionType
    class AxesSequence(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXES_SEQUENCE_XYZ: _ClassVar[Block.AxesSequence]
        AXES_SEQUENCE_XZY: _ClassVar[Block.AxesSequence]
        AXES_SEQUENCE_YXZ: _ClassVar[Block.AxesSequence]
        AXES_SEQUENCE_YZX: _ClassVar[Block.AxesSequence]
        AXES_SEQUENCE_ZXY: _ClassVar[Block.AxesSequence]
        AXES_SEQUENCE_ZYX: _ClassVar[Block.AxesSequence]
    AXES_SEQUENCE_XYZ: Block.AxesSequence
    AXES_SEQUENCE_XZY: Block.AxesSequence
    AXES_SEQUENCE_YXZ: Block.AxesSequence
    AXES_SEQUENCE_YZX: Block.AxesSequence
    AXES_SEQUENCE_ZXY: Block.AxesSequence
    AXES_SEQUENCE_ZYX: Block.AxesSequence
    class DirectedToNodeFirstAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIRECTED_TO_NODE_FIRST_AXIS_X: _ClassVar[Block.DirectedToNodeFirstAxis]
        DIRECTED_TO_NODE_FIRST_AXIS_Y: _ClassVar[Block.DirectedToNodeFirstAxis]
        DIRECTED_TO_NODE_FIRST_AXIS_Z: _ClassVar[Block.DirectedToNodeFirstAxis]
    DIRECTED_TO_NODE_FIRST_AXIS_X: Block.DirectedToNodeFirstAxis
    DIRECTED_TO_NODE_FIRST_AXIS_Y: Block.DirectedToNodeFirstAxis
    DIRECTED_TO_NODE_FIRST_AXIS_Z: Block.DirectedToNodeFirstAxis
    class DirectedToNodeSecondAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIRECTED_TO_NODE_SECOND_AXIS_X: _ClassVar[Block.DirectedToNodeSecondAxis]
        DIRECTED_TO_NODE_SECOND_AXIS_Y: _ClassVar[Block.DirectedToNodeSecondAxis]
        DIRECTED_TO_NODE_SECOND_AXIS_Z: _ClassVar[Block.DirectedToNodeSecondAxis]
    DIRECTED_TO_NODE_SECOND_AXIS_X: Block.DirectedToNodeSecondAxis
    DIRECTED_TO_NODE_SECOND_AXIS_Y: Block.DirectedToNodeSecondAxis
    DIRECTED_TO_NODE_SECOND_AXIS_Z: Block.DirectedToNodeSecondAxis
    class ParallelToTwoNodesFirstAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARALLEL_TO_TWO_NODES_FIRST_AXIS_X: _ClassVar[Block.ParallelToTwoNodesFirstAxis]
        PARALLEL_TO_TWO_NODES_FIRST_AXIS_Y: _ClassVar[Block.ParallelToTwoNodesFirstAxis]
        PARALLEL_TO_TWO_NODES_FIRST_AXIS_Z: _ClassVar[Block.ParallelToTwoNodesFirstAxis]
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_X: Block.ParallelToTwoNodesFirstAxis
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_Y: Block.ParallelToTwoNodesFirstAxis
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_Z: Block.ParallelToTwoNodesFirstAxis
    class ParallelToTwoNodesSecondAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARALLEL_TO_TWO_NODES_SECOND_AXIS_X: _ClassVar[Block.ParallelToTwoNodesSecondAxis]
        PARALLEL_TO_TWO_NODES_SECOND_AXIS_Y: _ClassVar[Block.ParallelToTwoNodesSecondAxis]
        PARALLEL_TO_TWO_NODES_SECOND_AXIS_Z: _ClassVar[Block.ParallelToTwoNodesSecondAxis]
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_X: Block.ParallelToTwoNodesSecondAxis
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_Y: Block.ParallelToTwoNodesSecondAxis
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_Z: Block.ParallelToTwoNodesSecondAxis
    class ParametersTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[Block.ParametersTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[Block.ParametersTableRow, _Mapping]]] = ...) -> None: ...
    class ParametersTableRow(_message.Message):
        __slots__ = ("key", "caption", "symbol", "value", "unit", "children")
        KEY_FIELD_NUMBER: _ClassVar[int]
        CAPTION_FIELD_NUMBER: _ClassVar[int]
        SYMBOL_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        UNIT_FIELD_NUMBER: _ClassVar[int]
        CHILDREN_FIELD_NUMBER: _ClassVar[int]
        key: str
        caption: str
        symbol: str
        value: _common_pb2.Value
        unit: str
        children: _containers.RepeatedCompositeFieldContainer[Block.ParametersTableRow]
        def __init__(self, key: _Optional[str] = ..., caption: _Optional[str] = ..., symbol: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., unit: _Optional[str] = ..., children: _Optional[_Iterable[_Union[Block.ParametersTableRow, _Mapping]]] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    INSERT_NODE_ID_FIELD_NUMBER: _ClassVar[int]
    IS_INSERT_POINT_POSITION_DEFINED_BY_NODE_FIELD_NUMBER: _ClassVar[int]
    INSERT_POINT_POSITION_NODE_FIELD_NUMBER: _ClassVar[int]
    INSERT_POINT_POSITION_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    INSERT_POINT_POSITION_COORDINATE_X_FIELD_NUMBER: _ClassVar[int]
    INSERT_POINT_POSITION_COORDINATE_Y_FIELD_NUMBER: _ClassVar[int]
    INSERT_POINT_POSITION_COORDINATE_Z_FIELD_NUMBER: _ClassVar[int]
    ROTATION_COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    SPECIFIC_DIRECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_X_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_Y_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_Z_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_1_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_2_FIELD_NUMBER: _ClassVar[int]
    ROTATED_ABOUT_ANGLE_3_FIELD_NUMBER: _ClassVar[int]
    AXES_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_DIRECTION_NODE_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_PLANE_NODE_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_FIRST_AXIS_FIELD_NUMBER: _ClassVar[int]
    DIRECTED_TO_NODE_SECOND_AXIS_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_FIRST_NODE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_SECOND_NODE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_PLANE_NODE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_FIRST_AXIS_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_TWO_NODES_SECOND_AXIS_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_MEMBER_FIELD_NUMBER: _ClassVar[int]
    LOADS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NUMBERING_ENABLED_FIELD_NUMBER: _ClassVar[int]
    HAS_JAVASCRIPT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_ID_FIELD_NUMBER: _ClassVar[int]
    BLOCK_NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_TYPE_FIELD_NUMBER: _ClassVar[int]
    BLOCK_OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    MODEL_CATEGORY1_FIELD_NUMBER: _ClassVar[int]
    MODEL_SUBCATEGORY1_FIELD_NUMBER: _ClassVar[int]
    MODEL_CATEGORY2_FIELD_NUMBER: _ClassVar[int]
    MODEL_SUBCATEGORY2_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_BLOCK_ENABLED_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_BLOCK_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    EXPLODE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    coordinate_system: int
    insert_node_id: int
    is_insert_point_position_defined_by_node: Block.IsInsertPointPositionDefinedByNode
    insert_point_position_node: int
    insert_point_position_coordinates: _common_pb2.Vector3d
    insert_point_position_coordinate_x: float
    insert_point_position_coordinate_y: float
    insert_point_position_coordinate_z: float
    rotation_coordinate_system: int
    specific_direction_type: Block.SpecificDirectionType
    rotated_about_angle_x: float
    rotated_about_angle_y: float
    rotated_about_angle_z: float
    rotated_about_angle_1: float
    rotated_about_angle_2: float
    rotated_about_angle_3: float
    axes_sequence: Block.AxesSequence
    directed_to_node_direction_node: int
    directed_to_node_plane_node: int
    directed_to_node_first_axis: Block.DirectedToNodeFirstAxis
    directed_to_node_second_axis: Block.DirectedToNodeSecondAxis
    parallel_to_two_nodes_first_node: int
    parallel_to_two_nodes_second_node: int
    parallel_to_two_nodes_plane_node: int
    parallel_to_two_nodes_first_axis: Block.ParallelToTwoNodesFirstAxis
    parallel_to_two_nodes_second_axis: Block.ParallelToTwoNodesSecondAxis
    parallel_to_member: int
    loads_enabled: bool
    numbering_enabled: bool
    has_javascript: bool
    block_id: str
    block_name: str
    model_type: str
    block_object_type: str
    model_category1: str
    model_subcategory1: str
    model_category2: str
    model_subcategory2: str
    reference_block_enabled: bool
    reference_block: int
    comment: str
    script: str
    parameters: Block.ParametersTable
    explode_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., coordinate_system: _Optional[int] = ..., insert_node_id: _Optional[int] = ..., is_insert_point_position_defined_by_node: _Optional[_Union[Block.IsInsertPointPositionDefinedByNode, str]] = ..., insert_point_position_node: _Optional[int] = ..., insert_point_position_coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., insert_point_position_coordinate_x: _Optional[float] = ..., insert_point_position_coordinate_y: _Optional[float] = ..., insert_point_position_coordinate_z: _Optional[float] = ..., rotation_coordinate_system: _Optional[int] = ..., specific_direction_type: _Optional[_Union[Block.SpecificDirectionType, str]] = ..., rotated_about_angle_x: _Optional[float] = ..., rotated_about_angle_y: _Optional[float] = ..., rotated_about_angle_z: _Optional[float] = ..., rotated_about_angle_1: _Optional[float] = ..., rotated_about_angle_2: _Optional[float] = ..., rotated_about_angle_3: _Optional[float] = ..., axes_sequence: _Optional[_Union[Block.AxesSequence, str]] = ..., directed_to_node_direction_node: _Optional[int] = ..., directed_to_node_plane_node: _Optional[int] = ..., directed_to_node_first_axis: _Optional[_Union[Block.DirectedToNodeFirstAxis, str]] = ..., directed_to_node_second_axis: _Optional[_Union[Block.DirectedToNodeSecondAxis, str]] = ..., parallel_to_two_nodes_first_node: _Optional[int] = ..., parallel_to_two_nodes_second_node: _Optional[int] = ..., parallel_to_two_nodes_plane_node: _Optional[int] = ..., parallel_to_two_nodes_first_axis: _Optional[_Union[Block.ParallelToTwoNodesFirstAxis, str]] = ..., parallel_to_two_nodes_second_axis: _Optional[_Union[Block.ParallelToTwoNodesSecondAxis, str]] = ..., parallel_to_member: _Optional[int] = ..., loads_enabled: bool = ..., numbering_enabled: bool = ..., has_javascript: bool = ..., block_id: _Optional[str] = ..., block_name: _Optional[str] = ..., model_type: _Optional[str] = ..., block_object_type: _Optional[str] = ..., model_category1: _Optional[str] = ..., model_subcategory1: _Optional[str] = ..., model_category2: _Optional[str] = ..., model_subcategory2: _Optional[str] = ..., reference_block_enabled: bool = ..., reference_block: _Optional[int] = ..., comment: _Optional[str] = ..., script: _Optional[str] = ..., parameters: _Optional[_Union[Block.ParametersTable, _Mapping]] = ..., explode_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
