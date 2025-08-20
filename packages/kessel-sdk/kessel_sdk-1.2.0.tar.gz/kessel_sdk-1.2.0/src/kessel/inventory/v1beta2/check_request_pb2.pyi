from buf.validate import validate_pb2 as _validate_pb2
from kessel.inventory.v1beta2 import resource_reference_pb2 as _resource_reference_pb2
from kessel.inventory.v1beta2 import subject_reference_pb2 as _subject_reference_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CheckRequest(_message.Message):
    __slots__ = ("object", "relation", "subject")
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    object: _resource_reference_pb2.ResourceReference
    relation: str
    subject: _subject_reference_pb2.SubjectReference
    def __init__(self, object: _Optional[_Union[_resource_reference_pb2.ResourceReference, _Mapping]] = ..., relation: _Optional[str] = ..., subject: _Optional[_Union[_subject_reference_pb2.SubjectReference, _Mapping]] = ...) -> None: ...
