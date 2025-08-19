from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ShearWall(_message.Message):
    __slots__ = ("no", "type", "user_defined_name_enabled", "name", "surfaces", "surface_cells", "area", "mass", "volume", "center_of_gravity", "center_of_gravity_x", "center_of_gravity_y", "center_of_gravity_z", "segments", "member_set", "members", "sections", "result_sections", "comment", "is_generated", "generating_object_info", "create_result_sections", "create_result_sections_in_all_member_location", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[ShearWall.Type]
        TYPE_STANDARD: _ClassVar[ShearWall.Type]
    TYPE_UNKNOWN: ShearWall.Type
    TYPE_STANDARD: ShearWall.Type
    class SegmentsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[ShearWall.SegmentsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[ShearWall.SegmentsRow, _Mapping]]] = ...) -> None: ...
    class SegmentsRow(_message.Message):
        __slots__ = ("no", "description", "location_upper", "location_lower", "member", "section_start", "section_end")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        LOCATION_UPPER_FIELD_NUMBER: _ClassVar[int]
        LOCATION_LOWER_FIELD_NUMBER: _ClassVar[int]
        MEMBER_FIELD_NUMBER: _ClassVar[int]
        SECTION_START_FIELD_NUMBER: _ClassVar[int]
        SECTION_END_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        location_upper: float
        location_lower: float
        member: int
        section_start: int
        section_end: int
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., location_upper: _Optional[float] = ..., location_lower: _Optional[float] = ..., member: _Optional[int] = ..., section_start: _Optional[int] = ..., section_end: _Optional[int] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SURFACES_FIELD_NUMBER: _ClassVar[int]
    SURFACE_CELLS_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Z_FIELD_NUMBER: _ClassVar[int]
    SEGMENTS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SET_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    SECTIONS_FIELD_NUMBER: _ClassVar[int]
    RESULT_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    CREATE_RESULT_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    CREATE_RESULT_SECTIONS_IN_ALL_MEMBER_LOCATION_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: ShearWall.Type
    user_defined_name_enabled: bool
    name: str
    surfaces: _containers.RepeatedScalarFieldContainer[int]
    surface_cells: _containers.RepeatedScalarFieldContainer[int]
    area: float
    mass: float
    volume: float
    center_of_gravity: _common_pb2.Vector3d
    center_of_gravity_x: float
    center_of_gravity_y: float
    center_of_gravity_z: float
    segments: ShearWall.SegmentsTable
    member_set: _containers.RepeatedScalarFieldContainer[int]
    members: _containers.RepeatedScalarFieldContainer[int]
    sections: _containers.RepeatedScalarFieldContainer[int]
    result_sections: _containers.RepeatedScalarFieldContainer[int]
    comment: str
    is_generated: bool
    generating_object_info: str
    create_result_sections: bool
    create_result_sections_in_all_member_location: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[ShearWall.Type, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., surfaces: _Optional[_Iterable[int]] = ..., surface_cells: _Optional[_Iterable[int]] = ..., area: _Optional[float] = ..., mass: _Optional[float] = ..., volume: _Optional[float] = ..., center_of_gravity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_of_gravity_x: _Optional[float] = ..., center_of_gravity_y: _Optional[float] = ..., center_of_gravity_z: _Optional[float] = ..., segments: _Optional[_Union[ShearWall.SegmentsTable, _Mapping]] = ..., member_set: _Optional[_Iterable[int]] = ..., members: _Optional[_Iterable[int]] = ..., sections: _Optional[_Iterable[int]] = ..., result_sections: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., create_result_sections: bool = ..., create_result_sections_in_all_member_location: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
