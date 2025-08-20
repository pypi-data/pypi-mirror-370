
'Client and server classes corresponding to protobuf-defined services.'
import grpc
import warnings
from ..services import game_service_pb2 as services_dot_game__service__pb2
GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(((((f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in services/game_service_pb2_grpc.py depends on') + f' grpcio>={GRPC_GENERATED_VERSION}.') + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}') + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'))

class GameServiceStub(object):
    'GameService provides game management operations.\n    Handles game metadata, creation, and external database integration.\n    '

    def __init__(self, channel):
        'Constructor.\n\n        Args:\n            channel: A grpc.Channel.\n        '
        self.GetGames = channel.unary_unary('/parrygg.services.GameService/GetGames', request_serializer=services_dot_game__service__pb2.GetGamesRequest.SerializeToString, response_deserializer=services_dot_game__service__pb2.GetGamesResponse.FromString, _registered_method=True)

class GameServiceServicer(object):
    'GameService provides game management operations.\n    Handles game metadata, creation, and external database integration.\n    '

    def GetGames(self, request, context):
        'List all available games for tournaments.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_GameServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetGames': grpc.unary_unary_rpc_method_handler(servicer.GetGames, request_deserializer=services_dot_game__service__pb2.GetGamesRequest.FromString, response_serializer=services_dot_game__service__pb2.GetGamesResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('parrygg.services.GameService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('parrygg.services.GameService', rpc_method_handlers)

class GameService(object):
    'GameService provides game management operations.\n    Handles game metadata, creation, and external database integration.\n    '

    @staticmethod
    def GetGames(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.GameService/GetGames', services_dot_game__service__pb2.GetGamesRequest.SerializeToString, services_dot_game__service__pb2.GetGamesResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)
