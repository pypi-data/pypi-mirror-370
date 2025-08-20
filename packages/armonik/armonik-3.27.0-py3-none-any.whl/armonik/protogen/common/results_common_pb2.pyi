from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import result_status_pb2 as _result_status_pb2
from . import results_fields_pb2 as _results_fields_pb2
from . import results_filters_pb2 as _results_filters_pb2
from . import sort_direction_pb2 as _sort_direction_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResultRaw(_message.Message):
    __slots__ = ("session_id", "name", "owner_task_id", "status", "created_at", "completed_at", "result_id", "size", "created_by", "opaque_id", "manual_deletion")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_TASK_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    OPAQUE_ID_FIELD_NUMBER: _ClassVar[int]
    MANUAL_DELETION_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    name: str
    owner_task_id: str
    status: _result_status_pb2.ResultStatus
    created_at: _timestamp_pb2.Timestamp
    completed_at: _timestamp_pb2.Timestamp
    result_id: str
    size: int
    created_by: str
    opaque_id: bytes
    manual_deletion: bool
    def __init__(self, session_id: _Optional[str] = ..., name: _Optional[str] = ..., owner_task_id: _Optional[str] = ..., status: _Optional[_Union[_result_status_pb2.ResultStatus, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., completed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., result_id: _Optional[str] = ..., size: _Optional[int] = ..., created_by: _Optional[str] = ..., opaque_id: _Optional[bytes] = ..., manual_deletion: bool = ...) -> None: ...

class ListResultsRequest(_message.Message):
    __slots__ = ("page", "page_size", "filters", "sort")
    class Sort(_message.Message):
        __slots__ = ("field", "direction")
        FIELD_FIELD_NUMBER: _ClassVar[int]
        DIRECTION_FIELD_NUMBER: _ClassVar[int]
        field: _results_fields_pb2.ResultField
        direction: _sort_direction_pb2.SortDirection
        def __init__(self, field: _Optional[_Union[_results_fields_pb2.ResultField, _Mapping]] = ..., direction: _Optional[_Union[_sort_direction_pb2.SortDirection, str]] = ...) -> None: ...
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    filters: _results_filters_pb2.Filters
    sort: ListResultsRequest.Sort
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., filters: _Optional[_Union[_results_filters_pb2.Filters, _Mapping]] = ..., sort: _Optional[_Union[ListResultsRequest.Sort, _Mapping]] = ...) -> None: ...

class ListResultsResponse(_message.Message):
    __slots__ = ("results", "page", "page_size", "total")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ResultRaw]
    page: int
    page_size: int
    total: int
    def __init__(self, results: _Optional[_Iterable[_Union[ResultRaw, _Mapping]]] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class GetResultRequest(_message.Message):
    __slots__ = ("result_id",)
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    result_id: str
    def __init__(self, result_id: _Optional[str] = ...) -> None: ...

class GetResultResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: ResultRaw
    def __init__(self, result: _Optional[_Union[ResultRaw, _Mapping]] = ...) -> None: ...

class GetOwnerTaskIdRequest(_message.Message):
    __slots__ = ("session_id", "result_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    result_id: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, session_id: _Optional[str] = ..., result_id: _Optional[_Iterable[str]] = ...) -> None: ...

class GetOwnerTaskIdResponse(_message.Message):
    __slots__ = ("result_task", "session_id")
    class MapResultTask(_message.Message):
        __slots__ = ("result_id", "task_id")
        RESULT_ID_FIELD_NUMBER: _ClassVar[int]
        TASK_ID_FIELD_NUMBER: _ClassVar[int]
        result_id: str
        task_id: str
        def __init__(self, result_id: _Optional[str] = ..., task_id: _Optional[str] = ...) -> None: ...
    RESULT_TASK_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    result_task: _containers.RepeatedCompositeFieldContainer[GetOwnerTaskIdResponse.MapResultTask]
    session_id: str
    def __init__(self, result_task: _Optional[_Iterable[_Union[GetOwnerTaskIdResponse.MapResultTask, _Mapping]]] = ..., session_id: _Optional[str] = ...) -> None: ...

class CreateResultsMetaDataRequest(_message.Message):
    __slots__ = ("results", "session_id")
    class ResultCreate(_message.Message):
        __slots__ = ("name", "manual_deletion")
        NAME_FIELD_NUMBER: _ClassVar[int]
        MANUAL_DELETION_FIELD_NUMBER: _ClassVar[int]
        name: str
        manual_deletion: bool
        def __init__(self, name: _Optional[str] = ..., manual_deletion: bool = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[CreateResultsMetaDataRequest.ResultCreate]
    session_id: str
    def __init__(self, results: _Optional[_Iterable[_Union[CreateResultsMetaDataRequest.ResultCreate, _Mapping]]] = ..., session_id: _Optional[str] = ...) -> None: ...

class CreateResultsMetaDataResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ResultRaw]
    def __init__(self, results: _Optional[_Iterable[_Union[ResultRaw, _Mapping]]] = ...) -> None: ...

class CreateResultsRequest(_message.Message):
    __slots__ = ("results", "session_id")
    class ResultCreate(_message.Message):
        __slots__ = ("name", "data", "manual_deletion")
        NAME_FIELD_NUMBER: _ClassVar[int]
        DATA_FIELD_NUMBER: _ClassVar[int]
        MANUAL_DELETION_FIELD_NUMBER: _ClassVar[int]
        name: str
        data: bytes
        manual_deletion: bool
        def __init__(self, name: _Optional[str] = ..., data: _Optional[bytes] = ..., manual_deletion: bool = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[CreateResultsRequest.ResultCreate]
    session_id: str
    def __init__(self, results: _Optional[_Iterable[_Union[CreateResultsRequest.ResultCreate, _Mapping]]] = ..., session_id: _Optional[str] = ...) -> None: ...

class CreateResultsResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ResultRaw]
    def __init__(self, results: _Optional[_Iterable[_Union[ResultRaw, _Mapping]]] = ...) -> None: ...

class UploadResultDataRequest(_message.Message):
    __slots__ = ("id", "data_chunk")
    class ResultIdentifier(_message.Message):
        __slots__ = ("session_id", "result_id")
        SESSION_ID_FIELD_NUMBER: _ClassVar[int]
        RESULT_ID_FIELD_NUMBER: _ClassVar[int]
        session_id: str
        result_id: str
        def __init__(self, session_id: _Optional[str] = ..., result_id: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    DATA_CHUNK_FIELD_NUMBER: _ClassVar[int]
    id: UploadResultDataRequest.ResultIdentifier
    data_chunk: bytes
    def __init__(self, id: _Optional[_Union[UploadResultDataRequest.ResultIdentifier, _Mapping]] = ..., data_chunk: _Optional[bytes] = ...) -> None: ...

class UploadResultDataResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: ResultRaw
    def __init__(self, result: _Optional[_Union[ResultRaw, _Mapping]] = ...) -> None: ...

class ResultsServiceConfigurationResponse(_message.Message):
    __slots__ = ("data_chunk_max_size",)
    DATA_CHUNK_MAX_SIZE_FIELD_NUMBER: _ClassVar[int]
    data_chunk_max_size: int
    def __init__(self, data_chunk_max_size: _Optional[int] = ...) -> None: ...

class DownloadResultDataRequest(_message.Message):
    __slots__ = ("session_id", "result_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    result_id: str
    def __init__(self, session_id: _Optional[str] = ..., result_id: _Optional[str] = ...) -> None: ...

class DownloadResultDataResponse(_message.Message):
    __slots__ = ("data_chunk",)
    DATA_CHUNK_FIELD_NUMBER: _ClassVar[int]
    data_chunk: bytes
    def __init__(self, data_chunk: _Optional[bytes] = ...) -> None: ...

class DeleteResultsDataRequest(_message.Message):
    __slots__ = ("session_id", "result_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    result_id: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, session_id: _Optional[str] = ..., result_id: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteResultsDataResponse(_message.Message):
    __slots__ = ("session_id", "result_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    result_id: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, session_id: _Optional[str] = ..., result_id: _Optional[_Iterable[str]] = ...) -> None: ...

class ImportResultsDataRequest(_message.Message):
    __slots__ = ("session_id", "results")
    class ResultOpaqueId(_message.Message):
        __slots__ = ("result_id", "opaque_id")
        RESULT_ID_FIELD_NUMBER: _ClassVar[int]
        OPAQUE_ID_FIELD_NUMBER: _ClassVar[int]
        result_id: str
        opaque_id: bytes
        def __init__(self, result_id: _Optional[str] = ..., opaque_id: _Optional[bytes] = ...) -> None: ...
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    results: _containers.RepeatedCompositeFieldContainer[ImportResultsDataRequest.ResultOpaqueId]
    def __init__(self, session_id: _Optional[str] = ..., results: _Optional[_Iterable[_Union[ImportResultsDataRequest.ResultOpaqueId, _Mapping]]] = ...) -> None: ...

class ImportResultsDataResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ResultRaw]
    def __init__(self, results: _Optional[_Iterable[_Union[ResultRaw, _Mapping]]] = ...) -> None: ...

class WatchResultRequest(_message.Message):
    __slots__ = ("fetch_statuses", "watch_statuses", "result_ids")
    FETCH_STATUSES_FIELD_NUMBER: _ClassVar[int]
    WATCH_STATUSES_FIELD_NUMBER: _ClassVar[int]
    RESULT_IDS_FIELD_NUMBER: _ClassVar[int]
    fetch_statuses: _containers.RepeatedScalarFieldContainer[_result_status_pb2.ResultStatus]
    watch_statuses: _containers.RepeatedScalarFieldContainer[_result_status_pb2.ResultStatus]
    result_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, fetch_statuses: _Optional[_Iterable[_Union[_result_status_pb2.ResultStatus, str]]] = ..., watch_statuses: _Optional[_Iterable[_Union[_result_status_pb2.ResultStatus, str]]] = ..., result_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class WatchResultResponse(_message.Message):
    __slots__ = ("status", "result_ids")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_IDS_FIELD_NUMBER: _ClassVar[int]
    status: _result_status_pb2.ResultStatus
    result_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, status: _Optional[_Union[_result_status_pb2.ResultStatus, str]] = ..., result_ids: _Optional[_Iterable[str]] = ...) -> None: ...
