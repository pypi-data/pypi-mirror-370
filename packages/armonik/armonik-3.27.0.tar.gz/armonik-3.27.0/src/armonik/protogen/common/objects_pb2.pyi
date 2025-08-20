from google.protobuf import duration_pb2 as _duration_pb2
from . import task_status_pb2 as _task_status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TaskOptions(_message.Message):
    __slots__ = ("options", "max_duration", "max_retries", "priority", "partition_id", "application_name", "application_version", "application_namespace", "application_service", "engine_type")
    class OptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    MAX_DURATION_FIELD_NUMBER: _ClassVar[int]
    MAX_RETRIES_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    PARTITION_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_NAME_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_VERSION_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_SERVICE_FIELD_NUMBER: _ClassVar[int]
    ENGINE_TYPE_FIELD_NUMBER: _ClassVar[int]
    options: _containers.ScalarMap[str, str]
    max_duration: _duration_pb2.Duration
    max_retries: int
    priority: int
    partition_id: str
    application_name: str
    application_version: str
    application_namespace: str
    application_service: str
    engine_type: str
    def __init__(self, options: _Optional[_Mapping[str, str]] = ..., max_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., max_retries: _Optional[int] = ..., priority: _Optional[int] = ..., partition_id: _Optional[str] = ..., application_name: _Optional[str] = ..., application_version: _Optional[str] = ..., application_namespace: _Optional[str] = ..., application_service: _Optional[str] = ..., engine_type: _Optional[str] = ...) -> None: ...

class Session(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class Configuration(_message.Message):
    __slots__ = ("data_chunk_max_size",)
    DATA_CHUNK_MAX_SIZE_FIELD_NUMBER: _ClassVar[int]
    data_chunk_max_size: int
    def __init__(self, data_chunk_max_size: _Optional[int] = ...) -> None: ...

class Output(_message.Message):
    __slots__ = ("ok", "error")
    class Error(_message.Message):
        __slots__ = ("details",)
        DETAILS_FIELD_NUMBER: _ClassVar[int]
        details: str
        def __init__(self, details: _Optional[str] = ...) -> None: ...
    OK_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ok: Empty
    error: Output.Error
    def __init__(self, ok: _Optional[_Union[Empty, _Mapping]] = ..., error: _Optional[_Union[Output.Error, _Mapping]] = ...) -> None: ...

class TaskRequest(_message.Message):
    __slots__ = ("expected_output_keys", "data_dependencies", "payload", "payload_name")
    EXPECTED_OUTPUT_KEYS_FIELD_NUMBER: _ClassVar[int]
    DATA_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_NAME_FIELD_NUMBER: _ClassVar[int]
    expected_output_keys: _containers.RepeatedScalarFieldContainer[str]
    data_dependencies: _containers.RepeatedScalarFieldContainer[str]
    payload: bytes
    payload_name: str
    def __init__(self, expected_output_keys: _Optional[_Iterable[str]] = ..., data_dependencies: _Optional[_Iterable[str]] = ..., payload: _Optional[bytes] = ..., payload_name: _Optional[str] = ...) -> None: ...

class InitKeyedDataStream(_message.Message):
    __slots__ = ("key", "last_result")
    KEY_FIELD_NUMBER: _ClassVar[int]
    LAST_RESULT_FIELD_NUMBER: _ClassVar[int]
    key: str
    last_result: bool
    def __init__(self, key: _Optional[str] = ..., last_result: bool = ...) -> None: ...

class DataChunk(_message.Message):
    __slots__ = ("data", "data_complete")
    DATA_FIELD_NUMBER: _ClassVar[int]
    DATA_COMPLETE_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    data_complete: bool
    def __init__(self, data: _Optional[bytes] = ..., data_complete: bool = ...) -> None: ...

class TaskRequestHeader(_message.Message):
    __slots__ = ("expected_output_keys", "data_dependencies")
    EXPECTED_OUTPUT_KEYS_FIELD_NUMBER: _ClassVar[int]
    DATA_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    expected_output_keys: _containers.RepeatedScalarFieldContainer[str]
    data_dependencies: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, expected_output_keys: _Optional[_Iterable[str]] = ..., data_dependencies: _Optional[_Iterable[str]] = ...) -> None: ...

class InitTaskRequest(_message.Message):
    __slots__ = ("header", "last_task")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    LAST_TASK_FIELD_NUMBER: _ClassVar[int]
    header: TaskRequestHeader
    last_task: bool
    def __init__(self, header: _Optional[_Union[TaskRequestHeader, _Mapping]] = ..., last_task: bool = ...) -> None: ...

class TaskId(_message.Message):
    __slots__ = ("session", "task")
    SESSION_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    session: str
    task: str
    def __init__(self, session: _Optional[str] = ..., task: _Optional[str] = ...) -> None: ...

class TaskIdList(_message.Message):
    __slots__ = ("task_ids",)
    TASK_IDS_FIELD_NUMBER: _ClassVar[int]
    task_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, task_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class StatusCount(_message.Message):
    __slots__ = ("status", "count")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    status: _task_status_pb2.TaskStatus
    count: int
    def __init__(self, status: _Optional[_Union[_task_status_pb2.TaskStatus, str]] = ..., count: _Optional[int] = ...) -> None: ...

class Count(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[StatusCount]
    def __init__(self, values: _Optional[_Iterable[_Union[StatusCount, _Mapping]]] = ...) -> None: ...

class ResultRequest(_message.Message):
    __slots__ = ("session", "result_id")
    SESSION_FIELD_NUMBER: _ClassVar[int]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    session: str
    result_id: str
    def __init__(self, session: _Optional[str] = ..., result_id: _Optional[str] = ...) -> None: ...

class TaskOutputRequest(_message.Message):
    __slots__ = ("session", "task_id")
    SESSION_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    session: str
    task_id: str
    def __init__(self, session: _Optional[str] = ..., task_id: _Optional[str] = ...) -> None: ...

class Error(_message.Message):
    __slots__ = ("task_status", "detail")
    TASK_STATUS_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    task_status: _task_status_pb2.TaskStatus
    detail: str
    def __init__(self, task_status: _Optional[_Union[_task_status_pb2.TaskStatus, str]] = ..., detail: _Optional[str] = ...) -> None: ...

class TaskError(_message.Message):
    __slots__ = ("task_id", "errors")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    errors: _containers.RepeatedCompositeFieldContainer[Error]
    def __init__(self, task_id: _Optional[str] = ..., errors: _Optional[_Iterable[_Union[Error, _Mapping]]] = ...) -> None: ...

class TaskList(_message.Message):
    __slots__ = ("task_ids",)
    TASK_IDS_FIELD_NUMBER: _ClassVar[int]
    task_ids: _containers.RepeatedCompositeFieldContainer[TaskId]
    def __init__(self, task_ids: _Optional[_Iterable[_Union[TaskId, _Mapping]]] = ...) -> None: ...

class TaskIdWithStatus(_message.Message):
    __slots__ = ("task_id", "status")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    task_id: TaskId
    status: _task_status_pb2.TaskStatus
    def __init__(self, task_id: _Optional[_Union[TaskId, _Mapping]] = ..., status: _Optional[_Union[_task_status_pb2.TaskStatus, str]] = ...) -> None: ...
