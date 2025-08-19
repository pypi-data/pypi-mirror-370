from dlubal.api.common import model_id_pb2 as _model_id_pb2
from dlubal.api.rsection.results import results_type_pb2 as _results_type_pb2
from dlubal.api.rsection.results.settings import result_settings_pb2 as _result_settings_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResultsQuery(_message.Message):
    __slots__ = ("model_id", "results_type", "filters", "member_axes_system", "nodal_support_coordinate_system")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    RESULTS_TYPE_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_AXES_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    NODAL_SUPPORT_COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    model_id: _model_id_pb2.ModelId
    results_type: _results_type_pb2.ResultsType
    filters: _containers.RepeatedCompositeFieldContainer[ResultsFilter]
    member_axes_system: _result_settings_pb2.MemberAxesSystem
    nodal_support_coordinate_system: _result_settings_pb2.CoordinateSystem
    def __init__(self, model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ..., results_type: _Optional[_Union[_results_type_pb2.ResultsType, str]] = ..., filters: _Optional[_Iterable[_Union[ResultsFilter, _Mapping]]] = ..., member_axes_system: _Optional[_Union[_result_settings_pb2.MemberAxesSystem, str]] = ..., nodal_support_coordinate_system: _Optional[_Union[_result_settings_pb2.CoordinateSystem, str]] = ...) -> None: ...

class ResultsFilter(_message.Message):
    __slots__ = ("column_id", "filter_expression")
    COLUMN_ID_FIELD_NUMBER: _ClassVar[int]
    FILTER_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    column_id: str
    filter_expression: str
    def __init__(self, column_id: _Optional[str] = ..., filter_expression: _Optional[str] = ...) -> None: ...
