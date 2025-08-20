from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaskSummaryEnumField(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TASK_SUMMARY_ENUM_FIELD_UNSPECIFIED: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_TASK_ID: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_SESSION_ID: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_OWNER_POD_ID: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_INITIAL_TASK_ID: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_STATUS: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_CREATED_AT: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_SUBMITTED_AT: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_STARTED_AT: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_ENDED_AT: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_CREATION_TO_END_DURATION: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_PROCESSING_TO_END_DURATION: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_RECEIVED_TO_END_DURATION: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_POD_TTL: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_POD_HOSTNAME: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_RECEIVED_AT: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_ACQUIRED_AT: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_PROCESSED_AT: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_ERROR: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_FETCHED_AT: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_PAYLOAD_ID: _ClassVar[TaskSummaryEnumField]
    TASK_SUMMARY_ENUM_FIELD_CREATED_BY: _ClassVar[TaskSummaryEnumField]

class TaskOptionEnumField(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TASK_OPTION_ENUM_FIELD_UNSPECIFIED: _ClassVar[TaskOptionEnumField]
    TASK_OPTION_ENUM_FIELD_MAX_DURATION: _ClassVar[TaskOptionEnumField]
    TASK_OPTION_ENUM_FIELD_MAX_RETRIES: _ClassVar[TaskOptionEnumField]
    TASK_OPTION_ENUM_FIELD_PRIORITY: _ClassVar[TaskOptionEnumField]
    TASK_OPTION_ENUM_FIELD_PARTITION_ID: _ClassVar[TaskOptionEnumField]
    TASK_OPTION_ENUM_FIELD_APPLICATION_NAME: _ClassVar[TaskOptionEnumField]
    TASK_OPTION_ENUM_FIELD_APPLICATION_VERSION: _ClassVar[TaskOptionEnumField]
    TASK_OPTION_ENUM_FIELD_APPLICATION_NAMESPACE: _ClassVar[TaskOptionEnumField]
    TASK_OPTION_ENUM_FIELD_APPLICATION_SERVICE: _ClassVar[TaskOptionEnumField]
    TASK_OPTION_ENUM_FIELD_ENGINE_TYPE: _ClassVar[TaskOptionEnumField]
TASK_SUMMARY_ENUM_FIELD_UNSPECIFIED: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_TASK_ID: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_SESSION_ID: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_OWNER_POD_ID: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_INITIAL_TASK_ID: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_STATUS: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_CREATED_AT: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_SUBMITTED_AT: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_STARTED_AT: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_ENDED_AT: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_CREATION_TO_END_DURATION: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_PROCESSING_TO_END_DURATION: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_RECEIVED_TO_END_DURATION: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_POD_TTL: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_POD_HOSTNAME: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_RECEIVED_AT: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_ACQUIRED_AT: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_PROCESSED_AT: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_ERROR: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_FETCHED_AT: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_PAYLOAD_ID: TaskSummaryEnumField
TASK_SUMMARY_ENUM_FIELD_CREATED_BY: TaskSummaryEnumField
TASK_OPTION_ENUM_FIELD_UNSPECIFIED: TaskOptionEnumField
TASK_OPTION_ENUM_FIELD_MAX_DURATION: TaskOptionEnumField
TASK_OPTION_ENUM_FIELD_MAX_RETRIES: TaskOptionEnumField
TASK_OPTION_ENUM_FIELD_PRIORITY: TaskOptionEnumField
TASK_OPTION_ENUM_FIELD_PARTITION_ID: TaskOptionEnumField
TASK_OPTION_ENUM_FIELD_APPLICATION_NAME: TaskOptionEnumField
TASK_OPTION_ENUM_FIELD_APPLICATION_VERSION: TaskOptionEnumField
TASK_OPTION_ENUM_FIELD_APPLICATION_NAMESPACE: TaskOptionEnumField
TASK_OPTION_ENUM_FIELD_APPLICATION_SERVICE: TaskOptionEnumField
TASK_OPTION_ENUM_FIELD_ENGINE_TYPE: TaskOptionEnumField

class TaskSummaryField(_message.Message):
    __slots__ = ("field",)
    FIELD_FIELD_NUMBER: _ClassVar[int]
    field: TaskSummaryEnumField
    def __init__(self, field: _Optional[_Union[TaskSummaryEnumField, str]] = ...) -> None: ...

class TaskOptionField(_message.Message):
    __slots__ = ("field",)
    FIELD_FIELD_NUMBER: _ClassVar[int]
    field: TaskOptionEnumField
    def __init__(self, field: _Optional[_Union[TaskOptionEnumField, str]] = ...) -> None: ...

class TaskOptionGenericField(_message.Message):
    __slots__ = ("field",)
    FIELD_FIELD_NUMBER: _ClassVar[int]
    field: str
    def __init__(self, field: _Optional[str] = ...) -> None: ...

class TaskField(_message.Message):
    __slots__ = ("task_summary_field", "task_option_field", "task_option_generic_field")
    TASK_SUMMARY_FIELD_FIELD_NUMBER: _ClassVar[int]
    TASK_OPTION_FIELD_FIELD_NUMBER: _ClassVar[int]
    TASK_OPTION_GENERIC_FIELD_FIELD_NUMBER: _ClassVar[int]
    task_summary_field: TaskSummaryField
    task_option_field: TaskOptionField
    task_option_generic_field: TaskOptionGenericField
    def __init__(self, task_summary_field: _Optional[_Union[TaskSummaryField, _Mapping]] = ..., task_option_field: _Optional[_Union[TaskOptionField, _Mapping]] = ..., task_option_generic_field: _Optional[_Union[TaskOptionGenericField, _Mapping]] = ...) -> None: ...
