from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LineWeldedJoint(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "joint_type", "weld_type", "longitudinal_arrangement", "weld_size_a1", "weld_size_a2", "weld_length", "first_weld_position", "stress_analysis_configuration", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class JointType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        JOINT_TYPE_BUTT_JOINT: _ClassVar[LineWeldedJoint.JointType]
        JOINT_TYPE_CORNER_JOINT: _ClassVar[LineWeldedJoint.JointType]
        JOINT_TYPE_LAP_JOINT: _ClassVar[LineWeldedJoint.JointType]
        JOINT_TYPE_TEE_JOINT: _ClassVar[LineWeldedJoint.JointType]
    JOINT_TYPE_BUTT_JOINT: LineWeldedJoint.JointType
    JOINT_TYPE_CORNER_JOINT: LineWeldedJoint.JointType
    JOINT_TYPE_LAP_JOINT: LineWeldedJoint.JointType
    JOINT_TYPE_TEE_JOINT: LineWeldedJoint.JointType
    class WeldType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        WELD_TYPE_SINGLE_SQUARE: _ClassVar[LineWeldedJoint.WeldType]
        WELD_TYPE_BEVEL_AND_FILLET: _ClassVar[LineWeldedJoint.WeldType]
        WELD_TYPE_DOUBLE_BEVEL: _ClassVar[LineWeldedJoint.WeldType]
        WELD_TYPE_DOUBLE_FILLET: _ClassVar[LineWeldedJoint.WeldType]
        WELD_TYPE_DOUBLE_J: _ClassVar[LineWeldedJoint.WeldType]
        WELD_TYPE_DOUBLE_SQUARE: _ClassVar[LineWeldedJoint.WeldType]
        WELD_TYPE_DOUBLE_U: _ClassVar[LineWeldedJoint.WeldType]
        WELD_TYPE_DOUBLE_V: _ClassVar[LineWeldedJoint.WeldType]
        WELD_TYPE_J_AND_FILLET: _ClassVar[LineWeldedJoint.WeldType]
        WELD_TYPE_SINGLE_BEVEL: _ClassVar[LineWeldedJoint.WeldType]
        WELD_TYPE_SINGLE_FILLET: _ClassVar[LineWeldedJoint.WeldType]
        WELD_TYPE_SINGLE_J: _ClassVar[LineWeldedJoint.WeldType]
        WELD_TYPE_SINGLE_U: _ClassVar[LineWeldedJoint.WeldType]
        WELD_TYPE_SINGLE_V: _ClassVar[LineWeldedJoint.WeldType]
        WELD_TYPE_V_AND_FILLET: _ClassVar[LineWeldedJoint.WeldType]
    WELD_TYPE_SINGLE_SQUARE: LineWeldedJoint.WeldType
    WELD_TYPE_BEVEL_AND_FILLET: LineWeldedJoint.WeldType
    WELD_TYPE_DOUBLE_BEVEL: LineWeldedJoint.WeldType
    WELD_TYPE_DOUBLE_FILLET: LineWeldedJoint.WeldType
    WELD_TYPE_DOUBLE_J: LineWeldedJoint.WeldType
    WELD_TYPE_DOUBLE_SQUARE: LineWeldedJoint.WeldType
    WELD_TYPE_DOUBLE_U: LineWeldedJoint.WeldType
    WELD_TYPE_DOUBLE_V: LineWeldedJoint.WeldType
    WELD_TYPE_J_AND_FILLET: LineWeldedJoint.WeldType
    WELD_TYPE_SINGLE_BEVEL: LineWeldedJoint.WeldType
    WELD_TYPE_SINGLE_FILLET: LineWeldedJoint.WeldType
    WELD_TYPE_SINGLE_J: LineWeldedJoint.WeldType
    WELD_TYPE_SINGLE_U: LineWeldedJoint.WeldType
    WELD_TYPE_SINGLE_V: LineWeldedJoint.WeldType
    WELD_TYPE_V_AND_FILLET: LineWeldedJoint.WeldType
    class LongitudinalArrangement(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LONGITUDINAL_ARRANGEMENT_CONTINUOUS: _ClassVar[LineWeldedJoint.LongitudinalArrangement]
        LONGITUDINAL_ARRANGEMENT_INTERMITTENT_SMEARED_APPROACH: _ClassVar[LineWeldedJoint.LongitudinalArrangement]
    LONGITUDINAL_ARRANGEMENT_CONTINUOUS: LineWeldedJoint.LongitudinalArrangement
    LONGITUDINAL_ARRANGEMENT_INTERMITTENT_SMEARED_APPROACH: LineWeldedJoint.LongitudinalArrangement
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    JOINT_TYPE_FIELD_NUMBER: _ClassVar[int]
    WELD_TYPE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDINAL_ARRANGEMENT_FIELD_NUMBER: _ClassVar[int]
    WELD_SIZE_A1_FIELD_NUMBER: _ClassVar[int]
    WELD_SIZE_A2_FIELD_NUMBER: _ClassVar[int]
    WELD_LENGTH_FIELD_NUMBER: _ClassVar[int]
    FIRST_WELD_POSITION_FIELD_NUMBER: _ClassVar[int]
    STRESS_ANALYSIS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    joint_type: LineWeldedJoint.JointType
    weld_type: LineWeldedJoint.WeldType
    longitudinal_arrangement: LineWeldedJoint.LongitudinalArrangement
    weld_size_a1: float
    weld_size_a2: float
    weld_length: float
    first_weld_position: float
    stress_analysis_configuration: int
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., joint_type: _Optional[_Union[LineWeldedJoint.JointType, str]] = ..., weld_type: _Optional[_Union[LineWeldedJoint.WeldType, str]] = ..., longitudinal_arrangement: _Optional[_Union[LineWeldedJoint.LongitudinalArrangement, str]] = ..., weld_size_a1: _Optional[float] = ..., weld_size_a2: _Optional[float] = ..., weld_length: _Optional[float] = ..., first_weld_position: _Optional[float] = ..., stress_analysis_configuration: _Optional[int] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
