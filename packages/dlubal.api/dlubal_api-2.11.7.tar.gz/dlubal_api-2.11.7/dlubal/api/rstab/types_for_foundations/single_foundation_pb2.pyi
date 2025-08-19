from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SingleFoundation(_message.Message):
    __slots__ = ("all_nodes_to_design", "angle_of_soil_friction", "angle_of_wall_friction", "bucket_block_reinforcement_automatically_enabled", "bucket_material", "comment", "concrete_cover", "concrete_cover_bucket_or_block", "concrete_cover_different_at_section_sides_enabled", "concrete_cover_min", "concrete_cover_min_bucket_or_block", "concrete_cover_min_surface_bottom", "concrete_cover_min_surface_side", "concrete_cover_min_surface_top", "concrete_cover_surface_bottom", "concrete_cover_surface_side", "concrete_cover_surface_top", "concrete_cover_user_defined_enabled", "concrete_design_configuration", "concrete_durability", "concrete_durability_bucket", "concrete_durability_surface_bottom", "concrete_durability_surface_side", "concrete_durability_surface_top", "design_properties_enabled", "earth_covering_thickness", "foundation_type", "generated_by", "geotechnical_design_configuration", "groundwater_enabled", "groundwater_level", "horizontal_stirrups_type", "is_generated", "name", "no", "nodal_supports", "nodes_removed_from_design", "nodes_to_design", "not_valid_deactivated_nodes", "plate_material", "plate_reinforcement_automatically_enabled", "reinforcement_material", "reinforcement_type", "selected_nodes", "soil_definition_type", "soil_layer_bottom", "soil_layer_middle", "soil_layer_top", "subsoil_condition_type", "to_design", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class AngleOfSoilFriction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ANGLE_OF_SOIL_FRICTION_CAST_IN_SITU_CONCRETE_FOUNDATION: _ClassVar[SingleFoundation.AngleOfSoilFriction]
        ANGLE_OF_SOIL_FRICTION_SMOOTH_PRECAST_FOUNDATION: _ClassVar[SingleFoundation.AngleOfSoilFriction]
    ANGLE_OF_SOIL_FRICTION_CAST_IN_SITU_CONCRETE_FOUNDATION: SingleFoundation.AngleOfSoilFriction
    ANGLE_OF_SOIL_FRICTION_SMOOTH_PRECAST_FOUNDATION: SingleFoundation.AngleOfSoilFriction
    class AngleOfWallFriction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ANGLE_OF_WALL_FRICTION_UNIMPROVED_FOUNDATION_WALL: _ClassVar[SingleFoundation.AngleOfWallFriction]
        ANGLE_OF_WALL_FRICTION_ROUGH_FOUNDATION_WALL: _ClassVar[SingleFoundation.AngleOfWallFriction]
        ANGLE_OF_WALL_FRICTION_SMOOTH_FOUNDATION_WALL: _ClassVar[SingleFoundation.AngleOfWallFriction]
    ANGLE_OF_WALL_FRICTION_UNIMPROVED_FOUNDATION_WALL: SingleFoundation.AngleOfWallFriction
    ANGLE_OF_WALL_FRICTION_ROUGH_FOUNDATION_WALL: SingleFoundation.AngleOfWallFriction
    ANGLE_OF_WALL_FRICTION_SMOOTH_FOUNDATION_WALL: SingleFoundation.AngleOfWallFriction
    class FoundationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FOUNDATION_TYPE_UNKNOWN: _ClassVar[SingleFoundation.FoundationType]
        FOUNDATION_TYPE_BLOCK_FOUNDATION_WITH_ROUGH_BUCKET_SIDES: _ClassVar[SingleFoundation.FoundationType]
        FOUNDATION_TYPE_BLOCK_FOUNDATION_WITH_SMOOTH_BUCKET_SIDES: _ClassVar[SingleFoundation.FoundationType]
        FOUNDATION_TYPE_BUCKET_FOUNDATION_WITH_ROUGH_BUCKET_SIDES: _ClassVar[SingleFoundation.FoundationType]
        FOUNDATION_TYPE_BUCKET_FOUNDATION_WITH_SMOOTH_BUCKET_SIDES: _ClassVar[SingleFoundation.FoundationType]
        FOUNDATION_TYPE_FOUNDATION_PLATE: _ClassVar[SingleFoundation.FoundationType]
        FOUNDATION_TYPE_FOUNDATION_PLATE_WITHOUT_REINFORCEMENT: _ClassVar[SingleFoundation.FoundationType]
        FOUNDATION_TYPE_STEPPED_FOUNDATION: _ClassVar[SingleFoundation.FoundationType]
        FOUNDATION_TYPE_STEPPED_FOUNDATION_WITHOUT_REINFORCEMENT: _ClassVar[SingleFoundation.FoundationType]
    FOUNDATION_TYPE_UNKNOWN: SingleFoundation.FoundationType
    FOUNDATION_TYPE_BLOCK_FOUNDATION_WITH_ROUGH_BUCKET_SIDES: SingleFoundation.FoundationType
    FOUNDATION_TYPE_BLOCK_FOUNDATION_WITH_SMOOTH_BUCKET_SIDES: SingleFoundation.FoundationType
    FOUNDATION_TYPE_BUCKET_FOUNDATION_WITH_ROUGH_BUCKET_SIDES: SingleFoundation.FoundationType
    FOUNDATION_TYPE_BUCKET_FOUNDATION_WITH_SMOOTH_BUCKET_SIDES: SingleFoundation.FoundationType
    FOUNDATION_TYPE_FOUNDATION_PLATE: SingleFoundation.FoundationType
    FOUNDATION_TYPE_FOUNDATION_PLATE_WITHOUT_REINFORCEMENT: SingleFoundation.FoundationType
    FOUNDATION_TYPE_STEPPED_FOUNDATION: SingleFoundation.FoundationType
    FOUNDATION_TYPE_STEPPED_FOUNDATION_WITHOUT_REINFORCEMENT: SingleFoundation.FoundationType
    class HorizontalStirrupsType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        HORIZONTAL_STIRRUPS_TYPE_ENCLOSING_COLUMN: _ClassVar[SingleFoundation.HorizontalStirrupsType]
        HORIZONTAL_STIRRUPS_TYPE_ENTIRELY_LOCATED_IN_BUCKET_WALL: _ClassVar[SingleFoundation.HorizontalStirrupsType]
    HORIZONTAL_STIRRUPS_TYPE_ENCLOSING_COLUMN: SingleFoundation.HorizontalStirrupsType
    HORIZONTAL_STIRRUPS_TYPE_ENTIRELY_LOCATED_IN_BUCKET_WALL: SingleFoundation.HorizontalStirrupsType
    class ReinforcementType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REINFORCEMENT_TYPE_MESH_AND_REBARS: _ClassVar[SingleFoundation.ReinforcementType]
        REINFORCEMENT_TYPE_MESH: _ClassVar[SingleFoundation.ReinforcementType]
        REINFORCEMENT_TYPE_REBARS: _ClassVar[SingleFoundation.ReinforcementType]
    REINFORCEMENT_TYPE_MESH_AND_REBARS: SingleFoundation.ReinforcementType
    REINFORCEMENT_TYPE_MESH: SingleFoundation.ReinforcementType
    REINFORCEMENT_TYPE_REBARS: SingleFoundation.ReinforcementType
    class SoilDefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SOIL_DEFINITION_TYPE_SINGLE_LAYERED: _ClassVar[SingleFoundation.SoilDefinitionType]
    SOIL_DEFINITION_TYPE_SINGLE_LAYERED: SingleFoundation.SoilDefinitionType
    class SubsoilConditionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUBSOIL_CONDITION_TYPE_DRAINED: _ClassVar[SingleFoundation.SubsoilConditionType]
        SUBSOIL_CONDITION_TYPE_UNDRAINED: _ClassVar[SingleFoundation.SubsoilConditionType]
    SUBSOIL_CONDITION_TYPE_DRAINED: SingleFoundation.SubsoilConditionType
    SUBSOIL_CONDITION_TYPE_UNDRAINED: SingleFoundation.SubsoilConditionType
    ALL_NODES_TO_DESIGN_FIELD_NUMBER: _ClassVar[int]
    ANGLE_OF_SOIL_FRICTION_FIELD_NUMBER: _ClassVar[int]
    ANGLE_OF_WALL_FRICTION_FIELD_NUMBER: _ClassVar[int]
    BUCKET_BLOCK_REINFORCEMENT_AUTOMATICALLY_ENABLED_FIELD_NUMBER: _ClassVar[int]
    BUCKET_MATERIAL_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_BUCKET_OR_BLOCK_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_DIFFERENT_AT_SECTION_SIDES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_MIN_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_MIN_BUCKET_OR_BLOCK_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_MIN_SURFACE_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_MIN_SURFACE_SIDE_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_MIN_SURFACE_TOP_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_SURFACE_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_SURFACE_SIDE_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_SURFACE_TOP_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_USER_DEFINED_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DESIGN_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_BUCKET_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_SURFACE_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_SURFACE_SIDE_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_SURFACE_TOP_FIELD_NUMBER: _ClassVar[int]
    DESIGN_PROPERTIES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    EARTH_COVERING_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    FOUNDATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    GENERATED_BY_FIELD_NUMBER: _ClassVar[int]
    GEOTECHNICAL_DESIGN_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    GROUNDWATER_ENABLED_FIELD_NUMBER: _ClassVar[int]
    GROUNDWATER_LEVEL_FIELD_NUMBER: _ClassVar[int]
    HORIZONTAL_STIRRUPS_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    NODAL_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    NODES_REMOVED_FROM_DESIGN_FIELD_NUMBER: _ClassVar[int]
    NODES_TO_DESIGN_FIELD_NUMBER: _ClassVar[int]
    NOT_VALID_DEACTIVATED_NODES_FIELD_NUMBER: _ClassVar[int]
    PLATE_MATERIAL_FIELD_NUMBER: _ClassVar[int]
    PLATE_REINFORCEMENT_AUTOMATICALLY_ENABLED_FIELD_NUMBER: _ClassVar[int]
    REINFORCEMENT_MATERIAL_FIELD_NUMBER: _ClassVar[int]
    REINFORCEMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SELECTED_NODES_FIELD_NUMBER: _ClassVar[int]
    SOIL_DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOIL_LAYER_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    SOIL_LAYER_MIDDLE_FIELD_NUMBER: _ClassVar[int]
    SOIL_LAYER_TOP_FIELD_NUMBER: _ClassVar[int]
    SUBSOIL_CONDITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    TO_DESIGN_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    all_nodes_to_design: bool
    angle_of_soil_friction: SingleFoundation.AngleOfSoilFriction
    angle_of_wall_friction: SingleFoundation.AngleOfWallFriction
    bucket_block_reinforcement_automatically_enabled: bool
    bucket_material: int
    comment: str
    concrete_cover: float
    concrete_cover_bucket_or_block: float
    concrete_cover_different_at_section_sides_enabled: bool
    concrete_cover_min: float
    concrete_cover_min_bucket_or_block: float
    concrete_cover_min_surface_bottom: float
    concrete_cover_min_surface_side: float
    concrete_cover_min_surface_top: float
    concrete_cover_surface_bottom: float
    concrete_cover_surface_side: float
    concrete_cover_surface_top: float
    concrete_cover_user_defined_enabled: bool
    concrete_design_configuration: int
    concrete_durability: int
    concrete_durability_bucket: int
    concrete_durability_surface_bottom: int
    concrete_durability_surface_side: int
    concrete_durability_surface_top: int
    design_properties_enabled: bool
    earth_covering_thickness: float
    foundation_type: SingleFoundation.FoundationType
    generated_by: str
    geotechnical_design_configuration: int
    groundwater_enabled: bool
    groundwater_level: float
    horizontal_stirrups_type: SingleFoundation.HorizontalStirrupsType
    is_generated: bool
    name: str
    no: int
    nodal_supports: _containers.RepeatedScalarFieldContainer[int]
    nodes_removed_from_design: _containers.RepeatedScalarFieldContainer[int]
    nodes_to_design: _containers.RepeatedScalarFieldContainer[int]
    not_valid_deactivated_nodes: _containers.RepeatedScalarFieldContainer[int]
    plate_material: int
    plate_reinforcement_automatically_enabled: bool
    reinforcement_material: int
    reinforcement_type: SingleFoundation.ReinforcementType
    selected_nodes: _containers.RepeatedScalarFieldContainer[int]
    soil_definition_type: SingleFoundation.SoilDefinitionType
    soil_layer_bottom: int
    soil_layer_middle: int
    soil_layer_top: int
    subsoil_condition_type: SingleFoundation.SubsoilConditionType
    to_design: bool
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, all_nodes_to_design: bool = ..., angle_of_soil_friction: _Optional[_Union[SingleFoundation.AngleOfSoilFriction, str]] = ..., angle_of_wall_friction: _Optional[_Union[SingleFoundation.AngleOfWallFriction, str]] = ..., bucket_block_reinforcement_automatically_enabled: bool = ..., bucket_material: _Optional[int] = ..., comment: _Optional[str] = ..., concrete_cover: _Optional[float] = ..., concrete_cover_bucket_or_block: _Optional[float] = ..., concrete_cover_different_at_section_sides_enabled: bool = ..., concrete_cover_min: _Optional[float] = ..., concrete_cover_min_bucket_or_block: _Optional[float] = ..., concrete_cover_min_surface_bottom: _Optional[float] = ..., concrete_cover_min_surface_side: _Optional[float] = ..., concrete_cover_min_surface_top: _Optional[float] = ..., concrete_cover_surface_bottom: _Optional[float] = ..., concrete_cover_surface_side: _Optional[float] = ..., concrete_cover_surface_top: _Optional[float] = ..., concrete_cover_user_defined_enabled: bool = ..., concrete_design_configuration: _Optional[int] = ..., concrete_durability: _Optional[int] = ..., concrete_durability_bucket: _Optional[int] = ..., concrete_durability_surface_bottom: _Optional[int] = ..., concrete_durability_surface_side: _Optional[int] = ..., concrete_durability_surface_top: _Optional[int] = ..., design_properties_enabled: bool = ..., earth_covering_thickness: _Optional[float] = ..., foundation_type: _Optional[_Union[SingleFoundation.FoundationType, str]] = ..., generated_by: _Optional[str] = ..., geotechnical_design_configuration: _Optional[int] = ..., groundwater_enabled: bool = ..., groundwater_level: _Optional[float] = ..., horizontal_stirrups_type: _Optional[_Union[SingleFoundation.HorizontalStirrupsType, str]] = ..., is_generated: bool = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., nodal_supports: _Optional[_Iterable[int]] = ..., nodes_removed_from_design: _Optional[_Iterable[int]] = ..., nodes_to_design: _Optional[_Iterable[int]] = ..., not_valid_deactivated_nodes: _Optional[_Iterable[int]] = ..., plate_material: _Optional[int] = ..., plate_reinforcement_automatically_enabled: bool = ..., reinforcement_material: _Optional[int] = ..., reinforcement_type: _Optional[_Union[SingleFoundation.ReinforcementType, str]] = ..., selected_nodes: _Optional[_Iterable[int]] = ..., soil_definition_type: _Optional[_Union[SingleFoundation.SoilDefinitionType, str]] = ..., soil_layer_bottom: _Optional[int] = ..., soil_layer_middle: _Optional[int] = ..., soil_layer_top: _Optional[int] = ..., subsoil_condition_type: _Optional[_Union[SingleFoundation.SubsoilConditionType, str]] = ..., to_design: bool = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
