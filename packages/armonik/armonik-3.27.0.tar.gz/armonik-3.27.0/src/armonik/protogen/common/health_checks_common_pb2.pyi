from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HealthStatusEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HEALTH_STATUS_ENUM_UNSPECIFIED: _ClassVar[HealthStatusEnum]
    HEALTH_STATUS_ENUM_HEALTHY: _ClassVar[HealthStatusEnum]
    HEALTH_STATUS_ENUM_DEGRADED: _ClassVar[HealthStatusEnum]
    HEALTH_STATUS_ENUM_UNHEALTHY: _ClassVar[HealthStatusEnum]
HEALTH_STATUS_ENUM_UNSPECIFIED: HealthStatusEnum
HEALTH_STATUS_ENUM_HEALTHY: HealthStatusEnum
HEALTH_STATUS_ENUM_DEGRADED: HealthStatusEnum
HEALTH_STATUS_ENUM_UNHEALTHY: HealthStatusEnum

class CheckHealthRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CheckHealthResponse(_message.Message):
    __slots__ = ("services",)
    class ServiceHealth(_message.Message):
        __slots__ = ("name", "message", "healthy")
        NAME_FIELD_NUMBER: _ClassVar[int]
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        HEALTHY_FIELD_NUMBER: _ClassVar[int]
        name: str
        message: str
        healthy: HealthStatusEnum
        def __init__(self, name: _Optional[str] = ..., message: _Optional[str] = ..., healthy: _Optional[_Union[HealthStatusEnum, str]] = ...) -> None: ...
    SERVICES_FIELD_NUMBER: _ClassVar[int]
    services: _containers.RepeatedCompositeFieldContainer[CheckHealthResponse.ServiceHealth]
    def __init__(self, services: _Optional[_Iterable[_Union[CheckHealthResponse.ServiceHealth, _Mapping]]] = ...) -> None: ...
