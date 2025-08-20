from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ApplicationRawEnumField(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    APPLICATION_RAW_ENUM_FIELD_UNSPECIFIED: _ClassVar[ApplicationRawEnumField]
    APPLICATION_RAW_ENUM_FIELD_NAME: _ClassVar[ApplicationRawEnumField]
    APPLICATION_RAW_ENUM_FIELD_VERSION: _ClassVar[ApplicationRawEnumField]
    APPLICATION_RAW_ENUM_FIELD_NAMESPACE: _ClassVar[ApplicationRawEnumField]
    APPLICATION_RAW_ENUM_FIELD_SERVICE: _ClassVar[ApplicationRawEnumField]
APPLICATION_RAW_ENUM_FIELD_UNSPECIFIED: ApplicationRawEnumField
APPLICATION_RAW_ENUM_FIELD_NAME: ApplicationRawEnumField
APPLICATION_RAW_ENUM_FIELD_VERSION: ApplicationRawEnumField
APPLICATION_RAW_ENUM_FIELD_NAMESPACE: ApplicationRawEnumField
APPLICATION_RAW_ENUM_FIELD_SERVICE: ApplicationRawEnumField

class ApplicationRawField(_message.Message):
    __slots__ = ("field",)
    FIELD_FIELD_NUMBER: _ClassVar[int]
    field: ApplicationRawEnumField
    def __init__(self, field: _Optional[_Union[ApplicationRawEnumField, str]] = ...) -> None: ...

class ApplicationField(_message.Message):
    __slots__ = ("application_field",)
    APPLICATION_FIELD_FIELD_NUMBER: _ClassVar[int]
    application_field: ApplicationRawField
    def __init__(self, application_field: _Optional[_Union[ApplicationRawField, _Mapping]] = ...) -> None: ...
