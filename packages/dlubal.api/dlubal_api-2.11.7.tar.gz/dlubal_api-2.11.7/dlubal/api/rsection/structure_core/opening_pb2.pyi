from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Opening(_message.Message):
    __slots__ = ("no", "boundary_lines", "parts", "area", "center_of_opening", "center_of_opening_y", "center_of_opening_z", "comment", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_LINES_FIELD_NUMBER: _ClassVar[int]
    PARTS_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_OPENING_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_OPENING_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_OPENING_Z_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    boundary_lines: _containers.RepeatedScalarFieldContainer[int]
    parts: _containers.RepeatedScalarFieldContainer[int]
    area: float
    center_of_opening: _common_pb2.Vector3d
    center_of_opening_y: float
    center_of_opening_z: float
    comment: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., boundary_lines: _Optional[_Iterable[int]] = ..., parts: _Optional[_Iterable[int]] = ..., area: _Optional[float] = ..., center_of_opening: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_of_opening_y: _Optional[float] = ..., center_of_opening_z: _Optional[float] = ..., comment: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
