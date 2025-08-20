
'Client and server classes corresponding to protobuf-defined services.'
import grpc
import warnings
from ..services import event_service_pb2 as services_dot_event__service__pb2
GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(((((f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in services/event_service_pb2_grpc.py depends on') + f' grpcio>={GRPC_GENERATED_VERSION}.') + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}') + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'))

class EventServiceStub(object):
    'EventService provides tournament event management operations.\n    Handles event lifecycle, registration, and bracket administration.\n    '

    def __init__(self, channel):
        'Constructor.\n\n        Args:\n            channel: A grpc.Channel.\n        '
        self.GetEvent = channel.unary_unary('/parrygg.services.EventService/GetEvent', request_serializer=services_dot_event__service__pb2.GetEventRequest.SerializeToString, response_deserializer=services_dot_event__service__pb2.GetEventResponse.FromString, _registered_method=True)
        self.GetEvents = channel.unary_unary('/parrygg.services.EventService/GetEvents', request_serializer=services_dot_event__service__pb2.GetEventsRequest.SerializeToString, response_deserializer=services_dot_event__service__pb2.GetEventsResponse.FromString, _registered_method=True)
        self.GetEventPlacements = channel.unary_unary('/parrygg.services.EventService/GetEventPlacements', request_serializer=services_dot_event__service__pb2.GetEventPlacementsRequest.SerializeToString, response_deserializer=services_dot_event__service__pb2.GetEventPlacementsResponse.FromString, _registered_method=True)
        self.GetEventEntrants = channel.unary_unary('/parrygg.services.EventService/GetEventEntrants', request_serializer=services_dot_event__service__pb2.GetEventEntrantsRequest.SerializeToString, response_deserializer=services_dot_event__service__pb2.GetEventEntrantsResponse.FromString, _registered_method=True)
        self.ResetEvent = channel.unary_unary('/parrygg.services.EventService/ResetEvent', request_serializer=services_dot_event__service__pb2.ResetEventRequest.SerializeToString, response_deserializer=services_dot_event__service__pb2.ResetEventResponse.FromString, _registered_method=True)

class EventServiceServicer(object):
    'EventService provides tournament event management operations.\n    Handles event lifecycle, registration, and bracket administration.\n    '

    def GetEvent(self, request, context):
        'Retrieve a single event by ID.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetEvents(self, request, context):
        'List events matching filter criteria.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetEventPlacements(self, request, context):
        'Get final standings for a completed event.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetEventEntrants(self, request, context):
        'List all participants in an event.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ResetEvent(self, request, context):
        'Reset event brackets and matches to initial state.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_EventServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetEvent': grpc.unary_unary_rpc_method_handler(servicer.GetEvent, request_deserializer=services_dot_event__service__pb2.GetEventRequest.FromString, response_serializer=services_dot_event__service__pb2.GetEventResponse.SerializeToString), 'GetEvents': grpc.unary_unary_rpc_method_handler(servicer.GetEvents, request_deserializer=services_dot_event__service__pb2.GetEventsRequest.FromString, response_serializer=services_dot_event__service__pb2.GetEventsResponse.SerializeToString), 'GetEventPlacements': grpc.unary_unary_rpc_method_handler(servicer.GetEventPlacements, request_deserializer=services_dot_event__service__pb2.GetEventPlacementsRequest.FromString, response_serializer=services_dot_event__service__pb2.GetEventPlacementsResponse.SerializeToString), 'GetEventEntrants': grpc.unary_unary_rpc_method_handler(servicer.GetEventEntrants, request_deserializer=services_dot_event__service__pb2.GetEventEntrantsRequest.FromString, response_serializer=services_dot_event__service__pb2.GetEventEntrantsResponse.SerializeToString), 'ResetEvent': grpc.unary_unary_rpc_method_handler(servicer.ResetEvent, request_deserializer=services_dot_event__service__pb2.ResetEventRequest.FromString, response_serializer=services_dot_event__service__pb2.ResetEventResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('parrygg.services.EventService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('parrygg.services.EventService', rpc_method_handlers)

class EventService(object):
    'EventService provides tournament event management operations.\n    Handles event lifecycle, registration, and bracket administration.\n    '

    @staticmethod
    def GetEvent(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.EventService/GetEvent', services_dot_event__service__pb2.GetEventRequest.SerializeToString, services_dot_event__service__pb2.GetEventResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetEvents(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.EventService/GetEvents', services_dot_event__service__pb2.GetEventsRequest.SerializeToString, services_dot_event__service__pb2.GetEventsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetEventPlacements(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.EventService/GetEventPlacements', services_dot_event__service__pb2.GetEventPlacementsRequest.SerializeToString, services_dot_event__service__pb2.GetEventPlacementsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetEventEntrants(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.EventService/GetEventEntrants', services_dot_event__service__pb2.GetEventEntrantsRequest.SerializeToString, services_dot_event__service__pb2.GetEventEntrantsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def ResetEvent(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.EventService/ResetEvent', services_dot_event__service__pb2.ResetEventRequest.SerializeToString, services_dot_event__service__pb2.ResetEventResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)
