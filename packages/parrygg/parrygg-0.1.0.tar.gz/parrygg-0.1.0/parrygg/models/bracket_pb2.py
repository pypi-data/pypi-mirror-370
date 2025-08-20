
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'models/bracket.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from ..models import entrant_pb2 as models_dot_entrant__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14models/bracket.proto\x12\x0eparrygg.models\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x14models/entrant.proto"\xda\x02\n\x07Bracket\x12\n\n\x02id\x18\x01 \x01(\t\x12+\n\x05state\x18\x02 \x01(\x0e2\x1c.parrygg.models.BracketState\x12&\n\x07matches\x18\x03 \x03(\x0b2\x15.parrygg.models.Match\x121\n\x0cprogressions\x18\x04 \x03(\x0b2\x1b.parrygg.models.Progression\x12\r\n\x05index\x18\x05 \x01(\x05\x12#\n\x05seeds\x18\x06 \x03(\x0b2\x14.parrygg.models.Seed\x12.\n\nupdated_at\x18\x07 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x0c\n\x04name\x18\x08 \x01(\t\x12\x0c\n\x04slug\x18\t \x01(\t\x12\x10\n\x08checksum\x18\n \x01(\t\x12)\n\x04type\x18\x0b \x01(\x0e2\x1b.parrygg.models.BracketType"\xb2\x03\n\x05Match\x12\n\n\x02id\x18\x01 \x01(\t\x12\x12\n\nidentifier\x18\x02 \x01(\t\x12\r\n\x05round\x18\x05 \x01(\x05\x12\x14\n\x0cwinners_side\x18\x06 \x01(\x08\x12\x14\n\x0cgrand_finals\x18\x07 \x01(\x08\x12\x1c\n\x0fprev_match_id_1\x18\x08 \x01(\tH\x00\x88\x01\x01\x12\x1c\n\x0fprev_match_id_2\x18\t \x01(\tH\x01\x88\x01\x01\x12\x1d\n\x10winners_match_id\x18\n \x01(\tH\x02\x88\x01\x01\x12\x1c\n\x0flosers_match_id\x18\x0b \x01(\tH\x03\x88\x01\x01\x12)\n\x05state\x18\x0c \x01(\x0e2\x1a.parrygg.models.MatchState\x12#\n\x05slots\x18\r \x03(\x0b2\x14.parrygg.models.Slot\x124\n\x10state_updated_at\x18\x0e \x01(\x0b2\x1a.google.protobuf.TimestampB\x12\n\x10_prev_match_id_1B\x12\n\x10_prev_match_id_2B\x13\n\x11_winners_match_idB\x12\n\x10_losers_match_id"E\n\x0bMatchResult\x126\n\x05slots\x18\x01 \x03(\x0b2\'.parrygg.models.MatchResultSlotMutation"~\n\x17MatchResultSlotMutation\x12\x0c\n\x04slot\x18\x01 \x01(\x05\x12\x12\n\x05score\x18\x02 \x01(\x01H\x00\x88\x01\x01\x12-\n\x05state\x18\x03 \x01(\x0e2\x19.parrygg.models.SlotStateH\x01\x88\x01\x01B\x08\n\x06_scoreB\x08\n\x06_state"\xb0\x01\n\x0bProgression\x12\n\n\x02id\x18\x01 \x01(\t\x12\x10\n\x08match_id\x18\x02 \x01(\t\x12\x17\n\x0ftarget_phase_id\x18\x03 \x01(\t\x12\x0f\n\x07seed_id\x18\x04 \x01(\t\x12\x18\n\x10origin_placement\x18\x05 \x01(\x05\x12\x13\n\x0borigin_seed\x18\x06 \x01(\x05\x12\x14\n\x0cmatch_winner\x18\x07 \x01(\x08\x12\x14\n\x0cwinners_side\x18\x08 \x01(\x08"q\n\x04Slot\x12\x0c\n\x04slot\x18\x01 \x01(\x05\x12\x0f\n\x07seed_id\x18\x02 \x01(\t\x12\x11\n\tplacement\x18\x03 \x01(\x05\x12\r\n\x05score\x18\x04 \x01(\x01\x12(\n\x05state\x18\x05 \x01(\x0e2\x19.parrygg.models.SlotState"U\n\x04Seed\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04seed\x18\x02 \x01(\x05\x123\n\revent_entrant\x18\x03 \x01(\x0b2\x1c.parrygg.models.EventEntrant"*\n\x0cSeedMutation\x12\x11\n\x04seed\x18\x02 \x01(\x05H\x00\x88\x01\x01B\x07\n\x05_seed"f\n\rBracketSlugId\x12\x17\n\x0ftournament_slug\x18\x01 \x01(\t\x12\x12\n\nevent_slug\x18\x02 \x01(\t\x12\x12\n\nphase_slug\x18\x03 \x01(\t\x12\x14\n\x0cbracket_slug\x18\x04 \x01(\t*\x93\x01\n\x0bBracketType\x12\x1c\n\x18BRACKET_TYPE_UNSPECIFIED\x10\x00\x12#\n\x1fBRACKET_TYPE_SINGLE_ELIMINATION\x10\x01\x12#\n\x1fBRACKET_TYPE_DOUBLE_ELIMINATION\x10\x02\x12\x1c\n\x18BRACKET_TYPE_ROUND_ROBIN\x10\x03*\x9d\x01\n\x0cBracketState\x12\x1d\n\x19BRACKET_STATE_UNSPECIFIED\x10\x00\x12\x19\n\x15BRACKET_STATE_PENDING\x10\x01\x12\x17\n\x13BRACKET_STATE_READY\x10\x02\x12\x1d\n\x19BRACKET_STATE_IN_PROGRESS\x10\x03\x12\x1b\n\x17BRACKET_STATE_COMPLETED\x10\x04*\x91\x01\n\nMatchState\x12\x1b\n\x17MATCH_STATE_UNSPECIFIED\x10\x00\x12\x17\n\x13MATCH_STATE_PENDING\x10\x01\x12\x15\n\x11MATCH_STATE_READY\x10\x02\x12\x1b\n\x17MATCH_STATE_IN_PROGRESS\x10\x03\x12\x19\n\x15MATCH_STATE_COMPLETED\x10\x04*\xac\x01\n\x13ProgressionBehavior\x12$\n PROGRESSION_BEHAVIOR_UNSPECIFIED\x10\x00\x12 \n\x1cPROGRESSION_BEHAVIOR_NATURAL\x10\x01\x12&\n"PROGRESSION_BEHAVIOR_FORCE_WINNERS\x10\x02\x12%\n!PROGRESSION_BEHAVIOR_FORCE_LOSERS\x10\x03*~\n\tSlotState\x12\x1a\n\x16SLOT_STATE_UNSPECIFIED\x10\x00\x12\x16\n\x12SLOT_STATE_PENDING\x10\x01\x12\x16\n\x12SLOT_STATE_NUMERIC\x10\x02\x12\x11\n\rSLOT_STATE_DQ\x10\x03\x12\x12\n\x0eSLOT_STATE_BYE\x10\x04B\x18\n\x14gg.parry.grpc.modelsP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'models.bracket_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x14gg.parry.grpc.modelsP\x01'
    _globals['_BRACKETTYPE']._serialized_start = 1610
    _globals['_BRACKETTYPE']._serialized_end = 1757
    _globals['_BRACKETSTATE']._serialized_start = 1760
    _globals['_BRACKETSTATE']._serialized_end = 1917
    _globals['_MATCHSTATE']._serialized_start = 1920
    _globals['_MATCHSTATE']._serialized_end = 2065
    _globals['_PROGRESSIONBEHAVIOR']._serialized_start = 2068
    _globals['_PROGRESSIONBEHAVIOR']._serialized_end = 2240
    _globals['_SLOTSTATE']._serialized_start = 2242
    _globals['_SLOTSTATE']._serialized_end = 2368
    _globals['_BRACKET']._serialized_start = 96
    _globals['_BRACKET']._serialized_end = 442
    _globals['_MATCH']._serialized_start = 445
    _globals['_MATCH']._serialized_end = 879
    _globals['_MATCHRESULT']._serialized_start = 881
    _globals['_MATCHRESULT']._serialized_end = 950
    _globals['_MATCHRESULTSLOTMUTATION']._serialized_start = 952
    _globals['_MATCHRESULTSLOTMUTATION']._serialized_end = 1078
    _globals['_PROGRESSION']._serialized_start = 1081
    _globals['_PROGRESSION']._serialized_end = 1257
    _globals['_SLOT']._serialized_start = 1259
    _globals['_SLOT']._serialized_end = 1372
    _globals['_SEED']._serialized_start = 1374
    _globals['_SEED']._serialized_end = 1459
    _globals['_SEEDMUTATION']._serialized_start = 1461
    _globals['_SEEDMUTATION']._serialized_end = 1503
    _globals['_BRACKETSLUGID']._serialized_start = 1505
    _globals['_BRACKETSLUGID']._serialized_end = 1607
