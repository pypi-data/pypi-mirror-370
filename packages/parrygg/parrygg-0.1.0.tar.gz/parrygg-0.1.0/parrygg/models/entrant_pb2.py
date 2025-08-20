
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'models/entrant.proto')
_sym_db = _symbol_database.Default()
from ..models import request_pb2 as models_dot_request__pb2
from ..models import user_pb2 as models_dot_user__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14models/entrant.proto\x12\x0eparrygg.models\x1a\x14models/request.proto\x1a\x11models/user.proto":\n\x07Entrant\x12\n\n\x02id\x18\x01 \x01(\t\x12#\n\x05users\x18\x02 \x03(\x0b2\x14.parrygg.models.User"\xa0\x01\n\x0cEventEntrant\x12\x10\n\x08event_id\x18\x01 \x01(\t\x12(\n\x07entrant\x18\x02 \x01(\x0b2\x17.parrygg.models.Entrant\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\n\n\x02id\x18\x04 \x01(\t\x12:\n\x11teammate_requests\x18\x05 \x03(\x0b2\x1f.parrygg.models.TeammateRequest"2\n\x14EventEntrantMutation\x12\x11\n\x04name\x18\x01 \x01(\tH\x00\x88\x01\x01B\x07\n\x05_name"<\n\x0cTeamMutation\x12\x10\n\x08user_ids\x18\x01 \x03(\t\x12\x11\n\x04name\x18\x02 \x01(\tH\x00\x88\x01\x01B\x07\n\x05_name"q\n\tPlacement\x123\n\revent_entrant\x18\x01 \x01(\x0b2\x1c.parrygg.models.EventEntrant\x12\x11\n\tplacement\x18\x02 \x01(\x05\x12\x0c\n\x04wins\x18\x03 \x01(\x05\x12\x0e\n\x06losses\x18\x04 \x01(\x05B\x18\n\x14gg.parry.grpc.modelsP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'models.entrant_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x14gg.parry.grpc.modelsP\x01'
    _globals['_ENTRANT']._serialized_start = 81
    _globals['_ENTRANT']._serialized_end = 139
    _globals['_EVENTENTRANT']._serialized_start = 142
    _globals['_EVENTENTRANT']._serialized_end = 302
    _globals['_EVENTENTRANTMUTATION']._serialized_start = 304
    _globals['_EVENTENTRANTMUTATION']._serialized_end = 354
    _globals['_TEAMMUTATION']._serialized_start = 356
    _globals['_TEAMMUTATION']._serialized_end = 416
    _globals['_PLACEMENT']._serialized_start = 418
    _globals['_PLACEMENT']._serialized_end = 531
