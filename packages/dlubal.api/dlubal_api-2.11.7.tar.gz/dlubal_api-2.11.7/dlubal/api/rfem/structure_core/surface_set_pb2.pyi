from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SurfaceSet(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "set_type", "surfaces", "surface_area", "volume", "mass", "center_of_gravity", "center_of_gravity_x", "center_of_gravity_y", "center_of_gravity_z", "position", "position_short", "stress_analysis_configuration", "design_properties_activated", "timber_service_class", "timber_moisture_class", "timber_service_conditions", "comment", "is_generated", "generating_object_info", "is_user_defined_concrete_cover_enabled", "concrete_cover_top", "concrete_cover_bottom", "user_defined_concrete_cover_top", "user_defined_concrete_cover_bottom", "concrete_durability_top", "concrete_durability_bottom", "reinforcement_direction_top", "reinforcement_direction_bottom", "surface_reinforcements", "surface_reinforcement_table", "surface_concrete_design_uls_configuration", "surface_concrete_design_sls_configuration", "surface_concrete_design_fr_configuration", "surface_concrete_design_seismic_configuration", "deflection_check_surface_type", "deflection_check_displacement_reference", "deflection_check_reference_length_z", "deflection_check_reference_length_z_definition_type", "deflection_check_reference_plane_point_1", "deflection_check_reference_plane_point_1_x", "deflection_check_reference_plane_point_1_y", "deflection_check_reference_plane_point_1_z", "deflection_check_reference_plane_point_2", "deflection_check_reference_plane_point_2_x", "deflection_check_reference_plane_point_2_y", "deflection_check_reference_plane_point_2_z", "deflection_check_reference_plane_point_3", "deflection_check_reference_plane_point_3_x", "deflection_check_reference_plane_point_3_y", "deflection_check_reference_plane_point_3_z", "surface_timber_design_uls_configuration", "surface_timber_design_sls_configuration", "surface_timber_design_fr_configuration", "id_for_export_import", "metadata_for_export_import")
    class SetType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SET_TYPE_CONTINUOUS: _ClassVar[SurfaceSet.SetType]
        SET_TYPE_GROUP: _ClassVar[SurfaceSet.SetType]
    SET_TYPE_CONTINUOUS: SurfaceSet.SetType
    SET_TYPE_GROUP: SurfaceSet.SetType
    class DeflectionCheckSurfaceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFLECTION_CHECK_SURFACE_TYPE_DOUBLE_SUPPORTED: _ClassVar[SurfaceSet.DeflectionCheckSurfaceType]
        DEFLECTION_CHECK_SURFACE_TYPE_CANTILEVER: _ClassVar[SurfaceSet.DeflectionCheckSurfaceType]
    DEFLECTION_CHECK_SURFACE_TYPE_DOUBLE_SUPPORTED: SurfaceSet.DeflectionCheckSurfaceType
    DEFLECTION_CHECK_SURFACE_TYPE_CANTILEVER: SurfaceSet.DeflectionCheckSurfaceType
    class DeflectionCheckDisplacementReference(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_DEFORMED_USER_DEFINED_REFERENCE_PLANE: _ClassVar[SurfaceSet.DeflectionCheckDisplacementReference]
        DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_PARALLEL_SURFACE: _ClassVar[SurfaceSet.DeflectionCheckDisplacementReference]
        DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_UNDEFORMED_SYSTEM: _ClassVar[SurfaceSet.DeflectionCheckDisplacementReference]
    DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_DEFORMED_USER_DEFINED_REFERENCE_PLANE: SurfaceSet.DeflectionCheckDisplacementReference
    DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_PARALLEL_SURFACE: SurfaceSet.DeflectionCheckDisplacementReference
    DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_UNDEFORMED_SYSTEM: SurfaceSet.DeflectionCheckDisplacementReference
    class DeflectionCheckReferenceLengthZDefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFLECTION_CHECK_REFERENCE_LENGTH_Z_DEFINITION_TYPE_MANUALLY: _ClassVar[SurfaceSet.DeflectionCheckReferenceLengthZDefinitionType]
        DEFLECTION_CHECK_REFERENCE_LENGTH_Z_DEFINITION_TYPE_BY_MAXIMUM_BOUNDARY_LINE: _ClassVar[SurfaceSet.DeflectionCheckReferenceLengthZDefinitionType]
        DEFLECTION_CHECK_REFERENCE_LENGTH_Z_DEFINITION_TYPE_BY_MINIMUM_BOUNDARY_LINE: _ClassVar[SurfaceSet.DeflectionCheckReferenceLengthZDefinitionType]
    DEFLECTION_CHECK_REFERENCE_LENGTH_Z_DEFINITION_TYPE_MANUALLY: SurfaceSet.DeflectionCheckReferenceLengthZDefinitionType
    DEFLECTION_CHECK_REFERENCE_LENGTH_Z_DEFINITION_TYPE_BY_MAXIMUM_BOUNDARY_LINE: SurfaceSet.DeflectionCheckReferenceLengthZDefinitionType
    DEFLECTION_CHECK_REFERENCE_LENGTH_Z_DEFINITION_TYPE_BY_MINIMUM_BOUNDARY_LINE: SurfaceSet.DeflectionCheckReferenceLengthZDefinitionType
    class SurfaceReinforcementTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[SurfaceSet.SurfaceReinforcementTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[SurfaceSet.SurfaceReinforcementTableRow, _Mapping]]] = ...) -> None: ...
    class SurfaceReinforcementTableRow(_message.Message):
        __slots__ = ("no", "description", "surface_reinforcement")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        SURFACE_REINFORCEMENT_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        surface_reinforcement: int
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., surface_reinforcement: _Optional[int] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SET_TYPE_FIELD_NUMBER: _ClassVar[int]
    SURFACES_FIELD_NUMBER: _ClassVar[int]
    SURFACE_AREA_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Z_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    POSITION_SHORT_FIELD_NUMBER: _ClassVar[int]
    STRESS_ANALYSIS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    DESIGN_PROPERTIES_ACTIVATED_FIELD_NUMBER: _ClassVar[int]
    TIMBER_SERVICE_CLASS_FIELD_NUMBER: _ClassVar[int]
    TIMBER_MOISTURE_CLASS_FIELD_NUMBER: _ClassVar[int]
    TIMBER_SERVICE_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_USER_DEFINED_CONCRETE_COVER_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_TOP_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_CONCRETE_COVER_TOP_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_CONCRETE_COVER_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_TOP_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    REINFORCEMENT_DIRECTION_TOP_FIELD_NUMBER: _ClassVar[int]
    REINFORCEMENT_DIRECTION_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    SURFACE_REINFORCEMENTS_FIELD_NUMBER: _ClassVar[int]
    SURFACE_REINFORCEMENT_TABLE_FIELD_NUMBER: _ClassVar[int]
    SURFACE_CONCRETE_DESIGN_ULS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    SURFACE_CONCRETE_DESIGN_SLS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    SURFACE_CONCRETE_DESIGN_FR_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    SURFACE_CONCRETE_DESIGN_SEISMIC_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_SURFACE_TYPE_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_REFERENCE_LENGTH_Z_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_REFERENCE_LENGTH_Z_DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_REFERENCE_PLANE_POINT_1_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_REFERENCE_PLANE_POINT_1_X_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_REFERENCE_PLANE_POINT_1_Y_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_REFERENCE_PLANE_POINT_1_Z_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_REFERENCE_PLANE_POINT_2_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_REFERENCE_PLANE_POINT_2_X_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_REFERENCE_PLANE_POINT_2_Y_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_REFERENCE_PLANE_POINT_2_Z_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_REFERENCE_PLANE_POINT_3_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_REFERENCE_PLANE_POINT_3_X_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_REFERENCE_PLANE_POINT_3_Y_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_REFERENCE_PLANE_POINT_3_Z_FIELD_NUMBER: _ClassVar[int]
    SURFACE_TIMBER_DESIGN_ULS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    SURFACE_TIMBER_DESIGN_SLS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    SURFACE_TIMBER_DESIGN_FR_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    set_type: SurfaceSet.SetType
    surfaces: _containers.RepeatedScalarFieldContainer[int]
    surface_area: float
    volume: float
    mass: float
    center_of_gravity: _common_pb2.Vector3d
    center_of_gravity_x: float
    center_of_gravity_y: float
    center_of_gravity_z: float
    position: str
    position_short: str
    stress_analysis_configuration: int
    design_properties_activated: bool
    timber_service_class: int
    timber_moisture_class: int
    timber_service_conditions: int
    comment: str
    is_generated: bool
    generating_object_info: str
    is_user_defined_concrete_cover_enabled: bool
    concrete_cover_top: float
    concrete_cover_bottom: float
    user_defined_concrete_cover_top: float
    user_defined_concrete_cover_bottom: float
    concrete_durability_top: int
    concrete_durability_bottom: int
    reinforcement_direction_top: int
    reinforcement_direction_bottom: int
    surface_reinforcements: _containers.RepeatedScalarFieldContainer[int]
    surface_reinforcement_table: SurfaceSet.SurfaceReinforcementTable
    surface_concrete_design_uls_configuration: int
    surface_concrete_design_sls_configuration: int
    surface_concrete_design_fr_configuration: int
    surface_concrete_design_seismic_configuration: int
    deflection_check_surface_type: SurfaceSet.DeflectionCheckSurfaceType
    deflection_check_displacement_reference: SurfaceSet.DeflectionCheckDisplacementReference
    deflection_check_reference_length_z: float
    deflection_check_reference_length_z_definition_type: SurfaceSet.DeflectionCheckReferenceLengthZDefinitionType
    deflection_check_reference_plane_point_1: _common_pb2.Vector3d
    deflection_check_reference_plane_point_1_x: float
    deflection_check_reference_plane_point_1_y: float
    deflection_check_reference_plane_point_1_z: float
    deflection_check_reference_plane_point_2: _common_pb2.Vector3d
    deflection_check_reference_plane_point_2_x: float
    deflection_check_reference_plane_point_2_y: float
    deflection_check_reference_plane_point_2_z: float
    deflection_check_reference_plane_point_3: _common_pb2.Vector3d
    deflection_check_reference_plane_point_3_x: float
    deflection_check_reference_plane_point_3_y: float
    deflection_check_reference_plane_point_3_z: float
    surface_timber_design_uls_configuration: int
    surface_timber_design_sls_configuration: int
    surface_timber_design_fr_configuration: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., set_type: _Optional[_Union[SurfaceSet.SetType, str]] = ..., surfaces: _Optional[_Iterable[int]] = ..., surface_area: _Optional[float] = ..., volume: _Optional[float] = ..., mass: _Optional[float] = ..., center_of_gravity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_of_gravity_x: _Optional[float] = ..., center_of_gravity_y: _Optional[float] = ..., center_of_gravity_z: _Optional[float] = ..., position: _Optional[str] = ..., position_short: _Optional[str] = ..., stress_analysis_configuration: _Optional[int] = ..., design_properties_activated: bool = ..., timber_service_class: _Optional[int] = ..., timber_moisture_class: _Optional[int] = ..., timber_service_conditions: _Optional[int] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., is_user_defined_concrete_cover_enabled: bool = ..., concrete_cover_top: _Optional[float] = ..., concrete_cover_bottom: _Optional[float] = ..., user_defined_concrete_cover_top: _Optional[float] = ..., user_defined_concrete_cover_bottom: _Optional[float] = ..., concrete_durability_top: _Optional[int] = ..., concrete_durability_bottom: _Optional[int] = ..., reinforcement_direction_top: _Optional[int] = ..., reinforcement_direction_bottom: _Optional[int] = ..., surface_reinforcements: _Optional[_Iterable[int]] = ..., surface_reinforcement_table: _Optional[_Union[SurfaceSet.SurfaceReinforcementTable, _Mapping]] = ..., surface_concrete_design_uls_configuration: _Optional[int] = ..., surface_concrete_design_sls_configuration: _Optional[int] = ..., surface_concrete_design_fr_configuration: _Optional[int] = ..., surface_concrete_design_seismic_configuration: _Optional[int] = ..., deflection_check_surface_type: _Optional[_Union[SurfaceSet.DeflectionCheckSurfaceType, str]] = ..., deflection_check_displacement_reference: _Optional[_Union[SurfaceSet.DeflectionCheckDisplacementReference, str]] = ..., deflection_check_reference_length_z: _Optional[float] = ..., deflection_check_reference_length_z_definition_type: _Optional[_Union[SurfaceSet.DeflectionCheckReferenceLengthZDefinitionType, str]] = ..., deflection_check_reference_plane_point_1: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., deflection_check_reference_plane_point_1_x: _Optional[float] = ..., deflection_check_reference_plane_point_1_y: _Optional[float] = ..., deflection_check_reference_plane_point_1_z: _Optional[float] = ..., deflection_check_reference_plane_point_2: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., deflection_check_reference_plane_point_2_x: _Optional[float] = ..., deflection_check_reference_plane_point_2_y: _Optional[float] = ..., deflection_check_reference_plane_point_2_z: _Optional[float] = ..., deflection_check_reference_plane_point_3: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., deflection_check_reference_plane_point_3_x: _Optional[float] = ..., deflection_check_reference_plane_point_3_y: _Optional[float] = ..., deflection_check_reference_plane_point_3_z: _Optional[float] = ..., surface_timber_design_uls_configuration: _Optional[int] = ..., surface_timber_design_sls_configuration: _Optional[int] = ..., surface_timber_design_fr_configuration: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
