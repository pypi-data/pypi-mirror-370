from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LoadModel(_message.Message):
    __slots__ = ("comment", "load_components", "name", "no", "type", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[LoadModel.Type]
        TYPE_ON_MEMBERS: _ClassVar[LoadModel.Type]
        TYPE_ON_SURFACES: _ClassVar[LoadModel.Type]
    TYPE_UNKNOWN: LoadModel.Type
    TYPE_ON_MEMBERS: LoadModel.Type
    TYPE_ON_SURFACES: LoadModel.Type
    class LoadComponentsTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[LoadModel.LoadComponentsTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LoadModel.LoadComponentsTableRow, _Mapping]]] = ...) -> None: ...
    class LoadComponentsTableRow(_message.Message):
        __slots__ = ("key", "name", "symbol", "value", "unit", "count_of_components", "position_x", "position_y", "position_A", "position_B", "load_magnitude_P", "load_magnitude_P2", "load_magnitude_M", "load_magnitude_M2", "eccentricity_y", "eccentricity_z", "width", "length", "diameter", "gauge", "number_of_loads", "load_type", "coordinate_system", "load_direction", "type_of_load", "children")
        class LoadType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            LOAD_TYPE_UNKNOWN: _ClassVar[LoadModel.LoadComponentsTableRow.LoadType]
        LOAD_TYPE_UNKNOWN: LoadModel.LoadComponentsTableRow.LoadType
        class LoadDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            LOAD_DIRECTION_UNKNOWN: _ClassVar[LoadModel.LoadComponentsTableRow.LoadDirection]
        LOAD_DIRECTION_UNKNOWN: LoadModel.LoadComponentsTableRow.LoadDirection
        class TypeOfLoad(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            TYPE_OF_LOAD_UNKNOWN: _ClassVar[LoadModel.LoadComponentsTableRow.TypeOfLoad]
        TYPE_OF_LOAD_UNKNOWN: LoadModel.LoadComponentsTableRow.TypeOfLoad
        KEY_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        SYMBOL_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        UNIT_FIELD_NUMBER: _ClassVar[int]
        COUNT_OF_COMPONENTS_FIELD_NUMBER: _ClassVar[int]
        POSITION_X_FIELD_NUMBER: _ClassVar[int]
        POSITION_Y_FIELD_NUMBER: _ClassVar[int]
        POSITION_A_FIELD_NUMBER: _ClassVar[int]
        POSITION_B_FIELD_NUMBER: _ClassVar[int]
        LOAD_MAGNITUDE_P_FIELD_NUMBER: _ClassVar[int]
        LOAD_MAGNITUDE_P2_FIELD_NUMBER: _ClassVar[int]
        LOAD_MAGNITUDE_M_FIELD_NUMBER: _ClassVar[int]
        LOAD_MAGNITUDE_M2_FIELD_NUMBER: _ClassVar[int]
        ECCENTRICITY_Y_FIELD_NUMBER: _ClassVar[int]
        ECCENTRICITY_Z_FIELD_NUMBER: _ClassVar[int]
        WIDTH_FIELD_NUMBER: _ClassVar[int]
        LENGTH_FIELD_NUMBER: _ClassVar[int]
        DIAMETER_FIELD_NUMBER: _ClassVar[int]
        GAUGE_FIELD_NUMBER: _ClassVar[int]
        NUMBER_OF_LOADS_FIELD_NUMBER: _ClassVar[int]
        LOAD_TYPE_FIELD_NUMBER: _ClassVar[int]
        COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
        LOAD_DIRECTION_FIELD_NUMBER: _ClassVar[int]
        TYPE_OF_LOAD_FIELD_NUMBER: _ClassVar[int]
        CHILDREN_FIELD_NUMBER: _ClassVar[int]
        key: str
        name: str
        symbol: str
        value: str
        unit: str
        count_of_components: int
        position_x: float
        position_y: float
        position_A: float
        position_B: float
        load_magnitude_P: float
        load_magnitude_P2: float
        load_magnitude_M: float
        load_magnitude_M2: float
        eccentricity_y: float
        eccentricity_z: float
        width: float
        length: float
        diameter: float
        gauge: float
        number_of_loads: int
        load_type: LoadModel.LoadComponentsTableRow.LoadType
        coordinate_system: int
        load_direction: LoadModel.LoadComponentsTableRow.LoadDirection
        type_of_load: LoadModel.LoadComponentsTableRow.TypeOfLoad
        children: _containers.RepeatedCompositeFieldContainer[LoadModel.LoadComponentsTableRow]
        def __init__(self, key: _Optional[str] = ..., name: _Optional[str] = ..., symbol: _Optional[str] = ..., value: _Optional[str] = ..., unit: _Optional[str] = ..., count_of_components: _Optional[int] = ..., position_x: _Optional[float] = ..., position_y: _Optional[float] = ..., position_A: _Optional[float] = ..., position_B: _Optional[float] = ..., load_magnitude_P: _Optional[float] = ..., load_magnitude_P2: _Optional[float] = ..., load_magnitude_M: _Optional[float] = ..., load_magnitude_M2: _Optional[float] = ..., eccentricity_y: _Optional[float] = ..., eccentricity_z: _Optional[float] = ..., width: _Optional[float] = ..., length: _Optional[float] = ..., diameter: _Optional[float] = ..., gauge: _Optional[float] = ..., number_of_loads: _Optional[int] = ..., load_type: _Optional[_Union[LoadModel.LoadComponentsTableRow.LoadType, str]] = ..., coordinate_system: _Optional[int] = ..., load_direction: _Optional[_Union[LoadModel.LoadComponentsTableRow.LoadDirection, str]] = ..., type_of_load: _Optional[_Union[LoadModel.LoadComponentsTableRow.TypeOfLoad, str]] = ..., children: _Optional[_Iterable[_Union[LoadModel.LoadComponentsTableRow, _Mapping]]] = ...) -> None: ...
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    LOAD_COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    comment: str
    load_components: LoadModel.LoadComponentsTable
    name: str
    no: int
    type: LoadModel.Type
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, comment: _Optional[str] = ..., load_components: _Optional[_Union[LoadModel.LoadComponentsTable, _Mapping]] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., type: _Optional[_Union[LoadModel.Type, str]] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
