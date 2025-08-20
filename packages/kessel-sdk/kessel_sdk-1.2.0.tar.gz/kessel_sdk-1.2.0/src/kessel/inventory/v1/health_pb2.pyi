from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetLivezRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetLivezResponse(_message.Message):
    __slots__ = ("status", "code")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    status: str
    code: int
    def __init__(self, status: _Optional[str] = ..., code: _Optional[int] = ...) -> None: ...

class GetReadyzRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetReadyzResponse(_message.Message):
    __slots__ = ("status", "code")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    status: str
    code: int
    def __init__(self, status: _Optional[str] = ..., code: _Optional[int] = ...) -> None: ...
