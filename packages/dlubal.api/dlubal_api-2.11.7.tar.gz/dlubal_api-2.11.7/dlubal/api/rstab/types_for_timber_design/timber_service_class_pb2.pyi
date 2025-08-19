from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TimberServiceClass(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "members", "member_sets", "assigned_to_objects", "service_class", "comment", "id_for_export_import", "metadata_for_export_import")
    class ServiceClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SERVICE_CLASS_UNKNOWN: _ClassVar[TimberServiceClass.ServiceClass]
        SERVICE_CLASS_1: _ClassVar[TimberServiceClass.ServiceClass]
        SERVICE_CLASS_2: _ClassVar[TimberServiceClass.ServiceClass]
        SERVICE_CLASS_3: _ClassVar[TimberServiceClass.ServiceClass]
    SERVICE_CLASS_UNKNOWN: TimberServiceClass.ServiceClass
    SERVICE_CLASS_1: TimberServiceClass.ServiceClass
    SERVICE_CLASS_2: TimberServiceClass.ServiceClass
    SERVICE_CLASS_3: TimberServiceClass.ServiceClass
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_CLASS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    members: _containers.RepeatedScalarFieldContainer[int]
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_objects: str
    service_class: TimberServiceClass.ServiceClass
    comment: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., assigned_to_objects: _Optional[str] = ..., service_class: _Optional[_Union[TimberServiceClass.ServiceClass, str]] = ..., comment: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
