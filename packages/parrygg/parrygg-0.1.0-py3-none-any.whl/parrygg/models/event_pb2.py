
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'models/event.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from ..models import entrant_pb2 as models_dot_entrant__pb2
from ..models import game_pb2 as models_dot_game__pb2
from ..models import hierarchy_pb2 as models_dot_hierarchy__pb2
from ..models import phase_pb2 as models_dot_phase__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12models/event.proto\x12\x0eparrygg.models\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x14models/entrant.proto\x1a\x11models/game.proto\x1a\x16models/hierarchy.proto\x1a\x12models/phase.proto"\x92\x03\n\x05Event\x12\n\n\x02id\x18\x01 \x01(\t\x12\x15\n\rtournament_id\x18\x02 \x01(\t\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x16\n\x0edescription_md\x18\x04 \x01(\t\x12.\n\nstart_date\x18\x05 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12;\n\x17registration_close_time\x18\x06 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\r\n\x05price\x18\x07 \x01(\x05\x12\x13\n\x0bentrant_cap\x18\x08 \x01(\x05\x12\x14\n\x0centrant_size\x18\t \x01(\x05\x12"\n\x04game\x18\n \x01(\x0b2\x14.parrygg.models.Game\x12%\n\x06phases\x18\x0b \x03(\x0b2\x15.parrygg.models.Phase\x12)\n\x05state\x18\x0c \x01(\x0e2\x1a.parrygg.models.EventState\x12\x0c\n\x04slug\x18\r \x01(\t\x12\x15\n\rentrant_count\x18\x0e \x01(\x05"\x93\x03\n\rEventMutation\x12\x11\n\x04name\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x1b\n\x0edescription_md\x18\x02 \x01(\tH\x01\x88\x01\x01\x123\n\nstart_date\x18\x03 \x01(\x0b2\x1a.google.protobuf.TimestampH\x02\x88\x01\x01\x12@\n\x17registration_close_time\x18\x04 \x01(\x0b2\x1a.google.protobuf.TimestampH\x03\x88\x01\x01\x12\x12\n\x05price\x18\x05 \x01(\x05H\x04\x88\x01\x01\x12\x18\n\x0bentrant_cap\x18\x06 \x01(\x05H\x05\x88\x01\x01\x12\x19\n\x0centrant_size\x18\x07 \x01(\x05H\x06\x88\x01\x01\x12\x14\n\x07game_id\x18\x08 \x01(\tH\x07\x88\x01\x01B\x07\n\x05_nameB\x11\n\x0f_description_mdB\r\n\x0b_start_dateB\x1a\n\x18_registration_close_timeB\x08\n\x06_priceB\x0e\n\x0c_entrant_capB\x0f\n\r_entrant_sizeB\n\n\x08_game_id"\x97\x01\n\x11EventRegistration\x12\x10\n\x08event_id\x18\x01 \x01(\t\x12\x0f\n\x07user_id\x18\x02 \x01(\t\x12\x16\n\x0epaid_event_fee\x18\x03 \x01(\x08\x12\x12\n\nregistered\x18\x04 \x01(\x08\x123\n\revent_entrant\x18\x05 \x01(\x0b2\x1c.parrygg.models.EventEntrant"#\n\x0fEventAttendance\x12\x10\n\x08event_id\x18\x01 \x01(\t"\x85\x01\n\x19EventRegistrationMutation\x12\x10\n\x08event_id\x18\x01 \x01(\t\x12\x1b\n\x0epaid_event_fee\x18\x02 \x01(\x08H\x00\x88\x01\x01\x12\x17\n\nregistered\x18\x03 \x01(\x08H\x01\x88\x01\x01B\x11\n\x0f_paid_event_feeB\r\n\x0b_registered"-\n\x19EventRegistrationDeletion\x12\x10\n\x08event_id\x18\x01 \x01(\t"g\n\x0fEventIdentifier\x12\x0c\n\x02id\x18\x01 \x01(\tH\x00\x128\n\x0fevent_slug_path\x18\x02 \x01(\x0b2\x1d.parrygg.models.EventSlugPathH\x00B\x0c\n\nidentifier*\x91\x01\n\nEventState\x12\x1b\n\x17EVENT_STATE_UNSPECIFIED\x10\x00\x12\x17\n\x13EVENT_STATE_PENDING\x10\x01\x12\x15\n\x11EVENT_STATE_READY\x10\x02\x12\x1b\n\x17EVENT_STATE_IN_PROGRESS\x10\x03\x12\x19\n\x15EVENT_STATE_COMPLETED\x10\x04B\x18\n\x14gg.parry.grpc.modelsP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'models.event_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x14gg.parry.grpc.modelsP\x01'
    _globals['_EVENTSTATE']._serialized_start = 1447
    _globals['_EVENTSTATE']._serialized_end = 1592
    _globals['_EVENT']._serialized_start = 157
    _globals['_EVENT']._serialized_end = 559
    _globals['_EVENTMUTATION']._serialized_start = 562
    _globals['_EVENTMUTATION']._serialized_end = 965
    _globals['_EVENTREGISTRATION']._serialized_start = 968
    _globals['_EVENTREGISTRATION']._serialized_end = 1119
    _globals['_EVENTATTENDANCE']._serialized_start = 1121
    _globals['_EVENTATTENDANCE']._serialized_end = 1156
    _globals['_EVENTREGISTRATIONMUTATION']._serialized_start = 1159
    _globals['_EVENTREGISTRATIONMUTATION']._serialized_end = 1292
    _globals['_EVENTREGISTRATIONDELETION']._serialized_start = 1294
    _globals['_EVENTREGISTRATIONDELETION']._serialized_end = 1339
    _globals['_EVENTIDENTIFIER']._serialized_start = 1341
    _globals['_EVENTIDENTIFIER']._serialized_end = 1444
