from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberEccentricity(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "specification_type", "coordinate_system", "offset", "offset_x", "offset_y", "offset_z", "transverse_offset_active", "axial_offset_active", "hinge_location_at_node", "members", "horizontal_section_alignment", "vertical_section_alignment", "transverse_offset_reference_type", "transverse_offset_reference_member", "transverse_offset_member_reference_node", "transverse_offset_vertical_alignment", "transverse_offset_horizontal_alignment", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class SpecificationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SPECIFICATION_TYPE_RELATIVE_TO_SECTION: _ClassVar[MemberEccentricity.SpecificationType]
        SPECIFICATION_TYPE_ABSOLUTE: _ClassVar[MemberEccentricity.SpecificationType]
        SPECIFICATION_TYPE_RELATIVE_AND_ABSOLUTE: _ClassVar[MemberEccentricity.SpecificationType]
    SPECIFICATION_TYPE_RELATIVE_TO_SECTION: MemberEccentricity.SpecificationType
    SPECIFICATION_TYPE_ABSOLUTE: MemberEccentricity.SpecificationType
    SPECIFICATION_TYPE_RELATIVE_AND_ABSOLUTE: MemberEccentricity.SpecificationType
    class HorizontalSectionAlignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        HORIZONTAL_SECTION_ALIGNMENT_LEFT: _ClassVar[MemberEccentricity.HorizontalSectionAlignment]
        HORIZONTAL_SECTION_ALIGNMENT_CENTER: _ClassVar[MemberEccentricity.HorizontalSectionAlignment]
        HORIZONTAL_SECTION_ALIGNMENT_RIGHT: _ClassVar[MemberEccentricity.HorizontalSectionAlignment]
    HORIZONTAL_SECTION_ALIGNMENT_LEFT: MemberEccentricity.HorizontalSectionAlignment
    HORIZONTAL_SECTION_ALIGNMENT_CENTER: MemberEccentricity.HorizontalSectionAlignment
    HORIZONTAL_SECTION_ALIGNMENT_RIGHT: MemberEccentricity.HorizontalSectionAlignment
    class VerticalSectionAlignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        VERTICAL_SECTION_ALIGNMENT_TOP: _ClassVar[MemberEccentricity.VerticalSectionAlignment]
        VERTICAL_SECTION_ALIGNMENT_BOTTOM: _ClassVar[MemberEccentricity.VerticalSectionAlignment]
        VERTICAL_SECTION_ALIGNMENT_CENTER: _ClassVar[MemberEccentricity.VerticalSectionAlignment]
    VERTICAL_SECTION_ALIGNMENT_TOP: MemberEccentricity.VerticalSectionAlignment
    VERTICAL_SECTION_ALIGNMENT_BOTTOM: MemberEccentricity.VerticalSectionAlignment
    VERTICAL_SECTION_ALIGNMENT_CENTER: MemberEccentricity.VerticalSectionAlignment
    class TransverseOffsetReferenceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRANSVERSE_OFFSET_REFERENCE_TYPE_NONE: _ClassVar[MemberEccentricity.TransverseOffsetReferenceType]
        TRANSVERSE_OFFSET_REFERENCE_TYPE_FROM_MEMBER_SECTION: _ClassVar[MemberEccentricity.TransverseOffsetReferenceType]
    TRANSVERSE_OFFSET_REFERENCE_TYPE_NONE: MemberEccentricity.TransverseOffsetReferenceType
    TRANSVERSE_OFFSET_REFERENCE_TYPE_FROM_MEMBER_SECTION: MemberEccentricity.TransverseOffsetReferenceType
    class TransverseOffsetVerticalAlignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRANSVERSE_OFFSET_VERTICAL_ALIGNMENT_TOP: _ClassVar[MemberEccentricity.TransverseOffsetVerticalAlignment]
        TRANSVERSE_OFFSET_VERTICAL_ALIGNMENT_BOTTOM: _ClassVar[MemberEccentricity.TransverseOffsetVerticalAlignment]
        TRANSVERSE_OFFSET_VERTICAL_ALIGNMENT_CENTER: _ClassVar[MemberEccentricity.TransverseOffsetVerticalAlignment]
    TRANSVERSE_OFFSET_VERTICAL_ALIGNMENT_TOP: MemberEccentricity.TransverseOffsetVerticalAlignment
    TRANSVERSE_OFFSET_VERTICAL_ALIGNMENT_BOTTOM: MemberEccentricity.TransverseOffsetVerticalAlignment
    TRANSVERSE_OFFSET_VERTICAL_ALIGNMENT_CENTER: MemberEccentricity.TransverseOffsetVerticalAlignment
    class TransverseOffsetHorizontalAlignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRANSVERSE_OFFSET_HORIZONTAL_ALIGNMENT_LEFT: _ClassVar[MemberEccentricity.TransverseOffsetHorizontalAlignment]
        TRANSVERSE_OFFSET_HORIZONTAL_ALIGNMENT_CENTER: _ClassVar[MemberEccentricity.TransverseOffsetHorizontalAlignment]
        TRANSVERSE_OFFSET_HORIZONTAL_ALIGNMENT_RIGHT: _ClassVar[MemberEccentricity.TransverseOffsetHorizontalAlignment]
    TRANSVERSE_OFFSET_HORIZONTAL_ALIGNMENT_LEFT: MemberEccentricity.TransverseOffsetHorizontalAlignment
    TRANSVERSE_OFFSET_HORIZONTAL_ALIGNMENT_CENTER: MemberEccentricity.TransverseOffsetHorizontalAlignment
    TRANSVERSE_OFFSET_HORIZONTAL_ALIGNMENT_RIGHT: MemberEccentricity.TransverseOffsetHorizontalAlignment
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    OFFSET_X_FIELD_NUMBER: _ClassVar[int]
    OFFSET_Y_FIELD_NUMBER: _ClassVar[int]
    OFFSET_Z_FIELD_NUMBER: _ClassVar[int]
    TRANSVERSE_OFFSET_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    AXIAL_OFFSET_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    HINGE_LOCATION_AT_NODE_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    HORIZONTAL_SECTION_ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    VERTICAL_SECTION_ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    TRANSVERSE_OFFSET_REFERENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSVERSE_OFFSET_REFERENCE_MEMBER_FIELD_NUMBER: _ClassVar[int]
    TRANSVERSE_OFFSET_MEMBER_REFERENCE_NODE_FIELD_NUMBER: _ClassVar[int]
    TRANSVERSE_OFFSET_VERTICAL_ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    TRANSVERSE_OFFSET_HORIZONTAL_ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    specification_type: MemberEccentricity.SpecificationType
    coordinate_system: _common_pb2.CoordinateSystemRepresentation
    offset: _common_pb2.Vector3d
    offset_x: float
    offset_y: float
    offset_z: float
    transverse_offset_active: bool
    axial_offset_active: bool
    hinge_location_at_node: bool
    members: str
    horizontal_section_alignment: MemberEccentricity.HorizontalSectionAlignment
    vertical_section_alignment: MemberEccentricity.VerticalSectionAlignment
    transverse_offset_reference_type: MemberEccentricity.TransverseOffsetReferenceType
    transverse_offset_reference_member: int
    transverse_offset_member_reference_node: int
    transverse_offset_vertical_alignment: MemberEccentricity.TransverseOffsetVerticalAlignment
    transverse_offset_horizontal_alignment: MemberEccentricity.TransverseOffsetHorizontalAlignment
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., specification_type: _Optional[_Union[MemberEccentricity.SpecificationType, str]] = ..., coordinate_system: _Optional[_Union[_common_pb2.CoordinateSystemRepresentation, _Mapping]] = ..., offset: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., offset_x: _Optional[float] = ..., offset_y: _Optional[float] = ..., offset_z: _Optional[float] = ..., transverse_offset_active: bool = ..., axial_offset_active: bool = ..., hinge_location_at_node: bool = ..., members: _Optional[str] = ..., horizontal_section_alignment: _Optional[_Union[MemberEccentricity.HorizontalSectionAlignment, str]] = ..., vertical_section_alignment: _Optional[_Union[MemberEccentricity.VerticalSectionAlignment, str]] = ..., transverse_offset_reference_type: _Optional[_Union[MemberEccentricity.TransverseOffsetReferenceType, str]] = ..., transverse_offset_reference_member: _Optional[int] = ..., transverse_offset_member_reference_node: _Optional[int] = ..., transverse_offset_vertical_alignment: _Optional[_Union[MemberEccentricity.TransverseOffsetVerticalAlignment, str]] = ..., transverse_offset_horizontal_alignment: _Optional[_Union[MemberEccentricity.TransverseOffsetHorizontalAlignment, str]] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
