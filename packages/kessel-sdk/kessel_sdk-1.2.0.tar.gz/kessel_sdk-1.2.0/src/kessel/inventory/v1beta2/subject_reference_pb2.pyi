from buf.validate import validate_pb2 as _validate_pb2
from kessel.inventory.v1beta2 import resource_reference_pb2 as _resource_reference_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SubjectReference(_message.Message):
    __slots__ = ("relation", "resource")
    RELATION_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    relation: str
    resource: _resource_reference_pb2.ResourceReference
    def __init__(self, relation: _Optional[str] = ..., resource: _Optional[_Union[_resource_reference_pb2.ResourceReference, _Mapping]] = ...) -> None: ...
