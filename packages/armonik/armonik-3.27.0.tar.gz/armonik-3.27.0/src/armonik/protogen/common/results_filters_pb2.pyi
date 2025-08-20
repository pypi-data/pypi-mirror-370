from . import filters_common_pb2 as _filters_common_pb2
from . import result_status_pb2 as _result_status_pb2
from . import results_fields_pb2 as _results_fields_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilterStatus(_message.Message):
    __slots__ = ("value", "operator")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    value: _result_status_pb2.ResultStatus
    operator: _filters_common_pb2.FilterStatusOperator
    def __init__(self, value: _Optional[_Union[_result_status_pb2.ResultStatus, str]] = ..., operator: _Optional[_Union[_filters_common_pb2.FilterStatusOperator, str]] = ...) -> None: ...

class FilterField(_message.Message):
    __slots__ = ("field", "filter_string", "filter_date", "filter_array", "filter_status", "filter_number")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FILTER_STRING_FIELD_NUMBER: _ClassVar[int]
    FILTER_DATE_FIELD_NUMBER: _ClassVar[int]
    FILTER_ARRAY_FIELD_NUMBER: _ClassVar[int]
    FILTER_STATUS_FIELD_NUMBER: _ClassVar[int]
    FILTER_NUMBER_FIELD_NUMBER: _ClassVar[int]
    field: _results_fields_pb2.ResultField
    filter_string: _filters_common_pb2.FilterString
    filter_date: _filters_common_pb2.FilterDate
    filter_array: _filters_common_pb2.FilterArray
    filter_status: FilterStatus
    filter_number: _filters_common_pb2.FilterNumber
    def __init__(self, field: _Optional[_Union[_results_fields_pb2.ResultField, _Mapping]] = ..., filter_string: _Optional[_Union[_filters_common_pb2.FilterString, _Mapping]] = ..., filter_date: _Optional[_Union[_filters_common_pb2.FilterDate, _Mapping]] = ..., filter_array: _Optional[_Union[_filters_common_pb2.FilterArray, _Mapping]] = ..., filter_status: _Optional[_Union[FilterStatus, _Mapping]] = ..., filter_number: _Optional[_Union[_filters_common_pb2.FilterNumber, _Mapping]] = ...) -> None: ...

class FiltersAnd(_message.Message):
    __slots__ = ()
    AND_FIELD_NUMBER: _ClassVar[int]
    def __init__(self, **kwargs) -> None: ...

class Filters(_message.Message):
    __slots__ = ()
    OR_FIELD_NUMBER: _ClassVar[int]
    def __init__(self, **kwargs) -> None: ...
