from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ResponsePagination(_message.Message):
    __slots__ = ("continuation_token",)
    CONTINUATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    continuation_token: str
    def __init__(self, continuation_token: _Optional[str] = ...) -> None: ...
