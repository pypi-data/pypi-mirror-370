from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DesignStripWizard(_message.Message):
    __slots__ = ("analytical_area", "analytical_center_of_gravity", "analytical_center_of_gravity_x", "analytical_center_of_gravity_y", "analytical_center_of_gravity_z", "analytical_length", "analytical_mass", "analytical_volume", "area", "building_grid", "center_of_gravity", "center_of_gravity_x", "center_of_gravity_y", "center_of_gravity_z", "comment", "enable_column_strip_type", "enable_middle_strip_type", "enable_primary_reinforcement_direction", "enable_secondary_reinforcement_direction", "enable_user_defined_strip_width", "generating_object_info", "grid_plane", "is_generated", "length", "mass", "name", "no", "primary_reinforcement_direction", "secondary_reinforcement_direction", "surfaces", "type", "user_defined_name_enabled", "user_defined_strip_width", "volume", "id_for_export_import", "metadata_for_export_import")
    class GridPlane(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        GRID_PLANE_XY: _ClassVar[DesignStripWizard.GridPlane]
        GRID_PLANE_XZ: _ClassVar[DesignStripWizard.GridPlane]
        GRID_PLANE_YZ: _ClassVar[DesignStripWizard.GridPlane]
    GRID_PLANE_XY: DesignStripWizard.GridPlane
    GRID_PLANE_XZ: DesignStripWizard.GridPlane
    GRID_PLANE_YZ: DesignStripWizard.GridPlane
    class PrimaryReinforcementDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PRIMARY_REINFORCEMENT_DIRECTION_X: _ClassVar[DesignStripWizard.PrimaryReinforcementDirection]
        PRIMARY_REINFORCEMENT_DIRECTION_Y: _ClassVar[DesignStripWizard.PrimaryReinforcementDirection]
        PRIMARY_REINFORCEMENT_DIRECTION_Z: _ClassVar[DesignStripWizard.PrimaryReinforcementDirection]
    PRIMARY_REINFORCEMENT_DIRECTION_X: DesignStripWizard.PrimaryReinforcementDirection
    PRIMARY_REINFORCEMENT_DIRECTION_Y: DesignStripWizard.PrimaryReinforcementDirection
    PRIMARY_REINFORCEMENT_DIRECTION_Z: DesignStripWizard.PrimaryReinforcementDirection
    class SecondaryReinforcementDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SECONDARY_REINFORCEMENT_DIRECTION_X: _ClassVar[DesignStripWizard.SecondaryReinforcementDirection]
        SECONDARY_REINFORCEMENT_DIRECTION_Y: _ClassVar[DesignStripWizard.SecondaryReinforcementDirection]
        SECONDARY_REINFORCEMENT_DIRECTION_Z: _ClassVar[DesignStripWizard.SecondaryReinforcementDirection]
    SECONDARY_REINFORCEMENT_DIRECTION_X: DesignStripWizard.SecondaryReinforcementDirection
    SECONDARY_REINFORCEMENT_DIRECTION_Y: DesignStripWizard.SecondaryReinforcementDirection
    SECONDARY_REINFORCEMENT_DIRECTION_Z: DesignStripWizard.SecondaryReinforcementDirection
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[DesignStripWizard.Type]
        TYPE_STANDARD: _ClassVar[DesignStripWizard.Type]
    TYPE_UNKNOWN: DesignStripWizard.Type
    TYPE_STANDARD: DesignStripWizard.Type
    ANALYTICAL_AREA_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_CENTER_OF_GRAVITY_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_CENTER_OF_GRAVITY_X_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_CENTER_OF_GRAVITY_Z_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_LENGTH_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_MASS_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_VOLUME_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    BUILDING_GRID_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Z_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ENABLE_COLUMN_STRIP_TYPE_FIELD_NUMBER: _ClassVar[int]
    ENABLE_MIDDLE_STRIP_TYPE_FIELD_NUMBER: _ClassVar[int]
    ENABLE_PRIMARY_REINFORCEMENT_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    ENABLE_SECONDARY_REINFORCEMENT_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    ENABLE_USER_DEFINED_STRIP_WIDTH_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    GRID_PLANE_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_REINFORCEMENT_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_REINFORCEMENT_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    SURFACES_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_STRIP_WIDTH_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    analytical_area: float
    analytical_center_of_gravity: _common_pb2.Vector3d
    analytical_center_of_gravity_x: float
    analytical_center_of_gravity_y: float
    analytical_center_of_gravity_z: float
    analytical_length: float
    analytical_mass: float
    analytical_volume: float
    area: float
    building_grid: int
    center_of_gravity: _common_pb2.Vector3d
    center_of_gravity_x: float
    center_of_gravity_y: float
    center_of_gravity_z: float
    comment: str
    enable_column_strip_type: bool
    enable_middle_strip_type: bool
    enable_primary_reinforcement_direction: bool
    enable_secondary_reinforcement_direction: bool
    enable_user_defined_strip_width: bool
    generating_object_info: str
    grid_plane: DesignStripWizard.GridPlane
    is_generated: bool
    length: float
    mass: float
    name: str
    no: int
    primary_reinforcement_direction: DesignStripWizard.PrimaryReinforcementDirection
    secondary_reinforcement_direction: DesignStripWizard.SecondaryReinforcementDirection
    surfaces: _containers.RepeatedScalarFieldContainer[int]
    type: DesignStripWizard.Type
    user_defined_name_enabled: bool
    user_defined_strip_width: float
    volume: float
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, analytical_area: _Optional[float] = ..., analytical_center_of_gravity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., analytical_center_of_gravity_x: _Optional[float] = ..., analytical_center_of_gravity_y: _Optional[float] = ..., analytical_center_of_gravity_z: _Optional[float] = ..., analytical_length: _Optional[float] = ..., analytical_mass: _Optional[float] = ..., analytical_volume: _Optional[float] = ..., area: _Optional[float] = ..., building_grid: _Optional[int] = ..., center_of_gravity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_of_gravity_x: _Optional[float] = ..., center_of_gravity_y: _Optional[float] = ..., center_of_gravity_z: _Optional[float] = ..., comment: _Optional[str] = ..., enable_column_strip_type: bool = ..., enable_middle_strip_type: bool = ..., enable_primary_reinforcement_direction: bool = ..., enable_secondary_reinforcement_direction: bool = ..., enable_user_defined_strip_width: bool = ..., generating_object_info: _Optional[str] = ..., grid_plane: _Optional[_Union[DesignStripWizard.GridPlane, str]] = ..., is_generated: bool = ..., length: _Optional[float] = ..., mass: _Optional[float] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., primary_reinforcement_direction: _Optional[_Union[DesignStripWizard.PrimaryReinforcementDirection, str]] = ..., secondary_reinforcement_direction: _Optional[_Union[DesignStripWizard.SecondaryReinforcementDirection, str]] = ..., surfaces: _Optional[_Iterable[int]] = ..., type: _Optional[_Union[DesignStripWizard.Type, str]] = ..., user_defined_name_enabled: bool = ..., user_defined_strip_width: _Optional[float] = ..., volume: _Optional[float] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
