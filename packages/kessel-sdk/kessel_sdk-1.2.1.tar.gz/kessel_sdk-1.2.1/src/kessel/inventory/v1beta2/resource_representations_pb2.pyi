from google.protobuf import struct_pb2 as _struct_pb2
from kessel.inventory.v1beta2 import representation_metadata_pb2 as _representation_metadata_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResourceRepresentations(_message.Message):
    __slots__ = ("metadata", "common", "reporter")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    COMMON_FIELD_NUMBER: _ClassVar[int]
    REPORTER_FIELD_NUMBER: _ClassVar[int]
    metadata: _representation_metadata_pb2.RepresentationMetadata
    common: _struct_pb2.Struct
    reporter: _struct_pb2.Struct
    def __init__(self, metadata: _Optional[_Union[_representation_metadata_pb2.RepresentationMetadata, _Mapping]] = ..., common: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., reporter: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
