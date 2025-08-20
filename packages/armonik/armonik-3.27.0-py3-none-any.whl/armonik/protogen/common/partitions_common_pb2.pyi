from . import partitions_fields_pb2 as _partitions_fields_pb2
from . import partitions_filters_pb2 as _partitions_filters_pb2
from . import sort_direction_pb2 as _sort_direction_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PartitionRaw(_message.Message):
    __slots__ = ("id", "parent_partition_ids", "pod_reserved", "pod_max", "pod_configuration", "preemption_percentage", "priority")
    class PodConfigurationEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_PARTITION_IDS_FIELD_NUMBER: _ClassVar[int]
    POD_RESERVED_FIELD_NUMBER: _ClassVar[int]
    POD_MAX_FIELD_NUMBER: _ClassVar[int]
    POD_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    PREEMPTION_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    id: str
    parent_partition_ids: _containers.RepeatedScalarFieldContainer[str]
    pod_reserved: int
    pod_max: int
    pod_configuration: _containers.ScalarMap[str, str]
    preemption_percentage: int
    priority: int
    def __init__(self, id: _Optional[str] = ..., parent_partition_ids: _Optional[_Iterable[str]] = ..., pod_reserved: _Optional[int] = ..., pod_max: _Optional[int] = ..., pod_configuration: _Optional[_Mapping[str, str]] = ..., preemption_percentage: _Optional[int] = ..., priority: _Optional[int] = ...) -> None: ...

class ListPartitionsRequest(_message.Message):
    __slots__ = ("page", "page_size", "filters", "sort")
    class Sort(_message.Message):
        __slots__ = ("field", "direction")
        FIELD_FIELD_NUMBER: _ClassVar[int]
        DIRECTION_FIELD_NUMBER: _ClassVar[int]
        field: _partitions_fields_pb2.PartitionField
        direction: _sort_direction_pb2.SortDirection
        def __init__(self, field: _Optional[_Union[_partitions_fields_pb2.PartitionField, _Mapping]] = ..., direction: _Optional[_Union[_sort_direction_pb2.SortDirection, str]] = ...) -> None: ...
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    filters: _partitions_filters_pb2.Filters
    sort: ListPartitionsRequest.Sort
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., filters: _Optional[_Union[_partitions_filters_pb2.Filters, _Mapping]] = ..., sort: _Optional[_Union[ListPartitionsRequest.Sort, _Mapping]] = ...) -> None: ...

class ListPartitionsResponse(_message.Message):
    __slots__ = ("partitions", "page", "page_size", "total")
    PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    partitions: _containers.RepeatedCompositeFieldContainer[PartitionRaw]
    page: int
    page_size: int
    total: int
    def __init__(self, partitions: _Optional[_Iterable[_Union[PartitionRaw, _Mapping]]] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class GetPartitionRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetPartitionResponse(_message.Message):
    __slots__ = ("partition",)
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    partition: PartitionRaw
    def __init__(self, partition: _Optional[_Union[PartitionRaw, _Mapping]] = ...) -> None: ...
