
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'models/phase.proto')
_sym_db = _symbol_database.Default()
from ..models import bracket_pb2 as models_dot_bracket__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12models/phase.proto\x12\x0eparrygg.models\x1a\x14models/bracket.proto"\xd5\x01\n\x05Phase\x12\n\n\x02id\x18\x01 \x01(\t\x12)\n\x08brackets\x18\x03 \x03(\x0b2\x17.parrygg.models.Bracket\x12\x15\n\rdefault_entry\x18\x04 \x01(\x08\x121\n\x0cbracket_type\x18\x05 \x01(\x0e2\x1b.parrygg.models.BracketType\x12\x0c\n\x04name\x18\x06 \x01(\t\x12)\n\x05state\x18\x07 \x01(\x0e2\x1a.parrygg.models.PhaseState\x12\x0c\n\x04slug\x18\x08 \x01(\tJ\x04\x08\x02\x10\x03"z\n\rPhaseMutation\x126\n\x0cbracket_type\x18\x02 \x01(\x0e2\x1b.parrygg.models.BracketTypeH\x00\x88\x01\x01\x12\x11\n\x04name\x18\x03 \x01(\tH\x01\x88\x01\x01B\x0f\n\r_bracket_typeB\x07\n\x05_nameJ\x04\x08\x01\x10\x02"N\n\x0bPhaseSlugId\x12\x17\n\x0ftournament_slug\x18\x01 \x01(\t\x12\x12\n\nevent_slug\x18\x02 \x01(\t\x12\x12\n\nphase_slug\x18\x03 \x01(\t"]\n\x0fPhaseIdentifier\x12\x0c\n\x02id\x18\x01 \x01(\tH\x00\x12.\n\x07slug_id\x18\x02 \x01(\x0b2\x1b.parrygg.models.PhaseSlugIdH\x00B\x0c\n\nidentifier*\x91\x01\n\nPhaseState\x12\x1b\n\x17PHASE_STATE_UNSPECIFIED\x10\x00\x12\x17\n\x13PHASE_STATE_PENDING\x10\x01\x12\x15\n\x11PHASE_STATE_READY\x10\x02\x12\x1b\n\x17PHASE_STATE_IN_PROGRESS\x10\x03\x12\x19\n\x15PHASE_STATE_COMPLETED\x10\x04B\x18\n\x14gg.parry.grpc.modelsP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'models.phase_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x14gg.parry.grpc.modelsP\x01'
    _globals['_PHASESTATE']._serialized_start = 576
    _globals['_PHASESTATE']._serialized_end = 721
    _globals['_PHASE']._serialized_start = 61
    _globals['_PHASE']._serialized_end = 274
    _globals['_PHASEMUTATION']._serialized_start = 276
    _globals['_PHASEMUTATION']._serialized_end = 398
    _globals['_PHASESLUGID']._serialized_start = 400
    _globals['_PHASESLUGID']._serialized_end = 478
    _globals['_PHASEIDENTIFIER']._serialized_start = 480
    _globals['_PHASEIDENTIFIER']._serialized_end = 573
