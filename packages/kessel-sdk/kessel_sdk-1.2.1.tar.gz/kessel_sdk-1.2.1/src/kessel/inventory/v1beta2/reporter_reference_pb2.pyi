from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ReporterReference(_message.Message):
    __slots__ = ("type", "instance_id")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    type: str
    instance_id: str
    def __init__(self, type: _Optional[str] = ..., instance_id: _Optional[str] = ...) -> None: ...
