from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class LayerGroup(_message.Message):
    __slots__ = ("assigned_layers", "name", "no", "parent_layer_group", "id_for_export_import", "metadata_for_export_import")
    ASSIGNED_LAYERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    PARENT_LAYER_GROUP_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    assigned_layers: _containers.RepeatedScalarFieldContainer[int]
    name: str
    no: int
    parent_layer_group: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, assigned_layers: _Optional[_Iterable[int]] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., parent_layer_group: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
