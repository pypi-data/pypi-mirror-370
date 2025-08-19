from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RigidLink(_message.Message):
    __slots__ = ("no", "type", "line1", "line2", "surface", "rigid_link_type", "comment", "ignore_influence_of_distance", "user_defined_distribution", "line1_start_is_relative", "line1_start_relative", "line1_start_absolute", "line1_end_is_relative", "line1_end_relative", "line1_end_absolute", "line2_start_is_relative", "line2_start_relative", "line2_start_absolute", "line2_end_is_relative", "line2_end_relative", "line2_end_absolute", "nodes", "lines", "center_node_no", "center_user_defined", "center_point", "center_point_x", "center_point_y", "center_point_z", "link_plane_user_defined", "link_plane_node1_no", "link_plane_node2_no", "link_plane_node3_no", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[RigidLink.Type]
        TYPE_DIAPHRAGM: _ClassVar[RigidLink.Type]
        TYPE_LINE_TO_LINE: _ClassVar[RigidLink.Type]
        TYPE_LINE_TO_SURFACE: _ClassVar[RigidLink.Type]
    TYPE_UNKNOWN: RigidLink.Type
    TYPE_DIAPHRAGM: RigidLink.Type
    TYPE_LINE_TO_LINE: RigidLink.Type
    TYPE_LINE_TO_SURFACE: RigidLink.Type
    class RigidLinkType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        RIGID_LINK_TYPE_RIGID: _ClassVar[RigidLink.RigidLinkType]
        RIGID_LINK_TYPE_RESILIENT: _ClassVar[RigidLink.RigidLinkType]
    RIGID_LINK_TYPE_RIGID: RigidLink.RigidLinkType
    RIGID_LINK_TYPE_RESILIENT: RigidLink.RigidLinkType
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LINE1_FIELD_NUMBER: _ClassVar[int]
    LINE2_FIELD_NUMBER: _ClassVar[int]
    SURFACE_FIELD_NUMBER: _ClassVar[int]
    RIGID_LINK_TYPE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IGNORE_INFLUENCE_OF_DISTANCE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    LINE1_START_IS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    LINE1_START_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    LINE1_START_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    LINE1_END_IS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    LINE1_END_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    LINE1_END_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    LINE2_START_IS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    LINE2_START_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    LINE2_START_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    LINE2_END_IS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    LINE2_END_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    LINE2_END_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    LINES_FIELD_NUMBER: _ClassVar[int]
    CENTER_NODE_NO_FIELD_NUMBER: _ClassVar[int]
    CENTER_USER_DEFINED_FIELD_NUMBER: _ClassVar[int]
    CENTER_POINT_FIELD_NUMBER: _ClassVar[int]
    CENTER_POINT_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_POINT_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_POINT_Z_FIELD_NUMBER: _ClassVar[int]
    LINK_PLANE_USER_DEFINED_FIELD_NUMBER: _ClassVar[int]
    LINK_PLANE_NODE1_NO_FIELD_NUMBER: _ClassVar[int]
    LINK_PLANE_NODE2_NO_FIELD_NUMBER: _ClassVar[int]
    LINK_PLANE_NODE3_NO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: RigidLink.Type
    line1: int
    line2: int
    surface: int
    rigid_link_type: RigidLink.RigidLinkType
    comment: str
    ignore_influence_of_distance: bool
    user_defined_distribution: bool
    line1_start_is_relative: bool
    line1_start_relative: float
    line1_start_absolute: float
    line1_end_is_relative: bool
    line1_end_relative: float
    line1_end_absolute: float
    line2_start_is_relative: bool
    line2_start_relative: float
    line2_start_absolute: float
    line2_end_is_relative: bool
    line2_end_relative: float
    line2_end_absolute: float
    nodes: _containers.RepeatedScalarFieldContainer[int]
    lines: _containers.RepeatedScalarFieldContainer[int]
    center_node_no: int
    center_user_defined: bool
    center_point: _common_pb2.Vector3d
    center_point_x: float
    center_point_y: float
    center_point_z: float
    link_plane_user_defined: bool
    link_plane_node1_no: int
    link_plane_node2_no: int
    link_plane_node3_no: int
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[RigidLink.Type, str]] = ..., line1: _Optional[int] = ..., line2: _Optional[int] = ..., surface: _Optional[int] = ..., rigid_link_type: _Optional[_Union[RigidLink.RigidLinkType, str]] = ..., comment: _Optional[str] = ..., ignore_influence_of_distance: bool = ..., user_defined_distribution: bool = ..., line1_start_is_relative: bool = ..., line1_start_relative: _Optional[float] = ..., line1_start_absolute: _Optional[float] = ..., line1_end_is_relative: bool = ..., line1_end_relative: _Optional[float] = ..., line1_end_absolute: _Optional[float] = ..., line2_start_is_relative: bool = ..., line2_start_relative: _Optional[float] = ..., line2_start_absolute: _Optional[float] = ..., line2_end_is_relative: bool = ..., line2_end_relative: _Optional[float] = ..., line2_end_absolute: _Optional[float] = ..., nodes: _Optional[_Iterable[int]] = ..., lines: _Optional[_Iterable[int]] = ..., center_node_no: _Optional[int] = ..., center_user_defined: bool = ..., center_point: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_point_x: _Optional[float] = ..., center_point_y: _Optional[float] = ..., center_point_z: _Optional[float] = ..., link_plane_user_defined: bool = ..., link_plane_node1_no: _Optional[int] = ..., link_plane_node2_no: _Optional[int] = ..., link_plane_node3_no: _Optional[int] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
