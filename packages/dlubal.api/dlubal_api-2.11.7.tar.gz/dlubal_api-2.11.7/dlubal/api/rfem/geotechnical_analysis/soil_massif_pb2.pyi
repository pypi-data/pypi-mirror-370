from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SoilMassif(_message.Message):
    __slots__ = ("no", "type", "user_defined_name_enabled", "name", "assigned_to_type", "assigned_to_boreholes", "assigned_to_solids", "assigned_to_solid_sets", "assigned_to_solids_and_solid_sets", "topology_type", "depth_according_to_boreholes", "diameter_for_circle_topology", "boundary_lines_for_polygon_topology", "center_x", "center_y", "size", "size_x", "size_y", "size_z", "rotation_about_z", "groundwater", "groundwater_surface", "analysis_type", "mapped_mesh_under_surfaces", "surfaces_for_mapped_mesh", "user_defined_gradient_enabled", "gradient_of_size_increase_in_depth", "rock_beneath_last_layer", "depth_of_influence_zone_type", "depth_of_influence_zone", "comment", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_PHANTOM: _ClassVar[SoilMassif.Type]
        TYPE_STANDARD: _ClassVar[SoilMassif.Type]
    TYPE_PHANTOM: SoilMassif.Type
    TYPE_STANDARD: SoilMassif.Type
    class AssignedToType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ASSIGNED_TO_TYPE_BOREHOLES: _ClassVar[SoilMassif.AssignedToType]
        ASSIGNED_TO_TYPE_SOIL_SOLIDS: _ClassVar[SoilMassif.AssignedToType]
    ASSIGNED_TO_TYPE_BOREHOLES: SoilMassif.AssignedToType
    ASSIGNED_TO_TYPE_SOIL_SOLIDS: SoilMassif.AssignedToType
    class TopologyType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TOPOLOGY_TYPE_RECTANGLE: _ClassVar[SoilMassif.TopologyType]
        TOPOLOGY_TYPE_CIRCLE: _ClassVar[SoilMassif.TopologyType]
        TOPOLOGY_TYPE_POLYGON: _ClassVar[SoilMassif.TopologyType]
        TOPOLOGY_TYPE_POLYGON_FROM_POINTS: _ClassVar[SoilMassif.TopologyType]
    TOPOLOGY_TYPE_RECTANGLE: SoilMassif.TopologyType
    TOPOLOGY_TYPE_CIRCLE: SoilMassif.TopologyType
    TOPOLOGY_TYPE_POLYGON: SoilMassif.TopologyType
    TOPOLOGY_TYPE_POLYGON_FROM_POINTS: SoilMassif.TopologyType
    class AnalysisType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ANALYSIS_TYPE_FINITE_ELEMENT_METHOD: _ClassVar[SoilMassif.AnalysisType]
        ANALYSIS_TYPE_CONSTRAINED_MODULUS_METHOD: _ClassVar[SoilMassif.AnalysisType]
        ANALYSIS_TYPE_SUBGRADE_REACTION_MODEL: _ClassVar[SoilMassif.AnalysisType]
    ANALYSIS_TYPE_FINITE_ELEMENT_METHOD: SoilMassif.AnalysisType
    ANALYSIS_TYPE_CONSTRAINED_MODULUS_METHOD: SoilMassif.AnalysisType
    ANALYSIS_TYPE_SUBGRADE_REACTION_MODEL: SoilMassif.AnalysisType
    class DepthOfInfluenceZoneType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEPTH_OF_INFLUENCE_ZONE_TYPE_MANUALLY: _ClassVar[SoilMassif.DepthOfInfluenceZoneType]
        DEPTH_OF_INFLUENCE_ZONE_TYPE_AUTOMATICALLY: _ClassVar[SoilMassif.DepthOfInfluenceZoneType]
    DEPTH_OF_INFLUENCE_ZONE_TYPE_MANUALLY: SoilMassif.DepthOfInfluenceZoneType
    DEPTH_OF_INFLUENCE_ZONE_TYPE_AUTOMATICALLY: SoilMassif.DepthOfInfluenceZoneType
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_TYPE_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_BOREHOLES_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_SOLIDS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_SOLID_SETS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_SOLIDS_AND_SOLID_SETS_FIELD_NUMBER: _ClassVar[int]
    TOPOLOGY_TYPE_FIELD_NUMBER: _ClassVar[int]
    DEPTH_ACCORDING_TO_BOREHOLES_FIELD_NUMBER: _ClassVar[int]
    DIAMETER_FOR_CIRCLE_TOPOLOGY_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_LINES_FOR_POLYGON_TOPOLOGY_FIELD_NUMBER: _ClassVar[int]
    CENTER_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_Y_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    SIZE_X_FIELD_NUMBER: _ClassVar[int]
    SIZE_Y_FIELD_NUMBER: _ClassVar[int]
    SIZE_Z_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ABOUT_Z_FIELD_NUMBER: _ClassVar[int]
    GROUNDWATER_FIELD_NUMBER: _ClassVar[int]
    GROUNDWATER_SURFACE_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    MAPPED_MESH_UNDER_SURFACES_FIELD_NUMBER: _ClassVar[int]
    SURFACES_FOR_MAPPED_MESH_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_GRADIENT_ENABLED_FIELD_NUMBER: _ClassVar[int]
    GRADIENT_OF_SIZE_INCREASE_IN_DEPTH_FIELD_NUMBER: _ClassVar[int]
    ROCK_BENEATH_LAST_LAYER_FIELD_NUMBER: _ClassVar[int]
    DEPTH_OF_INFLUENCE_ZONE_TYPE_FIELD_NUMBER: _ClassVar[int]
    DEPTH_OF_INFLUENCE_ZONE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: SoilMassif.Type
    user_defined_name_enabled: bool
    name: str
    assigned_to_type: SoilMassif.AssignedToType
    assigned_to_boreholes: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_solids: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_solid_sets: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_solids_and_solid_sets: str
    topology_type: SoilMassif.TopologyType
    depth_according_to_boreholes: bool
    diameter_for_circle_topology: float
    boundary_lines_for_polygon_topology: _containers.RepeatedScalarFieldContainer[int]
    center_x: float
    center_y: float
    size: _common_pb2.Vector3d
    size_x: float
    size_y: float
    size_z: float
    rotation_about_z: float
    groundwater: bool
    groundwater_surface: int
    analysis_type: SoilMassif.AnalysisType
    mapped_mesh_under_surfaces: bool
    surfaces_for_mapped_mesh: _containers.RepeatedScalarFieldContainer[int]
    user_defined_gradient_enabled: bool
    gradient_of_size_increase_in_depth: float
    rock_beneath_last_layer: bool
    depth_of_influence_zone_type: SoilMassif.DepthOfInfluenceZoneType
    depth_of_influence_zone: float
    comment: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[SoilMassif.Type, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., assigned_to_type: _Optional[_Union[SoilMassif.AssignedToType, str]] = ..., assigned_to_boreholes: _Optional[_Iterable[int]] = ..., assigned_to_solids: _Optional[_Iterable[int]] = ..., assigned_to_solid_sets: _Optional[_Iterable[int]] = ..., assigned_to_solids_and_solid_sets: _Optional[str] = ..., topology_type: _Optional[_Union[SoilMassif.TopologyType, str]] = ..., depth_according_to_boreholes: bool = ..., diameter_for_circle_topology: _Optional[float] = ..., boundary_lines_for_polygon_topology: _Optional[_Iterable[int]] = ..., center_x: _Optional[float] = ..., center_y: _Optional[float] = ..., size: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., size_x: _Optional[float] = ..., size_y: _Optional[float] = ..., size_z: _Optional[float] = ..., rotation_about_z: _Optional[float] = ..., groundwater: bool = ..., groundwater_surface: _Optional[int] = ..., analysis_type: _Optional[_Union[SoilMassif.AnalysisType, str]] = ..., mapped_mesh_under_surfaces: bool = ..., surfaces_for_mapped_mesh: _Optional[_Iterable[int]] = ..., user_defined_gradient_enabled: bool = ..., gradient_of_size_increase_in_depth: _Optional[float] = ..., rock_beneath_last_layer: bool = ..., depth_of_influence_zone_type: _Optional[_Union[SoilMassif.DepthOfInfluenceZoneType, str]] = ..., depth_of_influence_zone: _Optional[float] = ..., comment: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
