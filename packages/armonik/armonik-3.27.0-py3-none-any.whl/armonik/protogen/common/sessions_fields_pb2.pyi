from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SessionRawEnumField(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SESSION_RAW_ENUM_FIELD_UNSPECIFIED: _ClassVar[SessionRawEnumField]
    SESSION_RAW_ENUM_FIELD_SESSION_ID: _ClassVar[SessionRawEnumField]
    SESSION_RAW_ENUM_FIELD_STATUS: _ClassVar[SessionRawEnumField]
    SESSION_RAW_ENUM_FIELD_PARTITION_IDS: _ClassVar[SessionRawEnumField]
    SESSION_RAW_ENUM_FIELD_OPTIONS: _ClassVar[SessionRawEnumField]
    SESSION_RAW_ENUM_FIELD_CREATED_AT: _ClassVar[SessionRawEnumField]
    SESSION_RAW_ENUM_FIELD_CANCELLED_AT: _ClassVar[SessionRawEnumField]
    SESSION_RAW_ENUM_FIELD_CLOSED_AT: _ClassVar[SessionRawEnumField]
    SESSION_RAW_ENUM_FIELD_PURGED_AT: _ClassVar[SessionRawEnumField]
    SESSION_RAW_ENUM_FIELD_DELETED_AT: _ClassVar[SessionRawEnumField]
    SESSION_RAW_ENUM_FIELD_DURATION: _ClassVar[SessionRawEnumField]
    SESSION_RAW_ENUM_FIELD_WORKER_SUBMISSION: _ClassVar[SessionRawEnumField]
    SESSION_RAW_ENUM_FIELD_CLIENT_SUBMISSION: _ClassVar[SessionRawEnumField]

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
SESSION_RAW_ENUM_FIELD_UNSPECIFIED: SessionRawEnumField
SESSION_RAW_ENUM_FIELD_SESSION_ID: SessionRawEnumField
SESSION_RAW_ENUM_FIELD_STATUS: SessionRawEnumField
SESSION_RAW_ENUM_FIELD_PARTITION_IDS: SessionRawEnumField
SESSION_RAW_ENUM_FIELD_OPTIONS: SessionRawEnumField
SESSION_RAW_ENUM_FIELD_CREATED_AT: SessionRawEnumField
SESSION_RAW_ENUM_FIELD_CANCELLED_AT: SessionRawEnumField
SESSION_RAW_ENUM_FIELD_CLOSED_AT: SessionRawEnumField
SESSION_RAW_ENUM_FIELD_PURGED_AT: SessionRawEnumField
SESSION_RAW_ENUM_FIELD_DELETED_AT: SessionRawEnumField
SESSION_RAW_ENUM_FIELD_DURATION: SessionRawEnumField
SESSION_RAW_ENUM_FIELD_WORKER_SUBMISSION: SessionRawEnumField
SESSION_RAW_ENUM_FIELD_CLIENT_SUBMISSION: SessionRawEnumField
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

class SessionRawField(_message.Message):
    __slots__ = ("field",)
    FIELD_FIELD_NUMBER: _ClassVar[int]
    field: SessionRawEnumField
    def __init__(self, field: _Optional[_Union[SessionRawEnumField, str]] = ...) -> None: ...

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

class SessionField(_message.Message):
    __slots__ = ("session_raw_field", "task_option_field", "task_option_generic_field")
    SESSION_RAW_FIELD_FIELD_NUMBER: _ClassVar[int]
    TASK_OPTION_FIELD_FIELD_NUMBER: _ClassVar[int]
    TASK_OPTION_GENERIC_FIELD_FIELD_NUMBER: _ClassVar[int]
    session_raw_field: SessionRawField
    task_option_field: TaskOptionField
    task_option_generic_field: TaskOptionGenericField
    def __init__(self, session_raw_field: _Optional[_Union[SessionRawField, _Mapping]] = ..., task_option_field: _Optional[_Union[TaskOptionField, _Mapping]] = ..., task_option_generic_field: _Optional[_Union[TaskOptionGenericField, _Mapping]] = ...) -> None: ...
