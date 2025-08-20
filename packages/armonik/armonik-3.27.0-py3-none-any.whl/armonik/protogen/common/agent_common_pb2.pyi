from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import objects_pb2 as _objects_pb2
from . import result_status_pb2 as _result_status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateTaskRequest(_message.Message):
    __slots__ = ("init_request", "init_task", "task_payload", "communication_token")
    class InitRequest(_message.Message):
        __slots__ = ("task_options",)
        TASK_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        task_options: _objects_pb2.TaskOptions
        def __init__(self, task_options: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ...) -> None: ...
    INIT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    INIT_TASK_FIELD_NUMBER: _ClassVar[int]
    TASK_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    COMMUNICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    init_request: CreateTaskRequest.InitRequest
    init_task: _objects_pb2.InitTaskRequest
    task_payload: _objects_pb2.DataChunk
    communication_token: str
    def __init__(self, init_request: _Optional[_Union[CreateTaskRequest.InitRequest, _Mapping]] = ..., init_task: _Optional[_Union[_objects_pb2.InitTaskRequest, _Mapping]] = ..., task_payload: _Optional[_Union[_objects_pb2.DataChunk, _Mapping]] = ..., communication_token: _Optional[str] = ...) -> None: ...

class CreateTaskReply(_message.Message):
    __slots__ = ("creation_status_list", "error", "communication_token")
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
    COMMUNICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    creation_status_list: CreateTaskReply.CreationStatusList
    error: str
    communication_token: str
    def __init__(self, creation_status_list: _Optional[_Union[CreateTaskReply.CreationStatusList, _Mapping]] = ..., error: _Optional[str] = ..., communication_token: _Optional[str] = ...) -> None: ...

class DataRequest(_message.Message):
    __slots__ = ("communication_token", "result_id")
    COMMUNICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    communication_token: str
    result_id: str
    def __init__(self, communication_token: _Optional[str] = ..., result_id: _Optional[str] = ...) -> None: ...

class DataResponse(_message.Message):
    __slots__ = ("result_id",)
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    result_id: str
    def __init__(self, result_id: _Optional[str] = ...) -> None: ...

class CreateResultsMetaDataRequest(_message.Message):
    __slots__ = ("results", "session_id", "communication_token")
    class ResultCreate(_message.Message):
        __slots__ = ("name",)
        NAME_FIELD_NUMBER: _ClassVar[int]
        name: str
        def __init__(self, name: _Optional[str] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    COMMUNICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[CreateResultsMetaDataRequest.ResultCreate]
    session_id: str
    communication_token: str
    def __init__(self, results: _Optional[_Iterable[_Union[CreateResultsMetaDataRequest.ResultCreate, _Mapping]]] = ..., session_id: _Optional[str] = ..., communication_token: _Optional[str] = ...) -> None: ...

class ResultMetaData(_message.Message):
    __slots__ = ("session_id", "result_id", "name", "status", "created_at")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    result_id: str
    name: str
    status: _result_status_pb2.ResultStatus
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, session_id: _Optional[str] = ..., result_id: _Optional[str] = ..., name: _Optional[str] = ..., status: _Optional[_Union[_result_status_pb2.ResultStatus, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateResultsMetaDataResponse(_message.Message):
    __slots__ = ("results", "communication_token")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    COMMUNICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ResultMetaData]
    communication_token: str
    def __init__(self, results: _Optional[_Iterable[_Union[ResultMetaData, _Mapping]]] = ..., communication_token: _Optional[str] = ...) -> None: ...

class SubmitTasksRequest(_message.Message):
    __slots__ = ("session_id", "task_options", "task_creations", "communication_token")
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
    COMMUNICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    task_options: _objects_pb2.TaskOptions
    task_creations: _containers.RepeatedCompositeFieldContainer[SubmitTasksRequest.TaskCreation]
    communication_token: str
    def __init__(self, session_id: _Optional[str] = ..., task_options: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ..., task_creations: _Optional[_Iterable[_Union[SubmitTasksRequest.TaskCreation, _Mapping]]] = ..., communication_token: _Optional[str] = ...) -> None: ...

class SubmitTasksResponse(_message.Message):
    __slots__ = ("task_infos", "communication_token")
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
    COMMUNICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    task_infos: _containers.RepeatedCompositeFieldContainer[SubmitTasksResponse.TaskInfo]
    communication_token: str
    def __init__(self, task_infos: _Optional[_Iterable[_Union[SubmitTasksResponse.TaskInfo, _Mapping]]] = ..., communication_token: _Optional[str] = ...) -> None: ...

class CreateResultsRequest(_message.Message):
    __slots__ = ("results", "session_id", "communication_token")
    class ResultCreate(_message.Message):
        __slots__ = ("name", "data")
        NAME_FIELD_NUMBER: _ClassVar[int]
        DATA_FIELD_NUMBER: _ClassVar[int]
        name: str
        data: bytes
        def __init__(self, name: _Optional[str] = ..., data: _Optional[bytes] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    COMMUNICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[CreateResultsRequest.ResultCreate]
    session_id: str
    communication_token: str
    def __init__(self, results: _Optional[_Iterable[_Union[CreateResultsRequest.ResultCreate, _Mapping]]] = ..., session_id: _Optional[str] = ..., communication_token: _Optional[str] = ...) -> None: ...

class CreateResultsResponse(_message.Message):
    __slots__ = ("results", "communication_token")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    COMMUNICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ResultMetaData]
    communication_token: str
    def __init__(self, results: _Optional[_Iterable[_Union[ResultMetaData, _Mapping]]] = ..., communication_token: _Optional[str] = ...) -> None: ...

class NotifyResultDataRequest(_message.Message):
    __slots__ = ("ids", "communication_token")
    class ResultIdentifier(_message.Message):
        __slots__ = ("session_id", "result_id")
        SESSION_ID_FIELD_NUMBER: _ClassVar[int]
        RESULT_ID_FIELD_NUMBER: _ClassVar[int]
        session_id: str
        result_id: str
        def __init__(self, session_id: _Optional[str] = ..., result_id: _Optional[str] = ...) -> None: ...
    IDS_FIELD_NUMBER: _ClassVar[int]
    COMMUNICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ids: _containers.RepeatedCompositeFieldContainer[NotifyResultDataRequest.ResultIdentifier]
    communication_token: str
    def __init__(self, ids: _Optional[_Iterable[_Union[NotifyResultDataRequest.ResultIdentifier, _Mapping]]] = ..., communication_token: _Optional[str] = ...) -> None: ...

class NotifyResultDataResponse(_message.Message):
    __slots__ = ("result_ids",)
    RESULT_IDS_FIELD_NUMBER: _ClassVar[int]
    result_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, result_ids: _Optional[_Iterable[str]] = ...) -> None: ...
