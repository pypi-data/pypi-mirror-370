from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImposedNodalDeformation(_message.Message):
    __slots__ = ("no", "nodes", "load_case", "imposed_displacement", "imposed_displacement_x", "imposed_displacement_y", "imposed_displacement_z", "imposed_rotation", "imposed_rotation_x", "imposed_rotation_y", "imposed_rotation_z", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    LOAD_CASE_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_DISPLACEMENT_X_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_DISPLACEMENT_Y_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_DISPLACEMENT_Z_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_ROTATION_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_ROTATION_X_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_ROTATION_Y_FIELD_NUMBER: _ClassVar[int]
    IMPOSED_ROTATION_Z_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    nodes: _containers.RepeatedScalarFieldContainer[int]
    load_case: int
    imposed_displacement: _common_pb2.Vector3d
    imposed_displacement_x: float
    imposed_displacement_y: float
    imposed_displacement_z: float
    imposed_rotation: _common_pb2.Vector3d
    imposed_rotation_x: float
    imposed_rotation_y: float
    imposed_rotation_z: float
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., nodes: _Optional[_Iterable[int]] = ..., load_case: _Optional[int] = ..., imposed_displacement: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., imposed_displacement_x: _Optional[float] = ..., imposed_displacement_y: _Optional[float] = ..., imposed_displacement_z: _Optional[float] = ..., imposed_rotation: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., imposed_rotation_x: _Optional[float] = ..., imposed_rotation_y: _Optional[float] = ..., imposed_rotation_z: _Optional[float] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
