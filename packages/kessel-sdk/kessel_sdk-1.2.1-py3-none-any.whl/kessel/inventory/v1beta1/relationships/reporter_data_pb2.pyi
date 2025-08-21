import datetime

from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReporterData(_message.Message):
    __slots__ = ("reporter_type", "reporter_instance_id", "reporter_version", "first_reported", "last_reported", "subject_local_resource_id", "object_local_resource_id")
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
    REPORTER_VERSION_FIELD_NUMBER: _ClassVar[int]
    FIRST_REPORTED_FIELD_NUMBER: _ClassVar[int]
    LAST_REPORTED_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_LOCAL_RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_LOCAL_RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    reporter_type: ReporterData.ReporterType
    reporter_instance_id: str
    reporter_version: str
    first_reported: _timestamp_pb2.Timestamp
    last_reported: _timestamp_pb2.Timestamp
    subject_local_resource_id: str
    object_local_resource_id: str
    def __init__(self, reporter_type: _Optional[_Union[ReporterData.ReporterType, str]] = ..., reporter_instance_id: _Optional[str] = ..., reporter_version: _Optional[str] = ..., first_reported: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., last_reported: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., subject_local_resource_id: _Optional[str] = ..., object_local_resource_id: _Optional[str] = ...) -> None: ...
