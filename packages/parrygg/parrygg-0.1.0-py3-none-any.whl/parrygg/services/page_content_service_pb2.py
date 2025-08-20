
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'services/page_content_service.proto')
_sym_db = _symbol_database.Default()
from ..models import tournament_pb2 as models_dot_tournament__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#services/page_content_service.proto\x12\x10parrygg.services\x1a\x17models/tournament.proto"t\n\x16GetPageContentsRequest\x12\x15\n\rtournament_id\x18\x01 \x01(\t\x12C\n\x15tournament_identifier\x18\x02 \x01(\x0b2$.parrygg.models.TournamentIdentifier"M\n\x17GetPageContentsResponse\x122\n\rpage_contents\x18\x01 \x03(\x0b2\x1b.parrygg.models.PageContent"k\n\x18CreatePageContentRequest\x12\x15\n\rtournament_id\x18\x01 \x01(\t\x128\n\x0cpage_content\x18\x02 \x01(\x0b2".parrygg.models.MutablePageContent"N\n\x19CreatePageContentResponse\x121\n\x0cpage_content\x18\x01 \x01(\x0b2\x1b.parrygg.models.PageContent"`\n\x18UpdatePageContentRequest\x12\n\n\x02id\x18\x01 \x01(\t\x128\n\x0cpage_content\x18\x02 \x01(\x0b2".parrygg.models.MutablePageContent"Z\n\x19UpdatePageContentResponse\x12\n\n\x02id\x18\x01 \x01(\t\x121\n\x0cpage_content\x18\x02 \x01(\x0b2\x1b.parrygg.models.PageContent"&\n\x18DeletePageContentRequest\x12\n\n\x02id\x18\x01 \x01(\t"N\n\x19DeletePageContentResponse\x121\n\x0cpage_content\x18\x01 \x01(\x0b2\x1b.parrygg.models.PageContent2\xce\x03\n\x12PageContentService\x12h\n\x0fGetPageContents\x12(.parrygg.services.GetPageContentsRequest\x1a).parrygg.services.GetPageContentsResponse"\x00\x12n\n\x11CreatePageContent\x12*.parrygg.services.CreatePageContentRequest\x1a+.parrygg.services.CreatePageContentResponse"\x00\x12n\n\x11UpdatePageContent\x12*.parrygg.services.UpdatePageContentRequest\x1a+.parrygg.services.UpdatePageContentResponse"\x00\x12n\n\x11DeletePageContent\x12*.parrygg.services.DeletePageContentRequest\x1a+.parrygg.services.DeletePageContentResponse"\x00B\x1a\n\x16gg.parry.grpc.servicesP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'services.page_content_service_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x16gg.parry.grpc.servicesP\x01'
    _globals['_GETPAGECONTENTSREQUEST']._serialized_start = 82
    _globals['_GETPAGECONTENTSREQUEST']._serialized_end = 198
    _globals['_GETPAGECONTENTSRESPONSE']._serialized_start = 200
    _globals['_GETPAGECONTENTSRESPONSE']._serialized_end = 277
    _globals['_CREATEPAGECONTENTREQUEST']._serialized_start = 279
    _globals['_CREATEPAGECONTENTREQUEST']._serialized_end = 386
    _globals['_CREATEPAGECONTENTRESPONSE']._serialized_start = 388
    _globals['_CREATEPAGECONTENTRESPONSE']._serialized_end = 466
    _globals['_UPDATEPAGECONTENTREQUEST']._serialized_start = 468
    _globals['_UPDATEPAGECONTENTREQUEST']._serialized_end = 564
    _globals['_UPDATEPAGECONTENTRESPONSE']._serialized_start = 566
    _globals['_UPDATEPAGECONTENTRESPONSE']._serialized_end = 656
    _globals['_DELETEPAGECONTENTREQUEST']._serialized_start = 658
    _globals['_DELETEPAGECONTENTREQUEST']._serialized_end = 696
    _globals['_DELETEPAGECONTENTRESPONSE']._serialized_start = 698
    _globals['_DELETEPAGECONTENTRESPONSE']._serialized_end = 776
    _globals['_PAGECONTENTSERVICE']._serialized_start = 779
    _globals['_PAGECONTENTSERVICE']._serialized_end = 1241
