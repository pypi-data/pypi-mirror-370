from . import filters_common_pb2 as _filters_common_pb2
from . import partitions_fields_pb2 as _partitions_fields_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilterField(_message.Message):
    __slots__ = ("field", "filter_string", "filter_number", "filter_boolean", "filter_array")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FILTER_STRING_FIELD_NUMBER: _ClassVar[int]
    FILTER_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FILTER_BOOLEAN_FIELD_NUMBER: _ClassVar[int]
    FILTER_ARRAY_FIELD_NUMBER: _ClassVar[int]
    field: _partitions_fields_pb2.PartitionField
    filter_string: _filters_common_pb2.FilterString
    filter_number: _filters_common_pb2.FilterNumber
    filter_boolean: _filters_common_pb2.FilterBoolean
    filter_array: _filters_common_pb2.FilterArray
    def __init__(self, field: _Optional[_Union[_partitions_fields_pb2.PartitionField, _Mapping]] = ..., filter_string: _Optional[_Union[_filters_common_pb2.FilterString, _Mapping]] = ..., filter_number: _Optional[_Union[_filters_common_pb2.FilterNumber, _Mapping]] = ..., filter_boolean: _Optional[_Union[_filters_common_pb2.FilterBoolean, _Mapping]] = ..., filter_array: _Optional[_Union[_filters_common_pb2.FilterArray, _Mapping]] = ...) -> None: ...

class FiltersAnd(_message.Message):
    __slots__ = ()
    AND_FIELD_NUMBER: _ClassVar[int]
    def __init__(self, **kwargs) -> None: ...

class Filters(_message.Message):
    __slots__ = ()
    OR_FIELD_NUMBER: _ClassVar[int]
    def __init__(self, **kwargs) -> None: ...
