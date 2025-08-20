
'Client and server classes corresponding to protobuf-defined services.'
import grpc
import warnings
from ..services import hierarchy_service_pb2 as services_dot_hierarchy__service__pb2
GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(((((f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in services/hierarchy_service_pb2_grpc.py depends on') + f' grpcio>={GRPC_GENERATED_VERSION}.') + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}') + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'))

class HierarchyServiceStub(object):
    'Missing associated documentation comment in .proto file.'

    def __init__(self, channel):
        'Constructor.\n\n        Args:\n            channel: A grpc.Channel.\n        '
        self.GetEventHierarchy = channel.unary_unary('/parrygg.services.HierarchyService/GetEventHierarchy', request_serializer=services_dot_hierarchy__service__pb2.GetEventHierarchyRequest.SerializeToString, response_deserializer=services_dot_hierarchy__service__pb2.GetEventHierarchyResponse.FromString, _registered_method=True)
        self.GetPhaseHierarchy = channel.unary_unary('/parrygg.services.HierarchyService/GetPhaseHierarchy', request_serializer=services_dot_hierarchy__service__pb2.GetPhaseHierarchyRequest.SerializeToString, response_deserializer=services_dot_hierarchy__service__pb2.GetPhaseHierarchyResponse.FromString, _registered_method=True)
        self.GetBracketHierarchy = channel.unary_unary('/parrygg.services.HierarchyService/GetBracketHierarchy', request_serializer=services_dot_hierarchy__service__pb2.GetBracketHierarchyRequest.SerializeToString, response_deserializer=services_dot_hierarchy__service__pb2.GetBracketHierarchyResponse.FromString, _registered_method=True)

class HierarchyServiceServicer(object):
    'Missing associated documentation comment in .proto file.'

    def GetEventHierarchy(self, request, context):
        'Retrieves the complete hierarchy structure for an event by ID or slug path.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPhaseHierarchy(self, request, context):
        'Retrieves the complete hierarchy structure for a phase by ID or slug path.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetBracketHierarchy(self, request, context):
        'Retrieves the complete hierarchy structure for a bracket by ID or slug path.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_HierarchyServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetEventHierarchy': grpc.unary_unary_rpc_method_handler(servicer.GetEventHierarchy, request_deserializer=services_dot_hierarchy__service__pb2.GetEventHierarchyRequest.FromString, response_serializer=services_dot_hierarchy__service__pb2.GetEventHierarchyResponse.SerializeToString), 'GetPhaseHierarchy': grpc.unary_unary_rpc_method_handler(servicer.GetPhaseHierarchy, request_deserializer=services_dot_hierarchy__service__pb2.GetPhaseHierarchyRequest.FromString, response_serializer=services_dot_hierarchy__service__pb2.GetPhaseHierarchyResponse.SerializeToString), 'GetBracketHierarchy': grpc.unary_unary_rpc_method_handler(servicer.GetBracketHierarchy, request_deserializer=services_dot_hierarchy__service__pb2.GetBracketHierarchyRequest.FromString, response_serializer=services_dot_hierarchy__service__pb2.GetBracketHierarchyResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('parrygg.services.HierarchyService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('parrygg.services.HierarchyService', rpc_method_handlers)

class HierarchyService(object):
    'Missing associated documentation comment in .proto file.'

    @staticmethod
    def GetEventHierarchy(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.HierarchyService/GetEventHierarchy', services_dot_hierarchy__service__pb2.GetEventHierarchyRequest.SerializeToString, services_dot_hierarchy__service__pb2.GetEventHierarchyResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetPhaseHierarchy(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.HierarchyService/GetPhaseHierarchy', services_dot_hierarchy__service__pb2.GetPhaseHierarchyRequest.SerializeToString, services_dot_hierarchy__service__pb2.GetPhaseHierarchyResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetBracketHierarchy(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.HierarchyService/GetBracketHierarchy', services_dot_hierarchy__service__pb2.GetBracketHierarchyRequest.SerializeToString, services_dot_hierarchy__service__pb2.GetBracketHierarchyResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)
