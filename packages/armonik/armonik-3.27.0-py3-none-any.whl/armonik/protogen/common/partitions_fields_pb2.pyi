from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PartitionRawEnumField(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PARTITION_RAW_ENUM_FIELD_UNSPECIFIED: _ClassVar[PartitionRawEnumField]
    PARTITION_RAW_ENUM_FIELD_ID: _ClassVar[PartitionRawEnumField]
    PARTITION_RAW_ENUM_FIELD_PARENT_PARTITION_IDS: _ClassVar[PartitionRawEnumField]
    PARTITION_RAW_ENUM_FIELD_POD_RESERVED: _ClassVar[PartitionRawEnumField]
    PARTITION_RAW_ENUM_FIELD_POD_MAX: _ClassVar[PartitionRawEnumField]
    PARTITION_RAW_ENUM_FIELD_PREEMPTION_PERCENTAGE: _ClassVar[PartitionRawEnumField]
    PARTITION_RAW_ENUM_FIELD_PRIORITY: _ClassVar[PartitionRawEnumField]
PARTITION_RAW_ENUM_FIELD_UNSPECIFIED: PartitionRawEnumField
PARTITION_RAW_ENUM_FIELD_ID: PartitionRawEnumField
PARTITION_RAW_ENUM_FIELD_PARENT_PARTITION_IDS: PartitionRawEnumField
PARTITION_RAW_ENUM_FIELD_POD_RESERVED: PartitionRawEnumField
PARTITION_RAW_ENUM_FIELD_POD_MAX: PartitionRawEnumField
PARTITION_RAW_ENUM_FIELD_PREEMPTION_PERCENTAGE: PartitionRawEnumField
PARTITION_RAW_ENUM_FIELD_PRIORITY: PartitionRawEnumField

class PartitionRawField(_message.Message):
    __slots__ = ("field",)
    FIELD_FIELD_NUMBER: _ClassVar[int]
    field: PartitionRawEnumField
    def __init__(self, field: _Optional[_Union[PartitionRawEnumField, str]] = ...) -> None: ...

class PartitionField(_message.Message):
    __slots__ = ("partition_raw_field",)
    PARTITION_RAW_FIELD_FIELD_NUMBER: _ClassVar[int]
    partition_raw_field: PartitionRawField
    def __init__(self, partition_raw_field: _Optional[_Union[PartitionRawField, _Mapping]] = ...) -> None: ...
