from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberLoadsFromAreaLoad(_message.Message):
    __slots__ = ("absolute_tolerance_for_member_on_plane", "absolute_tolerance_for_node_on_line", "area_of_application", "comment", "consider_member_eccentricity", "consider_section_distribution", "convert_to_single_members", "excluded_members", "excluded_parallel_members", "generated_on", "generating_object_info", "is_generated", "load_case", "lock_for_new_members", "name", "no", "relative_tolerance_for_member_on_plane", "relative_tolerance_for_node_on_line", "smooth_punctual_load_enabled", "tolerance_type_for_member_on_plane", "tolerance_type_for_node_on_line", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class AreaOfApplication(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AREA_OF_APPLICATION_FULLY_CLOSED: _ClassVar[MemberLoadsFromAreaLoad.AreaOfApplication]
        AREA_OF_APPLICATION_EMPTY: _ClassVar[MemberLoadsFromAreaLoad.AreaOfApplication]
    AREA_OF_APPLICATION_FULLY_CLOSED: MemberLoadsFromAreaLoad.AreaOfApplication
    AREA_OF_APPLICATION_EMPTY: MemberLoadsFromAreaLoad.AreaOfApplication
    class ToleranceTypeForMemberOnPlane(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TOLERANCE_TYPE_FOR_MEMBER_ON_PLANE_ABSOLUTE: _ClassVar[MemberLoadsFromAreaLoad.ToleranceTypeForMemberOnPlane]
        TOLERANCE_TYPE_FOR_MEMBER_ON_PLANE_RELATIVE: _ClassVar[MemberLoadsFromAreaLoad.ToleranceTypeForMemberOnPlane]
    TOLERANCE_TYPE_FOR_MEMBER_ON_PLANE_ABSOLUTE: MemberLoadsFromAreaLoad.ToleranceTypeForMemberOnPlane
    TOLERANCE_TYPE_FOR_MEMBER_ON_PLANE_RELATIVE: MemberLoadsFromAreaLoad.ToleranceTypeForMemberOnPlane
    class ToleranceTypeForNodeOnLine(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TOLERANCE_TYPE_FOR_NODE_ON_LINE_ABSOLUTE: _ClassVar[MemberLoadsFromAreaLoad.ToleranceTypeForNodeOnLine]
        TOLERANCE_TYPE_FOR_NODE_ON_LINE_RELATIVE: _ClassVar[MemberLoadsFromAreaLoad.ToleranceTypeForNodeOnLine]
    TOLERANCE_TYPE_FOR_NODE_ON_LINE_ABSOLUTE: MemberLoadsFromAreaLoad.ToleranceTypeForNodeOnLine
    TOLERANCE_TYPE_FOR_NODE_ON_LINE_RELATIVE: MemberLoadsFromAreaLoad.ToleranceTypeForNodeOnLine
    ABSOLUTE_TOLERANCE_FOR_MEMBER_ON_PLANE_FIELD_NUMBER: _ClassVar[int]
    ABSOLUTE_TOLERANCE_FOR_NODE_ON_LINE_FIELD_NUMBER: _ClassVar[int]
    AREA_OF_APPLICATION_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_MEMBER_ECCENTRICITY_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_SECTION_DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    CONVERT_TO_SINGLE_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    EXCLUDED_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    EXCLUDED_PARALLEL_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    GENERATED_ON_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    LOAD_CASE_FIELD_NUMBER: _ClassVar[int]
    LOCK_FOR_NEW_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_TOLERANCE_FOR_MEMBER_ON_PLANE_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_TOLERANCE_FOR_NODE_ON_LINE_FIELD_NUMBER: _ClassVar[int]
    SMOOTH_PUNCTUAL_LOAD_ENABLED_FIELD_NUMBER: _ClassVar[int]
    TOLERANCE_TYPE_FOR_MEMBER_ON_PLANE_FIELD_NUMBER: _ClassVar[int]
    TOLERANCE_TYPE_FOR_NODE_ON_LINE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    absolute_tolerance_for_member_on_plane: float
    absolute_tolerance_for_node_on_line: float
    area_of_application: MemberLoadsFromAreaLoad.AreaOfApplication
    comment: str
    consider_member_eccentricity: bool
    consider_section_distribution: bool
    convert_to_single_members: bool
    excluded_members: _containers.RepeatedScalarFieldContainer[int]
    excluded_parallel_members: _containers.RepeatedScalarFieldContainer[int]
    generated_on: _containers.RepeatedScalarFieldContainer[int]
    generating_object_info: str
    is_generated: bool
    load_case: int
    lock_for_new_members: bool
    name: str
    no: int
    relative_tolerance_for_member_on_plane: float
    relative_tolerance_for_node_on_line: float
    smooth_punctual_load_enabled: bool
    tolerance_type_for_member_on_plane: MemberLoadsFromAreaLoad.ToleranceTypeForMemberOnPlane
    tolerance_type_for_node_on_line: MemberLoadsFromAreaLoad.ToleranceTypeForNodeOnLine
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, absolute_tolerance_for_member_on_plane: _Optional[float] = ..., absolute_tolerance_for_node_on_line: _Optional[float] = ..., area_of_application: _Optional[_Union[MemberLoadsFromAreaLoad.AreaOfApplication, str]] = ..., comment: _Optional[str] = ..., consider_member_eccentricity: bool = ..., consider_section_distribution: bool = ..., convert_to_single_members: bool = ..., excluded_members: _Optional[_Iterable[int]] = ..., excluded_parallel_members: _Optional[_Iterable[int]] = ..., generated_on: _Optional[_Iterable[int]] = ..., generating_object_info: _Optional[str] = ..., is_generated: bool = ..., load_case: _Optional[int] = ..., lock_for_new_members: bool = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., relative_tolerance_for_member_on_plane: _Optional[float] = ..., relative_tolerance_for_node_on_line: _Optional[float] = ..., smooth_punctual_load_enabled: bool = ..., tolerance_type_for_member_on_plane: _Optional[_Union[MemberLoadsFromAreaLoad.ToleranceTypeForMemberOnPlane, str]] = ..., tolerance_type_for_node_on_line: _Optional[_Union[MemberLoadsFromAreaLoad.ToleranceTypeForNodeOnLine, str]] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
