from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResultRawEnumField(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESULT_RAW_ENUM_FIELD_UNSPECIFIED: _ClassVar[ResultRawEnumField]
    RESULT_RAW_ENUM_FIELD_SESSION_ID: _ClassVar[ResultRawEnumField]
    RESULT_RAW_ENUM_FIELD_NAME: _ClassVar[ResultRawEnumField]
    RESULT_RAW_ENUM_FIELD_OWNER_TASK_ID: _ClassVar[ResultRawEnumField]
    RESULT_RAW_ENUM_FIELD_STATUS: _ClassVar[ResultRawEnumField]
    RESULT_RAW_ENUM_FIELD_CREATED_AT: _ClassVar[ResultRawEnumField]
    RESULT_RAW_ENUM_FIELD_COMPLETED_AT: _ClassVar[ResultRawEnumField]
    RESULT_RAW_ENUM_FIELD_RESULT_ID: _ClassVar[ResultRawEnumField]
    RESULT_RAW_ENUM_FIELD_SIZE: _ClassVar[ResultRawEnumField]
    RESULT_RAW_ENUM_FIELD_CREATED_BY: _ClassVar[ResultRawEnumField]
    RESULT_RAW_ENUM_FIELD_OPAQUE_ID: _ClassVar[ResultRawEnumField]
    RESULT_RAW_ENUM_FIELD_MANUAL_DELETION: _ClassVar[ResultRawEnumField]
RESULT_RAW_ENUM_FIELD_UNSPECIFIED: ResultRawEnumField
RESULT_RAW_ENUM_FIELD_SESSION_ID: ResultRawEnumField
RESULT_RAW_ENUM_FIELD_NAME: ResultRawEnumField
RESULT_RAW_ENUM_FIELD_OWNER_TASK_ID: ResultRawEnumField
RESULT_RAW_ENUM_FIELD_STATUS: ResultRawEnumField
RESULT_RAW_ENUM_FIELD_CREATED_AT: ResultRawEnumField
RESULT_RAW_ENUM_FIELD_COMPLETED_AT: ResultRawEnumField
RESULT_RAW_ENUM_FIELD_RESULT_ID: ResultRawEnumField
RESULT_RAW_ENUM_FIELD_SIZE: ResultRawEnumField
RESULT_RAW_ENUM_FIELD_CREATED_BY: ResultRawEnumField
RESULT_RAW_ENUM_FIELD_OPAQUE_ID: ResultRawEnumField
RESULT_RAW_ENUM_FIELD_MANUAL_DELETION: ResultRawEnumField

class ResultRawField(_message.Message):
    __slots__ = ("field",)
    FIELD_FIELD_NUMBER: _ClassVar[int]
    field: ResultRawEnumField
    def __init__(self, field: _Optional[_Union[ResultRawEnumField, str]] = ...) -> None: ...

class ResultField(_message.Message):
    __slots__ = ("result_raw_field",)
    RESULT_RAW_FIELD_FIELD_NUMBER: _ClassVar[int]
    result_raw_field: ResultRawField
    def __init__(self, result_raw_field: _Optional[_Union[ResultRawField, _Mapping]] = ...) -> None: ...
