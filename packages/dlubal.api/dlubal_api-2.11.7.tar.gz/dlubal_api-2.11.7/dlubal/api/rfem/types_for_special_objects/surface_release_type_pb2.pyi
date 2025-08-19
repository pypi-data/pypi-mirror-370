from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SurfaceReleaseType(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "surface_releases", "translational_release_u_x", "translational_release_u_y", "translational_release_u_z", "comment", "is_generated", "generating_object_info", "local_axis_system_type", "translational_release_u_x_nonlinearity", "translational_release_u_y_nonlinearity", "translational_release_u_z_nonlinearity", "diagram_along_x_symmetric", "diagram_along_y_symmetric", "diagram_along_z_symmetric", "diagram_along_x_is_sorted", "diagram_along_y_is_sorted", "diagram_along_z_is_sorted", "diagram_along_x_table", "diagram_along_y_table", "diagram_along_z_table", "diagram_along_x_start", "diagram_along_y_start", "diagram_along_z_start", "diagram_along_x_end", "diagram_along_y_end", "diagram_along_z_end", "diagram_along_x_ac_yield_minus", "diagram_along_y_ac_yield_minus", "diagram_along_z_ac_yield_minus", "diagram_along_x_ac_yield_plus", "diagram_along_y_ac_yield_plus", "diagram_along_z_ac_yield_plus", "diagram_along_x_acceptance_criteria_active", "diagram_along_y_acceptance_criteria_active", "diagram_along_z_acceptance_criteria_active", "diagram_along_x_minus_color_one", "diagram_along_y_minus_color_one", "diagram_along_z_minus_color_one", "diagram_along_x_minus_color_two", "diagram_along_y_minus_color_two", "diagram_along_z_minus_color_two", "diagram_along_x_plus_color_one", "diagram_along_y_plus_color_one", "diagram_along_z_plus_color_one", "diagram_along_x_plus_color_two", "diagram_along_y_plus_color_two", "diagram_along_z_plus_color_two", "diagram_along_x_color_table", "diagram_along_y_color_table", "diagram_along_z_color_table", "id_for_export_import", "metadata_for_export_import")
    class LocalAxisSystemType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOCAL_AXIS_SYSTEM_TYPE_SAME_AS_ORIGINAL_SURFACE: _ClassVar[SurfaceReleaseType.LocalAxisSystemType]
        LOCAL_AXIS_SYSTEM_TYPE_REVERSED_TO_ORIGINAL_SURFACE: _ClassVar[SurfaceReleaseType.LocalAxisSystemType]
    LOCAL_AXIS_SYSTEM_TYPE_SAME_AS_ORIGINAL_SURFACE: SurfaceReleaseType.LocalAxisSystemType
    LOCAL_AXIS_SYSTEM_TYPE_REVERSED_TO_ORIGINAL_SURFACE: SurfaceReleaseType.LocalAxisSystemType
    class TranslationalReleaseUXNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_NONE: _ClassVar[SurfaceReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_DIAGRAM: _ClassVar[SurfaceReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[SurfaceReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[SurfaceReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[SurfaceReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[SurfaceReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[SurfaceReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[SurfaceReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[SurfaceReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[SurfaceReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[SurfaceReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[SurfaceReleaseType.TranslationalReleaseUXNonlinearity]
        TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[SurfaceReleaseType.TranslationalReleaseUXNonlinearity]
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_NONE: SurfaceReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_DIAGRAM: SurfaceReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: SurfaceReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: SurfaceReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_IF_NEGATIVE: SurfaceReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FAILURE_IF_POSITIVE: SurfaceReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FORCE_MOMENT_DIAGRAM: SurfaceReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1: SurfaceReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1_2: SurfaceReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: SurfaceReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FRICTION_DIRECTION_2: SurfaceReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_PARTIAL_ACTIVITY: SurfaceReleaseType.TranslationalReleaseUXNonlinearity
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_STIFFNESS_DIAGRAM: SurfaceReleaseType.TranslationalReleaseUXNonlinearity
    class TranslationalReleaseUYNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_NONE: _ClassVar[SurfaceReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_DIAGRAM: _ClassVar[SurfaceReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[SurfaceReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[SurfaceReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[SurfaceReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[SurfaceReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[SurfaceReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[SurfaceReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[SurfaceReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[SurfaceReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[SurfaceReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[SurfaceReleaseType.TranslationalReleaseUYNonlinearity]
        TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[SurfaceReleaseType.TranslationalReleaseUYNonlinearity]
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_NONE: SurfaceReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_DIAGRAM: SurfaceReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: SurfaceReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: SurfaceReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_IF_NEGATIVE: SurfaceReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FAILURE_IF_POSITIVE: SurfaceReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FORCE_MOMENT_DIAGRAM: SurfaceReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1: SurfaceReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1_2: SurfaceReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: SurfaceReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FRICTION_DIRECTION_2: SurfaceReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_PARTIAL_ACTIVITY: SurfaceReleaseType.TranslationalReleaseUYNonlinearity
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_STIFFNESS_DIAGRAM: SurfaceReleaseType.TranslationalReleaseUYNonlinearity
    class TranslationalReleaseUZNonlinearity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_NONE: _ClassVar[SurfaceReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_DIAGRAM: _ClassVar[SurfaceReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: _ClassVar[SurfaceReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: _ClassVar[SurfaceReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_IF_NEGATIVE: _ClassVar[SurfaceReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_IF_POSITIVE: _ClassVar[SurfaceReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FORCE_MOMENT_DIAGRAM: _ClassVar[SurfaceReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1: _ClassVar[SurfaceReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1_2: _ClassVar[SurfaceReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: _ClassVar[SurfaceReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_2: _ClassVar[SurfaceReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_PARTIAL_ACTIVITY: _ClassVar[SurfaceReleaseType.TranslationalReleaseUZNonlinearity]
        TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_STIFFNESS_DIAGRAM: _ClassVar[SurfaceReleaseType.TranslationalReleaseUZNonlinearity]
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_NONE: SurfaceReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_DIAGRAM: SurfaceReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_ALL_IF_NEGATIVE: SurfaceReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_ALL_IF_POSITIVE: SurfaceReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_IF_NEGATIVE: SurfaceReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FAILURE_IF_POSITIVE: SurfaceReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FORCE_MOMENT_DIAGRAM: SurfaceReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1: SurfaceReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1_2: SurfaceReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_1_PLUS_2: SurfaceReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FRICTION_DIRECTION_2: SurfaceReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_PARTIAL_ACTIVITY: SurfaceReleaseType.TranslationalReleaseUZNonlinearity
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_STIFFNESS_DIAGRAM: SurfaceReleaseType.TranslationalReleaseUZNonlinearity
    class DiagramAlongXStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_X_START_FAILURE: _ClassVar[SurfaceReleaseType.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_CONTINUOUS: _ClassVar[SurfaceReleaseType.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_STOP: _ClassVar[SurfaceReleaseType.DiagramAlongXStart]
        DIAGRAM_ALONG_X_START_YIELDING: _ClassVar[SurfaceReleaseType.DiagramAlongXStart]
    DIAGRAM_ALONG_X_START_FAILURE: SurfaceReleaseType.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_CONTINUOUS: SurfaceReleaseType.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_STOP: SurfaceReleaseType.DiagramAlongXStart
    DIAGRAM_ALONG_X_START_YIELDING: SurfaceReleaseType.DiagramAlongXStart
    class DiagramAlongYStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Y_START_FAILURE: _ClassVar[SurfaceReleaseType.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_CONTINUOUS: _ClassVar[SurfaceReleaseType.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_STOP: _ClassVar[SurfaceReleaseType.DiagramAlongYStart]
        DIAGRAM_ALONG_Y_START_YIELDING: _ClassVar[SurfaceReleaseType.DiagramAlongYStart]
    DIAGRAM_ALONG_Y_START_FAILURE: SurfaceReleaseType.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_CONTINUOUS: SurfaceReleaseType.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_STOP: SurfaceReleaseType.DiagramAlongYStart
    DIAGRAM_ALONG_Y_START_YIELDING: SurfaceReleaseType.DiagramAlongYStart
    class DiagramAlongZStart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Z_START_FAILURE: _ClassVar[SurfaceReleaseType.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_CONTINUOUS: _ClassVar[SurfaceReleaseType.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_STOP: _ClassVar[SurfaceReleaseType.DiagramAlongZStart]
        DIAGRAM_ALONG_Z_START_YIELDING: _ClassVar[SurfaceReleaseType.DiagramAlongZStart]
    DIAGRAM_ALONG_Z_START_FAILURE: SurfaceReleaseType.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_CONTINUOUS: SurfaceReleaseType.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_STOP: SurfaceReleaseType.DiagramAlongZStart
    DIAGRAM_ALONG_Z_START_YIELDING: SurfaceReleaseType.DiagramAlongZStart
    class DiagramAlongXEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_X_END_FAILURE: _ClassVar[SurfaceReleaseType.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_CONTINUOUS: _ClassVar[SurfaceReleaseType.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_STOP: _ClassVar[SurfaceReleaseType.DiagramAlongXEnd]
        DIAGRAM_ALONG_X_END_YIELDING: _ClassVar[SurfaceReleaseType.DiagramAlongXEnd]
    DIAGRAM_ALONG_X_END_FAILURE: SurfaceReleaseType.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_CONTINUOUS: SurfaceReleaseType.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_STOP: SurfaceReleaseType.DiagramAlongXEnd
    DIAGRAM_ALONG_X_END_YIELDING: SurfaceReleaseType.DiagramAlongXEnd
    class DiagramAlongYEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Y_END_FAILURE: _ClassVar[SurfaceReleaseType.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_CONTINUOUS: _ClassVar[SurfaceReleaseType.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_STOP: _ClassVar[SurfaceReleaseType.DiagramAlongYEnd]
        DIAGRAM_ALONG_Y_END_YIELDING: _ClassVar[SurfaceReleaseType.DiagramAlongYEnd]
    DIAGRAM_ALONG_Y_END_FAILURE: SurfaceReleaseType.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_CONTINUOUS: SurfaceReleaseType.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_STOP: SurfaceReleaseType.DiagramAlongYEnd
    DIAGRAM_ALONG_Y_END_YIELDING: SurfaceReleaseType.DiagramAlongYEnd
    class DiagramAlongZEnd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIAGRAM_ALONG_Z_END_FAILURE: _ClassVar[SurfaceReleaseType.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_CONTINUOUS: _ClassVar[SurfaceReleaseType.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_STOP: _ClassVar[SurfaceReleaseType.DiagramAlongZEnd]
        DIAGRAM_ALONG_Z_END_YIELDING: _ClassVar[SurfaceReleaseType.DiagramAlongZEnd]
    DIAGRAM_ALONG_Z_END_FAILURE: SurfaceReleaseType.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_CONTINUOUS: SurfaceReleaseType.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_STOP: SurfaceReleaseType.DiagramAlongZEnd
    DIAGRAM_ALONG_Z_END_YIELDING: SurfaceReleaseType.DiagramAlongZEnd
    class DiagramAlongXTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[SurfaceReleaseType.DiagramAlongXTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[SurfaceReleaseType.DiagramAlongXTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAlongXTableRow(_message.Message):
        __slots__ = ("no", "description", "displacement", "force", "spring", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
        FORCE_FIELD_NUMBER: _ClassVar[int]
        SPRING_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        displacement: float
        force: float
        spring: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., displacement: _Optional[float] = ..., force: _Optional[float] = ..., spring: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    class DiagramAlongYTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[SurfaceReleaseType.DiagramAlongYTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[SurfaceReleaseType.DiagramAlongYTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAlongYTableRow(_message.Message):
        __slots__ = ("no", "description", "displacement", "force", "spring", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
        FORCE_FIELD_NUMBER: _ClassVar[int]
        SPRING_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        displacement: float
        force: float
        spring: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., displacement: _Optional[float] = ..., force: _Optional[float] = ..., spring: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    class DiagramAlongZTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[SurfaceReleaseType.DiagramAlongZTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[SurfaceReleaseType.DiagramAlongZTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAlongZTableRow(_message.Message):
        __slots__ = ("no", "description", "displacement", "force", "spring", "note")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
        FORCE_FIELD_NUMBER: _ClassVar[int]
        SPRING_FIELD_NUMBER: _ClassVar[int]
        NOTE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        displacement: float
        force: float
        spring: float
        note: str
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., displacement: _Optional[float] = ..., force: _Optional[float] = ..., spring: _Optional[float] = ..., note: _Optional[str] = ...) -> None: ...
    class DiagramAlongXColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[SurfaceReleaseType.DiagramAlongXColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[SurfaceReleaseType.DiagramAlongXColorTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAlongXColorTableRow(_message.Message):
        __slots__ = ("no", "description", "color")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        color: _common_pb2.Color
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., color: _Optional[_Union[_common_pb2.Color, _Mapping]] = ...) -> None: ...
    class DiagramAlongYColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[SurfaceReleaseType.DiagramAlongYColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[SurfaceReleaseType.DiagramAlongYColorTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAlongYColorTableRow(_message.Message):
        __slots__ = ("no", "description", "color")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        color: _common_pb2.Color
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., color: _Optional[_Union[_common_pb2.Color, _Mapping]] = ...) -> None: ...
    class DiagramAlongZColorTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[SurfaceReleaseType.DiagramAlongZColorTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[SurfaceReleaseType.DiagramAlongZColorTableRow, _Mapping]]] = ...) -> None: ...
    class DiagramAlongZColorTableRow(_message.Message):
        __slots__ = ("no", "description", "color")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        color: _common_pb2.Color
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., color: _Optional[_Union[_common_pb2.Color, _Mapping]] = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SURFACE_RELEASES_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_X_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_Y_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_Z_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    LOCAL_AXIS_SYSTEM_TYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_X_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_Y_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONAL_RELEASE_U_Z_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_SYMMETRIC_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_IS_SORTED_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_START_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_END_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_AC_YIELD_MINUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_AC_YIELD_MINUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_AC_YIELD_MINUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_AC_YIELD_PLUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_AC_YIELD_PLUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_AC_YIELD_PLUS_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_ACCEPTANCE_CRITERIA_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_ACCEPTANCE_CRITERIA_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_ACCEPTANCE_CRITERIA_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_MINUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_MINUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_PLUS_COLOR_ONE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_PLUS_COLOR_TWO_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_X_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Y_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    DIAGRAM_ALONG_Z_COLOR_TABLE_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    surface_releases: _containers.RepeatedScalarFieldContainer[int]
    translational_release_u_x: float
    translational_release_u_y: float
    translational_release_u_z: float
    comment: str
    is_generated: bool
    generating_object_info: str
    local_axis_system_type: SurfaceReleaseType.LocalAxisSystemType
    translational_release_u_x_nonlinearity: SurfaceReleaseType.TranslationalReleaseUXNonlinearity
    translational_release_u_y_nonlinearity: SurfaceReleaseType.TranslationalReleaseUYNonlinearity
    translational_release_u_z_nonlinearity: SurfaceReleaseType.TranslationalReleaseUZNonlinearity
    diagram_along_x_symmetric: bool
    diagram_along_y_symmetric: bool
    diagram_along_z_symmetric: bool
    diagram_along_x_is_sorted: bool
    diagram_along_y_is_sorted: bool
    diagram_along_z_is_sorted: bool
    diagram_along_x_table: SurfaceReleaseType.DiagramAlongXTable
    diagram_along_y_table: SurfaceReleaseType.DiagramAlongYTable
    diagram_along_z_table: SurfaceReleaseType.DiagramAlongZTable
    diagram_along_x_start: SurfaceReleaseType.DiagramAlongXStart
    diagram_along_y_start: SurfaceReleaseType.DiagramAlongYStart
    diagram_along_z_start: SurfaceReleaseType.DiagramAlongZStart
    diagram_along_x_end: SurfaceReleaseType.DiagramAlongXEnd
    diagram_along_y_end: SurfaceReleaseType.DiagramAlongYEnd
    diagram_along_z_end: SurfaceReleaseType.DiagramAlongZEnd
    diagram_along_x_ac_yield_minus: float
    diagram_along_y_ac_yield_minus: float
    diagram_along_z_ac_yield_minus: float
    diagram_along_x_ac_yield_plus: float
    diagram_along_y_ac_yield_plus: float
    diagram_along_z_ac_yield_plus: float
    diagram_along_x_acceptance_criteria_active: bool
    diagram_along_y_acceptance_criteria_active: bool
    diagram_along_z_acceptance_criteria_active: bool
    diagram_along_x_minus_color_one: _common_pb2.Color
    diagram_along_y_minus_color_one: _common_pb2.Color
    diagram_along_z_minus_color_one: _common_pb2.Color
    diagram_along_x_minus_color_two: _common_pb2.Color
    diagram_along_y_minus_color_two: _common_pb2.Color
    diagram_along_z_minus_color_two: _common_pb2.Color
    diagram_along_x_plus_color_one: _common_pb2.Color
    diagram_along_y_plus_color_one: _common_pb2.Color
    diagram_along_z_plus_color_one: _common_pb2.Color
    diagram_along_x_plus_color_two: _common_pb2.Color
    diagram_along_y_plus_color_two: _common_pb2.Color
    diagram_along_z_plus_color_two: _common_pb2.Color
    diagram_along_x_color_table: SurfaceReleaseType.DiagramAlongXColorTable
    diagram_along_y_color_table: SurfaceReleaseType.DiagramAlongYColorTable
    diagram_along_z_color_table: SurfaceReleaseType.DiagramAlongZColorTable
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., surface_releases: _Optional[_Iterable[int]] = ..., translational_release_u_x: _Optional[float] = ..., translational_release_u_y: _Optional[float] = ..., translational_release_u_z: _Optional[float] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., local_axis_system_type: _Optional[_Union[SurfaceReleaseType.LocalAxisSystemType, str]] = ..., translational_release_u_x_nonlinearity: _Optional[_Union[SurfaceReleaseType.TranslationalReleaseUXNonlinearity, str]] = ..., translational_release_u_y_nonlinearity: _Optional[_Union[SurfaceReleaseType.TranslationalReleaseUYNonlinearity, str]] = ..., translational_release_u_z_nonlinearity: _Optional[_Union[SurfaceReleaseType.TranslationalReleaseUZNonlinearity, str]] = ..., diagram_along_x_symmetric: bool = ..., diagram_along_y_symmetric: bool = ..., diagram_along_z_symmetric: bool = ..., diagram_along_x_is_sorted: bool = ..., diagram_along_y_is_sorted: bool = ..., diagram_along_z_is_sorted: bool = ..., diagram_along_x_table: _Optional[_Union[SurfaceReleaseType.DiagramAlongXTable, _Mapping]] = ..., diagram_along_y_table: _Optional[_Union[SurfaceReleaseType.DiagramAlongYTable, _Mapping]] = ..., diagram_along_z_table: _Optional[_Union[SurfaceReleaseType.DiagramAlongZTable, _Mapping]] = ..., diagram_along_x_start: _Optional[_Union[SurfaceReleaseType.DiagramAlongXStart, str]] = ..., diagram_along_y_start: _Optional[_Union[SurfaceReleaseType.DiagramAlongYStart, str]] = ..., diagram_along_z_start: _Optional[_Union[SurfaceReleaseType.DiagramAlongZStart, str]] = ..., diagram_along_x_end: _Optional[_Union[SurfaceReleaseType.DiagramAlongXEnd, str]] = ..., diagram_along_y_end: _Optional[_Union[SurfaceReleaseType.DiagramAlongYEnd, str]] = ..., diagram_along_z_end: _Optional[_Union[SurfaceReleaseType.DiagramAlongZEnd, str]] = ..., diagram_along_x_ac_yield_minus: _Optional[float] = ..., diagram_along_y_ac_yield_minus: _Optional[float] = ..., diagram_along_z_ac_yield_minus: _Optional[float] = ..., diagram_along_x_ac_yield_plus: _Optional[float] = ..., diagram_along_y_ac_yield_plus: _Optional[float] = ..., diagram_along_z_ac_yield_plus: _Optional[float] = ..., diagram_along_x_acceptance_criteria_active: bool = ..., diagram_along_y_acceptance_criteria_active: bool = ..., diagram_along_z_acceptance_criteria_active: bool = ..., diagram_along_x_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_minus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_minus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_plus_color_one: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_y_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_z_plus_color_two: _Optional[_Union[_common_pb2.Color, _Mapping]] = ..., diagram_along_x_color_table: _Optional[_Union[SurfaceReleaseType.DiagramAlongXColorTable, _Mapping]] = ..., diagram_along_y_color_table: _Optional[_Union[SurfaceReleaseType.DiagramAlongYColorTable, _Mapping]] = ..., diagram_along_z_color_table: _Optional[_Union[SurfaceReleaseType.DiagramAlongZColorTable, _Mapping]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
