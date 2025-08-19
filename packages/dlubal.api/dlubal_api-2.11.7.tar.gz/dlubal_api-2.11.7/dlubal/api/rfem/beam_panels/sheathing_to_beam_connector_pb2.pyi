from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SheathingToBeamConnector(_message.Message):
    __slots__ = ("comment", "connector_type", "diameter", "dimension_a", "dimension_b", "dry_lumber", "generating_object_info", "is_generated", "length", "line_hinge", "nail_type", "name", "no", "parameter_d", "parameter_l", "spacing", "stiffness_calculation", "stiffness_longitudinal_only", "structural_one_grade_sheathing", "thicknesses", "type", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class ConnectorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CONNECTOR_TYPE_NAIL: _ClassVar[SheathingToBeamConnector.ConnectorType]
        CONNECTOR_TYPE_STAPLE: _ClassVar[SheathingToBeamConnector.ConnectorType]
        CONNECTOR_TYPE_USER_DEFINED: _ClassVar[SheathingToBeamConnector.ConnectorType]
    CONNECTOR_TYPE_NAIL: SheathingToBeamConnector.ConnectorType
    CONNECTOR_TYPE_STAPLE: SheathingToBeamConnector.ConnectorType
    CONNECTOR_TYPE_USER_DEFINED: SheathingToBeamConnector.ConnectorType
    class NailType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NAIL_TYPE_USER_DEFINED: _ClassVar[SheathingToBeamConnector.NailType]
        NAIL_TYPE_10D_COMMON: _ClassVar[SheathingToBeamConnector.NailType]
        NAIL_TYPE_6D_COMMON: _ClassVar[SheathingToBeamConnector.NailType]
        NAIL_TYPE_8D_COMMON: _ClassVar[SheathingToBeamConnector.NailType]
    NAIL_TYPE_USER_DEFINED: SheathingToBeamConnector.NailType
    NAIL_TYPE_10D_COMMON: SheathingToBeamConnector.NailType
    NAIL_TYPE_6D_COMMON: SheathingToBeamConnector.NailType
    NAIL_TYPE_8D_COMMON: SheathingToBeamConnector.NailType
    class StiffnessCalculation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STIFFNESS_CALCULATION_EN_1995: _ClassVar[SheathingToBeamConnector.StiffnessCalculation]
        STIFFNESS_CALCULATION_CSA_O86: _ClassVar[SheathingToBeamConnector.StiffnessCalculation]
        STIFFNESS_CALCULATION_NDS: _ClassVar[SheathingToBeamConnector.StiffnessCalculation]
    STIFFNESS_CALCULATION_EN_1995: SheathingToBeamConnector.StiffnessCalculation
    STIFFNESS_CALCULATION_CSA_O86: SheathingToBeamConnector.StiffnessCalculation
    STIFFNESS_CALCULATION_NDS: SheathingToBeamConnector.StiffnessCalculation
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[SheathingToBeamConnector.Type]
        TYPE_STANDARD: _ClassVar[SheathingToBeamConnector.Type]
    TYPE_UNKNOWN: SheathingToBeamConnector.Type
    TYPE_STANDARD: SheathingToBeamConnector.Type
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    CONNECTOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    DIAMETER_FIELD_NUMBER: _ClassVar[int]
    DIMENSION_A_FIELD_NUMBER: _ClassVar[int]
    DIMENSION_B_FIELD_NUMBER: _ClassVar[int]
    DRY_LUMBER_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    LINE_HINGE_FIELD_NUMBER: _ClassVar[int]
    NAIL_TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_D_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_L_FIELD_NUMBER: _ClassVar[int]
    SPACING_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_CALCULATION_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_LONGITUDINAL_ONLY_FIELD_NUMBER: _ClassVar[int]
    STRUCTURAL_ONE_GRADE_SHEATHING_FIELD_NUMBER: _ClassVar[int]
    THICKNESSES_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    comment: str
    connector_type: SheathingToBeamConnector.ConnectorType
    diameter: float
    dimension_a: float
    dimension_b: float
    dry_lumber: bool
    generating_object_info: str
    is_generated: bool
    length: float
    line_hinge: int
    nail_type: SheathingToBeamConnector.NailType
    name: str
    no: int
    parameter_d: float
    parameter_l: float
    spacing: float
    stiffness_calculation: SheathingToBeamConnector.StiffnessCalculation
    stiffness_longitudinal_only: bool
    structural_one_grade_sheathing: bool
    thicknesses: _containers.RepeatedScalarFieldContainer[int]
    type: SheathingToBeamConnector.Type
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, comment: _Optional[str] = ..., connector_type: _Optional[_Union[SheathingToBeamConnector.ConnectorType, str]] = ..., diameter: _Optional[float] = ..., dimension_a: _Optional[float] = ..., dimension_b: _Optional[float] = ..., dry_lumber: bool = ..., generating_object_info: _Optional[str] = ..., is_generated: bool = ..., length: _Optional[float] = ..., line_hinge: _Optional[int] = ..., nail_type: _Optional[_Union[SheathingToBeamConnector.NailType, str]] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., parameter_d: _Optional[float] = ..., parameter_l: _Optional[float] = ..., spacing: _Optional[float] = ..., stiffness_calculation: _Optional[_Union[SheathingToBeamConnector.StiffnessCalculation, str]] = ..., stiffness_longitudinal_only: bool = ..., structural_one_grade_sheathing: bool = ..., thicknesses: _Optional[_Iterable[int]] = ..., type: _Optional[_Union[SheathingToBeamConnector.Type, str]] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
