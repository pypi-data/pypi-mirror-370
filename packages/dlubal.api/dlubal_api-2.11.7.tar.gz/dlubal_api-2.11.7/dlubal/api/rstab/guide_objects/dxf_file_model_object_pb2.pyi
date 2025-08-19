from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DxfFileModelObject(_message.Message):
    __slots__ = ("no", "origin_coordinates", "origin_coordinate_x", "origin_coordinate_y", "origin_coordinate_z", "rotation_angles_sequence", "rotation_angle_1", "rotation_angle_2", "rotation_angle_3", "user_defined_name_enabled", "name", "file_path", "file_name", "coordinate_system", "insert_point", "scale_is_nonuniform", "scale_is_defined_as_relative", "scale_relative", "scale_absolute", "scale_relative_x", "scale_relative_y", "scale_relative_z", "scale_absolute_x", "scale_absolute_y", "scale_absolute_z", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class RotationAnglesSequence(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROTATION_ANGLES_SEQUENCE_XYZ: _ClassVar[DxfFileModelObject.RotationAnglesSequence]
        ROTATION_ANGLES_SEQUENCE_XZY: _ClassVar[DxfFileModelObject.RotationAnglesSequence]
        ROTATION_ANGLES_SEQUENCE_YXZ: _ClassVar[DxfFileModelObject.RotationAnglesSequence]
        ROTATION_ANGLES_SEQUENCE_YZX: _ClassVar[DxfFileModelObject.RotationAnglesSequence]
        ROTATION_ANGLES_SEQUENCE_ZXY: _ClassVar[DxfFileModelObject.RotationAnglesSequence]
        ROTATION_ANGLES_SEQUENCE_ZYX: _ClassVar[DxfFileModelObject.RotationAnglesSequence]
    ROTATION_ANGLES_SEQUENCE_XYZ: DxfFileModelObject.RotationAnglesSequence
    ROTATION_ANGLES_SEQUENCE_XZY: DxfFileModelObject.RotationAnglesSequence
    ROTATION_ANGLES_SEQUENCE_YXZ: DxfFileModelObject.RotationAnglesSequence
    ROTATION_ANGLES_SEQUENCE_YZX: DxfFileModelObject.RotationAnglesSequence
    ROTATION_ANGLES_SEQUENCE_ZXY: DxfFileModelObject.RotationAnglesSequence
    ROTATION_ANGLES_SEQUENCE_ZYX: DxfFileModelObject.RotationAnglesSequence
    class InsertPoint(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        INSERT_POINT_CENTER: _ClassVar[DxfFileModelObject.InsertPoint]
        INSERT_POINT_MX: _ClassVar[DxfFileModelObject.InsertPoint]
        INSERT_POINT_MXMYMZ: _ClassVar[DxfFileModelObject.InsertPoint]
        INSERT_POINT_MXMYPZ: _ClassVar[DxfFileModelObject.InsertPoint]
        INSERT_POINT_MXPYMZ: _ClassVar[DxfFileModelObject.InsertPoint]
        INSERT_POINT_MXPYPZ: _ClassVar[DxfFileModelObject.InsertPoint]
        INSERT_POINT_MY: _ClassVar[DxfFileModelObject.InsertPoint]
        INSERT_POINT_MZ: _ClassVar[DxfFileModelObject.InsertPoint]
        INSERT_POINT_ORIGINAL_POSITION: _ClassVar[DxfFileModelObject.InsertPoint]
        INSERT_POINT_PX: _ClassVar[DxfFileModelObject.InsertPoint]
        INSERT_POINT_PXMYMZ: _ClassVar[DxfFileModelObject.InsertPoint]
        INSERT_POINT_PXMYPZ: _ClassVar[DxfFileModelObject.InsertPoint]
        INSERT_POINT_PXPYMZ: _ClassVar[DxfFileModelObject.InsertPoint]
        INSERT_POINT_PXPYPZ: _ClassVar[DxfFileModelObject.InsertPoint]
        INSERT_POINT_PY: _ClassVar[DxfFileModelObject.InsertPoint]
        INSERT_POINT_PZ: _ClassVar[DxfFileModelObject.InsertPoint]
    INSERT_POINT_CENTER: DxfFileModelObject.InsertPoint
    INSERT_POINT_MX: DxfFileModelObject.InsertPoint
    INSERT_POINT_MXMYMZ: DxfFileModelObject.InsertPoint
    INSERT_POINT_MXMYPZ: DxfFileModelObject.InsertPoint
    INSERT_POINT_MXPYMZ: DxfFileModelObject.InsertPoint
    INSERT_POINT_MXPYPZ: DxfFileModelObject.InsertPoint
    INSERT_POINT_MY: DxfFileModelObject.InsertPoint
    INSERT_POINT_MZ: DxfFileModelObject.InsertPoint
    INSERT_POINT_ORIGINAL_POSITION: DxfFileModelObject.InsertPoint
    INSERT_POINT_PX: DxfFileModelObject.InsertPoint
    INSERT_POINT_PXMYMZ: DxfFileModelObject.InsertPoint
    INSERT_POINT_PXMYPZ: DxfFileModelObject.InsertPoint
    INSERT_POINT_PXPYMZ: DxfFileModelObject.InsertPoint
    INSERT_POINT_PXPYPZ: DxfFileModelObject.InsertPoint
    INSERT_POINT_PY: DxfFileModelObject.InsertPoint
    INSERT_POINT_PZ: DxfFileModelObject.InsertPoint
    NO_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_COORDINATE_X_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_COORDINATE_Y_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_COORDINATE_Z_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLES_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLE_1_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLE_2_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLE_3_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    INSERT_POINT_FIELD_NUMBER: _ClassVar[int]
    SCALE_IS_NONUNIFORM_FIELD_NUMBER: _ClassVar[int]
    SCALE_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    SCALE_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    SCALE_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    SCALE_RELATIVE_X_FIELD_NUMBER: _ClassVar[int]
    SCALE_RELATIVE_Y_FIELD_NUMBER: _ClassVar[int]
    SCALE_RELATIVE_Z_FIELD_NUMBER: _ClassVar[int]
    SCALE_ABSOLUTE_X_FIELD_NUMBER: _ClassVar[int]
    SCALE_ABSOLUTE_Y_FIELD_NUMBER: _ClassVar[int]
    SCALE_ABSOLUTE_Z_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    origin_coordinates: _common_pb2.Vector3d
    origin_coordinate_x: float
    origin_coordinate_y: float
    origin_coordinate_z: float
    rotation_angles_sequence: DxfFileModelObject.RotationAnglesSequence
    rotation_angle_1: float
    rotation_angle_2: float
    rotation_angle_3: float
    user_defined_name_enabled: bool
    name: str
    file_path: str
    file_name: str
    coordinate_system: int
    insert_point: DxfFileModelObject.InsertPoint
    scale_is_nonuniform: bool
    scale_is_defined_as_relative: bool
    scale_relative: float
    scale_absolute: float
    scale_relative_x: float
    scale_relative_y: float
    scale_relative_z: float
    scale_absolute_x: float
    scale_absolute_y: float
    scale_absolute_z: float
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., origin_coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., origin_coordinate_x: _Optional[float] = ..., origin_coordinate_y: _Optional[float] = ..., origin_coordinate_z: _Optional[float] = ..., rotation_angles_sequence: _Optional[_Union[DxfFileModelObject.RotationAnglesSequence, str]] = ..., rotation_angle_1: _Optional[float] = ..., rotation_angle_2: _Optional[float] = ..., rotation_angle_3: _Optional[float] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., file_path: _Optional[str] = ..., file_name: _Optional[str] = ..., coordinate_system: _Optional[int] = ..., insert_point: _Optional[_Union[DxfFileModelObject.InsertPoint, str]] = ..., scale_is_nonuniform: bool = ..., scale_is_defined_as_relative: bool = ..., scale_relative: _Optional[float] = ..., scale_absolute: _Optional[float] = ..., scale_relative_x: _Optional[float] = ..., scale_relative_y: _Optional[float] = ..., scale_relative_z: _Optional[float] = ..., scale_absolute_x: _Optional[float] = ..., scale_absolute_y: _Optional[float] = ..., scale_absolute_z: _Optional[float] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
