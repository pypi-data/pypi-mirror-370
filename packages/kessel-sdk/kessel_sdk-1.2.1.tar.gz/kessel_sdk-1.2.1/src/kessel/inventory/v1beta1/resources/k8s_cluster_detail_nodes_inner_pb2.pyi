from buf.validate import validate_pb2 as _validate_pb2
from kessel.inventory.v1beta1.resources import resource_label_pb2 as _resource_label_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class K8sClusterDetailNodesInner(_message.Message):
    __slots__ = ("name", "cpu", "memory", "labels")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CPU_FIELD_NUMBER: _ClassVar[int]
    MEMORY_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    name: str
    cpu: str
    memory: str
    labels: _containers.RepeatedCompositeFieldContainer[_resource_label_pb2.ResourceLabel]
    def __init__(self, name: _Optional[str] = ..., cpu: _Optional[str] = ..., memory: _Optional[str] = ..., labels: _Optional[_Iterable[_Union[_resource_label_pb2.ResourceLabel, _Mapping]]] = ...) -> None: ...
