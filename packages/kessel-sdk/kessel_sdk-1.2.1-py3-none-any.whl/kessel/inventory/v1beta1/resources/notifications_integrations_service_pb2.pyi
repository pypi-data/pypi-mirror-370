from google.api import annotations_pb2 as _annotations_pb2
from buf.validate import validate_pb2 as _validate_pb2
from kessel.inventory.v1beta1.authz import common_pb2 as _common_pb2
from kessel.inventory.v1beta1.resources import notifications_integration_pb2 as _notifications_integration_pb2
from kessel.inventory.v1beta1.resources import reporter_data_pb2 as _reporter_data_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateNotificationsIntegrationRequest(_message.Message):
    __slots__ = ("integration",)
    INTEGRATION_FIELD_NUMBER: _ClassVar[int]
    integration: _notifications_integration_pb2.NotificationsIntegration
    def __init__(self, integration: _Optional[_Union[_notifications_integration_pb2.NotificationsIntegration, _Mapping]] = ...) -> None: ...

class CreateNotificationsIntegrationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UpdateNotificationsIntegrationRequest(_message.Message):
    __slots__ = ("integration",)
    INTEGRATION_FIELD_NUMBER: _ClassVar[int]
    integration: _notifications_integration_pb2.NotificationsIntegration
    def __init__(self, integration: _Optional[_Union[_notifications_integration_pb2.NotificationsIntegration, _Mapping]] = ...) -> None: ...

class UpdateNotificationsIntegrationsRequest(_message.Message):
    __slots__ = ("integration",)
    INTEGRATION_FIELD_NUMBER: _ClassVar[int]
    integration: _notifications_integration_pb2.NotificationsIntegration
    def __init__(self, integration: _Optional[_Union[_notifications_integration_pb2.NotificationsIntegration, _Mapping]] = ...) -> None: ...

class UpdateNotificationsIntegrationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UpdateNotificationsIntegrationsResponse(_message.Message):
    __slots__ = ("upserts_completed",)
    UPSERTS_COMPLETED_FIELD_NUMBER: _ClassVar[int]
    upserts_completed: int
    def __init__(self, upserts_completed: _Optional[int] = ...) -> None: ...

class DeleteNotificationsIntegrationRequest(_message.Message):
    __slots__ = ("reporter_data",)
    REPORTER_DATA_FIELD_NUMBER: _ClassVar[int]
    reporter_data: _reporter_data_pb2.ReporterData
    def __init__(self, reporter_data: _Optional[_Union[_reporter_data_pb2.ReporterData, _Mapping]] = ...) -> None: ...

class DeleteNotificationsIntegrationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListNotificationsIntegrationsRequest(_message.Message):
    __slots__ = ("resource_type", "relation", "subject", "parent")
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    PARENT_FIELD_NUMBER: _ClassVar[int]
    resource_type: _common_pb2.ObjectType
    relation: str
    subject: _common_pb2.SubjectReference
    parent: _common_pb2.ObjectReference
    def __init__(self, resource_type: _Optional[_Union[_common_pb2.ObjectType, _Mapping]] = ..., relation: _Optional[str] = ..., subject: _Optional[_Union[_common_pb2.SubjectReference, _Mapping]] = ..., parent: _Optional[_Union[_common_pb2.ObjectReference, _Mapping]] = ...) -> None: ...

class ListNotificationsIntegrationsResponse(_message.Message):
    __slots__ = ("integrations",)
    INTEGRATIONS_FIELD_NUMBER: _ClassVar[int]
    integrations: _notifications_integration_pb2.NotificationsIntegration
    def __init__(self, integrations: _Optional[_Union[_notifications_integration_pb2.NotificationsIntegration, _Mapping]] = ...) -> None: ...
