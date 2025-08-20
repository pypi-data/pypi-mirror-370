from kessel.inventory.v1beta2 import allowed_pb2 as _allowed_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CheckForUpdateResponse(_message.Message):
    __slots__ = ("allowed",)
    ALLOWED_FIELD_NUMBER: _ClassVar[int]
    allowed: _allowed_pb2.Allowed
    def __init__(self, allowed: _Optional[_Union[_allowed_pb2.Allowed, str]] = ...) -> None: ...
