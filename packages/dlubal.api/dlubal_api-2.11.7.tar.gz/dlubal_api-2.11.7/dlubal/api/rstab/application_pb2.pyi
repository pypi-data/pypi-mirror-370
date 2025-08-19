from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from dlubal.api.common import model_id_pb2 as _model_id_pb2
from dlubal.api.common import table_data_pb2 as _table_data_pb2
from dlubal.api.common import common_messages_pb2 as _common_messages_pb2
from dlubal.api.rstab import base_data_pb2 as _base_data_pb2
from dlubal.api.rstab import object_type_pb2 as _object_type_pb2
from dlubal.api.rstab import object_id_pb2 as _object_id_pb2
from dlubal.api.rstab.results import result_table_pb2 as _result_table_pb2
from dlubal.api.rstab.results import results_query_pb2 as _results_query_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetObjectIdListRequest(_message.Message):
    __slots__ = ("object_type", "parent_no", "model_id")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARENT_NO_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    object_type: _object_type_pb2.ObjectType
    parent_no: int
    model_id: _model_id_pb2.ModelId
    def __init__(self, object_type: _Optional[_Union[_object_type_pb2.ObjectType, str]] = ..., parent_no: _Optional[int] = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ...) -> None: ...

class BaseDataRequest(_message.Message):
    __slots__ = ("base_data", "model_id")
    BASE_DATA_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    base_data: _base_data_pb2.BaseData
    model_id: _model_id_pb2.ModelId
    def __init__(self, base_data: _Optional[_Union[_base_data_pb2.BaseData, _Mapping]] = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ...) -> None: ...

class HasResultsRequest(_message.Message):
    __slots__ = ("loading", "model_id")
    LOADING_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    loading: _object_id_pb2.ObjectId
    model_id: _model_id_pb2.ModelId
    def __init__(self, loading: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ...) -> None: ...

class GetResultTableRequest(_message.Message):
    __slots__ = ("table", "loading", "model_id")
    TABLE_FIELD_NUMBER: _ClassVar[int]
    LOADING_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    table: _result_table_pb2.ResultTable
    loading: _object_id_pb2.ObjectId
    model_id: _model_id_pb2.ModelId
    def __init__(self, table: _Optional[_Union[_result_table_pb2.ResultTable, str]] = ..., loading: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ...) -> None: ...

class CalculateSpecificRequest(_message.Message):
    __slots__ = ("loadings", "skip_warnings", "model_id")
    LOADINGS_FIELD_NUMBER: _ClassVar[int]
    SKIP_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    loadings: _containers.RepeatedCompositeFieldContainer[_object_id_pb2.ObjectId]
    skip_warnings: bool
    model_id: _model_id_pb2.ModelId
    def __init__(self, loadings: _Optional[_Iterable[_Union[_object_id_pb2.ObjectId, _Mapping]]] = ..., skip_warnings: bool = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ...) -> None: ...
