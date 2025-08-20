from google.api import annotations_pb2 as _annotations_pb2
from buf.validate import validate_pb2 as _validate_pb2
from kessel.inventory.v1beta1.resources import k8s_policy_pb2 as _k8s_policy_pb2
from kessel.inventory.v1beta1.resources import reporter_data_pb2 as _reporter_data_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateK8sPolicyRequest(_message.Message):
    __slots__ = ("k8s_policy",)
    K8S_POLICY_FIELD_NUMBER: _ClassVar[int]
    k8s_policy: _k8s_policy_pb2.K8sPolicy
    def __init__(self, k8s_policy: _Optional[_Union[_k8s_policy_pb2.K8sPolicy, _Mapping]] = ...) -> None: ...

class CreateK8sPolicyResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UpdateK8sPolicyRequest(_message.Message):
    __slots__ = ("k8s_policy",)
    K8S_POLICY_FIELD_NUMBER: _ClassVar[int]
    k8s_policy: _k8s_policy_pb2.K8sPolicy
    def __init__(self, k8s_policy: _Optional[_Union[_k8s_policy_pb2.K8sPolicy, _Mapping]] = ...) -> None: ...

class UpdateK8sPolicyResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteK8sPolicyRequest(_message.Message):
    __slots__ = ("reporter_data",)
    REPORTER_DATA_FIELD_NUMBER: _ClassVar[int]
    reporter_data: _reporter_data_pb2.ReporterData
    def __init__(self, reporter_data: _Optional[_Union[_reporter_data_pb2.ReporterData, _Mapping]] = ...) -> None: ...

class DeleteK8sPolicyResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
