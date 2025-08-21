from google.api import field_behavior_pb2 as _field_behavior_pb2
from buf.validate import validate_pb2 as _validate_pb2
from kessel.inventory.v1beta1.resources import metadata_pb2 as _metadata_pb2
from kessel.inventory.v1beta1.resources import reporter_data_pb2 as _reporter_data_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NotificationsIntegration(_message.Message):
    __slots__ = ("metadata", "reporter_data")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    REPORTER_DATA_FIELD_NUMBER: _ClassVar[int]
    metadata: _metadata_pb2.Metadata
    reporter_data: _reporter_data_pb2.ReporterData
    def __init__(self, metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ..., reporter_data: _Optional[_Union[_reporter_data_pb2.ReporterData, _Mapping]] = ...) -> None: ...
