
'Client and server classes corresponding to protobuf-defined services.'
import grpc
import warnings
from ..services import page_content_service_pb2 as services_dot_page__content__service__pb2
GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(((((f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in services/page_content_service_pb2_grpc.py depends on') + f' grpcio>={GRPC_GENERATED_VERSION}.') + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}') + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'))

class PageContentServiceStub(object):
    'Missing associated documentation comment in .proto file.'

    def __init__(self, channel):
        'Constructor.\n\n        Args:\n            channel: A grpc.Channel.\n        '
        self.GetPageContents = channel.unary_unary('/parrygg.services.PageContentService/GetPageContents', request_serializer=services_dot_page__content__service__pb2.GetPageContentsRequest.SerializeToString, response_deserializer=services_dot_page__content__service__pb2.GetPageContentsResponse.FromString, _registered_method=True)
        self.CreatePageContent = channel.unary_unary('/parrygg.services.PageContentService/CreatePageContent', request_serializer=services_dot_page__content__service__pb2.CreatePageContentRequest.SerializeToString, response_deserializer=services_dot_page__content__service__pb2.CreatePageContentResponse.FromString, _registered_method=True)
        self.UpdatePageContent = channel.unary_unary('/parrygg.services.PageContentService/UpdatePageContent', request_serializer=services_dot_page__content__service__pb2.UpdatePageContentRequest.SerializeToString, response_deserializer=services_dot_page__content__service__pb2.UpdatePageContentResponse.FromString, _registered_method=True)
        self.DeletePageContent = channel.unary_unary('/parrygg.services.PageContentService/DeletePageContent', request_serializer=services_dot_page__content__service__pb2.DeletePageContentRequest.SerializeToString, response_deserializer=services_dot_page__content__service__pb2.DeletePageContentResponse.FromString, _registered_method=True)

class PageContentServiceServicer(object):
    'Missing associated documentation comment in .proto file.'

    def GetPageContents(self, request, context):
        'Retrieves all page contents for a tournament by ID or identifier.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreatePageContent(self, request, context):
        'Creates new page content for a tournament.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdatePageContent(self, request, context):
        'Updates existing page content by ID.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeletePageContent(self, request, context):
        'Deletes page content by ID.\n        '
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_PageContentServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetPageContents': grpc.unary_unary_rpc_method_handler(servicer.GetPageContents, request_deserializer=services_dot_page__content__service__pb2.GetPageContentsRequest.FromString, response_serializer=services_dot_page__content__service__pb2.GetPageContentsResponse.SerializeToString), 'CreatePageContent': grpc.unary_unary_rpc_method_handler(servicer.CreatePageContent, request_deserializer=services_dot_page__content__service__pb2.CreatePageContentRequest.FromString, response_serializer=services_dot_page__content__service__pb2.CreatePageContentResponse.SerializeToString), 'UpdatePageContent': grpc.unary_unary_rpc_method_handler(servicer.UpdatePageContent, request_deserializer=services_dot_page__content__service__pb2.UpdatePageContentRequest.FromString, response_serializer=services_dot_page__content__service__pb2.UpdatePageContentResponse.SerializeToString), 'DeletePageContent': grpc.unary_unary_rpc_method_handler(servicer.DeletePageContent, request_deserializer=services_dot_page__content__service__pb2.DeletePageContentRequest.FromString, response_serializer=services_dot_page__content__service__pb2.DeletePageContentResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('parrygg.services.PageContentService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('parrygg.services.PageContentService', rpc_method_handlers)

class PageContentService(object):
    'Missing associated documentation comment in .proto file.'

    @staticmethod
    def GetPageContents(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.PageContentService/GetPageContents', services_dot_page__content__service__pb2.GetPageContentsRequest.SerializeToString, services_dot_page__content__service__pb2.GetPageContentsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def CreatePageContent(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.PageContentService/CreatePageContent', services_dot_page__content__service__pb2.CreatePageContentRequest.SerializeToString, services_dot_page__content__service__pb2.CreatePageContentResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def UpdatePageContent(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.PageContentService/UpdatePageContent', services_dot_page__content__service__pb2.UpdatePageContentRequest.SerializeToString, services_dot_page__content__service__pb2.UpdatePageContentResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def DeletePageContent(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/parrygg.services.PageContentService/DeletePageContent', services_dot_page__content__service__pb2.DeletePageContentRequest.SerializeToString, services_dot_page__content__service__pb2.DeletePageContentResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)
