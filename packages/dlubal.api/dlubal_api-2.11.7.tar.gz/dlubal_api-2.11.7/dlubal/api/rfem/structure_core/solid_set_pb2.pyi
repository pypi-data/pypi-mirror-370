from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SolidSet(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "set_type", "solids", "surface_area", "volume", "mass", "center_of_gravity", "center_of_gravity_x", "center_of_gravity_y", "center_of_gravity_z", "stress_analysis_configuration", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class SetType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SET_TYPE_CONTINUOUS: _ClassVar[SolidSet.SetType]
        SET_TYPE_GROUP: _ClassVar[SolidSet.SetType]
    SET_TYPE_CONTINUOUS: SolidSet.SetType
    SET_TYPE_GROUP: SolidSet.SetType
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SET_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOLIDS_FIELD_NUMBER: _ClassVar[int]
    SURFACE_AREA_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Z_FIELD_NUMBER: _ClassVar[int]
    STRESS_ANALYSIS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    set_type: SolidSet.SetType
    solids: _containers.RepeatedScalarFieldContainer[int]
    surface_area: float
    volume: float
    mass: float
    center_of_gravity: _common_pb2.Vector3d
    center_of_gravity_x: float
    center_of_gravity_y: float
    center_of_gravity_z: float
    stress_analysis_configuration: int
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., set_type: _Optional[_Union[SolidSet.SetType, str]] = ..., solids: _Optional[_Iterable[int]] = ..., surface_area: _Optional[float] = ..., volume: _Optional[float] = ..., mass: _Optional[float] = ..., center_of_gravity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_of_gravity_x: _Optional[float] = ..., center_of_gravity_y: _Optional[float] = ..., center_of_gravity_z: _Optional[float] = ..., stress_analysis_configuration: _Optional[int] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
