
'Client and server classes corresponding to protobuf-defined services.'
import grpc
import warnings
from ..services import entrant_service_pb2 as services_dot_entrant__service__pb2
GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(((((f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in services/entrant_service_pb2_grpc.py depends on') + f' grpcio>={GRPC_GENERATED_VERSION}.') + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}') + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'))

class EntrantServiceStub(object):
    'Missing associated documentation comment in .proto file.'

    def __init__(self, channel):
        'Constructor.\n\n        Args:\n            channel: A grpc.Channel.\n        '
        self.GetEventEntrant = channel.unary_unary('/parrygg.services.EntrantService/GetEventEntrant', request_serializer=services_dot_entrant__service__pb2.GetEventEntrantRequest.SerializeToString, response_deserializer=services_dot_entrant__service__pb2.GetEventEntrantResponse.FromString, _registered_method=True)
        self.CreateEventEntrant = channel.unary_unary('/parrygg.services.EntrantService/CreateEventEntrant', request_serializer=services_dot_entrant__service__pb2.CreateEventEntrantRequest.SerializeToString, response_deserializer=services_dot_entrant__service__pb2.CreateEventEntrantResponse.FromString, _registered_method=True)
        self.UpdateEventEntrant = channel.unary_unary('/parrygg.services.EntrantService/UpdateEventEntrant', request_serializer=services_dot_entrant__service__pb2.UpdateEventEntrantRequest.SerializeToString, response_deserializer=services_dot_entrant__service__pb2.UpdateEventEntrantResponse.FromString, _registered_method=True)
        self.DeleteEventEntrant = channel.unary_unary('/parrygg.services.EntrantService/DeleteEventEntrant', request_serializer=services_dot_entrant__service__pb2.DeleteEventEntrantRequest.SerializeToString, response_deserializer=services_dot_entrant__service__pb2.DeleteEventEntrantResponse.FromString, _registered_method=True)
        self.RemoveFromEventEntrant = channel.unary_unary('/parrygg.services.EntrantService/RemoveFromEventEntrant', request_serializer=services_dot_entrant__service__pb2.RemoveFromEventEntrantRequest.SerializeToString, response_deserializer=services_dot_entrant__service__pb2.RemoveFromEventEntrantResponse.FromString, _registered_method=True)
        self.DisbandEventEntrant = channel.unary_unary('/parrygg.services.EntrantService/DisbandEventEntrant', request_serializer=services_dot_entrant__service__pb2.DisbandEventEntrantRequest.SerializeToString, response_deserializer=services_dot_entrant__service__pb2.DisbandEventEntrantResponse.FromString, _registered_method=True)
        self.CreateTeam = channel.unary_unary('/parrygg.services.EntrantService/CreateTeam', request_serializer=services_dot_entrant__service__pb2.CreateTeamRequest.SerializeToString, response_deserializer=services_dot_entrant__service__pb2.CreateTeamResponse.FromString, _registered_method=True)
        self.UpdateTeam = channel.unary_unary('/parrygg.services.EntrantService/UpdateTeam', request_serializer=services_dot_entrant__service__pb2.UpdateTeamRequest.SerializeToString, response_deserializer=services_dot_entrant__service__pb2.UpdateTeamResponse.FromString, _registered_method=True)

class EntrantServiceServicer(object):
    'Missing associated documentation comment in .proto file.'

    def GetEventEntrant(self, request, context):
        'Missing associated documentation comment in .proto file.'
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateEventEntrant(self, request, context):
        'Missing associated documentation comment in .proto file.'
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateEventEntrant(self, request, context):
        'Missing associated documentation comment in .proto file.'
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteEventEntrant(self, request, context):
        'Missing associated documentation comment in .proto file.'
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RemoveFromEventEntrant(self, request, context):
        'Missing associated documentation comment in .proto file.'
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DisbandEventEntrant(self, request, context):
        'Missing associated documentation comment in .proto file.'
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateTeam(self, request, context):
        'Missing associated documentation comment in .proto file.'
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateTeam(self, request, context):
        'Missing associated documentation comment in .proto file.'
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_EntrantServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetEventEntrant': grpc.unary_unary_rpc_method_handler(servicer.GetEventEntrant, request_deserializer=services_dot_entrant__service__pb2.GetEventEntrantRequest.FromString, response_serializer=services_dot_entrant__service__pb2.GetEventEntrantResponse.SerializeToString), 'CreateEventEntrant': grpc.unary_unary_rpc_method_handler(servicer.CreateEventEntrant, request_deserializer=services_dot_entrant__service__pb2.CreateEventEntrantRequest.FromString, response_serializer=services_dot_entrant__service__pb2.CreateEventEntrantResponse.SerializeToString), 'UpdateEventEntrant': grpc.unary_unary_rpc_method_handler(servicer.UpdateEventEntrant, request_deserializer=services_dot_entrant__service__pb2.UpdateEventEntrantRequest.FromString, response_serializer=services_dot_entrant__service__pb2.UpdateEventEntrantResponse.SerializeToString), 'DeleteEventEntrant': grpc.unary_unary_rpc_method_handler(servicer.DeleteEventEntrant, request_deserializer=services_dot_entrant__service__pb2.DeleteEventEntrantRequest.FromString, response_serializer=services_dot_entrant__service__pb2.DeleteEventEntrantResponse.SerializeToString), 'RemoveFromEventEntrant': grpc.unary_unary_rpc_method_handler(servicer.RemoveFromEventEntrant, request_deserializer=services_dot_entrant__service__pb2.RemoveFromEventEntrantRequest.FromString, response_serializer=services_dot_entrant__service__pb2.RemoveFromEventEntrantResponse.SerializeToString), 'DisbandEventEntrant': grpc.unary_unary_rpc_method_handler(servicer.DisbandEventEntrant, request_deserializer=services_dot_entrant__service__pb2.DisbandEventEntrantRequest.FromString, response_serializer=services_dot_entrant__service__pb2.DisbandEventEntrantResponse.SerializeToString), 'CreateTeam': grpc.unary_unary_rpc_method_handler(servicer.CreateTeam, request_deserializer=services_dot_entrant__service__pb2.CreateTeamRequest.FromString, response_serializer=services_dot_entrant__service__pb2.CreateTeamResponse.SerializeToString), 'UpdateTeam': grpc.unary_unary_rpc_method_handler(servicer.UpdateTeam, request_deserializer=services_dot_entrant__service__pb2.UpdateTeamRequest.FromString, response_serializer=services_dot_entrant__service__pb2.UpdateTeamResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('parrygg.services.EntrantService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('parrygg.services.EntrantService', rpc_method_handlers)

class EntrantService(object):
    'Missing associated documentation comment in .proto file.'

    @staticmethod
    def GetEventEntrant(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.EntrantService/GetEventEntrant', services_dot_entrant__service__pb2.GetEventEntrantRequest.SerializeToString, services_dot_entrant__service__pb2.GetEventEntrantResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def CreateEventEntrant(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.EntrantService/CreateEventEntrant', services_dot_entrant__service__pb2.CreateEventEntrantRequest.SerializeToString, services_dot_entrant__service__pb2.CreateEventEntrantResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def UpdateEventEntrant(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.EntrantService/UpdateEventEntrant', services_dot_entrant__service__pb2.UpdateEventEntrantRequest.SerializeToString, services_dot_entrant__service__pb2.UpdateEventEntrantResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def DeleteEventEntrant(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.EntrantService/DeleteEventEntrant', services_dot_entrant__service__pb2.DeleteEventEntrantRequest.SerializeToString, services_dot_entrant__service__pb2.DeleteEventEntrantResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def RemoveFromEventEntrant(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.EntrantService/RemoveFromEventEntrant', services_dot_entrant__service__pb2.RemoveFromEventEntrantRequest.SerializeToString, services_dot_entrant__service__pb2.RemoveFromEventEntrantResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def DisbandEventEntrant(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.EntrantService/DisbandEventEntrant', services_dot_entrant__service__pb2.DisbandEventEntrantRequest.SerializeToString, services_dot_entrant__service__pb2.DisbandEventEntrantResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def CreateTeam(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.EntrantService/CreateTeam', services_dot_entrant__service__pb2.CreateTeamRequest.SerializeToString, services_dot_entrant__service__pb2.CreateTeamResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def UpdateTeam(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.EntrantService/UpdateTeam', services_dot_entrant__service__pb2.UpdateTeamRequest.SerializeToString, services_dot_entrant__service__pb2.UpdateTeamResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)
