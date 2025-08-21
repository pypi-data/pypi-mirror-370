from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RepresentationType(_message.Message):
    __slots__ = ("resource_type", "reporter_type")
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REPORTER_TYPE_FIELD_NUMBER: _ClassVar[int]
    resource_type: str
    reporter_type: str
    def __init__(self, resource_type: _Optional[str] = ..., reporter_type: _Optional[str] = ...) -> None: ...
