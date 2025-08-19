from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BuildingStory(_message.Message):
    __slots__ = ("no", "type", "user_defined_name_enabled", "name", "story_no", "elevation", "bottom_elevation", "height", "modified_height", "thickness", "info", "comment", "total_info", "modify_geometry_type", "thickness_type", "slab_stiffness_type", "floor_stiffness_type", "vertical_result_line_active", "vertical_result_line_position_x", "vertical_result_line_position_y", "vertical_result_line_relative", "vertical_result_line_relative_position_x", "vertical_result_line_relative_position_y", "mass", "center_of_gravity_x", "center_of_gravity_y", "line_support_model", "nodal_support_model", "building_stories_zero_value", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[BuildingStory.Type]
        TYPE_STANDARD: _ClassVar[BuildingStory.Type]
    TYPE_UNKNOWN: BuildingStory.Type
    TYPE_STANDARD: BuildingStory.Type
    class ModifyGeometryType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MODIFY_GEOMETRY_TYPE_DO_NOTHING: _ClassVar[BuildingStory.ModifyGeometryType]
        MODIFY_GEOMETRY_TYPE_CONST_FROM_STORY_GROUND: _ClassVar[BuildingStory.ModifyGeometryType]
        MODIFY_GEOMETRY_TYPE_CONST_FROM_STORY_ROOF: _ClassVar[BuildingStory.ModifyGeometryType]
        MODIFY_GEOMETRY_TYPE_PROPORTIONAL: _ClassVar[BuildingStory.ModifyGeometryType]
    MODIFY_GEOMETRY_TYPE_DO_NOTHING: BuildingStory.ModifyGeometryType
    MODIFY_GEOMETRY_TYPE_CONST_FROM_STORY_GROUND: BuildingStory.ModifyGeometryType
    MODIFY_GEOMETRY_TYPE_CONST_FROM_STORY_ROOF: BuildingStory.ModifyGeometryType
    MODIFY_GEOMETRY_TYPE_PROPORTIONAL: BuildingStory.ModifyGeometryType
    class ThicknessType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        THICKNESS_TYPE_EFFECTIVE_HEIGHT: _ClassVar[BuildingStory.ThicknessType]
        THICKNESS_TYPE_CLEAR_HEIGHT: _ClassVar[BuildingStory.ThicknessType]
    THICKNESS_TYPE_EFFECTIVE_HEIGHT: BuildingStory.ThicknessType
    THICKNESS_TYPE_CLEAR_HEIGHT: BuildingStory.ThicknessType
    class SlabStiffnessType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SLAB_STIFFNESS_TYPE_STANDARD: _ClassVar[BuildingStory.SlabStiffnessType]
        SLAB_STIFFNESS_TYPE_RIGID_DIAPHRAGM: _ClassVar[BuildingStory.SlabStiffnessType]
    SLAB_STIFFNESS_TYPE_STANDARD: BuildingStory.SlabStiffnessType
    SLAB_STIFFNESS_TYPE_RIGID_DIAPHRAGM: BuildingStory.SlabStiffnessType
    class FloorStiffnessType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FLOOR_STIFFNESS_TYPE_STANDARD: _ClassVar[BuildingStory.FloorStiffnessType]
        FLOOR_STIFFNESS_TYPE_FLEXIBLE_DIAPHRAGM: _ClassVar[BuildingStory.FloorStiffnessType]
        FLOOR_STIFFNESS_TYPE_RIGID_DIAPHRAGM: _ClassVar[BuildingStory.FloorStiffnessType]
        FLOOR_STIFFNESS_TYPE_SEMIRIGID: _ClassVar[BuildingStory.FloorStiffnessType]
    FLOOR_STIFFNESS_TYPE_STANDARD: BuildingStory.FloorStiffnessType
    FLOOR_STIFFNESS_TYPE_FLEXIBLE_DIAPHRAGM: BuildingStory.FloorStiffnessType
    FLOOR_STIFFNESS_TYPE_RIGID_DIAPHRAGM: BuildingStory.FloorStiffnessType
    FLOOR_STIFFNESS_TYPE_SEMIRIGID: BuildingStory.FloorStiffnessType
    class LineSupportModel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LINE_SUPPORT_MODEL_HINGED: _ClassVar[BuildingStory.LineSupportModel]
        LINE_SUPPORT_MODEL_HINGE_HINGE: _ClassVar[BuildingStory.LineSupportModel]
        LINE_SUPPORT_MODEL_HINGE_RIGID: _ClassVar[BuildingStory.LineSupportModel]
        LINE_SUPPORT_MODEL_RIGID_HINGE: _ClassVar[BuildingStory.LineSupportModel]
        LINE_SUPPORT_MODEL_RIGID_RIGID: _ClassVar[BuildingStory.LineSupportModel]
    LINE_SUPPORT_MODEL_HINGED: BuildingStory.LineSupportModel
    LINE_SUPPORT_MODEL_HINGE_HINGE: BuildingStory.LineSupportModel
    LINE_SUPPORT_MODEL_HINGE_RIGID: BuildingStory.LineSupportModel
    LINE_SUPPORT_MODEL_RIGID_HINGE: BuildingStory.LineSupportModel
    LINE_SUPPORT_MODEL_RIGID_RIGID: BuildingStory.LineSupportModel
    class NodalSupportModel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NODAL_SUPPORT_MODEL_HINGED: _ClassVar[BuildingStory.NodalSupportModel]
        NODAL_SUPPORT_MODEL_ACCORDING_TO_MEMBER_TYPE: _ClassVar[BuildingStory.NodalSupportModel]
        NODAL_SUPPORT_MODEL_HINGE_HINGE: _ClassVar[BuildingStory.NodalSupportModel]
        NODAL_SUPPORT_MODEL_HINGE_RIGID: _ClassVar[BuildingStory.NodalSupportModel]
        NODAL_SUPPORT_MODEL_RIGID_HINGE: _ClassVar[BuildingStory.NodalSupportModel]
        NODAL_SUPPORT_MODEL_RIGID_RIGID: _ClassVar[BuildingStory.NodalSupportModel]
    NODAL_SUPPORT_MODEL_HINGED: BuildingStory.NodalSupportModel
    NODAL_SUPPORT_MODEL_ACCORDING_TO_MEMBER_TYPE: BuildingStory.NodalSupportModel
    NODAL_SUPPORT_MODEL_HINGE_HINGE: BuildingStory.NodalSupportModel
    NODAL_SUPPORT_MODEL_HINGE_RIGID: BuildingStory.NodalSupportModel
    NODAL_SUPPORT_MODEL_RIGID_HINGE: BuildingStory.NodalSupportModel
    NODAL_SUPPORT_MODEL_RIGID_RIGID: BuildingStory.NodalSupportModel
    class InfoTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[BuildingStory.InfoTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[BuildingStory.InfoTableRow, _Mapping]]] = ...) -> None: ...
    class InfoTableRow(_message.Message):
        __slots__ = ("key", "description", "symbol", "value", "value_from_mesh", "unit", "children")
        KEY_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        SYMBOL_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        VALUE_FROM_MESH_FIELD_NUMBER: _ClassVar[int]
        UNIT_FIELD_NUMBER: _ClassVar[int]
        CHILDREN_FIELD_NUMBER: _ClassVar[int]
        key: str
        description: str
        symbol: str
        value: float
        value_from_mesh: float
        unit: str
        children: _containers.RepeatedCompositeFieldContainer[BuildingStory.InfoTableRow]
        def __init__(self, key: _Optional[str] = ..., description: _Optional[str] = ..., symbol: _Optional[str] = ..., value: _Optional[float] = ..., value_from_mesh: _Optional[float] = ..., unit: _Optional[str] = ..., children: _Optional[_Iterable[_Union[BuildingStory.InfoTableRow, _Mapping]]] = ...) -> None: ...
    class TotalInfoTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[BuildingStory.TotalInfoTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[BuildingStory.TotalInfoTableRow, _Mapping]]] = ...) -> None: ...
    class TotalInfoTableRow(_message.Message):
        __slots__ = ("key", "description", "symbol", "value", "value_from_mesh", "unit", "children")
        KEY_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        SYMBOL_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        VALUE_FROM_MESH_FIELD_NUMBER: _ClassVar[int]
        UNIT_FIELD_NUMBER: _ClassVar[int]
        CHILDREN_FIELD_NUMBER: _ClassVar[int]
        key: str
        description: str
        symbol: str
        value: float
        value_from_mesh: float
        unit: str
        children: _containers.RepeatedCompositeFieldContainer[BuildingStory.TotalInfoTableRow]
        def __init__(self, key: _Optional[str] = ..., description: _Optional[str] = ..., symbol: _Optional[str] = ..., value: _Optional[float] = ..., value_from_mesh: _Optional[float] = ..., unit: _Optional[str] = ..., children: _Optional[_Iterable[_Union[BuildingStory.TotalInfoTableRow, _Mapping]]] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STORY_NO_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_FIELD_NUMBER: _ClassVar[int]
    BOTTOM_ELEVATION_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_INFO_FIELD_NUMBER: _ClassVar[int]
    MODIFY_GEOMETRY_TYPE_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    SLAB_STIFFNESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    FLOOR_STIFFNESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    VERTICAL_RESULT_LINE_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    VERTICAL_RESULT_LINE_POSITION_X_FIELD_NUMBER: _ClassVar[int]
    VERTICAL_RESULT_LINE_POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    VERTICAL_RESULT_LINE_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    VERTICAL_RESULT_LINE_RELATIVE_POSITION_X_FIELD_NUMBER: _ClassVar[int]
    VERTICAL_RESULT_LINE_RELATIVE_POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    LINE_SUPPORT_MODEL_FIELD_NUMBER: _ClassVar[int]
    NODAL_SUPPORT_MODEL_FIELD_NUMBER: _ClassVar[int]
    BUILDING_STORIES_ZERO_VALUE_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: BuildingStory.Type
    user_defined_name_enabled: bool
    name: str
    story_no: int
    elevation: float
    bottom_elevation: float
    height: float
    modified_height: float
    thickness: float
    info: BuildingStory.InfoTable
    comment: str
    total_info: BuildingStory.TotalInfoTable
    modify_geometry_type: BuildingStory.ModifyGeometryType
    thickness_type: BuildingStory.ThicknessType
    slab_stiffness_type: BuildingStory.SlabStiffnessType
    floor_stiffness_type: BuildingStory.FloorStiffnessType
    vertical_result_line_active: bool
    vertical_result_line_position_x: float
    vertical_result_line_position_y: float
    vertical_result_line_relative: bool
    vertical_result_line_relative_position_x: float
    vertical_result_line_relative_position_y: float
    mass: float
    center_of_gravity_x: float
    center_of_gravity_y: float
    line_support_model: BuildingStory.LineSupportModel
    nodal_support_model: BuildingStory.NodalSupportModel
    building_stories_zero_value: float
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[BuildingStory.Type, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., story_no: _Optional[int] = ..., elevation: _Optional[float] = ..., bottom_elevation: _Optional[float] = ..., height: _Optional[float] = ..., modified_height: _Optional[float] = ..., thickness: _Optional[float] = ..., info: _Optional[_Union[BuildingStory.InfoTable, _Mapping]] = ..., comment: _Optional[str] = ..., total_info: _Optional[_Union[BuildingStory.TotalInfoTable, _Mapping]] = ..., modify_geometry_type: _Optional[_Union[BuildingStory.ModifyGeometryType, str]] = ..., thickness_type: _Optional[_Union[BuildingStory.ThicknessType, str]] = ..., slab_stiffness_type: _Optional[_Union[BuildingStory.SlabStiffnessType, str]] = ..., floor_stiffness_type: _Optional[_Union[BuildingStory.FloorStiffnessType, str]] = ..., vertical_result_line_active: bool = ..., vertical_result_line_position_x: _Optional[float] = ..., vertical_result_line_position_y: _Optional[float] = ..., vertical_result_line_relative: bool = ..., vertical_result_line_relative_position_x: _Optional[float] = ..., vertical_result_line_relative_position_y: _Optional[float] = ..., mass: _Optional[float] = ..., center_of_gravity_x: _Optional[float] = ..., center_of_gravity_y: _Optional[float] = ..., line_support_model: _Optional[_Union[BuildingStory.LineSupportModel, str]] = ..., nodal_support_model: _Optional[_Union[BuildingStory.NodalSupportModel, str]] = ..., building_stories_zero_value: _Optional[float] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
