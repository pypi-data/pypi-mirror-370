from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class ResultStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESULT_STATUS_UNSPECIFIED: _ClassVar[ResultStatus]
    RESULT_STATUS_CREATED: _ClassVar[ResultStatus]
    RESULT_STATUS_COMPLETED: _ClassVar[ResultStatus]
    RESULT_STATUS_ABORTED: _ClassVar[ResultStatus]
    RESULT_STATUS_DELETED: _ClassVar[ResultStatus]
    RESULT_STATUS_NOTFOUND: _ClassVar[ResultStatus]
RESULT_STATUS_UNSPECIFIED: ResultStatus
RESULT_STATUS_CREATED: ResultStatus
RESULT_STATUS_COMPLETED: ResultStatus
RESULT_STATUS_ABORTED: ResultStatus
RESULT_STATUS_DELETED: ResultStatus
RESULT_STATUS_NOTFOUND: ResultStatus
