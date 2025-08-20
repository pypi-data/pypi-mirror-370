
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'services/bracket_service.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from ..models import bracket_pb2 as models_dot_bracket__pb2
from ..models import entrant_pb2 as models_dot_entrant__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1eservices/bracket_service.proto\x12\x10parrygg.services\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x14models/bracket.proto\x1a\x14models/entrant.proto"a\n\x11GetBracketRequest\x12\x0c\n\x02id\x18\x01 \x01(\tH\x00\x120\n\x07slug_id\x18\x02 \x01(\x0b2\x1d.parrygg.models.BracketSlugIdH\x00B\x0c\n\nidentifier">\n\x12GetBracketResponse\x12(\n\x07bracket\x18\x01 \x01(\x0b2\x17.parrygg.models.Bracket"(\n\x1aGetBracketTimestampRequest\x12\n\n\x02id\x18\x01 \x01(\t"M\n\x1bGetBracketTimestampResponse\x12.\n\nupdated_at\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp"!\n\x13ResetBracketRequest\x12\n\n\x02id\x18\x01 \x01(\t"\x16\n\x14ResetBracketResponse")\n\x1bGetBracketPlacementsRequest\x12\n\n\x02id\x18\x01 \x01(\t"M\n\x1cGetBracketPlacementsResponse\x12-\n\nplacements\x18\x01 \x03(\x0b2\x19.parrygg.models.Placement"!\n\x13StartBracketRequest\x12\n\n\x02id\x18\x01 \x01(\t"@\n\x14StartBracketResponse\x12(\n\x07bracket\x18\x01 \x01(\x0b2\x17.parrygg.models.Bracket2\x9c\x04\n\x0eBracketService\x12Y\n\nGetBracket\x12#.parrygg.services.GetBracketRequest\x1a$.parrygg.services.GetBracketResponse"\x00\x12t\n\x13GetBracketTimestamp\x12,.parrygg.services.GetBracketTimestampRequest\x1a-.parrygg.services.GetBracketTimestampResponse"\x00\x12_\n\x0cResetBracket\x12%.parrygg.services.ResetBracketRequest\x1a&.parrygg.services.ResetBracketResponse"\x00\x12w\n\x14GetBracketPlacements\x12-.parrygg.services.GetBracketPlacementsRequest\x1a..parrygg.services.GetBracketPlacementsResponse"\x00\x12_\n\x0cStartBracket\x12%.parrygg.services.StartBracketRequest\x1a&.parrygg.services.StartBracketResponse"\x00B\x1a\n\x16gg.parry.grpc.servicesP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'services.bracket_service_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x16gg.parry.grpc.servicesP\x01'
    _globals['_GETBRACKETREQUEST']._serialized_start = 129
    _globals['_GETBRACKETREQUEST']._serialized_end = 226
    _globals['_GETBRACKETRESPONSE']._serialized_start = 228
    _globals['_GETBRACKETRESPONSE']._serialized_end = 290
    _globals['_GETBRACKETTIMESTAMPREQUEST']._serialized_start = 292
    _globals['_GETBRACKETTIMESTAMPREQUEST']._serialized_end = 332
    _globals['_GETBRACKETTIMESTAMPRESPONSE']._serialized_start = 334
    _globals['_GETBRACKETTIMESTAMPRESPONSE']._serialized_end = 411
    _globals['_RESETBRACKETREQUEST']._serialized_start = 413
    _globals['_RESETBRACKETREQUEST']._serialized_end = 446
    _globals['_RESETBRACKETRESPONSE']._serialized_start = 448
    _globals['_RESETBRACKETRESPONSE']._serialized_end = 470
    _globals['_GETBRACKETPLACEMENTSREQUEST']._serialized_start = 472
    _globals['_GETBRACKETPLACEMENTSREQUEST']._serialized_end = 513
    _globals['_GETBRACKETPLACEMENTSRESPONSE']._serialized_start = 515
    _globals['_GETBRACKETPLACEMENTSRESPONSE']._serialized_end = 592
    _globals['_STARTBRACKETREQUEST']._serialized_start = 594
    _globals['_STARTBRACKETREQUEST']._serialized_end = 627
    _globals['_STARTBRACKETRESPONSE']._serialized_start = 629
    _globals['_STARTBRACKETRESPONSE']._serialized_end = 693
    _globals['_BRACKETSERVICE']._serialized_start = 696
    _globals['_BRACKETSERVICE']._serialized_end = 1236
