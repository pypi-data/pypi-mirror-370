from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Opening(_message.Message):
    __slots__ = ("no", "area", "boundary_lines", "center_of_opening", "center_of_opening_x", "center_of_opening_y", "center_of_opening_z", "position_full_description", "position_short_description", "surfaces", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_LINES_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_OPENING_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_OPENING_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_OPENING_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_OPENING_Z_FIELD_NUMBER: _ClassVar[int]
    POSITION_FULL_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    POSITION_SHORT_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SURFACES_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    area: float
    boundary_lines: _containers.RepeatedScalarFieldContainer[int]
    center_of_opening: _common_pb2.Vector3d
    center_of_opening_x: float
    center_of_opening_y: float
    center_of_opening_z: float
    position_full_description: str
    position_short_description: str
    surfaces: _containers.RepeatedScalarFieldContainer[int]
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., area: _Optional[float] = ..., boundary_lines: _Optional[_Iterable[int]] = ..., center_of_opening: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_of_opening_x: _Optional[float] = ..., center_of_opening_y: _Optional[float] = ..., center_of_opening_z: _Optional[float] = ..., position_full_description: _Optional[str] = ..., position_short_description: _Optional[str] = ..., surfaces: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
