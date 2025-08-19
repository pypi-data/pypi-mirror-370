from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeepBeam(_message.Message):
    __slots__ = ("area", "center_of_gravity", "center_of_gravity_x", "center_of_gravity_y", "center_of_gravity_z", "comment", "create_result_sections", "create_result_sections_in_all_member_location", "generating_object_info", "is_generated", "mass", "member_set", "members", "name", "no", "result_sections", "sections", "segments", "surface_cells", "surfaces", "type", "user_defined_name_enabled", "volume", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[DeepBeam.Type]
        TYPE_STANDARD: _ClassVar[DeepBeam.Type]
    TYPE_UNKNOWN: DeepBeam.Type
    TYPE_STANDARD: DeepBeam.Type
    class SegmentsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[DeepBeam.SegmentsRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[DeepBeam.SegmentsRow, _Mapping]]] = ...) -> None: ...
    class SegmentsRow(_message.Message):
        __slots__ = ("no", "description", "location_xi", "location_yi", "location_xj", "location_yj", "member", "section_start", "section_end")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        LOCATION_XI_FIELD_NUMBER: _ClassVar[int]
        LOCATION_YI_FIELD_NUMBER: _ClassVar[int]
        LOCATION_XJ_FIELD_NUMBER: _ClassVar[int]
        LOCATION_YJ_FIELD_NUMBER: _ClassVar[int]
        MEMBER_FIELD_NUMBER: _ClassVar[int]
        SECTION_START_FIELD_NUMBER: _ClassVar[int]
        SECTION_END_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        location_xi: float
        location_yi: float
        location_xj: float
        location_yj: float
        member: int
        section_start: int
        section_end: int
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., location_xi: _Optional[float] = ..., location_yi: _Optional[float] = ..., location_xj: _Optional[float] = ..., location_yj: _Optional[float] = ..., member: _Optional[int] = ..., section_start: _Optional[int] = ..., section_end: _Optional[int] = ...) -> None: ...
    AREA_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Z_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    CREATE_RESULT_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    CREATE_RESULT_SECTIONS_IN_ALL_MEMBER_LOCATION_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SET_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    RESULT_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    SECTIONS_FIELD_NUMBER: _ClassVar[int]
    SEGMENTS_FIELD_NUMBER: _ClassVar[int]
    SURFACE_CELLS_FIELD_NUMBER: _ClassVar[int]
    SURFACES_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    area: float
    center_of_gravity: _common_pb2.Vector3d
    center_of_gravity_x: float
    center_of_gravity_y: float
    center_of_gravity_z: float
    comment: str
    create_result_sections: bool
    create_result_sections_in_all_member_location: bool
    generating_object_info: str
    is_generated: bool
    mass: float
    member_set: _containers.RepeatedScalarFieldContainer[int]
    members: _containers.RepeatedScalarFieldContainer[int]
    name: str
    no: int
    result_sections: _containers.RepeatedScalarFieldContainer[int]
    sections: _containers.RepeatedScalarFieldContainer[int]
    segments: DeepBeam.SegmentsTable
    surface_cells: _containers.RepeatedScalarFieldContainer[int]
    surfaces: _containers.RepeatedScalarFieldContainer[int]
    type: DeepBeam.Type
    user_defined_name_enabled: bool
    volume: float
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, area: _Optional[float] = ..., center_of_gravity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_of_gravity_x: _Optional[float] = ..., center_of_gravity_y: _Optional[float] = ..., center_of_gravity_z: _Optional[float] = ..., comment: _Optional[str] = ..., create_result_sections: bool = ..., create_result_sections_in_all_member_location: bool = ..., generating_object_info: _Optional[str] = ..., is_generated: bool = ..., mass: _Optional[float] = ..., member_set: _Optional[_Iterable[int]] = ..., members: _Optional[_Iterable[int]] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., result_sections: _Optional[_Iterable[int]] = ..., sections: _Optional[_Iterable[int]] = ..., segments: _Optional[_Union[DeepBeam.SegmentsTable, _Mapping]] = ..., surface_cells: _Optional[_Iterable[int]] = ..., surfaces: _Optional[_Iterable[int]] = ..., type: _Optional[_Union[DeepBeam.Type, str]] = ..., user_defined_name_enabled: bool = ..., volume: _Optional[float] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
