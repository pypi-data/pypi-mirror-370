
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'services/entrant_service.proto')
_sym_db = _symbol_database.Default()
from ..models import entrant_pb2 as models_dot_entrant__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1eservices/entrant_service.proto\x12\x10parrygg.services\x1a\x14models/entrant.proto">\n\x16GetEventEntrantRequest\x12\x10\n\x08event_id\x18\x01 \x01(\t\x12\x12\n\nentrant_id\x18\x02 \x01(\t"N\n\x17GetEventEntrantResponse\x123\n\revent_entrant\x18\x01 \x01(\x0b2\x1c.parrygg.models.EventEntrant"A\n\x19CreateEventEntrantRequest\x12\x10\n\x08event_id\x18\x01 \x01(\t\x12\x12\n\nentrant_id\x18\x02 \x01(\t"Q\n\x1aCreateEventEntrantResponse\x123\n\revent_entrant\x18\x01 \x01(\x0b2\x1c.parrygg.models.EventEntrant"~\n\x19UpdateEventEntrantRequest\x12\x10\n\x08event_id\x18\x01 \x01(\t\x12\x12\n\nentrant_id\x18\x02 \x01(\t\x12;\n\revent_entrant\x18\x03 \x01(\x0b2$.parrygg.models.EventEntrantMutation"Q\n\x1aUpdateEventEntrantResponse\x123\n\revent_entrant\x18\x01 \x01(\x0b2\x1c.parrygg.models.EventEntrant"A\n\x19DeleteEventEntrantRequest\x12\x10\n\x08event_id\x18\x01 \x01(\t\x12\x12\n\nentrant_id\x18\x02 \x01(\t"\x1c\n\x1aDeleteEventEntrantResponse"a\n\x1dRemoveFromEventEntrantRequest\x12\x18\n\x10event_entrant_id\x18\x01 \x01(\t\x12\x0f\n\x07user_id\x18\x02 \x01(\t\x12\x15\n\rkeep_in_event\x18\x03 \x01(\x08"\x8f\x01\n\x1eRemoveFromEventEntrantResponse\x123\n\revent_entrant\x18\x01 \x01(\x0b2\x1c.parrygg.models.EventEntrant\x128\n\x12removed_free_agent\x18\x02 \x01(\x0b2\x1c.parrygg.models.EventEntrant"6\n\x1aDisbandEventEntrantRequest\x12\x18\n\x10event_entrant_id\x18\x01 \x01(\t"R\n\x1bDisbandEventEntrantResponse\x123\n\revent_entrant\x18\x01 \x01(\x0b2\x1c.parrygg.models.EventEntrant"Z\n\x11CreateTeamRequest\x12\x10\n\x08event_id\x18\x01 \x01(\t\x123\n\rteam_mutation\x18\x02 \x01(\x0b2\x1c.parrygg.models.TeamMutation"@\n\x12CreateTeamResponse\x12*\n\x04team\x18\x01 \x01(\x0b2\x1c.parrygg.models.EventEntrant"T\n\x11UpdateTeamRequest\x12\n\n\x02id\x18\x01 \x01(\t\x123\n\rteam_mutation\x18\x02 \x01(\x0b2\x1c.parrygg.models.TeamMutation"@\n\x12UpdateTeamResponse\x12*\n\x04team\x18\x01 \x01(\x0b2\x1c.parrygg.models.EventEntrant2\xfe\x06\n\x0eEntrantService\x12h\n\x0fGetEventEntrant\x12(.parrygg.services.GetEventEntrantRequest\x1a).parrygg.services.GetEventEntrantResponse"\x00\x12q\n\x12CreateEventEntrant\x12+.parrygg.services.CreateEventEntrantRequest\x1a,.parrygg.services.CreateEventEntrantResponse"\x00\x12q\n\x12UpdateEventEntrant\x12+.parrygg.services.UpdateEventEntrantRequest\x1a,.parrygg.services.UpdateEventEntrantResponse"\x00\x12q\n\x12DeleteEventEntrant\x12+.parrygg.services.DeleteEventEntrantRequest\x1a,.parrygg.services.DeleteEventEntrantResponse"\x00\x12}\n\x16RemoveFromEventEntrant\x12/.parrygg.services.RemoveFromEventEntrantRequest\x1a0.parrygg.services.RemoveFromEventEntrantResponse"\x00\x12t\n\x13DisbandEventEntrant\x12,.parrygg.services.DisbandEventEntrantRequest\x1a-.parrygg.services.DisbandEventEntrantResponse"\x00\x12Y\n\nCreateTeam\x12#.parrygg.services.CreateTeamRequest\x1a$.parrygg.services.CreateTeamResponse"\x00\x12Y\n\nUpdateTeam\x12#.parrygg.services.UpdateTeamRequest\x1a$.parrygg.services.UpdateTeamResponse"\x00B\x1a\n\x16gg.parry.grpc.servicesP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'services.entrant_service_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x16gg.parry.grpc.servicesP\x01'
    _globals['_GETEVENTENTRANTREQUEST']._serialized_start = 74
    _globals['_GETEVENTENTRANTREQUEST']._serialized_end = 136
    _globals['_GETEVENTENTRANTRESPONSE']._serialized_start = 138
    _globals['_GETEVENTENTRANTRESPONSE']._serialized_end = 216
    _globals['_CREATEEVENTENTRANTREQUEST']._serialized_start = 218
    _globals['_CREATEEVENTENTRANTREQUEST']._serialized_end = 283
    _globals['_CREATEEVENTENTRANTRESPONSE']._serialized_start = 285
    _globals['_CREATEEVENTENTRANTRESPONSE']._serialized_end = 366
    _globals['_UPDATEEVENTENTRANTREQUEST']._serialized_start = 368
    _globals['_UPDATEEVENTENTRANTREQUEST']._serialized_end = 494
    _globals['_UPDATEEVENTENTRANTRESPONSE']._serialized_start = 496
    _globals['_UPDATEEVENTENTRANTRESPONSE']._serialized_end = 577
    _globals['_DELETEEVENTENTRANTREQUEST']._serialized_start = 579
    _globals['_DELETEEVENTENTRANTREQUEST']._serialized_end = 644
    _globals['_DELETEEVENTENTRANTRESPONSE']._serialized_start = 646
    _globals['_DELETEEVENTENTRANTRESPONSE']._serialized_end = 674
    _globals['_REMOVEFROMEVENTENTRANTREQUEST']._serialized_start = 676
    _globals['_REMOVEFROMEVENTENTRANTREQUEST']._serialized_end = 773
    _globals['_REMOVEFROMEVENTENTRANTRESPONSE']._serialized_start = 776
    _globals['_REMOVEFROMEVENTENTRANTRESPONSE']._serialized_end = 919
    _globals['_DISBANDEVENTENTRANTREQUEST']._serialized_start = 921
    _globals['_DISBANDEVENTENTRANTREQUEST']._serialized_end = 975
    _globals['_DISBANDEVENTENTRANTRESPONSE']._serialized_start = 977
    _globals['_DISBANDEVENTENTRANTRESPONSE']._serialized_end = 1059
    _globals['_CREATETEAMREQUEST']._serialized_start = 1061
    _globals['_CREATETEAMREQUEST']._serialized_end = 1151
    _globals['_CREATETEAMRESPONSE']._serialized_start = 1153
    _globals['_CREATETEAMRESPONSE']._serialized_end = 1217
    _globals['_UPDATETEAMREQUEST']._serialized_start = 1219
    _globals['_UPDATETEAMREQUEST']._serialized_end = 1303
    _globals['_UPDATETEAMRESPONSE']._serialized_start = 1305
    _globals['_UPDATETEAMRESPONSE']._serialized_end = 1369
    _globals['_ENTRANTSERVICE']._serialized_start = 1372
    _globals['_ENTRANTSERVICE']._serialized_end = 2266
