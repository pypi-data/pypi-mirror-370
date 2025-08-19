from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TimberServiceConditions(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "members", "member_sets", "assigned_to_objects", "moisture_service_condition", "treatment", "temperature", "outdoor_environment", "long_term_high_temperature_of_surface", "permanent_load_design_situation", "timber_structures", "short_term_construction_or_maintenance", "timber_is_point_impregnated", "member_pressure_treated", "equilibrium_moisture_content", "user_defined_temperature", "impregnation_with_flame_retardant_under_pressure", "comment", "id_for_export_import", "metadata_for_export_import")
    class MoistureServiceCondition(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MOISTURE_SERVICE_CONDITION_UNKNOWN: _ClassVar[TimberServiceConditions.MoistureServiceCondition]
        MOISTURE_SERVICE_CONDITION_DRY: _ClassVar[TimberServiceConditions.MoistureServiceCondition]
        MOISTURE_SERVICE_CONDITION_MOIST: _ClassVar[TimberServiceConditions.MoistureServiceCondition]
        MOISTURE_SERVICE_CONDITION_RATHER_DRY: _ClassVar[TimberServiceConditions.MoistureServiceCondition]
        MOISTURE_SERVICE_CONDITION_RATHER_WET: _ClassVar[TimberServiceConditions.MoistureServiceCondition]
        MOISTURE_SERVICE_CONDITION_VERY_DRY: _ClassVar[TimberServiceConditions.MoistureServiceCondition]
        MOISTURE_SERVICE_CONDITION_WET: _ClassVar[TimberServiceConditions.MoistureServiceCondition]
    MOISTURE_SERVICE_CONDITION_UNKNOWN: TimberServiceConditions.MoistureServiceCondition
    MOISTURE_SERVICE_CONDITION_DRY: TimberServiceConditions.MoistureServiceCondition
    MOISTURE_SERVICE_CONDITION_MOIST: TimberServiceConditions.MoistureServiceCondition
    MOISTURE_SERVICE_CONDITION_RATHER_DRY: TimberServiceConditions.MoistureServiceCondition
    MOISTURE_SERVICE_CONDITION_RATHER_WET: TimberServiceConditions.MoistureServiceCondition
    MOISTURE_SERVICE_CONDITION_VERY_DRY: TimberServiceConditions.MoistureServiceCondition
    MOISTURE_SERVICE_CONDITION_WET: TimberServiceConditions.MoistureServiceCondition
    class Treatment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TREATMENT_UNKNOWN: _ClassVar[TimberServiceConditions.Treatment]
        TREATMENT_FIRE_RETARDANT: _ClassVar[TimberServiceConditions.Treatment]
        TREATMENT_NONE: _ClassVar[TimberServiceConditions.Treatment]
        TREATMENT_PRESERVATIVE: _ClassVar[TimberServiceConditions.Treatment]
    TREATMENT_UNKNOWN: TimberServiceConditions.Treatment
    TREATMENT_FIRE_RETARDANT: TimberServiceConditions.Treatment
    TREATMENT_NONE: TimberServiceConditions.Treatment
    TREATMENT_PRESERVATIVE: TimberServiceConditions.Treatment
    class Temperature(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TEMPERATURE_UNKNOWN: _ClassVar[TimberServiceConditions.Temperature]
        TEMPERATURE_EQUAL_TO_50: _ClassVar[TimberServiceConditions.Temperature]
        TEMPERATURE_LESS_OR_EQUAL_100: _ClassVar[TimberServiceConditions.Temperature]
        TEMPERATURE_LESS_OR_EQUAL_35: _ClassVar[TimberServiceConditions.Temperature]
        TEMPERATURE_RANGE_100_125: _ClassVar[TimberServiceConditions.Temperature]
        TEMPERATURE_RANGE_125_150: _ClassVar[TimberServiceConditions.Temperature]
        TEMPERATURE_RANGE_35_50: _ClassVar[TimberServiceConditions.Temperature]
        TEMPERATURE_TEMPERATURE_ZONE_1: _ClassVar[TimberServiceConditions.Temperature]
        TEMPERATURE_TEMPERATURE_ZONE_2: _ClassVar[TimberServiceConditions.Temperature]
        TEMPERATURE_TEMPERATURE_ZONE_3: _ClassVar[TimberServiceConditions.Temperature]
    TEMPERATURE_UNKNOWN: TimberServiceConditions.Temperature
    TEMPERATURE_EQUAL_TO_50: TimberServiceConditions.Temperature
    TEMPERATURE_LESS_OR_EQUAL_100: TimberServiceConditions.Temperature
    TEMPERATURE_LESS_OR_EQUAL_35: TimberServiceConditions.Temperature
    TEMPERATURE_RANGE_100_125: TimberServiceConditions.Temperature
    TEMPERATURE_RANGE_125_150: TimberServiceConditions.Temperature
    TEMPERATURE_RANGE_35_50: TimberServiceConditions.Temperature
    TEMPERATURE_TEMPERATURE_ZONE_1: TimberServiceConditions.Temperature
    TEMPERATURE_TEMPERATURE_ZONE_2: TimberServiceConditions.Temperature
    TEMPERATURE_TEMPERATURE_ZONE_3: TimberServiceConditions.Temperature
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    MOISTURE_SERVICE_CONDITION_FIELD_NUMBER: _ClassVar[int]
    TREATMENT_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    OUTDOOR_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    LONG_TERM_HIGH_TEMPERATURE_OF_SURFACE_FIELD_NUMBER: _ClassVar[int]
    PERMANENT_LOAD_DESIGN_SITUATION_FIELD_NUMBER: _ClassVar[int]
    TIMBER_STRUCTURES_FIELD_NUMBER: _ClassVar[int]
    SHORT_TERM_CONSTRUCTION_OR_MAINTENANCE_FIELD_NUMBER: _ClassVar[int]
    TIMBER_IS_POINT_IMPREGNATED_FIELD_NUMBER: _ClassVar[int]
    MEMBER_PRESSURE_TREATED_FIELD_NUMBER: _ClassVar[int]
    EQUILIBRIUM_MOISTURE_CONTENT_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    IMPREGNATION_WITH_FLAME_RETARDANT_UNDER_PRESSURE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    members: _containers.RepeatedScalarFieldContainer[int]
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_objects: str
    moisture_service_condition: TimberServiceConditions.MoistureServiceCondition
    treatment: TimberServiceConditions.Treatment
    temperature: TimberServiceConditions.Temperature
    outdoor_environment: bool
    long_term_high_temperature_of_surface: bool
    permanent_load_design_situation: bool
    timber_structures: bool
    short_term_construction_or_maintenance: bool
    timber_is_point_impregnated: bool
    member_pressure_treated: bool
    equilibrium_moisture_content: float
    user_defined_temperature: float
    impregnation_with_flame_retardant_under_pressure: bool
    comment: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., assigned_to_objects: _Optional[str] = ..., moisture_service_condition: _Optional[_Union[TimberServiceConditions.MoistureServiceCondition, str]] = ..., treatment: _Optional[_Union[TimberServiceConditions.Treatment, str]] = ..., temperature: _Optional[_Union[TimberServiceConditions.Temperature, str]] = ..., outdoor_environment: bool = ..., long_term_high_temperature_of_surface: bool = ..., permanent_load_design_situation: bool = ..., timber_structures: bool = ..., short_term_construction_or_maintenance: bool = ..., timber_is_point_impregnated: bool = ..., member_pressure_treated: bool = ..., equilibrium_moisture_content: _Optional[float] = ..., user_defined_temperature: _Optional[float] = ..., impregnation_with_flame_retardant_under_pressure: bool = ..., comment: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
