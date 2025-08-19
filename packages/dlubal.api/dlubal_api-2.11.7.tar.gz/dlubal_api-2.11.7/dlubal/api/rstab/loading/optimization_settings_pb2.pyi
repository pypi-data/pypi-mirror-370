from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OptimizationSettings(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "active", "target_value_type", "target_global_parameter", "optimizer_type", "percent_of_mutations", "optimization_values_table", "total_number_of_mutations", "comment", "id_for_export_import", "metadata_for_export_import")
    class TargetValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TARGET_VALUE_TYPE_MIN_TOTAL_WEIGHT: _ClassVar[OptimizationSettings.TargetValueType]
        TARGET_VALUE_TYPE_MAX_GLOBAL_PARAMETER: _ClassVar[OptimizationSettings.TargetValueType]
        TARGET_VALUE_TYPE_MIN_CO2_EMISSIONS: _ClassVar[OptimizationSettings.TargetValueType]
        TARGET_VALUE_TYPE_MIN_COST: _ClassVar[OptimizationSettings.TargetValueType]
        TARGET_VALUE_TYPE_MIN_GLOBAL_PARAMETER: _ClassVar[OptimizationSettings.TargetValueType]
        TARGET_VALUE_TYPE_MIN_MEMBER_DEFORMATION: _ClassVar[OptimizationSettings.TargetValueType]
        TARGET_VALUE_TYPE_MIN_NODAL_DEFORMATION: _ClassVar[OptimizationSettings.TargetValueType]
        TARGET_VALUE_TYPE_MIN_SURFACE_DEFORMATION: _ClassVar[OptimizationSettings.TargetValueType]
        TARGET_VALUE_TYPE_MIN_VECTORIAL_DISPLACEMENT: _ClassVar[OptimizationSettings.TargetValueType]
    TARGET_VALUE_TYPE_MIN_TOTAL_WEIGHT: OptimizationSettings.TargetValueType
    TARGET_VALUE_TYPE_MAX_GLOBAL_PARAMETER: OptimizationSettings.TargetValueType
    TARGET_VALUE_TYPE_MIN_CO2_EMISSIONS: OptimizationSettings.TargetValueType
    TARGET_VALUE_TYPE_MIN_COST: OptimizationSettings.TargetValueType
    TARGET_VALUE_TYPE_MIN_GLOBAL_PARAMETER: OptimizationSettings.TargetValueType
    TARGET_VALUE_TYPE_MIN_MEMBER_DEFORMATION: OptimizationSettings.TargetValueType
    TARGET_VALUE_TYPE_MIN_NODAL_DEFORMATION: OptimizationSettings.TargetValueType
    TARGET_VALUE_TYPE_MIN_SURFACE_DEFORMATION: OptimizationSettings.TargetValueType
    TARGET_VALUE_TYPE_MIN_VECTORIAL_DISPLACEMENT: OptimizationSettings.TargetValueType
    class OptimizerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OPTIMIZER_TYPE_ALL_MUTATIONS: _ClassVar[OptimizationSettings.OptimizerType]
        OPTIMIZER_TYPE_ANT_COLONY: _ClassVar[OptimizationSettings.OptimizerType]
        OPTIMIZER_TYPE_PARTICLE_SWARM: _ClassVar[OptimizationSettings.OptimizerType]
        OPTIMIZER_TYPE_RANDOM_MUTATIONS: _ClassVar[OptimizationSettings.OptimizerType]
    OPTIMIZER_TYPE_ALL_MUTATIONS: OptimizationSettings.OptimizerType
    OPTIMIZER_TYPE_ANT_COLONY: OptimizationSettings.OptimizerType
    OPTIMIZER_TYPE_PARTICLE_SWARM: OptimizationSettings.OptimizerType
    OPTIMIZER_TYPE_RANDOM_MUTATIONS: OptimizationSettings.OptimizerType
    class OptimizationValuesTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[OptimizationSettings.OptimizationValuesTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[OptimizationSettings.OptimizationValuesTableRow, _Mapping]]] = ...) -> None: ...
    class OptimizationValuesTableRow(_message.Message):
        __slots__ = ("no", "description", "value_to_optimize", "default_value", "unit", "number_of_states", "sensitivity_factor", "active")
        NO_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        VALUE_TO_OPTIMIZE_FIELD_NUMBER: _ClassVar[int]
        DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
        UNIT_FIELD_NUMBER: _ClassVar[int]
        NUMBER_OF_STATES_FIELD_NUMBER: _ClassVar[int]
        SENSITIVITY_FACTOR_FIELD_NUMBER: _ClassVar[int]
        ACTIVE_FIELD_NUMBER: _ClassVar[int]
        no: int
        description: str
        value_to_optimize: str
        default_value: str
        unit: str
        number_of_states: int
        sensitivity_factor: float
        active: bool
        def __init__(self, no: _Optional[int] = ..., description: _Optional[str] = ..., value_to_optimize: _Optional[str] = ..., default_value: _Optional[str] = ..., unit: _Optional[str] = ..., number_of_states: _Optional[int] = ..., sensitivity_factor: _Optional[float] = ..., active: bool = ...) -> None: ...
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    TARGET_VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_GLOBAL_PARAMETER_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZER_TYPE_FIELD_NUMBER: _ClassVar[int]
    PERCENT_OF_MUTATIONS_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATION_VALUES_TABLE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_NUMBER_OF_MUTATIONS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    active: bool
    target_value_type: OptimizationSettings.TargetValueType
    target_global_parameter: int
    optimizer_type: OptimizationSettings.OptimizerType
    percent_of_mutations: float
    optimization_values_table: OptimizationSettings.OptimizationValuesTable
    total_number_of_mutations: int
    comment: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., active: bool = ..., target_value_type: _Optional[_Union[OptimizationSettings.TargetValueType, str]] = ..., target_global_parameter: _Optional[int] = ..., optimizer_type: _Optional[_Union[OptimizationSettings.OptimizerType, str]] = ..., percent_of_mutations: _Optional[float] = ..., optimization_values_table: _Optional[_Union[OptimizationSettings.OptimizationValuesTable, _Mapping]] = ..., total_number_of_mutations: _Optional[int] = ..., comment: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
