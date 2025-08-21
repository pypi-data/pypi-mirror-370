from google.api import field_behavior_pb2 as _field_behavior_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReporterData(_message.Message):
    __slots__ = ("reporter_type", "reporter_instance_id", "console_href", "api_href", "local_resource_id", "reporter_version")
    class ReporterType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REPORTER_TYPE_UNSPECIFIED: _ClassVar[ReporterData.ReporterType]
        REPORTER_TYPE_OTHER: _ClassVar[ReporterData.ReporterType]
        ACM: _ClassVar[ReporterData.ReporterType]
        HBI: _ClassVar[ReporterData.ReporterType]
        OCM: _ClassVar[ReporterData.ReporterType]
        NOTIFICATIONS: _ClassVar[ReporterData.ReporterType]
    REPORTER_TYPE_UNSPECIFIED: ReporterData.ReporterType
    REPORTER_TYPE_OTHER: ReporterData.ReporterType
    ACM: ReporterData.ReporterType
    HBI: ReporterData.ReporterType
    OCM: ReporterData.ReporterType
    NOTIFICATIONS: ReporterData.ReporterType
    REPORTER_TYPE_FIELD_NUMBER: _ClassVar[int]
    REPORTER_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    CONSOLE_HREF_FIELD_NUMBER: _ClassVar[int]
    API_HREF_FIELD_NUMBER: _ClassVar[int]
    LOCAL_RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    REPORTER_VERSION_FIELD_NUMBER: _ClassVar[int]
    reporter_type: ReporterData.ReporterType
    reporter_instance_id: str
    console_href: str
    api_href: str
    local_resource_id: str
    reporter_version: str
    def __init__(self, reporter_type: _Optional[_Union[ReporterData.ReporterType, str]] = ..., reporter_instance_id: _Optional[str] = ..., console_href: _Optional[str] = ..., api_href: _Optional[str] = ..., local_resource_id: _Optional[str] = ..., reporter_version: _Optional[str] = ...) -> None: ...
