from . import applications_fields_pb2 as _applications_fields_pb2
from . import applications_filters_pb2 as _applications_filters_pb2
from . import sort_direction_pb2 as _sort_direction_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ApplicationRaw(_message.Message):
    __slots__ = ("name", "version", "namespace", "service")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    name: str
    version: str
    namespace: str
    service: str
    def __init__(self, name: _Optional[str] = ..., version: _Optional[str] = ..., namespace: _Optional[str] = ..., service: _Optional[str] = ...) -> None: ...

class ListApplicationsRequest(_message.Message):
    __slots__ = ("page", "page_size", "filters", "sort")
    class Sort(_message.Message):
        __slots__ = ("fields", "direction")
        FIELDS_FIELD_NUMBER: _ClassVar[int]
        DIRECTION_FIELD_NUMBER: _ClassVar[int]
        fields: _containers.RepeatedCompositeFieldContainer[_applications_fields_pb2.ApplicationField]
        direction: _sort_direction_pb2.SortDirection
        def __init__(self, fields: _Optional[_Iterable[_Union[_applications_fields_pb2.ApplicationField, _Mapping]]] = ..., direction: _Optional[_Union[_sort_direction_pb2.SortDirection, str]] = ...) -> None: ...
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    filters: _applications_filters_pb2.Filters
    sort: ListApplicationsRequest.Sort
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., filters: _Optional[_Union[_applications_filters_pb2.Filters, _Mapping]] = ..., sort: _Optional[_Union[ListApplicationsRequest.Sort, _Mapping]] = ...) -> None: ...

class ListApplicationsResponse(_message.Message):
    __slots__ = ("applications", "page", "page_size", "total")
    APPLICATIONS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    applications: _containers.RepeatedCompositeFieldContainer[ApplicationRaw]
    page: int
    page_size: int
    total: int
    def __init__(self, applications: _Optional[_Iterable[_Union[ApplicationRaw, _Mapping]]] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...
