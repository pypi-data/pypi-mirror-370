from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class Allowed(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALLOWED_UNSPECIFIED: _ClassVar[Allowed]
    ALLOWED_TRUE: _ClassVar[Allowed]
    ALLOWED_FALSE: _ClassVar[Allowed]
ALLOWED_UNSPECIFIED: Allowed
ALLOWED_TRUE: Allowed
ALLOWED_FALSE: Allowed
