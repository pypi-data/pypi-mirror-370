from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class WriteVisibility(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WRITE_VISIBILITY_UNSPECIFIED: _ClassVar[WriteVisibility]
    MINIMIZE_LATENCY: _ClassVar[WriteVisibility]
    IMMEDIATE: _ClassVar[WriteVisibility]
WRITE_VISIBILITY_UNSPECIFIED: WriteVisibility
MINIMIZE_LATENCY: WriteVisibility
IMMEDIATE: WriteVisibility
