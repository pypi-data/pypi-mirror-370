
'Client and server classes corresponding to protobuf-defined services.'
import grpc
import warnings
from ..services import phase_service_pb2 as services_dot_phase__service__pb2
GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(((((f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in services/phase_service_pb2_grpc.py depends on') + f' grpcio>={GRPC_GENERATED_VERSION}.') + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}') + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'))

class PhaseServiceStub(object):
    'Missing associated documentation comment in .proto file.'

    def __init__(self, channel):
        'Constructor.\n\n        Args:\n            channel: A grpc.Channel.\n        '
        self.GetPhase = channel.unary_unary('/parrygg.services.PhaseService/GetPhase', request_serializer=services_dot_phase__service__pb2.GetPhaseRequest.SerializeToString, response_deserializer=services_dot_phase__service__pb2.GetPhaseResponse.FromString, _registered_method=True)
        self.GetPhasePlacements = channel.unary_unary('/parrygg.services.PhaseService/GetPhasePlacements', request_serializer=services_dot_phase__service__pb2.GetPhasePlacementsRequest.SerializeToString, response_deserializer=services_dot_phase__service__pb2.GetPhasePlacementsResponse.FromString, _registered_method=True)

class PhaseServiceServicer(object):
    'Missing associated documentation comment in .proto file.'

    def GetPhase(self, request, context):
        'Retrieves a phase by ID or slug identifier.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPhasePlacements(self, request, context):
        'Retrieves final placements for participants in a completed phase.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_PhaseServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetPhase': grpc.unary_unary_rpc_method_handler(servicer.GetPhase, request_deserializer=services_dot_phase__service__pb2.GetPhaseRequest.FromString, response_serializer=services_dot_phase__service__pb2.GetPhaseResponse.SerializeToString), 'GetPhasePlacements': grpc.unary_unary_rpc_method_handler(servicer.GetPhasePlacements, request_deserializer=services_dot_phase__service__pb2.GetPhasePlacementsRequest.FromString, response_serializer=services_dot_phase__service__pb2.GetPhasePlacementsResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('parrygg.services.PhaseService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('parrygg.services.PhaseService', rpc_method_handlers)

class PhaseService(object):
    'Missing associated documentation comment in .proto file.'

    @staticmethod
    def GetPhase(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.PhaseService/GetPhase', services_dot_phase__service__pb2.GetPhaseRequest.SerializeToString, services_dot_phase__service__pb2.GetPhaseResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetPhasePlacements(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.PhaseService/GetPhasePlacements', services_dot_phase__service__pb2.GetPhasePlacementsRequest.SerializeToString, services_dot_phase__service__pb2.GetPhasePlacementsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)
