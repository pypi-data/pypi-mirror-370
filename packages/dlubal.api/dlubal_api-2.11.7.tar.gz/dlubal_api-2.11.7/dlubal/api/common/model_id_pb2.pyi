from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ModelId(_message.Message):
    __slots__ = ("guid",)
    GUID_FIELD_NUMBER: _ClassVar[int]
    guid: str
    def __init__(self, guid: _Optional[str] = ...) -> None: ...

class OptionalModelId(_message.Message):
    __slots__ = ("guid",)
    GUID_FIELD_NUMBER: _ClassVar[int]
    guid: str
    def __init__(self, guid: _Optional[str] = ...) -> None: ...
