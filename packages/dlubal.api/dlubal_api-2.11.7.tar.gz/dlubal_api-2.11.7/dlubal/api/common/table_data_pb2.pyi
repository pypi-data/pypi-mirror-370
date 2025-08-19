from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TableData(_message.Message):
    __slots__ = ("column_ids", "rows")
    COLUMN_IDS_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    column_ids: _containers.RepeatedScalarFieldContainer[str]
    rows: _containers.RepeatedCompositeFieldContainer[TableRow]
    def __init__(self, column_ids: _Optional[_Iterable[str]] = ..., rows: _Optional[_Iterable[_Union[TableRow, _Mapping]]] = ...) -> None: ...

class TableRow(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[_common_pb2.Value]
    def __init__(self, values: _Optional[_Iterable[_Union[_common_pb2.Value, _Mapping]]] = ...) -> None: ...
