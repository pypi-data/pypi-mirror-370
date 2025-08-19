from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InnerStudsStructure(_message.Message):
    __slots__ = ("comment", "generating_object_info", "inclination_relative_to_surface_y_axis", "is_generated", "name", "no", "number_of_inner_studs", "offset_of_first_stud_absolute", "section", "spacing_absolute", "spacing_definition_relative", "spacing_distribution_gap", "spacing_relative", "thicknesses", "type", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[InnerStudsStructure.Type]
        TYPE_STANDARD: _ClassVar[InnerStudsStructure.Type]
    TYPE_UNKNOWN: InnerStudsStructure.Type
    TYPE_STANDARD: InnerStudsStructure.Type
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    INCLINATION_RELATIVE_TO_SURFACE_Y_AXIS_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_INNER_STUDS_FIELD_NUMBER: _ClassVar[int]
    OFFSET_OF_FIRST_STUD_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    SECTION_FIELD_NUMBER: _ClassVar[int]
    SPACING_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    SPACING_DEFINITION_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    SPACING_DISTRIBUTION_GAP_FIELD_NUMBER: _ClassVar[int]
    SPACING_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    THICKNESSES_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    comment: str
    generating_object_info: str
    inclination_relative_to_surface_y_axis: float
    is_generated: bool
    name: str
    no: int
    number_of_inner_studs: int
    offset_of_first_stud_absolute: float
    section: int
    spacing_absolute: float
    spacing_definition_relative: bool
    spacing_distribution_gap: bool
    spacing_relative: float
    thicknesses: _containers.RepeatedScalarFieldContainer[int]
    type: InnerStudsStructure.Type
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, comment: _Optional[str] = ..., generating_object_info: _Optional[str] = ..., inclination_relative_to_surface_y_axis: _Optional[float] = ..., is_generated: bool = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., number_of_inner_studs: _Optional[int] = ..., offset_of_first_stud_absolute: _Optional[float] = ..., section: _Optional[int] = ..., spacing_absolute: _Optional[float] = ..., spacing_definition_relative: bool = ..., spacing_distribution_gap: bool = ..., spacing_relative: _Optional[float] = ..., thicknesses: _Optional[_Iterable[int]] = ..., type: _Optional[_Union[InnerStudsStructure.Type, str]] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
