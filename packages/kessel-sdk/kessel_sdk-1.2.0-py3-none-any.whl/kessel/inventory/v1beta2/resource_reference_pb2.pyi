from buf.validate import validate_pb2 as _validate_pb2
from kessel.inventory.v1beta2 import reporter_reference_pb2 as _reporter_reference_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResourceReference(_message.Message):
    __slots__ = ("resource_type", "resource_id", "reporter")
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    REPORTER_FIELD_NUMBER: _ClassVar[int]
    resource_type: str
    resource_id: str
    reporter: _reporter_reference_pb2.ReporterReference
    def __init__(self, resource_type: _Optional[str] = ..., resource_id: _Optional[str] = ..., reporter: _Optional[_Union[_reporter_reference_pb2.ReporterReference, _Mapping]] = ...) -> None: ...
