from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImposedLineDeformation(_message.Message):
    __slots__ = ("no", "lines", "load_case", "imposed_displacement_line_start", "imposed_displacement_line_start_x", "imposed_displacement_line_start_y", "imposed_displacement_line_start_z", "imposed_displacement_line_end", "imposed_displacement_line_end_x", "imposed_displacement_line_end_y", "imposed_displacement_line_end_z", "imposed_rotation_line_start", "imposed_rotation_line_end", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    LINES_FIELD_NUMBER: _ClassVar[int]
    LOAD_CASE_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_DISPLACEMENT_LINE_START_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_DISPLACEMENT_LINE_START_X_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_DISPLACEMENT_LINE_START_Y_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_DISPLACEMENT_LINE_START_Z_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_DISPLACEMENT_LINE_END_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_DISPLACEMENT_LINE_END_X_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_DISPLACEMENT_LINE_END_Y_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_DISPLACEMENT_LINE_END_Z_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_ROTATION_LINE_START_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_ROTATION_LINE_END_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    lines: _containers.RepeatedScalarFieldContainer[int]
    load_case: int
    imposed_displacement_line_start: _common_pb2.Vector3d
    imposed_displacement_line_start_x: float
    imposed_displacement_line_start_y: float
    imposed_displacement_line_start_z: float
    imposed_displacement_line_end: _common_pb2.Vector3d
    imposed_displacement_line_end_x: float
    imposed_displacement_line_end_y: float
    imposed_displacement_line_end_z: float
    imposed_rotation_line_start: float
    imposed_rotation_line_end: float
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., lines: _Optional[_Iterable[int]] = ..., load_case: _Optional[int] = ..., imposed_displacement_line_start: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., imposed_displacement_line_start_x: _Optional[float] = ..., imposed_displacement_line_start_y: _Optional[float] = ..., imposed_displacement_line_start_z: _Optional[float] = ..., imposed_displacement_line_end: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., imposed_displacement_line_end_x: _Optional[float] = ..., imposed_displacement_line_end_y: _Optional[float] = ..., imposed_displacement_line_end_z: _Optional[float] = ..., imposed_rotation_line_start: _Optional[float] = ..., imposed_rotation_line_end: _Optional[float] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
