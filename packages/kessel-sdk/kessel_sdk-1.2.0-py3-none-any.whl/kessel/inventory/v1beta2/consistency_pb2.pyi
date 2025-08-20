from buf.validate import validate_pb2 as _validate_pb2
from kessel.inventory.v1beta2 import consistency_token_pb2 as _consistency_token_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Consistency(_message.Message):
    __slots__ = ("minimize_latency", "at_least_as_fresh")
    MINIMIZE_LATENCY_FIELD_NUMBER: _ClassVar[int]
    AT_LEAST_AS_FRESH_FIELD_NUMBER: _ClassVar[int]
    minimize_latency: bool
    at_least_as_fresh: _consistency_token_pb2.ConsistencyToken
    def __init__(self, minimize_latency: bool = ..., at_least_as_fresh: _Optional[_Union[_consistency_token_pb2.ConsistencyToken, _Mapping]] = ...) -> None: ...
