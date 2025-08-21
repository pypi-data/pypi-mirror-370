from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RequestPagination(_message.Message):
    __slots__ = ("limit", "continuation_token")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    CONTINUATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    limit: int
    continuation_token: str
    def __init__(self, limit: _Optional[int] = ..., continuation_token: _Optional[str] = ...) -> None: ...
