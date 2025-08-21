from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class K8sPolicyDetail(_message.Message):
    __slots__ = ("disabled", "severity")
    class Severity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SEVERITY_UNSPECIFIED: _ClassVar[K8sPolicyDetail.Severity]
        SEVERITY_OTHER: _ClassVar[K8sPolicyDetail.Severity]
        LOW: _ClassVar[K8sPolicyDetail.Severity]
        MEDIUM: _ClassVar[K8sPolicyDetail.Severity]
        HIGH: _ClassVar[K8sPolicyDetail.Severity]
        CRITICAL: _ClassVar[K8sPolicyDetail.Severity]
    SEVERITY_UNSPECIFIED: K8sPolicyDetail.Severity
    SEVERITY_OTHER: K8sPolicyDetail.Severity
    LOW: K8sPolicyDetail.Severity
    MEDIUM: K8sPolicyDetail.Severity
    HIGH: K8sPolicyDetail.Severity
    CRITICAL: K8sPolicyDetail.Severity
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    disabled: bool
    severity: K8sPolicyDetail.Severity
    def __init__(self, disabled: bool = ..., severity: _Optional[_Union[K8sPolicyDetail.Severity, str]] = ...) -> None: ...
