from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Craneway(_message.Message):
    __slots__ = ("assigned_crane_number", "assigned_crane_one", "assigned_crane_three", "assigned_crane_two", "calculation_method", "consider_buffers", "crane_position_increment", "crane_type", "craneway_girder_one", "craneway_girder_two", "designed_craneway_girders_number", "end_buffer_height", "end_buffer_position", "members_to_design", "no", "serviceability_configuration", "start_buffer_height", "start_buffer_position", "to_design", "type", "ultimate_configuration", "id_for_export_import", "metadata_for_export_import")
    class AssignedCraneNumber(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ASSIGNED_CRANE_NUMBER_ONE: _ClassVar[Craneway.AssignedCraneNumber]
        ASSIGNED_CRANE_NUMBER_THREE: _ClassVar[Craneway.AssignedCraneNumber]
        ASSIGNED_CRANE_NUMBER_TWO: _ClassVar[Craneway.AssignedCraneNumber]
    ASSIGNED_CRANE_NUMBER_ONE: Craneway.AssignedCraneNumber
    ASSIGNED_CRANE_NUMBER_THREE: Craneway.AssignedCraneNumber
    ASSIGNED_CRANE_NUMBER_TWO: Craneway.AssignedCraneNumber
    class CalculationMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CALCULATION_METHOD_PARTIAL_INTERACTION_ONE: _ClassVar[Craneway.CalculationMethod]
        CALCULATION_METHOD_FULL_INTERACTION: _ClassVar[Craneway.CalculationMethod]
        CALCULATION_METHOD_PARTIAL_INTERACTION_TWO: _ClassVar[Craneway.CalculationMethod]
    CALCULATION_METHOD_PARTIAL_INTERACTION_ONE: Craneway.CalculationMethod
    CALCULATION_METHOD_FULL_INTERACTION: Craneway.CalculationMethod
    CALCULATION_METHOD_PARTIAL_INTERACTION_TWO: Craneway.CalculationMethod
    class ConsiderBuffers(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CONSIDER_BUFFERS_NONE: _ClassVar[Craneway.ConsiderBuffers]
        CONSIDER_BUFFERS_BOTH: _ClassVar[Craneway.ConsiderBuffers]
        CONSIDER_BUFFERS_END: _ClassVar[Craneway.ConsiderBuffers]
        CONSIDER_BUFFERS_START: _ClassVar[Craneway.ConsiderBuffers]
    CONSIDER_BUFFERS_NONE: Craneway.ConsiderBuffers
    CONSIDER_BUFFERS_BOTH: Craneway.ConsiderBuffers
    CONSIDER_BUFFERS_END: Craneway.ConsiderBuffers
    CONSIDER_BUFFERS_START: Craneway.ConsiderBuffers
    class CraneType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CRANE_TYPE_BRIDGE: _ClassVar[Craneway.CraneType]
        CRANE_TYPE_SUSPENSION: _ClassVar[Craneway.CraneType]
    CRANE_TYPE_BRIDGE: Craneway.CraneType
    CRANE_TYPE_SUSPENSION: Craneway.CraneType
    class DesignedCranewayGirdersNumber(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DESIGNED_CRANEWAY_GIRDERS_NUMBER_ONE: _ClassVar[Craneway.DesignedCranewayGirdersNumber]
        DESIGNED_CRANEWAY_GIRDERS_NUMBER_TWO: _ClassVar[Craneway.DesignedCranewayGirdersNumber]
    DESIGNED_CRANEWAY_GIRDERS_NUMBER_ONE: Craneway.DesignedCranewayGirdersNumber
    DESIGNED_CRANEWAY_GIRDERS_NUMBER_TWO: Craneway.DesignedCranewayGirdersNumber
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[Craneway.Type]
    TYPE_UNKNOWN: Craneway.Type
    ASSIGNED_CRANE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_CRANE_ONE_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_CRANE_THREE_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_CRANE_TWO_FIELD_NUMBER: _ClassVar[int]
    CALCULATION_METHOD_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_BUFFERS_FIELD_NUMBER: _ClassVar[int]
    CRANE_POSITION_INCREMENT_FIELD_NUMBER: _ClassVar[int]
    CRANE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CRANEWAY_GIRDER_ONE_FIELD_NUMBER: _ClassVar[int]
    CRANEWAY_GIRDER_TWO_FIELD_NUMBER: _ClassVar[int]
    DESIGNED_CRANEWAY_GIRDERS_NUMBER_FIELD_NUMBER: _ClassVar[int]
    END_BUFFER_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    END_BUFFER_POSITION_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_TO_DESIGN_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    SERVICEABILITY_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    START_BUFFER_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    START_BUFFER_POSITION_FIELD_NUMBER: _ClassVar[int]
    TO_DESIGN_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ULTIMATE_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    assigned_crane_number: Craneway.AssignedCraneNumber
    assigned_crane_one: int
    assigned_crane_three: int
    assigned_crane_two: int
    calculation_method: Craneway.CalculationMethod
    consider_buffers: Craneway.ConsiderBuffers
    crane_position_increment: float
    crane_type: Craneway.CraneType
    craneway_girder_one: _containers.RepeatedScalarFieldContainer[int]
    craneway_girder_two: _containers.RepeatedScalarFieldContainer[int]
    designed_craneway_girders_number: Craneway.DesignedCranewayGirdersNumber
    end_buffer_height: float
    end_buffer_position: float
    members_to_design: _containers.RepeatedScalarFieldContainer[int]
    no: int
    serviceability_configuration: int
    start_buffer_height: float
    start_buffer_position: float
    to_design: bool
    type: Craneway.Type
    ultimate_configuration: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, assigned_crane_number: _Optional[_Union[Craneway.AssignedCraneNumber, str]] = ..., assigned_crane_one: _Optional[int] = ..., assigned_crane_three: _Optional[int] = ..., assigned_crane_two: _Optional[int] = ..., calculation_method: _Optional[_Union[Craneway.CalculationMethod, str]] = ..., consider_buffers: _Optional[_Union[Craneway.ConsiderBuffers, str]] = ..., crane_position_increment: _Optional[float] = ..., crane_type: _Optional[_Union[Craneway.CraneType, str]] = ..., craneway_girder_one: _Optional[_Iterable[int]] = ..., craneway_girder_two: _Optional[_Iterable[int]] = ..., designed_craneway_girders_number: _Optional[_Union[Craneway.DesignedCranewayGirdersNumber, str]] = ..., end_buffer_height: _Optional[float] = ..., end_buffer_position: _Optional[float] = ..., members_to_design: _Optional[_Iterable[int]] = ..., no: _Optional[int] = ..., serviceability_configuration: _Optional[int] = ..., start_buffer_height: _Optional[float] = ..., start_buffer_position: _Optional[float] = ..., to_design: bool = ..., type: _Optional[_Union[Craneway.Type, str]] = ..., ultimate_configuration: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
