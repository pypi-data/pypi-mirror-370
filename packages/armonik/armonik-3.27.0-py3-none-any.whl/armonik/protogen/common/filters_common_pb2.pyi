from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilterStringOperator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILTER_STRING_OPERATOR_EQUAL: _ClassVar[FilterStringOperator]
    FILTER_STRING_OPERATOR_NOT_EQUAL: _ClassVar[FilterStringOperator]
    FILTER_STRING_OPERATOR_CONTAINS: _ClassVar[FilterStringOperator]
    FILTER_STRING_OPERATOR_NOT_CONTAINS: _ClassVar[FilterStringOperator]
    FILTER_STRING_OPERATOR_STARTS_WITH: _ClassVar[FilterStringOperator]
    FILTER_STRING_OPERATOR_ENDS_WITH: _ClassVar[FilterStringOperator]

class FilterNumberOperator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILTER_NUMBER_OPERATOR_EQUAL: _ClassVar[FilterNumberOperator]
    FILTER_NUMBER_OPERATOR_NOT_EQUAL: _ClassVar[FilterNumberOperator]
    FILTER_NUMBER_OPERATOR_LESS_THAN: _ClassVar[FilterNumberOperator]
    FILTER_NUMBER_OPERATOR_LESS_THAN_OR_EQUAL: _ClassVar[FilterNumberOperator]
    FILTER_NUMBER_OPERATOR_GREATER_THAN_OR_EQUAL: _ClassVar[FilterNumberOperator]
    FILTER_NUMBER_OPERATOR_GREATER_THAN: _ClassVar[FilterNumberOperator]

class FilterDateOperator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILTER_DATE_OPERATOR_EQUAL: _ClassVar[FilterDateOperator]
    FILTER_DATE_OPERATOR_NOT_EQUAL: _ClassVar[FilterDateOperator]
    FILTER_DATE_OPERATOR_BEFORE: _ClassVar[FilterDateOperator]
    FILTER_DATE_OPERATOR_BEFORE_OR_EQUAL: _ClassVar[FilterDateOperator]
    FILTER_DATE_OPERATOR_AFTER_OR_EQUAL: _ClassVar[FilterDateOperator]
    FILTER_DATE_OPERATOR_AFTER: _ClassVar[FilterDateOperator]

class FilterArrayOperator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILTER_ARRAY_OPERATOR_CONTAINS: _ClassVar[FilterArrayOperator]
    FILTER_ARRAY_OPERATOR_NOT_CONTAINS: _ClassVar[FilterArrayOperator]

class FilterStatusOperator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILTER_STATUS_OPERATOR_EQUAL: _ClassVar[FilterStatusOperator]
    FILTER_STATUS_OPERATOR_NOT_EQUAL: _ClassVar[FilterStatusOperator]

class FilterBooleanOperator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILTER_BOOLEAN_OPERATOR_IS: _ClassVar[FilterBooleanOperator]

class FilterDurationOperator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILTER_DURATION_OPERATOR_EQUAL: _ClassVar[FilterDurationOperator]
    FILTER_DURATION_OPERATOR_NOT_EQUAL: _ClassVar[FilterDurationOperator]
    FILTER_DURATION_OPERATOR_SHORTER_THAN: _ClassVar[FilterDurationOperator]
    FILTER_DURATION_OPERATOR_SHORTER_THAN_OR_EQUAL: _ClassVar[FilterDurationOperator]
    FILTER_DURATION_OPERATOR_LONGER_THAN_OR_EQUAL: _ClassVar[FilterDurationOperator]
    FILTER_DURATION_OPERATOR_LONGER_THAN: _ClassVar[FilterDurationOperator]
FILTER_STRING_OPERATOR_EQUAL: FilterStringOperator
FILTER_STRING_OPERATOR_NOT_EQUAL: FilterStringOperator
FILTER_STRING_OPERATOR_CONTAINS: FilterStringOperator
FILTER_STRING_OPERATOR_NOT_CONTAINS: FilterStringOperator
FILTER_STRING_OPERATOR_STARTS_WITH: FilterStringOperator
FILTER_STRING_OPERATOR_ENDS_WITH: FilterStringOperator
FILTER_NUMBER_OPERATOR_EQUAL: FilterNumberOperator
FILTER_NUMBER_OPERATOR_NOT_EQUAL: FilterNumberOperator
FILTER_NUMBER_OPERATOR_LESS_THAN: FilterNumberOperator
FILTER_NUMBER_OPERATOR_LESS_THAN_OR_EQUAL: FilterNumberOperator
FILTER_NUMBER_OPERATOR_GREATER_THAN_OR_EQUAL: FilterNumberOperator
FILTER_NUMBER_OPERATOR_GREATER_THAN: FilterNumberOperator
FILTER_DATE_OPERATOR_EQUAL: FilterDateOperator
FILTER_DATE_OPERATOR_NOT_EQUAL: FilterDateOperator
FILTER_DATE_OPERATOR_BEFORE: FilterDateOperator
FILTER_DATE_OPERATOR_BEFORE_OR_EQUAL: FilterDateOperator
FILTER_DATE_OPERATOR_AFTER_OR_EQUAL: FilterDateOperator
FILTER_DATE_OPERATOR_AFTER: FilterDateOperator
FILTER_ARRAY_OPERATOR_CONTAINS: FilterArrayOperator
FILTER_ARRAY_OPERATOR_NOT_CONTAINS: FilterArrayOperator
FILTER_STATUS_OPERATOR_EQUAL: FilterStatusOperator
FILTER_STATUS_OPERATOR_NOT_EQUAL: FilterStatusOperator
FILTER_BOOLEAN_OPERATOR_IS: FilterBooleanOperator
FILTER_DURATION_OPERATOR_EQUAL: FilterDurationOperator
FILTER_DURATION_OPERATOR_NOT_EQUAL: FilterDurationOperator
FILTER_DURATION_OPERATOR_SHORTER_THAN: FilterDurationOperator
FILTER_DURATION_OPERATOR_SHORTER_THAN_OR_EQUAL: FilterDurationOperator
FILTER_DURATION_OPERATOR_LONGER_THAN_OR_EQUAL: FilterDurationOperator
FILTER_DURATION_OPERATOR_LONGER_THAN: FilterDurationOperator

class FilterString(_message.Message):
    __slots__ = ("value", "operator")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    value: str
    operator: FilterStringOperator
    def __init__(self, value: _Optional[str] = ..., operator: _Optional[_Union[FilterStringOperator, str]] = ...) -> None: ...

class FilterNumber(_message.Message):
    __slots__ = ("value", "operator")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    value: int
    operator: FilterNumberOperator
    def __init__(self, value: _Optional[int] = ..., operator: _Optional[_Union[FilterNumberOperator, str]] = ...) -> None: ...

class FilterDate(_message.Message):
    __slots__ = ("value", "operator")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    value: _timestamp_pb2.Timestamp
    operator: FilterDateOperator
    def __init__(self, value: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., operator: _Optional[_Union[FilterDateOperator, str]] = ...) -> None: ...

class FilterArray(_message.Message):
    __slots__ = ("value", "operator")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    value: str
    operator: FilterArrayOperator
    def __init__(self, value: _Optional[str] = ..., operator: _Optional[_Union[FilterArrayOperator, str]] = ...) -> None: ...

class FilterBoolean(_message.Message):
    __slots__ = ("value", "operator")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    value: bool
    operator: FilterBooleanOperator
    def __init__(self, value: bool = ..., operator: _Optional[_Union[FilterBooleanOperator, str]] = ...) -> None: ...

class FilterDuration(_message.Message):
    __slots__ = ("value", "operator")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    value: _duration_pb2.Duration
    operator: FilterDurationOperator
    def __init__(self, value: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., operator: _Optional[_Union[FilterDurationOperator, str]] = ...) -> None: ...
