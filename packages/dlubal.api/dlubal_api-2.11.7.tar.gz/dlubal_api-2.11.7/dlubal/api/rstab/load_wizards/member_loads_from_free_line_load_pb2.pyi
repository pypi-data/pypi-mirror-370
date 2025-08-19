from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberLoadsFromFreeLineLoad(_message.Message):
    __slots__ = ("absolute_tolerance_for_member_on_plane", "absolute_tolerance_for_node_on_line", "comment", "consider_member_eccentricity", "consider_section_distribution", "convert_to_single_members", "coordinate_system", "excluded_members", "excluded_parallel_members", "generated_on", "generating_object_info", "is_generated", "load_case", "load_direction", "load_distribution", "lock_for_new_members", "magnitude_first", "magnitude_second", "magnitude_uniform", "name", "no", "node_1", "node_2", "node_3", "relative_tolerance_for_member_on_plane", "relative_tolerance_for_node_on_line", "tolerance_type_for_member_on_plane", "tolerance_type_for_node_on_line", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class LoadDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DIRECTION_UNKNOWN: _ClassVar[MemberLoadsFromFreeLineLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED_LENGTH: _ClassVar[MemberLoadsFromFreeLineLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: _ClassVar[MemberLoadsFromFreeLineLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_PROJECTED_LENGTH: _ClassVar[MemberLoadsFromFreeLineLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: _ClassVar[MemberLoadsFromFreeLineLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_PROJECTED_LENGTH: _ClassVar[MemberLoadsFromFreeLineLoad.LoadDirection]
        LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: _ClassVar[MemberLoadsFromFreeLineLoad.LoadDirection]
        LOAD_DIRECTION_LOCAL_Z: _ClassVar[MemberLoadsFromFreeLineLoad.LoadDirection]
    LOAD_DIRECTION_UNKNOWN: MemberLoadsFromFreeLineLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED_LENGTH: MemberLoadsFromFreeLineLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_TRUE_LENGTH: MemberLoadsFromFreeLineLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_PROJECTED_LENGTH: MemberLoadsFromFreeLineLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Y_OR_USER_DEFINED_V_TRUE_LENGTH: MemberLoadsFromFreeLineLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_PROJECTED_LENGTH: MemberLoadsFromFreeLineLoad.LoadDirection
    LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE_LENGTH: MemberLoadsFromFreeLineLoad.LoadDirection
    LOAD_DIRECTION_LOCAL_Z: MemberLoadsFromFreeLineLoad.LoadDirection
    class LoadDistribution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOAD_DISTRIBUTION_UNIFORM: _ClassVar[MemberLoadsFromFreeLineLoad.LoadDistribution]
        LOAD_DISTRIBUTION_LINEAR: _ClassVar[MemberLoadsFromFreeLineLoad.LoadDistribution]
    LOAD_DISTRIBUTION_UNIFORM: MemberLoadsFromFreeLineLoad.LoadDistribution
    LOAD_DISTRIBUTION_LINEAR: MemberLoadsFromFreeLineLoad.LoadDistribution
    class ToleranceTypeForMemberOnPlane(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TOLERANCE_TYPE_FOR_MEMBER_ON_PLANE_ABSOLUTE: _ClassVar[MemberLoadsFromFreeLineLoad.ToleranceTypeForMemberOnPlane]
        TOLERANCE_TYPE_FOR_MEMBER_ON_PLANE_RELATIVE: _ClassVar[MemberLoadsFromFreeLineLoad.ToleranceTypeForMemberOnPlane]
    TOLERANCE_TYPE_FOR_MEMBER_ON_PLANE_ABSOLUTE: MemberLoadsFromFreeLineLoad.ToleranceTypeForMemberOnPlane
    TOLERANCE_TYPE_FOR_MEMBER_ON_PLANE_RELATIVE: MemberLoadsFromFreeLineLoad.ToleranceTypeForMemberOnPlane
    class ToleranceTypeForNodeOnLine(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TOLERANCE_TYPE_FOR_NODE_ON_LINE_ABSOLUTE: _ClassVar[MemberLoadsFromFreeLineLoad.ToleranceTypeForNodeOnLine]
        TOLERANCE_TYPE_FOR_NODE_ON_LINE_RELATIVE: _ClassVar[MemberLoadsFromFreeLineLoad.ToleranceTypeForNodeOnLine]
    TOLERANCE_TYPE_FOR_NODE_ON_LINE_ABSOLUTE: MemberLoadsFromFreeLineLoad.ToleranceTypeForNodeOnLine
    TOLERANCE_TYPE_FOR_NODE_ON_LINE_RELATIVE: MemberLoadsFromFreeLineLoad.ToleranceTypeForNodeOnLine
    ABSOLUTE_TOLERANCE_FOR_MEMBER_ON_PLANE_FIELD_NUMBER: _ClassVar[int]
    ABSOLUTE_TOLERANCE_FOR_NODE_ON_LINE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_MEMBER_ECCENTRICITY_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_SECTION_DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    CONVERT_TO_SINGLE_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    EXCLUDED_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    EXCLUDED_PARALLEL_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    GENERATED_ON_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    LOAD_CASE_FIELD_NUMBER: _ClassVar[int]
    LOAD_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    LOAD_DISTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    LOCK_FOR_NEW_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_FIRST_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_SECOND_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_UNIFORM_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    NODE_1_FIELD_NUMBER: _ClassVar[int]
    NODE_2_FIELD_NUMBER: _ClassVar[int]
    NODE_3_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_TOLERANCE_FOR_MEMBER_ON_PLANE_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_TOLERANCE_FOR_NODE_ON_LINE_FIELD_NUMBER: _ClassVar[int]
    TOLERANCE_TYPE_FOR_MEMBER_ON_PLANE_FIELD_NUMBER: _ClassVar[int]
    TOLERANCE_TYPE_FOR_NODE_ON_LINE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    absolute_tolerance_for_member_on_plane: float
    absolute_tolerance_for_node_on_line: float
    comment: str
    consider_member_eccentricity: bool
    consider_section_distribution: bool
    convert_to_single_members: bool
    coordinate_system: _common_pb2.CoordinateSystemRepresentation
    excluded_members: _containers.RepeatedScalarFieldContainer[int]
    excluded_parallel_members: _containers.RepeatedScalarFieldContainer[int]
    generated_on: _containers.RepeatedScalarFieldContainer[int]
    generating_object_info: str
    is_generated: bool
    load_case: int
    load_direction: MemberLoadsFromFreeLineLoad.LoadDirection
    load_distribution: MemberLoadsFromFreeLineLoad.LoadDistribution
    lock_for_new_members: bool
    magnitude_first: float
    magnitude_second: float
    magnitude_uniform: float
    name: str
    no: int
    node_1: int
    node_2: int
    node_3: int
    relative_tolerance_for_member_on_plane: float
    relative_tolerance_for_node_on_line: float
    tolerance_type_for_member_on_plane: MemberLoadsFromFreeLineLoad.ToleranceTypeForMemberOnPlane
    tolerance_type_for_node_on_line: MemberLoadsFromFreeLineLoad.ToleranceTypeForNodeOnLine
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, absolute_tolerance_for_member_on_plane: _Optional[float] = ..., absolute_tolerance_for_node_on_line: _Optional[float] = ..., comment: _Optional[str] = ..., consider_member_eccentricity: bool = ..., consider_section_distribution: bool = ..., convert_to_single_members: bool = ..., coordinate_system: _Optional[_Union[_common_pb2.CoordinateSystemRepresentation, _Mapping]] = ..., excluded_members: _Optional[_Iterable[int]] = ..., excluded_parallel_members: _Optional[_Iterable[int]] = ..., generated_on: _Optional[_Iterable[int]] = ..., generating_object_info: _Optional[str] = ..., is_generated: bool = ..., load_case: _Optional[int] = ..., load_direction: _Optional[_Union[MemberLoadsFromFreeLineLoad.LoadDirection, str]] = ..., load_distribution: _Optional[_Union[MemberLoadsFromFreeLineLoad.LoadDistribution, str]] = ..., lock_for_new_members: bool = ..., magnitude_first: _Optional[float] = ..., magnitude_second: _Optional[float] = ..., magnitude_uniform: _Optional[float] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., node_1: _Optional[int] = ..., node_2: _Optional[int] = ..., node_3: _Optional[int] = ..., relative_tolerance_for_member_on_plane: _Optional[float] = ..., relative_tolerance_for_node_on_line: _Optional[float] = ..., tolerance_type_for_member_on_plane: _Optional[_Union[MemberLoadsFromFreeLineLoad.ToleranceTypeForMemberOnPlane, str]] = ..., tolerance_type_for_node_on_line: _Optional[_Union[MemberLoadsFromFreeLineLoad.ToleranceTypeForNodeOnLine, str]] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
