from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Accelerogram(_message.Message):
    __slots__ = ("no", "definition_type", "user_defined_name_enabled", "name", "library_id", "user_defined_accelerogram_step_enabled", "user_defined_accelerogram_time_step", "user_defined_accelerogram_sorted", "user_defined_accelerogram", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class DefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFINITION_TYPE_UNKNOWN: _ClassVar[Accelerogram.DefinitionType]
        DEFINITION_TYPE_FROM_LIBRARY: _ClassVar[Accelerogram.DefinitionType]
        DEFINITION_TYPE_USER_DEFINED: _ClassVar[Accelerogram.DefinitionType]
    DEFINITION_TYPE_UNKNOWN: Accelerogram.DefinitionType
    DEFINITION_TYPE_FROM_LIBRARY: Accelerogram.DefinitionType
    DEFINITION_TYPE_USER_DEFINED: Accelerogram.DefinitionType
    class UserDefinedAccelerogramTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[Accelerogram.UserDefinedAccelerogramRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[Accelerogram.UserDefinedAccelerogramRow, _Mapping]]] = ...) -> None: ...
    class UserDefinedAccelerogramRow(_message.Message):
        __slots__ = ("no", "description", "time", "acceleration_x", "acceleration_y", "acceleration_z")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        TIME_FIELD_NUMBER: _ClassVar[int]
        ACCELERATION_X_FIELD_NUMBER: _ClassVar[int]
        ACCELERATION_Y_FIELD_NUMBER: _ClassVar[int]
        ACCELERATION_Z_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        time: float
        acceleration_x: float
        acceleration_y: float
        acceleration_z: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., time: _Optional[float] = ..., acceleration_x: _Optional[float] = ..., acceleration_y: _Optional[float] = ..., acceleration_z: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LIBRARY_ID_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_ACCELEROGRAM_STEP_ENABLED_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_ACCELEROGRAM_TIME_STEP_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_ACCELEROGRAM_SORTED_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_ACCELEROGRAM_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    definition_type: Accelerogram.DefinitionType
    user_defined_name_enabled: bool
    name: str
    library_id: int
    user_defined_accelerogram_step_enabled: bool
    user_defined_accelerogram_time_step: float
    user_defined_accelerogram_sorted: bool
    user_defined_accelerogram: Accelerogram.UserDefinedAccelerogramTable
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., definition_type: _Optional[_Union[Accelerogram.DefinitionType, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., library_id: _Optional[int] = ..., user_defined_accelerogram_step_enabled: bool = ..., user_defined_accelerogram_time_step: _Optional[float] = ..., user_defined_accelerogram_sorted: bool = ..., user_defined_accelerogram: _Optional[_Union[Accelerogram.UserDefinedAccelerogramTable, _Mapping]] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
