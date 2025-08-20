from kessel.inventory.v1beta2 import resource_representations_pb2 as _resource_representations_pb2
from kessel.inventory.v1beta2 import write_visibility_pb2 as _write_visibility_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReportResourceRequest(_message.Message):
    __slots__ = ("inventory_id", "type", "reporter_type", "reporter_instance_id", "representations", "write_visibility")
    INVENTORY_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REPORTER_TYPE_FIELD_NUMBER: _ClassVar[int]
    REPORTER_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    REPRESENTATIONS_FIELD_NUMBER: _ClassVar[int]
    WRITE_VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    inventory_id: str
    type: str
    reporter_type: str
    reporter_instance_id: str
    representations: _resource_representations_pb2.ResourceRepresentations
    write_visibility: _write_visibility_pb2.WriteVisibility
    def __init__(self, inventory_id: _Optional[str] = ..., type: _Optional[str] = ..., reporter_type: _Optional[str] = ..., reporter_instance_id: _Optional[str] = ..., representations: _Optional[_Union[_resource_representations_pb2.ResourceRepresentations, _Mapping]] = ..., write_visibility: _Optional[_Union[_write_visibility_pb2.WriteVisibility, str]] = ...) -> None: ...
