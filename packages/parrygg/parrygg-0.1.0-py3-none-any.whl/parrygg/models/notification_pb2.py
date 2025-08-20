
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'models/notification.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from ..models import request_pb2 as models_dot_request__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19models/notification.proto\x12\x0eparrygg.models\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x14models/request.proto"Y\n\x16NotificationPreference\x12.\n\x04type\x18\x01 \x01(\x0e2 .parrygg.models.NotificationType\x12\x0f\n\x07enabled\x18\x02 \x01(\x08"\x89\x01\n\x0cNotification\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04body\x18\x02 \x01(\t\x125\n\x0edelivery_state\x18\x03 \x01(\x0e2\x1d.parrygg.models.DeliveryState\x12(\n\x07request\x18\x04 \x01(\x0b2\x17.parrygg.models.Request"M\n\x14NotificationMutation\x125\n\x0edelivery_state\x18\x01 \x01(\x0e2\x1d.parrygg.models.DeliveryState*\xd5\x01\n\x10NotificationType\x12!\n\x1dNOTIFICATION_TYPE_UNSPECIFIED\x10\x00\x12\x1d\n\x19NOTIFICATION_TYPE_ACCOUNT\x10\x01\x12\x1f\n\x1bNOTIFICATION_TYPE_ORGANIZER\x10\x02\x12\x1e\n\x1aNOTIFICATION_TYPE_ATTENDEE\x10\x03\x12\x1d\n\x19NOTIFICATION_TYPE_ENTRANT\x10\x04\x12\x1f\n\x1bNOTIFICATION_TYPE_SPECTATOR\x10\x05*\xb7\x01\n\rDeliveryState\x12\x1e\n\x1aDELIVERY_STATE_UNSPECIFIED\x10\x00\x12\x19\n\x15DELIVERY_STATE_UNSENT\x10\x01\x12\x17\n\x13DELIVERY_STATE_SENT\x10\x02\x12\x1b\n\x17DELIVERY_STATE_RECEIVED\x10\x03\x12\x1c\n\x18DELIVERY_STATE_DISMISSED\x10\x04\x12\x17\n\x13DELIVERY_STATE_SEEN\x10\x05B\x18\n\x14gg.parry.grpc.modelsP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'models.notification_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x14gg.parry.grpc.modelsP\x01'
    _globals['_NOTIFICATIONTYPE']._serialized_start = 411
    _globals['_NOTIFICATIONTYPE']._serialized_end = 624
    _globals['_DELIVERYSTATE']._serialized_start = 627
    _globals['_DELIVERYSTATE']._serialized_end = 810
    _globals['_NOTIFICATIONPREFERENCE']._serialized_start = 100
    _globals['_NOTIFICATIONPREFERENCE']._serialized_end = 189
    _globals['_NOTIFICATION']._serialized_start = 192
    _globals['_NOTIFICATION']._serialized_end = 329
    _globals['_NOTIFICATIONMUTATION']._serialized_start = 331
    _globals['_NOTIFICATIONMUTATION']._serialized_end = 408
