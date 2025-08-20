from . import filters_common_pb2 as _filters_common_pb2
from . import task_status_pb2 as _task_status_pb2
from . import tasks_fields_pb2 as _tasks_fields_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilterStatus(_message.Message):
    __slots__ = ("value", "operator")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    value: _task_status_pb2.TaskStatus
    operator: _filters_common_pb2.FilterStatusOperator
    def __init__(self, value: _Optional[_Union[_task_status_pb2.TaskStatus, str]] = ..., operator: _Optional[_Union[_filters_common_pb2.FilterStatusOperator, str]] = ...) -> None: ...

class FilterField(_message.Message):
    __slots__ = ("field", "filter_string", "filter_number", "filter_boolean", "filter_status", "filter_date", "filter_array", "filter_duration")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FILTER_STRING_FIELD_NUMBER: _ClassVar[int]
    FILTER_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FILTER_BOOLEAN_FIELD_NUMBER: _ClassVar[int]
    FILTER_STATUS_FIELD_NUMBER: _ClassVar[int]
    FILTER_DATE_FIELD_NUMBER: _ClassVar[int]
    FILTER_ARRAY_FIELD_NUMBER: _ClassVar[int]
    FILTER_DURATION_FIELD_NUMBER: _ClassVar[int]
    field: _tasks_fields_pb2.TaskField
    filter_string: _filters_common_pb2.FilterString
    filter_number: _filters_common_pb2.FilterNumber
    filter_boolean: _filters_common_pb2.FilterBoolean
    filter_status: FilterStatus
    filter_date: _filters_common_pb2.FilterDate
    filter_array: _filters_common_pb2.FilterArray
    filter_duration: _filters_common_pb2.FilterDuration
    def __init__(self, field: _Optional[_Union[_tasks_fields_pb2.TaskField, _Mapping]] = ..., filter_string: _Optional[_Union[_filters_common_pb2.FilterString, _Mapping]] = ..., filter_number: _Optional[_Union[_filters_common_pb2.FilterNumber, _Mapping]] = ..., filter_boolean: _Optional[_Union[_filters_common_pb2.FilterBoolean, _Mapping]] = ..., filter_status: _Optional[_Union[FilterStatus, _Mapping]] = ..., filter_date: _Optional[_Union[_filters_common_pb2.FilterDate, _Mapping]] = ..., filter_array: _Optional[_Union[_filters_common_pb2.FilterArray, _Mapping]] = ..., filter_duration: _Optional[_Union[_filters_common_pb2.FilterDuration, _Mapping]] = ...) -> None: ...

class FiltersAnd(_message.Message):
    __slots__ = ()
    AND_FIELD_NUMBER: _ClassVar[int]
    def __init__(self, **kwargs) -> None: ...

class Filters(_message.Message):
    __slots__ = ()
    OR_FIELD_NUMBER: _ClassVar[int]
    def __init__(self, **kwargs) -> None: ...
