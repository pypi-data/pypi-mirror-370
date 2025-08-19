from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class MemberAxesSystem(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_AXES_SYSTEM_UNSPECIFIED: _ClassVar[MemberAxesSystem]
    MEMBER_AXES_SYSTEM_PRINCIPAL_AXES_X_U_V: _ClassVar[MemberAxesSystem]
    MEMBER_AXES_SYSTEM_MEMBER_AXES_X_Y_Z: _ClassVar[MemberAxesSystem]

class CoordinateSystem(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COORDINATE_SYSTEM_UNSPECIFIED: _ClassVar[CoordinateSystem]
    COORDINATE_SYSTEM_LOCAL: _ClassVar[CoordinateSystem]
    COORDINATE_SYSTEM_GLOBAL: _ClassVar[CoordinateSystem]
MEMBER_AXES_SYSTEM_UNSPECIFIED: MemberAxesSystem
MEMBER_AXES_SYSTEM_PRINCIPAL_AXES_X_U_V: MemberAxesSystem
MEMBER_AXES_SYSTEM_MEMBER_AXES_X_Y_Z: MemberAxesSystem
COORDINATE_SYSTEM_UNSPECIFIED: CoordinateSystem
COORDINATE_SYSTEM_LOCAL: CoordinateSystem
COORDINATE_SYSTEM_GLOBAL: CoordinateSystem
