from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IfcFileModelObject(_message.Message):
    __slots__ = ("no", "filename", "axis_change_x", "axis_change_y", "axis_change_z", "mirror_axis_x", "mirror_axis_y", "mirror_axis_z", "origin_coordinate_x", "origin_coordinate_y", "origin_coordinate_z", "rotation_angle_0", "rotation_angle_1", "rotation_angle_2", "rotation_angles_sequence", "type", "id_for_export_import", "metadata_for_export_import")
    class AxisChangeX(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXIS_CHANGE_X: _ClassVar[IfcFileModelObject.AxisChangeX]
        AXIS_CHANGE_Y: _ClassVar[IfcFileModelObject.AxisChangeX]
        AXIS_CHANGE_Z: _ClassVar[IfcFileModelObject.AxisChangeX]
    AXIS_CHANGE_X: IfcFileModelObject.AxisChangeX
    AXIS_CHANGE_Y: IfcFileModelObject.AxisChangeX
    AXIS_CHANGE_Z: IfcFileModelObject.AxisChangeX
    class AxisChangeY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXIS_CHANGE_Y_X: _ClassVar[IfcFileModelObject.AxisChangeY]
        AXIS_CHANGE_Y_Y: _ClassVar[IfcFileModelObject.AxisChangeY]
        AXIS_CHANGE_Y_Z: _ClassVar[IfcFileModelObject.AxisChangeY]
    AXIS_CHANGE_Y_X: IfcFileModelObject.AxisChangeY
    AXIS_CHANGE_Y_Y: IfcFileModelObject.AxisChangeY
    AXIS_CHANGE_Y_Z: IfcFileModelObject.AxisChangeY
    class AxisChangeZ(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AXIS_CHANGE_Z_X: _ClassVar[IfcFileModelObject.AxisChangeZ]
        AXIS_CHANGE_Z_Y: _ClassVar[IfcFileModelObject.AxisChangeZ]
        AXIS_CHANGE_Z_Z: _ClassVar[IfcFileModelObject.AxisChangeZ]
    AXIS_CHANGE_Z_X: IfcFileModelObject.AxisChangeZ
    AXIS_CHANGE_Z_Y: IfcFileModelObject.AxisChangeZ
    AXIS_CHANGE_Z_Z: IfcFileModelObject.AxisChangeZ
    class RotationAnglesSequence(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROTATION_ANGLES_SEQUENCE_XYZ: _ClassVar[IfcFileModelObject.RotationAnglesSequence]
        ROTATION_ANGLES_SEQUENCE_XZY: _ClassVar[IfcFileModelObject.RotationAnglesSequence]
        ROTATION_ANGLES_SEQUENCE_YXZ: _ClassVar[IfcFileModelObject.RotationAnglesSequence]
        ROTATION_ANGLES_SEQUENCE_YZX: _ClassVar[IfcFileModelObject.RotationAnglesSequence]
        ROTATION_ANGLES_SEQUENCE_ZXY: _ClassVar[IfcFileModelObject.RotationAnglesSequence]
        ROTATION_ANGLES_SEQUENCE_ZYX: _ClassVar[IfcFileModelObject.RotationAnglesSequence]
    ROTATION_ANGLES_SEQUENCE_XYZ: IfcFileModelObject.RotationAnglesSequence
    ROTATION_ANGLES_SEQUENCE_XZY: IfcFileModelObject.RotationAnglesSequence
    ROTATION_ANGLES_SEQUENCE_YXZ: IfcFileModelObject.RotationAnglesSequence
    ROTATION_ANGLES_SEQUENCE_YZX: IfcFileModelObject.RotationAnglesSequence
    ROTATION_ANGLES_SEQUENCE_ZXY: IfcFileModelObject.RotationAnglesSequence
    ROTATION_ANGLES_SEQUENCE_ZYX: IfcFileModelObject.RotationAnglesSequence
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_PHANTOM: _ClassVar[IfcFileModelObject.Type]
        TYPE_STANDARD: _ClassVar[IfcFileModelObject.Type]
    TYPE_PHANTOM: IfcFileModelObject.Type
    TYPE_STANDARD: IfcFileModelObject.Type
    NO_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    AXIS_CHANGE_X_FIELD_NUMBER: _ClassVar[int]
    AXIS_CHANGE_Y_FIELD_NUMBER: _ClassVar[int]
    AXIS_CHANGE_Z_FIELD_NUMBER: _ClassVar[int]
    MIRROR_AXIS_X_FIELD_NUMBER: _ClassVar[int]
    MIRROR_AXIS_Y_FIELD_NUMBER: _ClassVar[int]
    MIRROR_AXIS_Z_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_COORDINATE_X_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_COORDINATE_Y_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_COORDINATE_Z_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLE_0_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLE_1_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLE_2_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLES_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    filename: str
    axis_change_x: IfcFileModelObject.AxisChangeX
    axis_change_y: IfcFileModelObject.AxisChangeY
    axis_change_z: IfcFileModelObject.AxisChangeZ
    mirror_axis_x: bool
    mirror_axis_y: bool
    mirror_axis_z: bool
    origin_coordinate_x: float
    origin_coordinate_y: float
    origin_coordinate_z: float
    rotation_angle_0: float
    rotation_angle_1: float
    rotation_angle_2: float
    rotation_angles_sequence: IfcFileModelObject.RotationAnglesSequence
    type: IfcFileModelObject.Type
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., filename: _Optional[str] = ..., axis_change_x: _Optional[_Union[IfcFileModelObject.AxisChangeX, str]] = ..., axis_change_y: _Optional[_Union[IfcFileModelObject.AxisChangeY, str]] = ..., axis_change_z: _Optional[_Union[IfcFileModelObject.AxisChangeZ, str]] = ..., mirror_axis_x: bool = ..., mirror_axis_y: bool = ..., mirror_axis_z: bool = ..., origin_coordinate_x: _Optional[float] = ..., origin_coordinate_y: _Optional[float] = ..., origin_coordinate_z: _Optional[float] = ..., rotation_angle_0: _Optional[float] = ..., rotation_angle_1: _Optional[float] = ..., rotation_angle_2: _Optional[float] = ..., rotation_angles_sequence: _Optional[_Union[IfcFileModelObject.RotationAnglesSequence, str]] = ..., type: _Optional[_Union[IfcFileModelObject.Type, str]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
