from kessel.inventory.v1beta1.relationships import metadata_pb2 as _metadata_pb2
from kessel.inventory.v1beta1.relationships import reporter_data_pb2 as _reporter_data_pb2
from kessel.inventory.v1beta1.relationships import k8spolicy_ispropagatedto_k8scluster_detail_pb2 as _k8spolicy_ispropagatedto_k8scluster_detail_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class K8SPolicyIsPropagatedToK8SCluster(_message.Message):
    __slots__ = ("metadata", "reporter_data", "relationship_data")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    REPORTER_DATA_FIELD_NUMBER: _ClassVar[int]
    RELATIONSHIP_DATA_FIELD_NUMBER: _ClassVar[int]
    metadata: _metadata_pb2.Metadata
    reporter_data: _reporter_data_pb2.ReporterData
    relationship_data: _k8spolicy_ispropagatedto_k8scluster_detail_pb2.K8SPolicyIsPropagatedToK8SClusterDetail
    def __init__(self, metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ..., reporter_data: _Optional[_Union[_reporter_data_pb2.ReporterData, _Mapping]] = ..., relationship_data: _Optional[_Union[_k8spolicy_ispropagatedto_k8scluster_detail_pb2.K8SPolicyIsPropagatedToK8SClusterDetail, _Mapping]] = ...) -> None: ...
