from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NullValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NULL_VALUE: _ClassVar[NullValue]
NULL_VALUE: NullValue

class Vector3d(_message.Message):
    __slots__ = ("x", "y", "z")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...

class Color(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class Value(_message.Message):
    __slots__ = ("null_value", "int_value", "double_value", "string_value", "bool_value")
    NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT_VALUE_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    null_value: NullValue
    int_value: int
    double_value: float
    string_value: str
    bool_value: bool
    def __init__(self, null_value: _Optional[_Union[NullValue, str]] = ..., int_value: _Optional[int] = ..., double_value: _Optional[float] = ..., string_value: _Optional[str] = ..., bool_value: bool = ...) -> None: ...

class CoordinateSystemRepresentation(_message.Message):
    __slots__ = ("no", "type")
    class CoordinateSystemType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COORDINATE_SYSTEM_TYPE_UNKNOWN: _ClassVar[CoordinateSystemRepresentation.CoordinateSystemType]
        COORDINATE_SYSTEM_TYPE_LOCAL: _ClassVar[CoordinateSystemRepresentation.CoordinateSystemType]
        COORDINATE_SYSTEM_TYPE_PRINCIPAL: _ClassVar[CoordinateSystemRepresentation.CoordinateSystemType]
    COORDINATE_SYSTEM_TYPE_UNKNOWN: CoordinateSystemRepresentation.CoordinateSystemType
    COORDINATE_SYSTEM_TYPE_LOCAL: CoordinateSystemRepresentation.CoordinateSystemType
    COORDINATE_SYSTEM_TYPE_PRINCIPAL: CoordinateSystemRepresentation.CoordinateSystemType
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: CoordinateSystemRepresentation.CoordinateSystemType
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[CoordinateSystemRepresentation.CoordinateSystemType, str]] = ...) -> None: ...
