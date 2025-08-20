from google.api import field_behavior_pb2 as _field_behavior_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class K8SPolicyIsPropagatedToK8SClusterDetail(_message.Message):
    __slots__ = ("k8s_policy_id", "k8s_cluster_id", "status")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNSPECIFIED: _ClassVar[K8SPolicyIsPropagatedToK8SClusterDetail.Status]
        STATUS_OTHER: _ClassVar[K8SPolicyIsPropagatedToK8SClusterDetail.Status]
        VIOLATIONS: _ClassVar[K8SPolicyIsPropagatedToK8SClusterDetail.Status]
        NO_VIOLATIONS: _ClassVar[K8SPolicyIsPropagatedToK8SClusterDetail.Status]
    STATUS_UNSPECIFIED: K8SPolicyIsPropagatedToK8SClusterDetail.Status
    STATUS_OTHER: K8SPolicyIsPropagatedToK8SClusterDetail.Status
    VIOLATIONS: K8SPolicyIsPropagatedToK8SClusterDetail.Status
    NO_VIOLATIONS: K8SPolicyIsPropagatedToK8SClusterDetail.Status
    K8S_POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    K8S_CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    k8s_policy_id: str
    k8s_cluster_id: str
    status: K8SPolicyIsPropagatedToK8SClusterDetail.Status
    def __init__(self, k8s_policy_id: _Optional[str] = ..., k8s_cluster_id: _Optional[str] = ..., status: _Optional[_Union[K8SPolicyIsPropagatedToK8SClusterDetail.Status, str]] = ...) -> None: ...
