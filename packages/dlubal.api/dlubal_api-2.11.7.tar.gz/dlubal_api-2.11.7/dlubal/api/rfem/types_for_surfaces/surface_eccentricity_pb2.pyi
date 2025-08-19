from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SurfaceEccentricity(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "offset", "assigned_to_surfaces", "thickness_alignment", "transverse_offset_active", "transverse_offset_reference_type", "transverse_offset_reference_member", "transverse_offset_reference_surface", "transverse_offset_member_reference_node", "transverse_offset_surface_reference_node", "transverse_offset_alignment", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class ThicknessAlignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        THICKNESS_ALIGNMENT_TOP: _ClassVar[SurfaceEccentricity.ThicknessAlignment]
        THICKNESS_ALIGNMENT_BOTTOM: _ClassVar[SurfaceEccentricity.ThicknessAlignment]
        THICKNESS_ALIGNMENT_CENTER: _ClassVar[SurfaceEccentricity.ThicknessAlignment]
    THICKNESS_ALIGNMENT_TOP: SurfaceEccentricity.ThicknessAlignment
    THICKNESS_ALIGNMENT_BOTTOM: SurfaceEccentricity.ThicknessAlignment
    THICKNESS_ALIGNMENT_CENTER: SurfaceEccentricity.ThicknessAlignment
    class TransverseOffsetReferenceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRANSVERSE_OFFSET_REFERENCE_TYPE_NONE: _ClassVar[SurfaceEccentricity.TransverseOffsetReferenceType]
        TRANSVERSE_OFFSET_REFERENCE_TYPE_FROM_MEMBER_SECTION: _ClassVar[SurfaceEccentricity.TransverseOffsetReferenceType]
        TRANSVERSE_OFFSET_REFERENCE_TYPE_FROM_SURFACE_THICKNESS: _ClassVar[SurfaceEccentricity.TransverseOffsetReferenceType]
    TRANSVERSE_OFFSET_REFERENCE_TYPE_NONE: SurfaceEccentricity.TransverseOffsetReferenceType
    TRANSVERSE_OFFSET_REFERENCE_TYPE_FROM_MEMBER_SECTION: SurfaceEccentricity.TransverseOffsetReferenceType
    TRANSVERSE_OFFSET_REFERENCE_TYPE_FROM_SURFACE_THICKNESS: SurfaceEccentricity.TransverseOffsetReferenceType
    class TransverseOffsetAlignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRANSVERSE_OFFSET_ALIGNMENT_TOP: _ClassVar[SurfaceEccentricity.TransverseOffsetAlignment]
        TRANSVERSE_OFFSET_ALIGNMENT_BOTTOM: _ClassVar[SurfaceEccentricity.TransverseOffsetAlignment]
        TRANSVERSE_OFFSET_ALIGNMENT_CENTER: _ClassVar[SurfaceEccentricity.TransverseOffsetAlignment]
    TRANSVERSE_OFFSET_ALIGNMENT_TOP: SurfaceEccentricity.TransverseOffsetAlignment
    TRANSVERSE_OFFSET_ALIGNMENT_BOTTOM: SurfaceEccentricity.TransverseOffsetAlignment
    TRANSVERSE_OFFSET_ALIGNMENT_CENTER: SurfaceEccentricity.TransverseOffsetAlignment
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_SURFACES_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    TRANSVERSE_OFFSET_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    TRANSVERSE_OFFSET_REFERENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSVERSE_OFFSET_REFERENCE_MEMBER_FIELD_NUMBER: _ClassVar[int]
    TRANSVERSE_OFFSET_REFERENCE_SURFACE_FIELD_NUMBER: _ClassVar[int]
    TRANSVERSE_OFFSET_MEMBER_REFERENCE_NODE_FIELD_NUMBER: _ClassVar[int]
    TRANSVERSE_OFFSET_SURFACE_REFERENCE_NODE_FIELD_NUMBER: _ClassVar[int]
    TRANSVERSE_OFFSET_ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    offset: float
    assigned_to_surfaces: _containers.RepeatedScalarFieldContainer[int]
    thickness_alignment: SurfaceEccentricity.ThicknessAlignment
    transverse_offset_active: bool
    transverse_offset_reference_type: SurfaceEccentricity.TransverseOffsetReferenceType
    transverse_offset_reference_member: int
    transverse_offset_reference_surface: int
    transverse_offset_member_reference_node: int
    transverse_offset_surface_reference_node: int
    transverse_offset_alignment: SurfaceEccentricity.TransverseOffsetAlignment
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., offset: _Optional[float] = ..., assigned_to_surfaces: _Optional[_Iterable[int]] = ..., thickness_alignment: _Optional[_Union[SurfaceEccentricity.ThicknessAlignment, str]] = ..., transverse_offset_active: bool = ..., transverse_offset_reference_type: _Optional[_Union[SurfaceEccentricity.TransverseOffsetReferenceType, str]] = ..., transverse_offset_reference_member: _Optional[int] = ..., transverse_offset_reference_surface: _Optional[int] = ..., transverse_offset_member_reference_node: _Optional[int] = ..., transverse_offset_surface_reference_node: _Optional[int] = ..., transverse_offset_alignment: _Optional[_Union[SurfaceEccentricity.TransverseOffsetAlignment, str]] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
