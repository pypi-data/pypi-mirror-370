
'Client and server classes corresponding to protobuf-defined services.'
import grpc
import warnings
from ..services import notification_service_pb2 as services_dot_notification__service__pb2
GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(((((f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in services/notification_service_pb2_grpc.py depends on') + f' grpcio>={GRPC_GENERATED_VERSION}.') + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}') + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'))

class NotificationServiceStub(object):
    'Missing associated documentation comment in .proto file.'

    def __init__(self, channel):
        'Constructor.\n\n        Args:\n            channel: A grpc.Channel.\n        '
        self.GetNotifications = channel.unary_unary('/parrygg.services.NotificationService/GetNotifications', request_serializer=services_dot_notification__service__pb2.GetNotificationsRequest.SerializeToString, response_deserializer=services_dot_notification__service__pb2.GetNotificationsResponse.FromString, _registered_method=True)

class NotificationServiceServicer(object):
    'Missing associated documentation comment in .proto file.'

    def GetNotifications(self, request, context):
        'Retrieves all notifications for a user.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_NotificationServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetNotifications': grpc.unary_unary_rpc_method_handler(servicer.GetNotifications, request_deserializer=services_dot_notification__service__pb2.GetNotificationsRequest.FromString, response_serializer=services_dot_notification__service__pb2.GetNotificationsResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('parrygg.services.NotificationService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('parrygg.services.NotificationService', rpc_method_handlers)

class NotificationService(object):
    'Missing associated documentation comment in .proto file.'

    @staticmethod
    def GetNotifications(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.NotificationService/GetNotifications', services_dot_notification__service__pb2.GetNotificationsRequest.SerializeToString, services_dot_notification__service__pb2.GetNotificationsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)
