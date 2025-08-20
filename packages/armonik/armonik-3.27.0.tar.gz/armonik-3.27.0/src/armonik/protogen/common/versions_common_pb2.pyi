from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ListVersionsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListVersionsResponse(_message.Message):
    __slots__ = ("core", "api")
    CORE_FIELD_NUMBER: _ClassVar[int]
    API_FIELD_NUMBER: _ClassVar[int]
    core: str
    api: str
    def __init__(self, core: _Optional[str] = ..., api: _Optional[str] = ...) -> None: ...
