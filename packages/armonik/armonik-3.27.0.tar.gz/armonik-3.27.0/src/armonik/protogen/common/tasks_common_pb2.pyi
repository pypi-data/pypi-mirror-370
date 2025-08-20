from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import objects_pb2 as _objects_pb2
from . import sort_direction_pb2 as _sort_direction_pb2
from . import task_status_pb2 as _task_status_pb2
from . import tasks_fields_pb2 as _tasks_fields_pb2
from . import tasks_filters_pb2 as _tasks_filters_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaskDetailed(_message.Message):
    __slots__ = ("id", "session_id", "owner_pod_id", "initial_task_id", "parent_task_ids", "data_dependencies", "expected_output_ids", "retry_of_ids", "status", "status_message", "options", "created_at", "submitted_at", "received_at", "acquired_at", "fetched_at", "started_at", "processed_at", "ended_at", "pod_ttl", "creation_to_end_duration", "processing_to_end_duration", "received_to_end_duration", "payload_id", "created_by", "output", "pod_hostname")
    class Output(_message.Message):
        __slots__ = ("success", "error")
        SUCCESS_FIELD_NUMBER: _ClassVar[int]
        ERROR_FIELD_NUMBER: _ClassVar[int]
        success: bool
        error: str
        def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_POD_ID_FIELD_NUMBER: _ClassVar[int]
    INITIAL_TASK_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_TASK_IDS_FIELD_NUMBER: _ClassVar[int]
    DATA_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_OUTPUT_IDS_FIELD_NUMBER: _ClassVar[int]
    RETRY_OF_IDS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    SUBMITTED_AT_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_AT_FIELD_NUMBER: _ClassVar[int]
    ACQUIRED_AT_FIELD_NUMBER: _ClassVar[int]
    FETCHED_AT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_AT_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    POD_TTL_FIELD_NUMBER: _ClassVar[int]
    CREATION_TO_END_DURATION_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_TO_END_DURATION_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_TO_END_DURATION_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    POD_HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    session_id: str
    owner_pod_id: str
    initial_task_id: str
    parent_task_ids: _containers.RepeatedScalarFieldContainer[str]
    data_dependencies: _containers.RepeatedScalarFieldContainer[str]
    expected_output_ids: _containers.RepeatedScalarFieldContainer[str]
    retry_of_ids: _containers.RepeatedScalarFieldContainer[str]
    status: _task_status_pb2.TaskStatus
    status_message: str
    options: _objects_pb2.TaskOptions
    created_at: _timestamp_pb2.Timestamp
    submitted_at: _timestamp_pb2.Timestamp
    received_at: _timestamp_pb2.Timestamp
    acquired_at: _timestamp_pb2.Timestamp
    fetched_at: _timestamp_pb2.Timestamp
    started_at: _timestamp_pb2.Timestamp
    processed_at: _timestamp_pb2.Timestamp
    ended_at: _timestamp_pb2.Timestamp
    pod_ttl: _timestamp_pb2.Timestamp
    creation_to_end_duration: _duration_pb2.Duration
    processing_to_end_duration: _duration_pb2.Duration
    received_to_end_duration: _duration_pb2.Duration
    payload_id: str
    created_by: str
    output: TaskDetailed.Output
    pod_hostname: str
    def __init__(self, id: _Optional[str] = ..., session_id: _Optional[str] = ..., owner_pod_id: _Optional[str] = ..., initial_task_id: _Optional[str] = ..., parent_task_ids: _Optional[_Iterable[str]] = ..., data_dependencies: _Optional[_Iterable[str]] = ..., expected_output_ids: _Optional[_Iterable[str]] = ..., retry_of_ids: _Optional[_Iterable[str]] = ..., status: _Optional[_Union[_task_status_pb2.TaskStatus, str]] = ..., status_message: _Optional[str] = ..., options: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., submitted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., received_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., acquired_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., fetched_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., processed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ended_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., pod_ttl: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., creation_to_end_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., processing_to_end_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., received_to_end_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., payload_id: _Optional[str] = ..., created_by: _Optional[str] = ..., output: _Optional[_Union[TaskDetailed.Output, _Mapping]] = ..., pod_hostname: _Optional[str] = ...) -> None: ...

class TaskSummary(_message.Message):
    __slots__ = ("id", "session_id", "owner_pod_id", "initial_task_id", "count_parent_task_ids", "count_data_dependencies", "count_expected_output_ids", "count_retry_of_ids", "status", "status_message", "options", "created_at", "submitted_at", "received_at", "acquired_at", "fetched_at", "started_at", "processed_at", "ended_at", "pod_ttl", "creation_to_end_duration", "processing_to_end_duration", "received_to_end_duration", "payload_id", "created_by", "error", "pod_hostname")
    ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_POD_ID_FIELD_NUMBER: _ClassVar[int]
    INITIAL_TASK_ID_FIELD_NUMBER: _ClassVar[int]
    COUNT_PARENT_TASK_IDS_FIELD_NUMBER: _ClassVar[int]
    COUNT_DATA_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    COUNT_EXPECTED_OUTPUT_IDS_FIELD_NUMBER: _ClassVar[int]
    COUNT_RETRY_OF_IDS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    SUBMITTED_AT_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_AT_FIELD_NUMBER: _ClassVar[int]
    ACQUIRED_AT_FIELD_NUMBER: _ClassVar[int]
    FETCHED_AT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_AT_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    POD_TTL_FIELD_NUMBER: _ClassVar[int]
    CREATION_TO_END_DURATION_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_TO_END_DURATION_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_TO_END_DURATION_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    POD_HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    session_id: str
    owner_pod_id: str
    initial_task_id: str
    count_parent_task_ids: int
    count_data_dependencies: int
    count_expected_output_ids: int
    count_retry_of_ids: int
    status: _task_status_pb2.TaskStatus
    status_message: str
    options: _objects_pb2.TaskOptions
    created_at: _timestamp_pb2.Timestamp
    submitted_at: _timestamp_pb2.Timestamp
    received_at: _timestamp_pb2.Timestamp
    acquired_at: _timestamp_pb2.Timestamp
    fetched_at: _timestamp_pb2.Timestamp
    started_at: _timestamp_pb2.Timestamp
    processed_at: _timestamp_pb2.Timestamp
    ended_at: _timestamp_pb2.Timestamp
    pod_ttl: _timestamp_pb2.Timestamp
    creation_to_end_duration: _duration_pb2.Duration
    processing_to_end_duration: _duration_pb2.Duration
    received_to_end_duration: _duration_pb2.Duration
    payload_id: str
    created_by: str
    error: str
    pod_hostname: str
    def __init__(self, id: _Optional[str] = ..., session_id: _Optional[str] = ..., owner_pod_id: _Optional[str] = ..., initial_task_id: _Optional[str] = ..., count_parent_task_ids: _Optional[int] = ..., count_data_dependencies: _Optional[int] = ..., count_expected_output_ids: _Optional[int] = ..., count_retry_of_ids: _Optional[int] = ..., status: _Optional[_Union[_task_status_pb2.TaskStatus, str]] = ..., status_message: _Optional[str] = ..., options: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., submitted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., received_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., acquired_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., fetched_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., processed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ended_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., pod_ttl: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., creation_to_end_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., processing_to_end_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., received_to_end_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., payload_id: _Optional[str] = ..., created_by: _Optional[str] = ..., error: _Optional[str] = ..., pod_hostname: _Optional[str] = ...) -> None: ...

class ListTasksRequest(_message.Message):
    __slots__ = ("page", "page_size", "filters", "sort", "with_errors")
    class Sort(_message.Message):
        __slots__ = ("field", "direction")
        FIELD_FIELD_NUMBER: _ClassVar[int]
        DIRECTION_FIELD_NUMBER: _ClassVar[int]
        field: _tasks_fields_pb2.TaskField
        direction: _sort_direction_pb2.SortDirection
        def __init__(self, field: _Optional[_Union[_tasks_fields_pb2.TaskField, _Mapping]] = ..., direction: _Optional[_Union[_sort_direction_pb2.SortDirection, str]] = ...) -> None: ...
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    WITH_ERRORS_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    filters: _tasks_filters_pb2.Filters
    sort: ListTasksRequest.Sort
    with_errors: bool
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., filters: _Optional[_Union[_tasks_filters_pb2.Filters, _Mapping]] = ..., sort: _Optional[_Union[ListTasksRequest.Sort, _Mapping]] = ..., with_errors: bool = ...) -> None: ...

class ListTasksResponse(_message.Message):
    __slots__ = ("tasks", "page", "page_size", "total")
    TASKS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    tasks: _containers.RepeatedCompositeFieldContainer[TaskSummary]
    page: int
    page_size: int
    total: int
    def __init__(self, tasks: _Optional[_Iterable[_Union[TaskSummary, _Mapping]]] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class ListTasksDetailedResponse(_message.Message):
    __slots__ = ("tasks", "page", "page_size", "total")
    TASKS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    tasks: _containers.RepeatedCompositeFieldContainer[TaskDetailed]
    page: int
    page_size: int
    total: int
    def __init__(self, tasks: _Optional[_Iterable[_Union[TaskDetailed, _Mapping]]] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class GetTaskRequest(_message.Message):
    __slots__ = ("task_id",)
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class GetTaskResponse(_message.Message):
    __slots__ = ("task",)
    TASK_FIELD_NUMBER: _ClassVar[int]
    task: TaskDetailed
    def __init__(self, task: _Optional[_Union[TaskDetailed, _Mapping]] = ...) -> None: ...

class CancelTasksRequest(_message.Message):
    __slots__ = ("task_ids",)
    TASK_IDS_FIELD_NUMBER: _ClassVar[int]
    task_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, task_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class CancelTasksResponse(_message.Message):
    __slots__ = ("tasks",)
    TASKS_FIELD_NUMBER: _ClassVar[int]
    tasks: _containers.RepeatedCompositeFieldContainer[TaskSummary]
    def __init__(self, tasks: _Optional[_Iterable[_Union[TaskSummary, _Mapping]]] = ...) -> None: ...

class GetResultIdsRequest(_message.Message):
    __slots__ = ("task_id",)
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, task_id: _Optional[_Iterable[str]] = ...) -> None: ...

class GetResultIdsResponse(_message.Message):
    __slots__ = ("task_results",)
    class MapTaskResult(_message.Message):
        __slots__ = ("task_id", "result_ids")
        TASK_ID_FIELD_NUMBER: _ClassVar[int]
        RESULT_IDS_FIELD_NUMBER: _ClassVar[int]
        task_id: str
        result_ids: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, task_id: _Optional[str] = ..., result_ids: _Optional[_Iterable[str]] = ...) -> None: ...
    TASK_RESULTS_FIELD_NUMBER: _ClassVar[int]
    task_results: _containers.RepeatedCompositeFieldContainer[GetResultIdsResponse.MapTaskResult]
    def __init__(self, task_results: _Optional[_Iterable[_Union[GetResultIdsResponse.MapTaskResult, _Mapping]]] = ...) -> None: ...

class CountTasksByStatusRequest(_message.Message):
    __slots__ = ("filters",)
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    filters: _tasks_filters_pb2.Filters
    def __init__(self, filters: _Optional[_Union[_tasks_filters_pb2.Filters, _Mapping]] = ...) -> None: ...

class CountTasksByStatusResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _containers.RepeatedCompositeFieldContainer[_objects_pb2.StatusCount]
    def __init__(self, status: _Optional[_Iterable[_Union[_objects_pb2.StatusCount, _Mapping]]] = ...) -> None: ...

class SubmitTasksRequest(_message.Message):
    __slots__ = ("session_id", "task_options", "task_creations")
    class TaskCreation(_message.Message):
        __slots__ = ("expected_output_keys", "data_dependencies", "payload_id", "task_options")
        EXPECTED_OUTPUT_KEYS_FIELD_NUMBER: _ClassVar[int]
        DATA_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
        PAYLOAD_ID_FIELD_NUMBER: _ClassVar[int]
        TASK_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        expected_output_keys: _containers.RepeatedScalarFieldContainer[str]
        data_dependencies: _containers.RepeatedScalarFieldContainer[str]
        payload_id: str
        task_options: _objects_pb2.TaskOptions
        def __init__(self, expected_output_keys: _Optional[_Iterable[str]] = ..., data_dependencies: _Optional[_Iterable[str]] = ..., payload_id: _Optional[str] = ..., task_options: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ...) -> None: ...
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    TASK_CREATIONS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    task_options: _objects_pb2.TaskOptions
    task_creations: _containers.RepeatedCompositeFieldContainer[SubmitTasksRequest.TaskCreation]
    def __init__(self, session_id: _Optional[str] = ..., task_options: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ..., task_creations: _Optional[_Iterable[_Union[SubmitTasksRequest.TaskCreation, _Mapping]]] = ...) -> None: ...

class SubmitTasksResponse(_message.Message):
    __slots__ = ("task_infos",)
    class TaskInfo(_message.Message):
        __slots__ = ("task_id", "expected_output_ids", "data_dependencies", "payload_id")
        TASK_ID_FIELD_NUMBER: _ClassVar[int]
        EXPECTED_OUTPUT_IDS_FIELD_NUMBER: _ClassVar[int]
        DATA_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
        PAYLOAD_ID_FIELD_NUMBER: _ClassVar[int]
        task_id: str
        expected_output_ids: _containers.RepeatedScalarFieldContainer[str]
        data_dependencies: _containers.RepeatedScalarFieldContainer[str]
        payload_id: str
        def __init__(self, task_id: _Optional[str] = ..., expected_output_ids: _Optional[_Iterable[str]] = ..., data_dependencies: _Optional[_Iterable[str]] = ..., payload_id: _Optional[str] = ...) -> None: ...
    TASK_INFOS_FIELD_NUMBER: _ClassVar[int]
    task_infos: _containers.RepeatedCompositeFieldContainer[SubmitTasksResponse.TaskInfo]
    def __init__(self, task_infos: _Optional[_Iterable[_Union[SubmitTasksResponse.TaskInfo, _Mapping]]] = ...) -> None: ...
