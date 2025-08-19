from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResponseSpectrum(_message.Message):
    __slots__ = ("no", "definition_type", "user_defined_name_enabled", "name", "user_defined_response_spectrum_step_enabled", "user_defined_response_spectrum_period_step", "user_defined_spectrum_sorted", "user_defined_response_spectrum", "comment", "is_generated", "generating_object_info", "damping", "min_t", "max_t", "direction", "sample_count", "accelerogram", "id_for_export_import", "metadata_for_export_import")
    class DefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFINITION_TYPE_UNKNOWN: _ClassVar[ResponseSpectrum.DefinitionType]
        DEFINITION_TYPE_ACCORDING_TO_STANDARD: _ClassVar[ResponseSpectrum.DefinitionType]
        DEFINITION_TYPE_GENERATED_FROM_ACCELEROGRAM: _ClassVar[ResponseSpectrum.DefinitionType]
        DEFINITION_TYPE_USER_DEFINED: _ClassVar[ResponseSpectrum.DefinitionType]
    DEFINITION_TYPE_UNKNOWN: ResponseSpectrum.DefinitionType
    DEFINITION_TYPE_ACCORDING_TO_STANDARD: ResponseSpectrum.DefinitionType
    DEFINITION_TYPE_GENERATED_FROM_ACCELEROGRAM: ResponseSpectrum.DefinitionType
    DEFINITION_TYPE_USER_DEFINED: ResponseSpectrum.DefinitionType
    class Direction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIRECTION_ALONG_X: _ClassVar[ResponseSpectrum.Direction]
        DIRECTION_ALONG_Y: _ClassVar[ResponseSpectrum.Direction]
        DIRECTION_ALONG_Z: _ClassVar[ResponseSpectrum.Direction]
    DIRECTION_ALONG_X: ResponseSpectrum.Direction
    DIRECTION_ALONG_Y: ResponseSpectrum.Direction
    DIRECTION_ALONG_Z: ResponseSpectrum.Direction
    class UserDefinedResponseSpectrumTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[ResponseSpectrum.UserDefinedResponseSpectrumRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[ResponseSpectrum.UserDefinedResponseSpectrumRow, _Mapping]]] = ...) -> None: ...
    class UserDefinedResponseSpectrumRow(_message.Message):
        __slots__ = ("no", "description", "period", "frequency", "acceleration", "acceleration_absolute", "acceleration_g_factor")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        PERIOD_FIELD_NUMBER: _ClassVar[int]
        FREQUENCY_FIELD_NUMBER: _ClassVar[int]
        ACCELERATION_FIELD_NUMBER: _ClassVar[int]
        ACCELERATION_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
        ACCELERATION_G_FACTOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        period: float
        frequency: float
        acceleration: float
        acceleration_absolute: float
        acceleration_g_factor: float
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., period: _Optional[float] = ..., frequency: _Optional[float] = ..., acceleration: _Optional[float] = ..., acceleration_absolute: _Optional[float] = ..., acceleration_g_factor: _Optional[float] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_RESPONSE_SPECTRUM_STEP_ENABLED_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_RESPONSE_SPECTRUM_PERIOD_STEP_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_SPECTRUM_SORTED_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_RESPONSE_SPECTRUM_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    DAMPING_FIELD_NUMBER: _ClassVar[int]
    MIN_T_FIELD_NUMBER: _ClassVar[int]
    MAX_T_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_COUNT_FIELD_NUMBER: _ClassVar[int]
    ACCELEROGRAM_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    definition_type: ResponseSpectrum.DefinitionType
    user_defined_name_enabled: bool
    name: str
    user_defined_response_spectrum_step_enabled: bool
    user_defined_response_spectrum_period_step: float
    user_defined_spectrum_sorted: bool
    user_defined_response_spectrum: ResponseSpectrum.UserDefinedResponseSpectrumTable
    comment: str
    is_generated: bool
    generating_object_info: str
    damping: float
    min_t: float
    max_t: float
    direction: ResponseSpectrum.Direction
    sample_count: int
    accelerogram: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., definition_type: _Optional[_Union[ResponseSpectrum.DefinitionType, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., user_defined_response_spectrum_step_enabled: bool = ..., user_defined_response_spectrum_period_step: _Optional[float] = ..., user_defined_spectrum_sorted: bool = ..., user_defined_response_spectrum: _Optional[_Union[ResponseSpectrum.UserDefinedResponseSpectrumTable, _Mapping]] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., damping: _Optional[float] = ..., min_t: _Optional[float] = ..., max_t: _Optional[float] = ..., direction: _Optional[_Union[ResponseSpectrum.Direction, str]] = ..., sample_count: _Optional[int] = ..., accelerogram: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
