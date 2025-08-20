
'Client and server classes corresponding to protobuf-defined services.'
import grpc
import warnings
from ..services import tournament_service_pb2 as services_dot_tournament__service__pb2
GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(((((f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in services/tournament_service_pb2_grpc.py depends on') + f' grpcio>={GRPC_GENERATED_VERSION}.') + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}') + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'))

class TournamentServiceStub(object):
    'Missing associated documentation comment in .proto file.'

    def __init__(self, channel):
        'Constructor.\n\n        Args:\n            channel: A grpc.Channel.\n        '
        self.GetTournament = channel.unary_unary('/parrygg.services.TournamentService/GetTournament', request_serializer=services_dot_tournament__service__pb2.GetTournamentRequest.SerializeToString, response_deserializer=services_dot_tournament__service__pb2.GetTournamentResponse.FromString, _registered_method=True)
        self.GetTournaments = channel.unary_unary('/parrygg.services.TournamentService/GetTournaments', request_serializer=services_dot_tournament__service__pb2.GetTournamentsRequest.SerializeToString, response_deserializer=services_dot_tournament__service__pb2.GetTournamentsResponse.FromString, _registered_method=True)
        self.GetTournamentAttendees = channel.unary_unary('/parrygg.services.TournamentService/GetTournamentAttendees', request_serializer=services_dot_tournament__service__pb2.GetTournamentAttendeesRequest.SerializeToString, response_deserializer=services_dot_tournament__service__pb2.GetTournamentAttendeesResponse.FromString, _registered_method=True)
        self.UpdateTournament = channel.unary_unary('/parrygg.services.TournamentService/UpdateTournament', request_serializer=services_dot_tournament__service__pb2.UpdateTournamentRequest.SerializeToString, response_deserializer=services_dot_tournament__service__pb2.UpdateTournamentResponse.FromString, _registered_method=True)

class TournamentServiceServicer(object):
    'Missing associated documentation comment in .proto file.'

    def GetTournament(self, request, context):
        'Retrieves a tournament by ID or slug.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTournaments(self, request, context):
        'Retrieves multiple tournaments based on filter criteria.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTournamentAttendees(self, request, context):
        'Retrieves all attendees for a tournament.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateTournament(self, request, context):
        'Updates an existing tournament by ID.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_TournamentServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetTournament': grpc.unary_unary_rpc_method_handler(servicer.GetTournament, request_deserializer=services_dot_tournament__service__pb2.GetTournamentRequest.FromString, response_serializer=services_dot_tournament__service__pb2.GetTournamentResponse.SerializeToString), 'GetTournaments': grpc.unary_unary_rpc_method_handler(servicer.GetTournaments, request_deserializer=services_dot_tournament__service__pb2.GetTournamentsRequest.FromString, response_serializer=services_dot_tournament__service__pb2.GetTournamentsResponse.SerializeToString), 'GetTournamentAttendees': grpc.unary_unary_rpc_method_handler(servicer.GetTournamentAttendees, request_deserializer=services_dot_tournament__service__pb2.GetTournamentAttendeesRequest.FromString, response_serializer=services_dot_tournament__service__pb2.GetTournamentAttendeesResponse.SerializeToString), 'UpdateTournament': grpc.unary_unary_rpc_method_handler(servicer.UpdateTournament, request_deserializer=services_dot_tournament__service__pb2.UpdateTournamentRequest.FromString, response_serializer=services_dot_tournament__service__pb2.UpdateTournamentResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('parrygg.services.TournamentService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('parrygg.services.TournamentService', rpc_method_handlers)

class TournamentService(object):
    'Missing associated documentation comment in .proto file.'

    @staticmethod
    def GetTournament(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.TournamentService/GetTournament', services_dot_tournament__service__pb2.GetTournamentRequest.SerializeToString, services_dot_tournament__service__pb2.GetTournamentResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetTournaments(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.TournamentService/GetTournaments', services_dot_tournament__service__pb2.GetTournamentsRequest.SerializeToString, services_dot_tournament__service__pb2.GetTournamentsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetTournamentAttendees(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.TournamentService/GetTournamentAttendees', services_dot_tournament__service__pb2.GetTournamentAttendeesRequest.SerializeToString, services_dot_tournament__service__pb2.GetTournamentAttendeesResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def UpdateTournament(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.TournamentService/UpdateTournament', services_dot_tournament__service__pb2.UpdateTournamentRequest.SerializeToString, services_dot_tournament__service__pb2.UpdateTournamentResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)
