from kessel.inventory.v1beta1.resources import k8s_cluster_detail_nodes_inner_pb2 as _k8s_cluster_detail_nodes_inner_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class K8sClusterDetail(_message.Message):
    __slots__ = ("external_cluster_id", "cluster_status", "cluster_reason", "kube_version", "kube_vendor", "vendor_version", "cloud_platform", "nodes")
    class ClusterStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CLUSTER_STATUS_UNSPECIFIED: _ClassVar[K8sClusterDetail.ClusterStatus]
        CLUSTER_STATUS_OTHER: _ClassVar[K8sClusterDetail.ClusterStatus]
        READY: _ClassVar[K8sClusterDetail.ClusterStatus]
        FAILED: _ClassVar[K8sClusterDetail.ClusterStatus]
        OFFLINE: _ClassVar[K8sClusterDetail.ClusterStatus]
    CLUSTER_STATUS_UNSPECIFIED: K8sClusterDetail.ClusterStatus
    CLUSTER_STATUS_OTHER: K8sClusterDetail.ClusterStatus
    READY: K8sClusterDetail.ClusterStatus
    FAILED: K8sClusterDetail.ClusterStatus
    OFFLINE: K8sClusterDetail.ClusterStatus
    class KubeVendor(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KUBE_VENDOR_UNSPECIFIED: _ClassVar[K8sClusterDetail.KubeVendor]
        KUBE_VENDOR_OTHER: _ClassVar[K8sClusterDetail.KubeVendor]
        AKS: _ClassVar[K8sClusterDetail.KubeVendor]
        EKS: _ClassVar[K8sClusterDetail.KubeVendor]
        IKS: _ClassVar[K8sClusterDetail.KubeVendor]
        OPENSHIFT: _ClassVar[K8sClusterDetail.KubeVendor]
        GKE: _ClassVar[K8sClusterDetail.KubeVendor]
    KUBE_VENDOR_UNSPECIFIED: K8sClusterDetail.KubeVendor
    KUBE_VENDOR_OTHER: K8sClusterDetail.KubeVendor
    AKS: K8sClusterDetail.KubeVendor
    EKS: K8sClusterDetail.KubeVendor
    IKS: K8sClusterDetail.KubeVendor
    OPENSHIFT: K8sClusterDetail.KubeVendor
    GKE: K8sClusterDetail.KubeVendor
    class CloudPlatform(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CLOUD_PLATFORM_UNSPECIFIED: _ClassVar[K8sClusterDetail.CloudPlatform]
        CLOUD_PLATFORM_OTHER: _ClassVar[K8sClusterDetail.CloudPlatform]
        NONE_UPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        BAREMETAL_IPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        BAREMETAL_UPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        AWS_IPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        AWS_UPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        AZURE_IPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        AZURE_UPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        IBMCLOUD_IPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        IBMCLOUD_UPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        KUBEVIRT_IPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        OPENSTACK_IPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        OPENSTACK_UPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        GCP_IPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        GCP_UPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        NUTANIX_IPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        NUTANIX_UPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        VSPHERE_IPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        VSPHERE_UPI: _ClassVar[K8sClusterDetail.CloudPlatform]
        OVIRT_IPI: _ClassVar[K8sClusterDetail.CloudPlatform]
    CLOUD_PLATFORM_UNSPECIFIED: K8sClusterDetail.CloudPlatform
    CLOUD_PLATFORM_OTHER: K8sClusterDetail.CloudPlatform
    NONE_UPI: K8sClusterDetail.CloudPlatform
    BAREMETAL_IPI: K8sClusterDetail.CloudPlatform
    BAREMETAL_UPI: K8sClusterDetail.CloudPlatform
    AWS_IPI: K8sClusterDetail.CloudPlatform
    AWS_UPI: K8sClusterDetail.CloudPlatform
    AZURE_IPI: K8sClusterDetail.CloudPlatform
    AZURE_UPI: K8sClusterDetail.CloudPlatform
    IBMCLOUD_IPI: K8sClusterDetail.CloudPlatform
    IBMCLOUD_UPI: K8sClusterDetail.CloudPlatform
    KUBEVIRT_IPI: K8sClusterDetail.CloudPlatform
    OPENSTACK_IPI: K8sClusterDetail.CloudPlatform
    OPENSTACK_UPI: K8sClusterDetail.CloudPlatform
    GCP_IPI: K8sClusterDetail.CloudPlatform
    GCP_UPI: K8sClusterDetail.CloudPlatform
    NUTANIX_IPI: K8sClusterDetail.CloudPlatform
    NUTANIX_UPI: K8sClusterDetail.CloudPlatform
    VSPHERE_IPI: K8sClusterDetail.CloudPlatform
    VSPHERE_UPI: K8sClusterDetail.CloudPlatform
    OVIRT_IPI: K8sClusterDetail.CloudPlatform
    EXTERNAL_CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_STATUS_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_REASON_FIELD_NUMBER: _ClassVar[int]
    KUBE_VERSION_FIELD_NUMBER: _ClassVar[int]
    KUBE_VENDOR_FIELD_NUMBER: _ClassVar[int]
    VENDOR_VERSION_FIELD_NUMBER: _ClassVar[int]
    CLOUD_PLATFORM_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    external_cluster_id: str
    cluster_status: K8sClusterDetail.ClusterStatus
    cluster_reason: str
    kube_version: str
    kube_vendor: K8sClusterDetail.KubeVendor
    vendor_version: str
    cloud_platform: K8sClusterDetail.CloudPlatform
    nodes: _containers.RepeatedCompositeFieldContainer[_k8s_cluster_detail_nodes_inner_pb2.K8sClusterDetailNodesInner]
    def __init__(self, external_cluster_id: _Optional[str] = ..., cluster_status: _Optional[_Union[K8sClusterDetail.ClusterStatus, str]] = ..., cluster_reason: _Optional[str] = ..., kube_version: _Optional[str] = ..., kube_vendor: _Optional[_Union[K8sClusterDetail.KubeVendor, str]] = ..., vendor_version: _Optional[str] = ..., cloud_platform: _Optional[_Union[K8sClusterDetail.CloudPlatform, str]] = ..., nodes: _Optional[_Iterable[_Union[_k8s_cluster_detail_nodes_inner_pb2.K8sClusterDetailNodesInner, _Mapping]]] = ...) -> None: ...
