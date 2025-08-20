
'Client and server classes corresponding to protobuf-defined services.'
import grpc
import warnings
from ..services import match_service_pb2 as services_dot_match__service__pb2
GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(((((f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in services/match_service_pb2_grpc.py depends on') + f' grpcio>={GRPC_GENERATED_VERSION}.') + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}') + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'))

class MatchServiceStub(object):
    'MatchService provides tournament match management operations.\n    Handles match lifecycle, scoring, and result reporting.\n    '

    def __init__(self, channel):
        'Constructor.\n\n        Args:\n            channel: A grpc.Channel.\n        '
        self.GetMatch = channel.unary_unary('/parrygg.services.MatchService/GetMatch', request_serializer=services_dot_match__service__pb2.GetMatchRequest.SerializeToString, response_deserializer=services_dot_match__service__pb2.GetMatchResponse.FromString, _registered_method=True)
        self.SetMatchResult = channel.unary_unary('/parrygg.services.MatchService/SetMatchResult', request_serializer=services_dot_match__service__pb2.SetMatchResultRequest.SerializeToString, response_deserializer=services_dot_match__service__pb2.SetMatchResultResponse.FromString, _registered_method=True)
        self.StartMatch = channel.unary_unary('/parrygg.services.MatchService/StartMatch', request_serializer=services_dot_match__service__pb2.StartMatchRequest.SerializeToString, response_deserializer=services_dot_match__service__pb2.StartMatchResponse.FromString, _registered_method=True)
        self.ResetMatch = channel.unary_unary('/parrygg.services.MatchService/ResetMatch', request_serializer=services_dot_match__service__pb2.ResetMatchRequest.SerializeToString, response_deserializer=services_dot_match__service__pb2.ResetMatchResponse.FromString, _registered_method=True)

class MatchServiceServicer(object):
    'MatchService provides tournament match management operations.\n    Handles match lifecycle, scoring, and result reporting.\n    '

    def GetMatch(self, request, context):
        'Retrieve a specific match by ID.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetMatchResult(self, request, context):
        'Update match results and participant scores.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StartMatch(self, request, context):
        'Start a match and change state to in-progress.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ResetMatch(self, request, context):
        'Reset a match to initial state, clearing results.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_MatchServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetMatch': grpc.unary_unary_rpc_method_handler(servicer.GetMatch, request_deserializer=services_dot_match__service__pb2.GetMatchRequest.FromString, response_serializer=services_dot_match__service__pb2.GetMatchResponse.SerializeToString), 'SetMatchResult': grpc.unary_unary_rpc_method_handler(servicer.SetMatchResult, request_deserializer=services_dot_match__service__pb2.SetMatchResultRequest.FromString, response_serializer=services_dot_match__service__pb2.SetMatchResultResponse.SerializeToString), 'StartMatch': grpc.unary_unary_rpc_method_handler(servicer.StartMatch, request_deserializer=services_dot_match__service__pb2.StartMatchRequest.FromString, response_serializer=services_dot_match__service__pb2.StartMatchResponse.SerializeToString), 'ResetMatch': grpc.unary_unary_rpc_method_handler(servicer.ResetMatch, request_deserializer=services_dot_match__service__pb2.ResetMatchRequest.FromString, response_serializer=services_dot_match__service__pb2.ResetMatchResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('parrygg.services.MatchService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('parrygg.services.MatchService', rpc_method_handlers)

class MatchService(object):
    'MatchService provides tournament match management operations.\n    Handles match lifecycle, scoring, and result reporting.\n    '

    @staticmethod
    def GetMatch(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.MatchService/GetMatch', services_dot_match__service__pb2.GetMatchRequest.SerializeToString, services_dot_match__service__pb2.GetMatchResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def SetMatchResult(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.MatchService/SetMatchResult', services_dot_match__service__pb2.SetMatchResultRequest.SerializeToString, services_dot_match__service__pb2.SetMatchResultResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def StartMatch(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.MatchService/StartMatch', services_dot_match__service__pb2.StartMatchRequest.SerializeToString, services_dot_match__service__pb2.StartMatchResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def ResetMatch(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.MatchService/ResetMatch', services_dot_match__service__pb2.ResetMatchRequest.SerializeToString, services_dot_match__service__pb2.ResetMatchResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)
