
'Client and server classes corresponding to protobuf-defined services.'
import grpc
import warnings
from ..services import user_service_pb2 as services_dot_user__service__pb2
GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(((((f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in services/user_service_pb2_grpc.py depends on') + f' grpcio>={GRPC_GENERATED_VERSION}.') + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}') + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'))

class UserServiceStub(object):
    'Missing associated documentation comment in .proto file.'

    def __init__(self, channel):
        'Constructor.\n\n        Args:\n            channel: A grpc.Channel.\n        '
        self.GetUser = channel.unary_unary('/parrygg.services.UserService/GetUser', request_serializer=services_dot_user__service__pb2.GetUserRequest.SerializeToString, response_deserializer=services_dot_user__service__pb2.GetUserResponse.FromString, _registered_method=True)
        self.GetUsers = channel.unary_unary('/parrygg.services.UserService/GetUsers', request_serializer=services_dot_user__service__pb2.GetUsersRequest.SerializeToString, response_deserializer=services_dot_user__service__pb2.GetUsersResponse.FromString, _registered_method=True)
        self.UpdateUser = channel.unary_unary('/parrygg.services.UserService/UpdateUser', request_serializer=services_dot_user__service__pb2.UpdateUserRequest.SerializeToString, response_deserializer=services_dot_user__service__pb2.UpdateUserResponse.FromString, _registered_method=True)

class UserServiceServicer(object):
    'Missing associated documentation comment in .proto file.'

    def GetUser(self, request, context):
        'Retrieves a user by ID or Keycloak entity ID.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetUsers(self, request, context):
        'Retrieves multiple users based on filter criteria.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateUser(self, request, context):
        'Updates an existing user profile.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_UserServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetUser': grpc.unary_unary_rpc_method_handler(servicer.GetUser, request_deserializer=services_dot_user__service__pb2.GetUserRequest.FromString, response_serializer=services_dot_user__service__pb2.GetUserResponse.SerializeToString), 'GetUsers': grpc.unary_unary_rpc_method_handler(servicer.GetUsers, request_deserializer=services_dot_user__service__pb2.GetUsersRequest.FromString, response_serializer=services_dot_user__service__pb2.GetUsersResponse.SerializeToString), 'UpdateUser': grpc.unary_unary_rpc_method_handler(servicer.UpdateUser, request_deserializer=services_dot_user__service__pb2.UpdateUserRequest.FromString, response_serializer=services_dot_user__service__pb2.UpdateUserResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('parrygg.services.UserService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('parrygg.services.UserService', rpc_method_handlers)

class UserService(object):
    'Missing associated documentation comment in .proto file.'

    @staticmethod
    def GetUser(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.UserService/GetUser', services_dot_user__service__pb2.GetUserRequest.SerializeToString, services_dot_user__service__pb2.GetUserResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetUsers(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.UserService/GetUsers', services_dot_user__service__pb2.GetUsersRequest.SerializeToString, services_dot_user__service__pb2.GetUsersResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def UpdateUser(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.UserService/UpdateUser', services_dot_user__service__pb2.UpdateUserRequest.SerializeToString, services_dot_user__service__pb2.UpdateUserResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)
