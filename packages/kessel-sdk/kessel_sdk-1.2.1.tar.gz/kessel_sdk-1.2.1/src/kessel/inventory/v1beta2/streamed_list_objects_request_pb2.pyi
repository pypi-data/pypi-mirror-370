from buf.validate import validate_pb2 as _validate_pb2
from kessel.inventory.v1beta2 import request_pagination_pb2 as _request_pagination_pb2
from kessel.inventory.v1beta2 import subject_reference_pb2 as _subject_reference_pb2
from kessel.inventory.v1beta2 import consistency_pb2 as _consistency_pb2
from kessel.inventory.v1beta2 import representation_type_pb2 as _representation_type_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StreamedListObjectsRequest(_message.Message):
    __slots__ = ("object_type", "relation", "subject", "pagination", "consistency")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    CONSISTENCY_FIELD_NUMBER: _ClassVar[int]
    object_type: _representation_type_pb2.RepresentationType
    relation: str
    subject: _subject_reference_pb2.SubjectReference
    pagination: _request_pagination_pb2.RequestPagination
    consistency: _consistency_pb2.Consistency
    def __init__(self, object_type: _Optional[_Union[_representation_type_pb2.RepresentationType, _Mapping]] = ..., relation: _Optional[str] = ..., subject: _Optional[_Union[_subject_reference_pb2.SubjectReference, _Mapping]] = ..., pagination: _Optional[_Union[_request_pagination_pb2.RequestPagination, _Mapping]] = ..., consistency: _Optional[_Union[_consistency_pb2.Consistency, _Mapping]] = ...) -> None: ...
