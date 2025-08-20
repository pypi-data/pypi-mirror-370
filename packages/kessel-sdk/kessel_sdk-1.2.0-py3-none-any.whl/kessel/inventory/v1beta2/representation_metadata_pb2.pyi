from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RepresentationMetadata(_message.Message):
    __slots__ = ("local_resource_id", "api_href", "console_href", "reporter_version")
    LOCAL_RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    API_HREF_FIELD_NUMBER: _ClassVar[int]
    CONSOLE_HREF_FIELD_NUMBER: _ClassVar[int]
    REPORTER_VERSION_FIELD_NUMBER: _ClassVar[int]
    local_resource_id: str
    api_href: str
    console_href: str
    reporter_version: str
    def __init__(self, local_resource_id: _Optional[str] = ..., api_href: _Optional[str] = ..., console_href: _Optional[str] = ..., reporter_version: _Optional[str] = ...) -> None: ...
