from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MemberDefinableStiffness(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "assigned_to", "torsional_stiffness", "bending_stiffness_y", "bending_stiffness_z", "axial_stiffness", "shear_stiffness_y", "shear_stiffness_z", "specific_weight", "section_area", "rotation", "thermal_expansion_alpha", "thermal_expansion_width", "thermal_expansion_height", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    TORSIONAL_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    BENDING_STIFFNESS_Y_FIELD_NUMBER: _ClassVar[int]
    BENDING_STIFFNESS_Z_FIELD_NUMBER: _ClassVar[int]
    AXIAL_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    SHEAR_STIFFNESS_Y_FIELD_NUMBER: _ClassVar[int]
    SHEAR_STIFFNESS_Z_FIELD_NUMBER: _ClassVar[int]
    SPECIFIC_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    SECTION_AREA_FIELD_NUMBER: _ClassVar[int]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    THERMAL_EXPANSION_ALPHA_FIELD_NUMBER: _ClassVar[int]
    THERMAL_EXPANSION_WIDTH_FIELD_NUMBER: _ClassVar[int]
    THERMAL_EXPANSION_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    assigned_to: _containers.RepeatedScalarFieldContainer[int]
    torsional_stiffness: float
    bending_stiffness_y: float
    bending_stiffness_z: float
    axial_stiffness: float
    shear_stiffness_y: float
    shear_stiffness_z: float
    specific_weight: float
    section_area: float
    rotation: float
    thermal_expansion_alpha: float
    thermal_expansion_width: float
    thermal_expansion_height: float
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., assigned_to: _Optional[_Iterable[int]] = ..., torsional_stiffness: _Optional[float] = ..., bending_stiffness_y: _Optional[float] = ..., bending_stiffness_z: _Optional[float] = ..., axial_stiffness: _Optional[float] = ..., shear_stiffness_y: _Optional[float] = ..., shear_stiffness_z: _Optional[float] = ..., specific_weight: _Optional[float] = ..., section_area: _Optional[float] = ..., rotation: _Optional[float] = ..., thermal_expansion_alpha: _Optional[float] = ..., thermal_expansion_width: _Optional[float] = ..., thermal_expansion_height: _Optional[float] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
