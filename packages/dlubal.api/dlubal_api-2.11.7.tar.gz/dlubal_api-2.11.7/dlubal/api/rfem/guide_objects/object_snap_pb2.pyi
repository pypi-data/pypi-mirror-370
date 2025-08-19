from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ObjectSnap(_message.Message):
    __slots__ = ("no", "type", "user_defined_name_enabled", "name", "snap_nodes", "snap_centers_and_focuses", "snap_intersections", "snap_perpendicular", "snap_extend", "snap_parallel", "snap_tangent", "snap_quadrants", "snap_parts", "snap_absolute_distance", "snap_relative_distance", "snap_snappable_points_only", "snap_guidelines", "snap_background_layers", "snap_building_grids", "comment", "parts_count", "absolute_distance", "relative_distance", "absolute_distance_on_section_edge", "parts_of_section_edge_count", "relative_distance_on_section_edge", "snap_absolute_distance_on_section_edge", "snap_corners", "snap_middle_edge", "snap_parts_of_section_edge", "snap_relative_distance_on_section_edge", "snap_surface_thickness_points", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[ObjectSnap.Type]
        TYPE_STANDARD: _ClassVar[ObjectSnap.Type]
    TYPE_UNKNOWN: ObjectSnap.Type
    TYPE_STANDARD: ObjectSnap.Type
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SNAP_NODES_FIELD_NUMBER: _ClassVar[int]
    SNAP_CENTERS_AND_FOCUSES_FIELD_NUMBER: _ClassVar[int]
    SNAP_INTERSECTIONS_FIELD_NUMBER: _ClassVar[int]
    SNAP_PERPENDICULAR_FIELD_NUMBER: _ClassVar[int]
    SNAP_EXTEND_FIELD_NUMBER: _ClassVar[int]
    SNAP_PARALLEL_FIELD_NUMBER: _ClassVar[int]
    SNAP_TANGENT_FIELD_NUMBER: _ClassVar[int]
    SNAP_QUADRANTS_FIELD_NUMBER: _ClassVar[int]
    SNAP_PARTS_FIELD_NUMBER: _ClassVar[int]
    SNAP_ABSOLUTE_DISTANCE_FIELD_NUMBER: _ClassVar[int]
    SNAP_RELATIVE_DISTANCE_FIELD_NUMBER: _ClassVar[int]
    SNAP_SNAPPABLE_POINTS_ONLY_FIELD_NUMBER: _ClassVar[int]
    SNAP_GUIDELINES_FIELD_NUMBER: _ClassVar[int]
    SNAP_BACKGROUND_LAYERS_FIELD_NUMBER: _ClassVar[int]
    SNAP_BUILDING_GRIDS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    PARTS_COUNT_FIELD_NUMBER: _ClassVar[int]
    ABSOLUTE_DISTANCE_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_DISTANCE_FIELD_NUMBER: _ClassVar[int]
    ABSOLUTE_DISTANCE_ON_SECTION_EDGE_FIELD_NUMBER: _ClassVar[int]
    PARTS_OF_SECTION_EDGE_COUNT_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_DISTANCE_ON_SECTION_EDGE_FIELD_NUMBER: _ClassVar[int]
    SNAP_ABSOLUTE_DISTANCE_ON_SECTION_EDGE_FIELD_NUMBER: _ClassVar[int]
    SNAP_CORNERS_FIELD_NUMBER: _ClassVar[int]
    SNAP_MIDDLE_EDGE_FIELD_NUMBER: _ClassVar[int]
    SNAP_PARTS_OF_SECTION_EDGE_FIELD_NUMBER: _ClassVar[int]
    SNAP_RELATIVE_DISTANCE_ON_SECTION_EDGE_FIELD_NUMBER: _ClassVar[int]
    SNAP_SURFACE_THICKNESS_POINTS_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: ObjectSnap.Type
    user_defined_name_enabled: bool
    name: str
    snap_nodes: bool
    snap_centers_and_focuses: bool
    snap_intersections: bool
    snap_perpendicular: bool
    snap_extend: bool
    snap_parallel: bool
    snap_tangent: bool
    snap_quadrants: bool
    snap_parts: bool
    snap_absolute_distance: bool
    snap_relative_distance: bool
    snap_snappable_points_only: bool
    snap_guidelines: bool
    snap_background_layers: bool
    snap_building_grids: bool
    comment: str
    parts_count: int
    absolute_distance: float
    relative_distance: float
    absolute_distance_on_section_edge: float
    parts_of_section_edge_count: int
    relative_distance_on_section_edge: float
    snap_absolute_distance_on_section_edge: bool
    snap_corners: bool
    snap_middle_edge: bool
    snap_parts_of_section_edge: bool
    snap_relative_distance_on_section_edge: bool
    snap_surface_thickness_points: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[ObjectSnap.Type, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., snap_nodes: bool = ..., snap_centers_and_focuses: bool = ..., snap_intersections: bool = ..., snap_perpendicular: bool = ..., snap_extend: bool = ..., snap_parallel: bool = ..., snap_tangent: bool = ..., snap_quadrants: bool = ..., snap_parts: bool = ..., snap_absolute_distance: bool = ..., snap_relative_distance: bool = ..., snap_snappable_points_only: bool = ..., snap_guidelines: bool = ..., snap_background_layers: bool = ..., snap_building_grids: bool = ..., comment: _Optional[str] = ..., parts_count: _Optional[int] = ..., absolute_distance: _Optional[float] = ..., relative_distance: _Optional[float] = ..., absolute_distance_on_section_edge: _Optional[float] = ..., parts_of_section_edge_count: _Optional[int] = ..., relative_distance_on_section_edge: _Optional[float] = ..., snap_absolute_distance_on_section_edge: bool = ..., snap_corners: bool = ..., snap_middle_edge: bool = ..., snap_parts_of_section_edge: bool = ..., snap_relative_distance_on_section_edge: bool = ..., snap_surface_thickness_points: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
