
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'services/notification_service.proto')
_sym_db = _symbol_database.Default()
from ..models import notification_pb2 as models_dot_notification__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#services/notification_service.proto\x12\x10parrygg.services\x1a\x19models/notification.proto"*\n\x17GetNotificationsRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t"O\n\x18GetNotificationsResponse\x123\n\rnotifications\x18\x01 \x03(\x0b2\x1c.parrygg.models.Notification2\x82\x01\n\x13NotificationService\x12k\n\x10GetNotifications\x12).parrygg.services.GetNotificationsRequest\x1a*.parrygg.services.GetNotificationsResponse"\x00B\x1a\n\x16gg.parry.grpc.servicesP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'services.notification_service_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x16gg.parry.grpc.servicesP\x01'
    _globals['_GETNOTIFICATIONSREQUEST']._serialized_start = 84
    _globals['_GETNOTIFICATIONSREQUEST']._serialized_end = 126
    _globals['_GETNOTIFICATIONSRESPONSE']._serialized_start = 128
    _globals['_GETNOTIFICATIONSRESPONSE']._serialized_end = 207
    _globals['_NOTIFICATIONSERVICE']._serialized_start = 210
    _globals['_NOTIFICATIONSERVICE']._serialized_end = 340
