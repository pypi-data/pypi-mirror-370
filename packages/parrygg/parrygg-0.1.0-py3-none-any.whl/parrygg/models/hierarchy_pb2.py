
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'models/hierarchy.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16models/hierarchy.proto\x12\x0eparrygg.models"V\n\x04Path\x12\n\n\x02id\x18\x01 \x01(\t\x12&\n\x04type\x18\x02 \x01(\x0e2\x18.parrygg.models.PathType\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x0c\n\x04slug\x18\x04 \x01(\t"<\n\rEventSlugPath\x12\x17\n\x0ftournament_slug\x18\x01 \x01(\t\x12\x12\n\nevent_slug\x18\x02 \x01(\t"P\n\rPhaseSlugPath\x12\x17\n\x0ftournament_slug\x18\x01 \x01(\t\x12\x12\n\nevent_slug\x18\x02 \x01(\t\x12\x12\n\nphase_slug\x18\x03 \x01(\t"h\n\x0fBracketSlugPath\x12\x17\n\x0ftournament_slug\x18\x01 \x01(\t\x12\x12\n\nevent_slug\x18\x02 \x01(\t\x12\x12\n\nphase_slug\x18\x03 \x01(\t\x12\x14\n\x0cbracket_slug\x18\x04 \x01(\t"0\n\tHierarchy\x12#\n\x05paths\x18\x01 \x03(\x0b2\x14.parrygg.models.Path*e\n\x08PathType\x12\x18\n\x14PATH_TYPE_TOURNAMENT\x10\x00\x12\x13\n\x0fPATH_TYPE_EVENT\x10\x01\x12\x13\n\x0fPATH_TYPE_PHASE\x10\x02\x12\x15\n\x11PATH_TYPE_BRACKET\x10\x03B\x18\n\x14gg.parry.grpc.modelsP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'models.hierarchy_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x14gg.parry.grpc.modelsP\x01'
    _globals['_PATHTYPE']._serialized_start = 430
    _globals['_PATHTYPE']._serialized_end = 531
    _globals['_PATH']._serialized_start = 42
    _globals['_PATH']._serialized_end = 128
    _globals['_EVENTSLUGPATH']._serialized_start = 130
    _globals['_EVENTSLUGPATH']._serialized_end = 190
    _globals['_PHASESLUGPATH']._serialized_start = 192
    _globals['_PHASESLUGPATH']._serialized_end = 272
    _globals['_BRACKETSLUGPATH']._serialized_start = 274
    _globals['_BRACKETSLUGPATH']._serialized_end = 378
    _globals['_HIERARCHY']._serialized_start = 380
    _globals['_HIERARCHY']._serialized_end = 428
