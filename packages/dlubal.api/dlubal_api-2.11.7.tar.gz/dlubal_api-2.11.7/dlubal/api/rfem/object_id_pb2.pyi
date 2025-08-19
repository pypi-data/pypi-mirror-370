from dlubal.api.rfem import object_type_pb2 as _object_type_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ObjectId(_message.Message):
    __slots__ = ("no", "object_type", "parent_no", "parent_object_type")
    NO_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARENT_NO_FIELD_NUMBER: _ClassVar[int]
    PARENT_OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    no: int
    object_type: _object_type_pb2.ObjectType
    parent_no: int
    parent_object_type: _object_type_pb2.ObjectType
    def __init__(self, no: _Optional[int] = ..., object_type: _Optional[_Union[_object_type_pb2.ObjectType, str]] = ..., parent_no: _Optional[int] = ..., parent_object_type: _Optional[_Union[_object_type_pb2.ObjectType, str]] = ...) -> None: ...

class ObjectIdList(_message.Message):
    __slots__ = ("object_id",)
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    object_id: _containers.RepeatedCompositeFieldContainer[ObjectId]
    def __init__(self, object_id: _Optional[_Iterable[_Union[ObjectId, _Mapping]]] = ...) -> None: ...
