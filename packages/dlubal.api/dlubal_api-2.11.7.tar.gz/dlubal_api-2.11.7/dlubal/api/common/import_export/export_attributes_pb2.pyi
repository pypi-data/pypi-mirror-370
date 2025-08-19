from google.protobuf import any_pb2 as _any_pb2
from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RotationAnglesSequence(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROTATION_ANGLES_SEQUENCE_UNSPECIFIED: _ClassVar[RotationAnglesSequence]
    ROTATION_ANGLES_SEQUENCE_XYZ: _ClassVar[RotationAnglesSequence]
    ROTATION_ANGLES_SEQUENCE_XZY: _ClassVar[RotationAnglesSequence]
    ROTATION_ANGLES_SEQUENCE_YXZ: _ClassVar[RotationAnglesSequence]
    ROTATION_ANGLES_SEQUENCE_YZX: _ClassVar[RotationAnglesSequence]
    ROTATION_ANGLES_SEQUENCE_ZXY: _ClassVar[RotationAnglesSequence]
    ROTATION_ANGLES_SEQUENCE_ZYX: _ClassVar[RotationAnglesSequence]

class AxisChange(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AXIS_CHANGE_UNSPECIFIED: _ClassVar[AxisChange]
    AXIS_CHANGE_X: _ClassVar[AxisChange]
    AXIS_CHANGE_Y: _ClassVar[AxisChange]
    AXIS_CHANGE_Z: _ClassVar[AxisChange]
ROTATION_ANGLES_SEQUENCE_UNSPECIFIED: RotationAnglesSequence
ROTATION_ANGLES_SEQUENCE_XYZ: RotationAnglesSequence
ROTATION_ANGLES_SEQUENCE_XZY: RotationAnglesSequence
ROTATION_ANGLES_SEQUENCE_YXZ: RotationAnglesSequence
ROTATION_ANGLES_SEQUENCE_YZX: RotationAnglesSequence
ROTATION_ANGLES_SEQUENCE_ZXY: RotationAnglesSequence
ROTATION_ANGLES_SEQUENCE_ZYX: RotationAnglesSequence
AXIS_CHANGE_UNSPECIFIED: AxisChange
AXIS_CHANGE_X: AxisChange
AXIS_CHANGE_Y: AxisChange
AXIS_CHANGE_Z: AxisChange

class PythonGrpcExportAttributes(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class IfcExportAttributes(_message.Message):
    __slots__ = ("type", "remove_accents", "mirror_axis_x", "mirror_axis_y", "mirror_axis_z", "origin_coordinates", "rotation_angles_sequence", "rotation_angles", "axis_change_x", "axis_change_y", "axis_change_z", "objects_to_export")
    class IfcExportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        IFC_EXPORT_TYPE_UNSPECIFIED: _ClassVar[IfcExportAttributes.IfcExportType]
        IFC_EXPORT_TYPE_REFERENCE_VIEW: _ClassVar[IfcExportAttributes.IfcExportType]
        IFC_EXPORT_TYPE_STRUCTURAL_ANALYSIS_VIEW: _ClassVar[IfcExportAttributes.IfcExportType]
    IFC_EXPORT_TYPE_UNSPECIFIED: IfcExportAttributes.IfcExportType
    IFC_EXPORT_TYPE_REFERENCE_VIEW: IfcExportAttributes.IfcExportType
    IFC_EXPORT_TYPE_STRUCTURAL_ANALYSIS_VIEW: IfcExportAttributes.IfcExportType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REMOVE_ACCENTS_FIELD_NUMBER: _ClassVar[int]
    MIRROR_AXIS_X_FIELD_NUMBER: _ClassVar[int]
    MIRROR_AXIS_Y_FIELD_NUMBER: _ClassVar[int]
    MIRROR_AXIS_Z_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLES_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLES_FIELD_NUMBER: _ClassVar[int]
    AXIS_CHANGE_X_FIELD_NUMBER: _ClassVar[int]
    AXIS_CHANGE_Y_FIELD_NUMBER: _ClassVar[int]
    AXIS_CHANGE_Z_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_TO_EXPORT_FIELD_NUMBER: _ClassVar[int]
    type: IfcExportAttributes.IfcExportType
    remove_accents: bool
    mirror_axis_x: bool
    mirror_axis_y: bool
    mirror_axis_z: bool
    origin_coordinates: _common_pb2.Vector3d
    rotation_angles_sequence: RotationAnglesSequence
    rotation_angles: _common_pb2.Vector3d
    axis_change_x: AxisChange
    axis_change_y: AxisChange
    axis_change_z: AxisChange
    objects_to_export: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    def __init__(self, type: _Optional[_Union[IfcExportAttributes.IfcExportType, str]] = ..., remove_accents: bool = ..., mirror_axis_x: bool = ..., mirror_axis_y: bool = ..., mirror_axis_z: bool = ..., origin_coordinates: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., rotation_angles_sequence: _Optional[_Union[RotationAnglesSequence, str]] = ..., rotation_angles: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., axis_change_x: _Optional[_Union[AxisChange, str]] = ..., axis_change_y: _Optional[_Union[AxisChange, str]] = ..., axis_change_z: _Optional[_Union[AxisChange, str]] = ..., objects_to_export: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ...) -> None: ...
