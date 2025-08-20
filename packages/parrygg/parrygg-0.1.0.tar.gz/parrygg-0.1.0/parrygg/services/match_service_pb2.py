
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'services/match_service.proto')
_sym_db = _symbol_database.Default()
from ..models import bracket_pb2 as models_dot_bracket__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1cservices/match_service.proto\x12\x10parrygg.services\x1a\x14models/bracket.proto"\x1d\n\x0fGetMatchRequest\x12\n\n\x02id\x18\x01 \x01(\t"8\n\x10GetMatchResponse\x12$\n\x05match\x18\x01 \x01(\x0b2\x15.parrygg.models.Match"P\n\x15SetMatchResultRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12+\n\x06result\x18\x02 \x01(\x0b2\x1b.parrygg.models.MatchResult"\x18\n\x16SetMatchResultResponse"\x1f\n\x11ResetMatchRequest\x12\n\n\x02id\x18\x01 \x01(\t"\x14\n\x12ResetMatchResponse"\x1f\n\x11StartMatchRequest\x12\n\n\x02id\x18\x01 \x01(\t"\x14\n\x12StartMatchResponse2\x80\x03\n\x0cMatchService\x12S\n\x08GetMatch\x12!.parrygg.services.GetMatchRequest\x1a".parrygg.services.GetMatchResponse"\x00\x12e\n\x0eSetMatchResult\x12\'.parrygg.services.SetMatchResultRequest\x1a(.parrygg.services.SetMatchResultResponse"\x00\x12Y\n\nStartMatch\x12#.parrygg.services.StartMatchRequest\x1a$.parrygg.services.StartMatchResponse"\x00\x12Y\n\nResetMatch\x12#.parrygg.services.ResetMatchRequest\x1a$.parrygg.services.ResetMatchResponse"\x00B\x1a\n\x16gg.parry.grpc.servicesP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'services.match_service_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x16gg.parry.grpc.servicesP\x01'
    _globals['_GETMATCHREQUEST']._serialized_start = 72
    _globals['_GETMATCHREQUEST']._serialized_end = 101
    _globals['_GETMATCHRESPONSE']._serialized_start = 103
    _globals['_GETMATCHRESPONSE']._serialized_end = 159
    _globals['_SETMATCHRESULTREQUEST']._serialized_start = 161
    _globals['_SETMATCHRESULTREQUEST']._serialized_end = 241
    _globals['_SETMATCHRESULTRESPONSE']._serialized_start = 243
    _globals['_SETMATCHRESULTRESPONSE']._serialized_end = 267
    _globals['_RESETMATCHREQUEST']._serialized_start = 269
    _globals['_RESETMATCHREQUEST']._serialized_end = 300
    _globals['_RESETMATCHRESPONSE']._serialized_start = 302
    _globals['_RESETMATCHRESPONSE']._serialized_end = 322
    _globals['_STARTMATCHREQUEST']._serialized_start = 324
    _globals['_STARTMATCHREQUEST']._serialized_end = 355
    _globals['_STARTMATCHRESPONSE']._serialized_start = 357
    _globals['_STARTMATCHRESPONSE']._serialized_end = 377
    _globals['_MATCHSERVICE']._serialized_start = 380
    _globals['_MATCHSERVICE']._serialized_end = 764
