from google.api import annotations_pb2 as _annotations_pb2
from buf.validate import validate_pb2 as _validate_pb2
from kessel.inventory.v1beta1.resources import rhel_host_pb2 as _rhel_host_pb2
from kessel.inventory.v1beta1.resources import reporter_data_pb2 as _reporter_data_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateRhelHostRequest(_message.Message):
    __slots__ = ("rhel_host",)
    RHEL_HOST_FIELD_NUMBER: _ClassVar[int]
    rhel_host: _rhel_host_pb2.RhelHost
    def __init__(self, rhel_host: _Optional[_Union[_rhel_host_pb2.RhelHost, _Mapping]] = ...) -> None: ...

class CreateRhelHostResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UpdateRhelHostRequest(_message.Message):
    __slots__ = ("rhel_host",)
    RHEL_HOST_FIELD_NUMBER: _ClassVar[int]
    rhel_host: _rhel_host_pb2.RhelHost
    def __init__(self, rhel_host: _Optional[_Union[_rhel_host_pb2.RhelHost, _Mapping]] = ...) -> None: ...

class UpdateRhelHostResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteRhelHostRequest(_message.Message):
    __slots__ = ("reporter_data",)
    REPORTER_DATA_FIELD_NUMBER: _ClassVar[int]
    reporter_data: _reporter_data_pb2.ReporterData
    def __init__(self, reporter_data: _Optional[_Union[_reporter_data_pb2.ReporterData, _Mapping]] = ...) -> None: ...

class DeleteRhelHostResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
