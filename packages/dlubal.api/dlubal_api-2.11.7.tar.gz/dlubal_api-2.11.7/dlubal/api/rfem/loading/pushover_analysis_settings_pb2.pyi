from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PushoverAnalysisSettings(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "comment", "assigned_to", "considering_iterative_procedure", "difference_treshold_for_iterative_procedure", "end_of_capacity_curve", "limit_deformation", "automatic_selection_of_the_highest_node", "control_node", "initial_load_factor", "load_factor_increment", "refinement_of_the_last_load_increment", "maximum_number_of_load_increments", "id_for_export_import", "metadata_for_export_import")
    class EndOfCapacityCurve(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        END_OF_CAPACITY_CURVE_LIMIT_DEFORMATION: _ClassVar[PushoverAnalysisSettings.EndOfCapacityCurve]
        END_OF_CAPACITY_CURVE_COLAPS: _ClassVar[PushoverAnalysisSettings.EndOfCapacityCurve]
    END_OF_CAPACITY_CURVE_LIMIT_DEFORMATION: PushoverAnalysisSettings.EndOfCapacityCurve
    END_OF_CAPACITY_CURVE_COLAPS: PushoverAnalysisSettings.EndOfCapacityCurve
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    CONSIDERING_ITERATIVE_PROCEDURE_FIELD_NUMBER: _ClassVar[int]
    DIFFERENCE_TRESHOLD_FOR_ITERATIVE_PROCEDURE_FIELD_NUMBER: _ClassVar[int]
    END_OF_CAPACITY_CURVE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_DEFORMATION_FIELD_NUMBER: _ClassVar[int]
    AUTOMATIC_SELECTION_OF_THE_HIGHEST_NODE_FIELD_NUMBER: _ClassVar[int]
    CONTROL_NODE_FIELD_NUMBER: _ClassVar[int]
    INITIAL_LOAD_FACTOR_FIELD_NUMBER: _ClassVar[int]
    LOAD_FACTOR_INCREMENT_FIELD_NUMBER: _ClassVar[int]
    REFINEMENT_OF_THE_LAST_LOAD_INCREMENT_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_NUMBER_OF_LOAD_INCREMENTS_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    comment: str
    assigned_to: str
    considering_iterative_procedure: bool
    difference_treshold_for_iterative_procedure: float
    end_of_capacity_curve: PushoverAnalysisSettings.EndOfCapacityCurve
    limit_deformation: float
    automatic_selection_of_the_highest_node: bool
    control_node: int
    initial_load_factor: float
    load_factor_increment: float
    refinement_of_the_last_load_increment: int
    maximum_number_of_load_increments: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., comment: _Optional[str] = ..., assigned_to: _Optional[str] = ..., considering_iterative_procedure: bool = ..., difference_treshold_for_iterative_procedure: _Optional[float] = ..., end_of_capacity_curve: _Optional[_Union[PushoverAnalysisSettings.EndOfCapacityCurve, str]] = ..., limit_deformation: _Optional[float] = ..., automatic_selection_of_the_highest_node: bool = ..., control_node: _Optional[int] = ..., initial_load_factor: _Optional[float] = ..., load_factor_increment: _Optional[float] = ..., refinement_of_the_last_load_increment: _Optional[int] = ..., maximum_number_of_load_increments: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
