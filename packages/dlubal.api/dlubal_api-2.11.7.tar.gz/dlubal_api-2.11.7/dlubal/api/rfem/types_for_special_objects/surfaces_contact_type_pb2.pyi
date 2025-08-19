from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SurfacesContactType(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "comment", "surfaces_contacts", "perpendicular_to_surface", "parallel_to_surface", "rigid_friction_type", "rigid_friction_coefficient", "rigid_friction_limit_stress", "elastic_behavior_shear_stiffness", "elastic_friction_type", "elastic_friction_coefficient", "elastic_friction_limit_stress", "elastic_friction_shear_stiffness", "id_for_export_import", "metadata_for_export_import")
    class PerpendicularToSurface(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PERPENDICULAR_TO_SURFACE_FULL_FORCE_TRANSMISSION: _ClassVar[SurfacesContactType.PerpendicularToSurface]
        PERPENDICULAR_TO_SURFACE_FAILURE_UNDER_COMPRESSION: _ClassVar[SurfacesContactType.PerpendicularToSurface]
        PERPENDICULAR_TO_SURFACE_FAILURE_UNDER_TENSION: _ClassVar[SurfacesContactType.PerpendicularToSurface]
    PERPENDICULAR_TO_SURFACE_FULL_FORCE_TRANSMISSION: SurfacesContactType.PerpendicularToSurface
    PERPENDICULAR_TO_SURFACE_FAILURE_UNDER_COMPRESSION: SurfacesContactType.PerpendicularToSurface
    PERPENDICULAR_TO_SURFACE_FAILURE_UNDER_TENSION: SurfacesContactType.PerpendicularToSurface
    class ParallelToSurface(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARALLEL_TO_SURFACE_FAILURE_IF_CONTACT_PERPENDICULAR_TO_SURFACES_FAILED: _ClassVar[SurfacesContactType.ParallelToSurface]
        PARALLEL_TO_SURFACE_ELASTIC_BEHAVIOR: _ClassVar[SurfacesContactType.ParallelToSurface]
        PARALLEL_TO_SURFACE_ELASTIC_FRICTION: _ClassVar[SurfacesContactType.ParallelToSurface]
        PARALLEL_TO_SURFACE_FULL_FORCE_TRANSMISSION: _ClassVar[SurfacesContactType.ParallelToSurface]
        PARALLEL_TO_SURFACE_RIGID_FRICTION: _ClassVar[SurfacesContactType.ParallelToSurface]
    PARALLEL_TO_SURFACE_FAILURE_IF_CONTACT_PERPENDICULAR_TO_SURFACES_FAILED: SurfacesContactType.ParallelToSurface
    PARALLEL_TO_SURFACE_ELASTIC_BEHAVIOR: SurfacesContactType.ParallelToSurface
    PARALLEL_TO_SURFACE_ELASTIC_FRICTION: SurfacesContactType.ParallelToSurface
    PARALLEL_TO_SURFACE_FULL_FORCE_TRANSMISSION: SurfacesContactType.ParallelToSurface
    PARALLEL_TO_SURFACE_RIGID_FRICTION: SurfacesContactType.ParallelToSurface
    class RigidFrictionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        RIGID_FRICTION_TYPE_COEFFICIENT: _ClassVar[SurfacesContactType.RigidFrictionType]
        RIGID_FRICTION_TYPE_LIMIT_STRESS: _ClassVar[SurfacesContactType.RigidFrictionType]
    RIGID_FRICTION_TYPE_COEFFICIENT: SurfacesContactType.RigidFrictionType
    RIGID_FRICTION_TYPE_LIMIT_STRESS: SurfacesContactType.RigidFrictionType
    class ElasticFrictionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ELASTIC_FRICTION_TYPE_COEFFICIENT: _ClassVar[SurfacesContactType.ElasticFrictionType]
        ELASTIC_FRICTION_TYPE_LIMIT_STRESS: _ClassVar[SurfacesContactType.ElasticFrictionType]
    ELASTIC_FRICTION_TYPE_COEFFICIENT: SurfacesContactType.ElasticFrictionType
    ELASTIC_FRICTION_TYPE_LIMIT_STRESS: SurfacesContactType.ElasticFrictionType
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    SURFACES_CONTACTS_FIELD_NUMBER: _ClassVar[int]
    PERPENDICULAR_TO_SURFACE_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TO_SURFACE_FIELD_NUMBER: _ClassVar[int]
    RIGID_FRICTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    RIGID_FRICTION_COEFFICIENT_FIELD_NUMBER: _ClassVar[int]
    RIGID_FRICTION_LIMIT_STRESS_FIELD_NUMBER: _ClassVar[int]
    ELASTIC_BEHAVIOR_SHEAR_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    ELASTIC_FRICTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    ELASTIC_FRICTION_COEFFICIENT_FIELD_NUMBER: _ClassVar[int]
    ELASTIC_FRICTION_LIMIT_STRESS_FIELD_NUMBER: _ClassVar[int]
    ELASTIC_FRICTION_SHEAR_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    comment: str
    surfaces_contacts: _containers.RepeatedScalarFieldContainer[int]
    perpendicular_to_surface: SurfacesContactType.PerpendicularToSurface
    parallel_to_surface: SurfacesContactType.ParallelToSurface
    rigid_friction_type: SurfacesContactType.RigidFrictionType
    rigid_friction_coefficient: float
    rigid_friction_limit_stress: float
    elastic_behavior_shear_stiffness: float
    elastic_friction_type: SurfacesContactType.ElasticFrictionType
    elastic_friction_coefficient: float
    elastic_friction_limit_stress: float
    elastic_friction_shear_stiffness: float
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., comment: _Optional[str] = ..., surfaces_contacts: _Optional[_Iterable[int]] = ..., perpendicular_to_surface: _Optional[_Union[SurfacesContactType.PerpendicularToSurface, str]] = ..., parallel_to_surface: _Optional[_Union[SurfacesContactType.ParallelToSurface, str]] = ..., rigid_friction_type: _Optional[_Union[SurfacesContactType.RigidFrictionType, str]] = ..., rigid_friction_coefficient: _Optional[float] = ..., rigid_friction_limit_stress: _Optional[float] = ..., elastic_behavior_shear_stiffness: _Optional[float] = ..., elastic_friction_type: _Optional[_Union[SurfacesContactType.ElasticFrictionType, str]] = ..., elastic_friction_coefficient: _Optional[float] = ..., elastic_friction_limit_stress: _Optional[float] = ..., elastic_friction_shear_stiffness: _Optional[float] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
