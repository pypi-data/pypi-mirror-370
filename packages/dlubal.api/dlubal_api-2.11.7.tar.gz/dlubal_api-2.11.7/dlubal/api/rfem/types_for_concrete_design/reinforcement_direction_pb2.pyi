from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReinforcementDirection(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "surfaces", "reinforcement_direction_type", "first_reinforcement_angle", "second_reinforcement_angle_to_first_angle", "second_reinforcement_angle", "is_angle_to_first_direction", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class ReinforcementDirectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REINFORCEMENT_DIRECTION_TYPE_FIRST_REINFORCEMENT_IN_X: _ClassVar[ReinforcementDirection.ReinforcementDirectionType]
        REINFORCEMENT_DIRECTION_TYPE_FIRST_REINFORCEMENT_IN_Y: _ClassVar[ReinforcementDirection.ReinforcementDirectionType]
        REINFORCEMENT_DIRECTION_TYPE_ROTATED: _ClassVar[ReinforcementDirection.ReinforcementDirectionType]
    REINFORCEMENT_DIRECTION_TYPE_FIRST_REINFORCEMENT_IN_X: ReinforcementDirection.ReinforcementDirectionType
    REINFORCEMENT_DIRECTION_TYPE_FIRST_REINFORCEMENT_IN_Y: ReinforcementDirection.ReinforcementDirectionType
    REINFORCEMENT_DIRECTION_TYPE_ROTATED: ReinforcementDirection.ReinforcementDirectionType
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SURFACES_FIELD_NUMBER: _ClassVar[int]
    REINFORCEMENT_DIRECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    FIRST_REINFORCEMENT_ANGLE_FIELD_NUMBER: _ClassVar[int]
    SECOND_REINFORCEMENT_ANGLE_TO_FIRST_ANGLE_FIELD_NUMBER: _ClassVar[int]
    SECOND_REINFORCEMENT_ANGLE_FIELD_NUMBER: _ClassVar[int]
    IS_ANGLE_TO_FIRST_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    surfaces: _containers.RepeatedScalarFieldContainer[int]
    reinforcement_direction_type: ReinforcementDirection.ReinforcementDirectionType
    first_reinforcement_angle: float
    second_reinforcement_angle_to_first_angle: float
    second_reinforcement_angle: float
    is_angle_to_first_direction: bool
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., surfaces: _Optional[_Iterable[int]] = ..., reinforcement_direction_type: _Optional[_Union[ReinforcementDirection.ReinforcementDirectionType, str]] = ..., first_reinforcement_angle: _Optional[float] = ..., second_reinforcement_angle_to_first_angle: _Optional[float] = ..., second_reinforcement_angle: _Optional[float] = ..., is_angle_to_first_direction: bool = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
