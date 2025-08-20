from . import result_status_pb2 as _result_status_pb2
from . import results_filters_pb2 as _results_filters_pb2
from . import task_status_pb2 as _task_status_pb2
from . import tasks_filters_pb2 as _tasks_filters_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EventsEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENTS_ENUM_UNSPECIFIED: _ClassVar[EventsEnum]
    EVENTS_ENUM_NEW_TASK: _ClassVar[EventsEnum]
    EVENTS_ENUM_TASK_STATUS_UPDATE: _ClassVar[EventsEnum]
    EVENTS_ENUM_NEW_RESULT: _ClassVar[EventsEnum]
    EVENTS_ENUM_RESULT_STATUS_UPDATE: _ClassVar[EventsEnum]
    EVENTS_ENUM_RESULT_OWNER_UPDATE: _ClassVar[EventsEnum]
EVENTS_ENUM_UNSPECIFIED: EventsEnum
EVENTS_ENUM_NEW_TASK: EventsEnum
EVENTS_ENUM_TASK_STATUS_UPDATE: EventsEnum
EVENTS_ENUM_NEW_RESULT: EventsEnum
EVENTS_ENUM_RESULT_STATUS_UPDATE: EventsEnum
EVENTS_ENUM_RESULT_OWNER_UPDATE: EventsEnum

class EventSubscriptionRequest(_message.Message):
    __slots__ = ("session_id", "tasks_filters", "results_filters", "returned_events")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    TASKS_FILTERS_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FILTERS_FIELD_NUMBER: _ClassVar[int]
    RETURNED_EVENTS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    tasks_filters: _tasks_filters_pb2.Filters
    results_filters: _results_filters_pb2.Filters
    returned_events: _containers.RepeatedScalarFieldContainer[EventsEnum]
    def __init__(self, session_id: _Optional[str] = ..., tasks_filters: _Optional[_Union[_tasks_filters_pb2.Filters, _Mapping]] = ..., results_filters: _Optional[_Union[_results_filters_pb2.Filters, _Mapping]] = ..., returned_events: _Optional[_Iterable[_Union[EventsEnum, str]]] = ...) -> None: ...

class EventSubscriptionResponse(_message.Message):
    __slots__ = ("session_id", "task_status_update", "result_status_update", "result_owner_update", "new_task", "new_result")
    class TaskStatusUpdate(_message.Message):
        __slots__ = ("task_id", "status")
        TASK_ID_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        task_id: str
        status: _task_status_pb2.TaskStatus
        def __init__(self, task_id: _Optional[str] = ..., status: _Optional[_Union[_task_status_pb2.TaskStatus, str]] = ...) -> None: ...
    class ResultStatusUpdate(_message.Message):
        __slots__ = ("result_id", "status")
        RESULT_ID_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        result_id: str
        status: _result_status_pb2.ResultStatus
        def __init__(self, result_id: _Optional[str] = ..., status: _Optional[_Union[_result_status_pb2.ResultStatus, str]] = ...) -> None: ...
    class ResultOwnerUpdate(_message.Message):
        __slots__ = ("result_id", "previous_owner_id", "current_owner_id")
        RESULT_ID_FIELD_NUMBER: _ClassVar[int]
        PREVIOUS_OWNER_ID_FIELD_NUMBER: _ClassVar[int]
        CURRENT_OWNER_ID_FIELD_NUMBER: _ClassVar[int]
        result_id: str
        previous_owner_id: str
        current_owner_id: str
        def __init__(self, result_id: _Optional[str] = ..., previous_owner_id: _Optional[str] = ..., current_owner_id: _Optional[str] = ...) -> None: ...
    class NewTask(_message.Message):
        __slots__ = ("task_id", "payload_id", "origin_task_id", "status", "expected_output_keys", "data_dependencies", "retry_of_ids", "parent_task_ids")
        TASK_ID_FIELD_NUMBER: _ClassVar[int]
        PAYLOAD_ID_FIELD_NUMBER: _ClassVar[int]
        ORIGIN_TASK_ID_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        EXPECTED_OUTPUT_KEYS_FIELD_NUMBER: _ClassVar[int]
        DATA_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
        RETRY_OF_IDS_FIELD_NUMBER: _ClassVar[int]
        PARENT_TASK_IDS_FIELD_NUMBER: _ClassVar[int]
        task_id: str
        payload_id: str
        origin_task_id: str
        status: _task_status_pb2.TaskStatus
        expected_output_keys: _containers.RepeatedScalarFieldContainer[str]
        data_dependencies: _containers.RepeatedScalarFieldContainer[str]
        retry_of_ids: _containers.RepeatedScalarFieldContainer[str]
        parent_task_ids: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, task_id: _Optional[str] = ..., payload_id: _Optional[str] = ..., origin_task_id: _Optional[str] = ..., status: _Optional[_Union[_task_status_pb2.TaskStatus, str]] = ..., expected_output_keys: _Optional[_Iterable[str]] = ..., data_dependencies: _Optional[_Iterable[str]] = ..., retry_of_ids: _Optional[_Iterable[str]] = ..., parent_task_ids: _Optional[_Iterable[str]] = ...) -> None: ...
    class NewResult(_message.Message):
        __slots__ = ("result_id", "owner_id", "status")
        RESULT_ID_FIELD_NUMBER: _ClassVar[int]
        OWNER_ID_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        result_id: str
        owner_id: str
        status: _result_status_pb2.ResultStatus
        def __init__(self, result_id: _Optional[str] = ..., owner_id: _Optional[str] = ..., status: _Optional[_Union[_result_status_pb2.ResultStatus, str]] = ...) -> None: ...
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_STATUS_UPDATE_FIELD_NUMBER: _ClassVar[int]
    RESULT_STATUS_UPDATE_FIELD_NUMBER: _ClassVar[int]
    RESULT_OWNER_UPDATE_FIELD_NUMBER: _ClassVar[int]
    NEW_TASK_FIELD_NUMBER: _ClassVar[int]
    NEW_RESULT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    task_status_update: EventSubscriptionResponse.TaskStatusUpdate
    result_status_update: EventSubscriptionResponse.ResultStatusUpdate
    result_owner_update: EventSubscriptionResponse.ResultOwnerUpdate
    new_task: EventSubscriptionResponse.NewTask
    new_result: EventSubscriptionResponse.NewResult
    def __init__(self, session_id: _Optional[str] = ..., task_status_update: _Optional[_Union[EventSubscriptionResponse.TaskStatusUpdate, _Mapping]] = ..., result_status_update: _Optional[_Union[EventSubscriptionResponse.ResultStatusUpdate, _Mapping]] = ..., result_owner_update: _Optional[_Union[EventSubscriptionResponse.ResultOwnerUpdate, _Mapping]] = ..., new_task: _Optional[_Union[EventSubscriptionResponse.NewTask, _Mapping]] = ..., new_result: _Optional[_Union[EventSubscriptionResponse.NewResult, _Mapping]] = ...) -> None: ...
