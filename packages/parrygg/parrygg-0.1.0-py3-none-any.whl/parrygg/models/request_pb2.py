
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'models/request.proto')
_sym_db = _symbol_database.Default()
from ..models import user_pb2 as models_dot_user__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14models/request.proto\x12\x0eparrygg.models\x1a\x11models/user.proto"\xb1\x01\n\x07Request\x12\n\n\x02id\x18\x01 \x01(\t\x12\x14\n\x0cfrom_user_id\x18\x02 \x01(\t\x12\x12\n\nto_user_id\x18\x03 \x01(\t\x12+\n\x05state\x18\x04 \x01(\x0e2\x1c.parrygg.models.RequestState\x12;\n\x10teammate_request\x18\x05 \x01(\x0b2\x1f.parrygg.models.TeammateRequestH\x00B\x06\n\x04type"\x88\x01\n\x0fRequestCreation\x12\x14\n\x0cfrom_user_id\x18\x02 \x01(\t\x12\x12\n\nto_user_id\x18\x03 \x01(\t\x12C\n\x10teammate_request\x18\x05 \x01(\x0b2\'.parrygg.models.TeammateRequestCreationH\x00B\x06\n\x04type">\n\x0fRequestMutation\x12+\n\x05state\x18\x01 \x01(\x0e2\x1c.parrygg.models.RequestState"{\n\x0fTeammateRequest\x12\x18\n\x10event_entrant_id\x18\x01 \x01(\t\x12%\n\x07to_user\x18\x02 \x01(\x0b2\x14.parrygg.models.User\x12\'\n\tfrom_user\x18\x03 \x01(\x0b2\x14.parrygg.models.User"3\n\x17TeammateRequestCreation\x12\x18\n\x10event_entrant_id\x18\x01 \x01(\t*\x80\x01\n\x0cRequestState\x12\x1d\n\x19REQUEST_STATE_UNSPECIFIED\x10\x00\x12\x19\n\x15REQUEST_STATE_PENDING\x10\x01\x12\x1a\n\x16REQUEST_STATE_ACCEPTED\x10\x02\x12\x1a\n\x16REQUEST_STATE_REJECTED\x10\x03B\x18\n\x14gg.parry.grpc.modelsP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'models.request_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x14gg.parry.grpc.modelsP\x01'
    _globals['_REQUESTSTATE']._serialized_start = 621
    _globals['_REQUESTSTATE']._serialized_end = 749
    _globals['_REQUEST']._serialized_start = 60
    _globals['_REQUEST']._serialized_end = 237
    _globals['_REQUESTCREATION']._serialized_start = 240
    _globals['_REQUESTCREATION']._serialized_end = 376
    _globals['_REQUESTMUTATION']._serialized_start = 378
    _globals['_REQUESTMUTATION']._serialized_end = 440
    _globals['_TEAMMATEREQUEST']._serialized_start = 442
    _globals['_TEAMMATEREQUEST']._serialized_end = 565
    _globals['_TEAMMATEREQUESTCREATION']._serialized_start = 567
    _globals['_TEAMMATEREQUESTCREATION']._serialized_end = 618
