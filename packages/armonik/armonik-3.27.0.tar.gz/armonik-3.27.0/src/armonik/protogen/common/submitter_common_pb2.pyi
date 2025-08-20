from . import objects_pb2 as _objects_pb2
from . import result_status_pb2 as _result_status_pb2
from . import session_status_pb2 as _session_status_pb2
from . import task_status_pb2 as _task_status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SessionList(_message.Message):
    __slots__ = ("sessions",)
    SESSIONS_FIELD_NUMBER: _ClassVar[int]
    sessions: _containers.RepeatedCompositeFieldContainer[_objects_pb2.Session]
    def __init__(self, sessions: _Optional[_Iterable[_Union[_objects_pb2.Session, _Mapping]]] = ...) -> None: ...

class SessionIdList(_message.Message):
    __slots__ = ("session_ids",)
    SESSION_IDS_FIELD_NUMBER: _ClassVar[int]
    session_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, session_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateSessionRequest(_message.Message):
    __slots__ = ("default_task_option", "partition_ids")
    DEFAULT_TASK_OPTION_FIELD_NUMBER: _ClassVar[int]
    PARTITION_IDS_FIELD_NUMBER: _ClassVar[int]
    default_task_option: _objects_pb2.TaskOptions
    partition_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, default_task_option: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ..., partition_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateSessionReply(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class CreateSmallTaskRequest(_message.Message):
    __slots__ = ("session_id", "task_options", "task_requests")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    TASK_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    task_options: _objects_pb2.TaskOptions
    task_requests: _containers.RepeatedCompositeFieldContainer[_objects_pb2.TaskRequest]
    def __init__(self, session_id: _Optional[str] = ..., task_options: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ..., task_requests: _Optional[_Iterable[_Union[_objects_pb2.TaskRequest, _Mapping]]] = ...) -> None: ...

class CreateLargeTaskRequest(_message.Message):
    __slots__ = ("init_request", "init_task", "task_payload")
    class InitRequest(_message.Message):
        __slots__ = ("session_id", "task_options")
        SESSION_ID_FIELD_NUMBER: _ClassVar[int]
        TASK_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        session_id: str
        task_options: _objects_pb2.TaskOptions
        def __init__(self, session_id: _Optional[str] = ..., task_options: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ...) -> None: ...
    INIT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    INIT_TASK_FIELD_NUMBER: _ClassVar[int]
    TASK_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    init_request: CreateLargeTaskRequest.InitRequest
    init_task: _objects_pb2.InitTaskRequest
    task_payload: _objects_pb2.DataChunk
    def __init__(self, init_request: _Optional[_Union[CreateLargeTaskRequest.InitRequest, _Mapping]] = ..., init_task: _Optional[_Union[_objects_pb2.InitTaskRequest, _Mapping]] = ..., task_payload: _Optional[_Union[_objects_pb2.DataChunk, _Mapping]] = ...) -> None: ...

class CreateTaskReply(_message.Message):
    __slots__ = ("creation_status_list", "error")
    class TaskInfo(_message.Message):
        __slots__ = ("task_id", "expected_output_keys", "data_dependencies", "payload_id")
        TASK_ID_FIELD_NUMBER: _ClassVar[int]
        EXPECTED_OUTPUT_KEYS_FIELD_NUMBER: _ClassVar[int]
        DATA_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
        PAYLOAD_ID_FIELD_NUMBER: _ClassVar[int]
        task_id: str
        expected_output_keys: _containers.RepeatedScalarFieldContainer[str]
        data_dependencies: _containers.RepeatedScalarFieldContainer[str]
        payload_id: str
        def __init__(self, task_id: _Optional[str] = ..., expected_output_keys: _Optional[_Iterable[str]] = ..., data_dependencies: _Optional[_Iterable[str]] = ..., payload_id: _Optional[str] = ...) -> None: ...
    class CreationStatus(_message.Message):
        __slots__ = ("task_info", "error")
        TASK_INFO_FIELD_NUMBER: _ClassVar[int]
        ERROR_FIELD_NUMBER: _ClassVar[int]
        task_info: CreateTaskReply.TaskInfo
        error: str
        def __init__(self, task_info: _Optional[_Union[CreateTaskReply.TaskInfo, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...
    class CreationStatusList(_message.Message):
        __slots__ = ("creation_statuses",)
        CREATION_STATUSES_FIELD_NUMBER: _ClassVar[int]
        creation_statuses: _containers.RepeatedCompositeFieldContainer[CreateTaskReply.CreationStatus]
        def __init__(self, creation_statuses: _Optional[_Iterable[_Union[CreateTaskReply.CreationStatus, _Mapping]]] = ...) -> None: ...
    CREATION_STATUS_LIST_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    creation_status_list: CreateTaskReply.CreationStatusList
    error: str
    def __init__(self, creation_status_list: _Optional[_Union[CreateTaskReply.CreationStatusList, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class TaskFilter(_message.Message):
    __slots__ = ("session", "task", "included", "excluded")
    class IdsRequest(_message.Message):
        __slots__ = ("ids",)
        IDS_FIELD_NUMBER: _ClassVar[int]
        ids: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, ids: _Optional[_Iterable[str]] = ...) -> None: ...
    class StatusesRequest(_message.Message):
        __slots__ = ("statuses",)
        STATUSES_FIELD_NUMBER: _ClassVar[int]
        statuses: _containers.RepeatedScalarFieldContainer[_task_status_pb2.TaskStatus]
        def __init__(self, statuses: _Optional[_Iterable[_Union[_task_status_pb2.TaskStatus, str]]] = ...) -> None: ...
    SESSION_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    INCLUDED_FIELD_NUMBER: _ClassVar[int]
    EXCLUDED_FIELD_NUMBER: _ClassVar[int]
    session: TaskFilter.IdsRequest
    task: TaskFilter.IdsRequest
    included: TaskFilter.StatusesRequest
    excluded: TaskFilter.StatusesRequest
    def __init__(self, session: _Optional[_Union[TaskFilter.IdsRequest, _Mapping]] = ..., task: _Optional[_Union[TaskFilter.IdsRequest, _Mapping]] = ..., included: _Optional[_Union[TaskFilter.StatusesRequest, _Mapping]] = ..., excluded: _Optional[_Union[TaskFilter.StatusesRequest, _Mapping]] = ...) -> None: ...

class SessionFilter(_message.Message):
    __slots__ = ("sessions", "included", "excluded")
    class StatusesRequest(_message.Message):
        __slots__ = ("statuses",)
        STATUSES_FIELD_NUMBER: _ClassVar[int]
        statuses: _containers.RepeatedScalarFieldContainer[_session_status_pb2.SessionStatus]
        def __init__(self, statuses: _Optional[_Iterable[_Union[_session_status_pb2.SessionStatus, str]]] = ...) -> None: ...
    SESSIONS_FIELD_NUMBER: _ClassVar[int]
    INCLUDED_FIELD_NUMBER: _ClassVar[int]
    EXCLUDED_FIELD_NUMBER: _ClassVar[int]
    sessions: _containers.RepeatedScalarFieldContainer[str]
    included: SessionFilter.StatusesRequest
    excluded: SessionFilter.StatusesRequest
    def __init__(self, sessions: _Optional[_Iterable[str]] = ..., included: _Optional[_Union[SessionFilter.StatusesRequest, _Mapping]] = ..., excluded: _Optional[_Union[SessionFilter.StatusesRequest, _Mapping]] = ...) -> None: ...

class GetTaskStatusRequest(_message.Message):
    __slots__ = ("task_ids",)
    TASK_IDS_FIELD_NUMBER: _ClassVar[int]
    task_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, task_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class GetTaskStatusReply(_message.Message):
    __slots__ = ("id_statuses",)
    class IdStatus(_message.Message):
        __slots__ = ("task_id", "status")
        TASK_ID_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        task_id: str
        status: _task_status_pb2.TaskStatus
        def __init__(self, task_id: _Optional[str] = ..., status: _Optional[_Union[_task_status_pb2.TaskStatus, str]] = ...) -> None: ...
    ID_STATUSES_FIELD_NUMBER: _ClassVar[int]
    id_statuses: _containers.RepeatedCompositeFieldContainer[GetTaskStatusReply.IdStatus]
    def __init__(self, id_statuses: _Optional[_Iterable[_Union[GetTaskStatusReply.IdStatus, _Mapping]]] = ...) -> None: ...

class GetResultStatusRequest(_message.Message):
    __slots__ = ("result_ids", "session_id")
    RESULT_IDS_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    result_ids: _containers.RepeatedScalarFieldContainer[str]
    session_id: str
    def __init__(self, result_ids: _Optional[_Iterable[str]] = ..., session_id: _Optional[str] = ...) -> None: ...

class GetResultStatusReply(_message.Message):
    __slots__ = ("id_statuses",)
    class IdStatus(_message.Message):
        __slots__ = ("result_id", "status")
        RESULT_ID_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        result_id: str
        status: _result_status_pb2.ResultStatus
        def __init__(self, result_id: _Optional[str] = ..., status: _Optional[_Union[_result_status_pb2.ResultStatus, str]] = ...) -> None: ...
    ID_STATUSES_FIELD_NUMBER: _ClassVar[int]
    id_statuses: _containers.RepeatedCompositeFieldContainer[GetResultStatusReply.IdStatus]
    def __init__(self, id_statuses: _Optional[_Iterable[_Union[GetResultStatusReply.IdStatus, _Mapping]]] = ...) -> None: ...

class ResultReply(_message.Message):
    __slots__ = ("result", "error", "not_completed_task")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    NOT_COMPLETED_TASK_FIELD_NUMBER: _ClassVar[int]
    result: _objects_pb2.DataChunk
    error: _objects_pb2.TaskError
    not_completed_task: str
    def __init__(self, result: _Optional[_Union[_objects_pb2.DataChunk, _Mapping]] = ..., error: _Optional[_Union[_objects_pb2.TaskError, _Mapping]] = ..., not_completed_task: _Optional[str] = ...) -> None: ...

class AvailabilityReply(_message.Message):
    __slots__ = ("ok", "error", "not_completed_task")
    OK_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    NOT_COMPLETED_TASK_FIELD_NUMBER: _ClassVar[int]
    ok: _objects_pb2.Empty
    error: _objects_pb2.TaskError
    not_completed_task: str
    def __init__(self, ok: _Optional[_Union[_objects_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[_objects_pb2.TaskError, _Mapping]] = ..., not_completed_task: _Optional[str] = ...) -> None: ...

class WaitRequest(_message.Message):
    __slots__ = ("filter", "stop_on_first_task_error", "stop_on_first_task_cancellation")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    STOP_ON_FIRST_TASK_ERROR_FIELD_NUMBER: _ClassVar[int]
    STOP_ON_FIRST_TASK_CANCELLATION_FIELD_NUMBER: _ClassVar[int]
    filter: TaskFilter
    stop_on_first_task_error: bool
    stop_on_first_task_cancellation: bool
    def __init__(self, filter: _Optional[_Union[TaskFilter, _Mapping]] = ..., stop_on_first_task_error: bool = ..., stop_on_first_task_cancellation: bool = ...) -> None: ...

class WatchResultRequest(_message.Message):
    __slots__ = ("fetch_statuses", "watch_statuses", "result_ids")
    FETCH_STATUSES_FIELD_NUMBER: _ClassVar[int]
    WATCH_STATUSES_FIELD_NUMBER: _ClassVar[int]
    RESULT_IDS_FIELD_NUMBER: _ClassVar[int]
    fetch_statuses: _containers.RepeatedScalarFieldContainer[_result_status_pb2.ResultStatus]
    watch_statuses: _containers.RepeatedScalarFieldContainer[_result_status_pb2.ResultStatus]
    result_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, fetch_statuses: _Optional[_Iterable[_Union[_result_status_pb2.ResultStatus, str]]] = ..., watch_statuses: _Optional[_Iterable[_Union[_result_status_pb2.ResultStatus, str]]] = ..., result_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class WatchResultStream(_message.Message):
    __slots__ = ("status", "result_ids")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_IDS_FIELD_NUMBER: _ClassVar[int]
    status: _result_status_pb2.ResultStatus
    result_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, status: _Optional[_Union[_result_status_pb2.ResultStatus, str]] = ..., result_ids: _Optional[_Iterable[str]] = ...) -> None: ...
