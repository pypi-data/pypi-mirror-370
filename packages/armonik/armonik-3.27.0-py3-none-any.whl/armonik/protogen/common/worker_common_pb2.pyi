from . import objects_pb2 as _objects_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProcessRequest(_message.Message):
    __slots__ = ("communication_token", "session_id", "task_id", "task_options", "expected_output_keys", "payload_id", "data_dependencies", "data_folder", "configuration")
    COMMUNICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_OUTPUT_KEYS_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    DATA_FOLDER_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    communication_token: str
    session_id: str
    task_id: str
    task_options: _objects_pb2.TaskOptions
    expected_output_keys: _containers.RepeatedScalarFieldContainer[str]
    payload_id: str
    data_dependencies: _containers.RepeatedScalarFieldContainer[str]
    data_folder: str
    configuration: _objects_pb2.Configuration
    def __init__(self, communication_token: _Optional[str] = ..., session_id: _Optional[str] = ..., task_id: _Optional[str] = ..., task_options: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ..., expected_output_keys: _Optional[_Iterable[str]] = ..., payload_id: _Optional[str] = ..., data_dependencies: _Optional[_Iterable[str]] = ..., data_folder: _Optional[str] = ..., configuration: _Optional[_Union[_objects_pb2.Configuration, _Mapping]] = ...) -> None: ...

class ProcessReply(_message.Message):
    __slots__ = ("output",)
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    output: _objects_pb2.Output
    def __init__(self, output: _Optional[_Union[_objects_pb2.Output, _Mapping]] = ...) -> None: ...

class HealthCheckReply(_message.Message):
    __slots__ = ("status",)
    class ServingStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[HealthCheckReply.ServingStatus]
        SERVING: _ClassVar[HealthCheckReply.ServingStatus]
        NOT_SERVING: _ClassVar[HealthCheckReply.ServingStatus]
    UNKNOWN: HealthCheckReply.ServingStatus
    SERVING: HealthCheckReply.ServingStatus
    NOT_SERVING: HealthCheckReply.ServingStatus
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: HealthCheckReply.ServingStatus
    def __init__(self, status: _Optional[_Union[HealthCheckReply.ServingStatus, str]] = ...) -> None: ...
