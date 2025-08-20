
'Client and server classes corresponding to protobuf-defined services.'
import grpc
import warnings
from ..services import bracket_service_pb2 as services_dot_bracket__service__pb2
GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(((((f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in services/bracket_service_pb2_grpc.py depends on') + f' grpcio>={GRPC_GENERATED_VERSION}.') + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}') + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'))

class BracketServiceStub(object):
    'BracketService provides tournament bracket management operations.\n    Handles bracket lifecycle, match progression, and final results.\n    '

    def __init__(self, channel):
        'Constructor.\n\n        Args:\n            channel: A grpc.Channel.\n        '
        self.GetBracket = channel.unary_unary('/parrygg.services.BracketService/GetBracket', request_serializer=services_dot_bracket__service__pb2.GetBracketRequest.SerializeToString, response_deserializer=services_dot_bracket__service__pb2.GetBracketResponse.FromString, _registered_method=True)
        self.GetBracketTimestamp = channel.unary_unary('/parrygg.services.BracketService/GetBracketTimestamp', request_serializer=services_dot_bracket__service__pb2.GetBracketTimestampRequest.SerializeToString, response_deserializer=services_dot_bracket__service__pb2.GetBracketTimestampResponse.FromString, _registered_method=True)
        self.ResetBracket = channel.unary_unary('/parrygg.services.BracketService/ResetBracket', request_serializer=services_dot_bracket__service__pb2.ResetBracketRequest.SerializeToString, response_deserializer=services_dot_bracket__service__pb2.ResetBracketResponse.FromString, _registered_method=True)
        self.GetBracketPlacements = channel.unary_unary('/parrygg.services.BracketService/GetBracketPlacements', request_serializer=services_dot_bracket__service__pb2.GetBracketPlacementsRequest.SerializeToString, response_deserializer=services_dot_bracket__service__pb2.GetBracketPlacementsResponse.FromString, _registered_method=True)
        self.StartBracket = channel.unary_unary('/parrygg.services.BracketService/StartBracket', request_serializer=services_dot_bracket__service__pb2.StartBracketRequest.SerializeToString, response_deserializer=services_dot_bracket__service__pb2.StartBracketResponse.FromString, _registered_method=True)

class BracketServiceServicer(object):
    'BracketService provides tournament bracket management operations.\n    Handles bracket lifecycle, match progression, and final results.\n    '

    def GetBracket(self, request, context):
        'Retrieve a bracket by ID or slug path.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetBracketTimestamp(self, request, context):
        'Get the last modification timestamp for a bracket.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ResetBracket(self, request, context):
        'Reset a bracket to initial state, clearing all matches.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetBracketPlacements(self, request, context):
        'Get final standings for a completed bracket.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StartBracket(self, request, context):
        'Start bracket competition and create initial matches.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_BracketServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetBracket': grpc.unary_unary_rpc_method_handler(servicer.GetBracket, request_deserializer=services_dot_bracket__service__pb2.GetBracketRequest.FromString, response_serializer=services_dot_bracket__service__pb2.GetBracketResponse.SerializeToString), 'GetBracketTimestamp': grpc.unary_unary_rpc_method_handler(servicer.GetBracketTimestamp, request_deserializer=services_dot_bracket__service__pb2.GetBracketTimestampRequest.FromString, response_serializer=services_dot_bracket__service__pb2.GetBracketTimestampResponse.SerializeToString), 'ResetBracket': grpc.unary_unary_rpc_method_handler(servicer.ResetBracket, request_deserializer=services_dot_bracket__service__pb2.ResetBracketRequest.FromString, response_serializer=services_dot_bracket__service__pb2.ResetBracketResponse.SerializeToString), 'GetBracketPlacements': grpc.unary_unary_rpc_method_handler(servicer.GetBracketPlacements, request_deserializer=services_dot_bracket__service__pb2.GetBracketPlacementsRequest.FromString, response_serializer=services_dot_bracket__service__pb2.GetBracketPlacementsResponse.SerializeToString), 'StartBracket': grpc.unary_unary_rpc_method_handler(servicer.StartBracket, request_deserializer=services_dot_bracket__service__pb2.StartBracketRequest.FromString, response_serializer=services_dot_bracket__service__pb2.StartBracketResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('parrygg.services.BracketService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('parrygg.services.BracketService', rpc_method_handlers)

class BracketService(object):
    'BracketService provides tournament bracket management operations.\n    Handles bracket lifecycle, match progression, and final results.\n    '

    @staticmethod
    def GetBracket(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.BracketService/GetBracket', services_dot_bracket__service__pb2.GetBracketRequest.SerializeToString, services_dot_bracket__service__pb2.GetBracketResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetBracketTimestamp(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.BracketService/GetBracketTimestamp', services_dot_bracket__service__pb2.GetBracketTimestampRequest.SerializeToString, services_dot_bracket__service__pb2.GetBracketTimestampResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def ResetBracket(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.BracketService/ResetBracket', services_dot_bracket__service__pb2.ResetBracketRequest.SerializeToString, services_dot_bracket__service__pb2.ResetBracketResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetBracketPlacements(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.BracketService/GetBracketPlacements', services_dot_bracket__service__pb2.GetBracketPlacementsRequest.SerializeToString, services_dot_bracket__service__pb2.GetBracketPlacementsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def StartBracket(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.BracketService/StartBracket', services_dot_bracket__service__pb2.StartBracketRequest.SerializeToString, services_dot_bracket__service__pb2.StartBracketResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)
