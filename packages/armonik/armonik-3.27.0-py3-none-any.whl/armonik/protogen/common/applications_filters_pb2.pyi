from . import applications_fields_pb2 as _applications_fields_pb2
from . import filters_common_pb2 as _filters_common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilterField(_message.Message):
    __slots__ = ("field", "filter_string")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FILTER_STRING_FIELD_NUMBER: _ClassVar[int]
    field: _applications_fields_pb2.ApplicationField
    filter_string: _filters_common_pb2.FilterString
    def __init__(self, field: _Optional[_Union[_applications_fields_pb2.ApplicationField, _Mapping]] = ..., filter_string: _Optional[_Union[_filters_common_pb2.FilterString, _Mapping]] = ...) -> None: ...

class FiltersAnd(_message.Message):
    __slots__ = ()
    AND_FIELD_NUMBER: _ClassVar[int]
    def __init__(self, **kwargs) -> None: ...

class Filters(_message.Message):
    __slots__ = ()
    OR_FIELD_NUMBER: _ClassVar[int]
    def __init__(self, **kwargs) -> None: ...
