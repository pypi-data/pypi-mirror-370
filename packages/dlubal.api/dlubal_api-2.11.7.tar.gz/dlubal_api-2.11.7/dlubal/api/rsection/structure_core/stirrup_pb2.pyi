from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Stirrup(_message.Message):
    __slots__ = ("no", "material", "cover_points", "diameter", "diameter_of_curvature", "mandrel_diameter_factor", "reinforcement_area", "length", "weight", "comment", "generating_object_info", "is_generated", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_FIELD_NUMBER: _ClassVar[int]
    COVER_POINTS_FIELD_NUMBER: _ClassVar[int]
    DIAMETER_FIELD_NUMBER: _ClassVar[int]
    DIAMETER_OF_CURVATURE_FIELD_NUMBER: _ClassVar[int]
    MANDREL_DIAMETER_FACTOR_FIELD_NUMBER: _ClassVar[int]
    REINFORCEMENT_AREA_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    material: int
    cover_points: _containers.RepeatedScalarFieldContainer[int]
    diameter: float
    diameter_of_curvature: float
    mandrel_diameter_factor: float
    reinforcement_area: float
    length: float
    weight: float
    comment: str
    generating_object_info: str
    is_generated: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., material: _Optional[int] = ..., cover_points: _Optional[_Iterable[int]] = ..., diameter: _Optional[float] = ..., diameter_of_curvature: _Optional[float] = ..., mandrel_diameter_factor: _Optional[float] = ..., reinforcement_area: _Optional[float] = ..., length: _Optional[float] = ..., weight: _Optional[float] = ..., comment: _Optional[str] = ..., generating_object_info: _Optional[str] = ..., is_generated: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
