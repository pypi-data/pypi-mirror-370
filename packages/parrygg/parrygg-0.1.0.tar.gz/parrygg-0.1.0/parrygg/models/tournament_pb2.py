
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'models/tournament.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from ..models import image_pb2 as models_dot_image__pb2
from ..models import event_pb2 as models_dot_event__pb2
from ..models import slug_pb2 as models_dot_slug__pb2
from ..models import user_pb2 as models_dot_user__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17models/tournament.proto\x12\x0eparrygg.models\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x12models/image.proto\x1a\x12models/event.proto\x1a\x11models/slug.proto\x1a\x11models/user.proto"\xcf\x03\n\nTournament\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x12\n\nshort_name\x18\x03 \x01(\t\x12\x15\n\rvenue_address\x18\x04 \x01(\t\x12\x15\n\radmin_contact\x18\x07 \x01(\t\x12\x15\n\rcurrency_code\x18\x08 \x01(\t\x12.\n\nstart_date\x18\t \x01(\x0b2\x1a.google.protobuf.Timestamp\x12,\n\x08end_date\x18\n \x01(\x0b2\x1a.google.protobuf.Timestamp\x12.\n\x05state\x18\x0b \x01(\x0e2\x1f.parrygg.models.TournamentState\x12%\n\x06images\x18\x0c \x03(\x0b2\x15.parrygg.models.Image\x12%\n\x06events\x18\r \x03(\x0b2\x15.parrygg.models.Event\x12\x15\n\rnum_attendees\x18\x0e \x01(\x05\x12\x10\n\x08owner_id\x18\x0f \x01(\t\x12#\n\x05slugs\x18\x10 \x03(\x0b2\x14.parrygg.models.Slug\x12\x11\n\tvenue_fee\x18\x11 \x01(\x05\x12\x11\n\ttime_zone\x18\x12 \x01(\t"\xd6\x03\n\x12TournamentMutation\x12\x11\n\x04name\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x17\n\nshort_name\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x1a\n\rvenue_address\x18\x03 \x01(\tH\x02\x88\x01\x01\x12\x1a\n\radmin_contact\x18\x06 \x01(\tH\x03\x88\x01\x01\x12\x1a\n\rcurrency_code\x18\x07 \x01(\tH\x04\x88\x01\x01\x123\n\nstart_date\x18\x08 \x01(\x0b2\x1a.google.protobuf.TimestampH\x05\x88\x01\x01\x121\n\x08end_date\x18\t \x01(\x0b2\x1a.google.protobuf.TimestampH\x06\x88\x01\x01\x12\x15\n\x08owner_id\x18\n \x01(\tH\x07\x88\x01\x01\x12\x16\n\tvenue_fee\x18\x0b \x01(\x05H\x08\x88\x01\x01\x12\x16\n\ttime_zone\x18\x0c \x01(\tH\t\x88\x01\x01B\x07\n\x05_nameB\r\n\x0b_short_nameB\x10\n\x0e_venue_addressB\x10\n\x0e_admin_contactB\x10\n\x0e_currency_codeB\r\n\x0b_start_dateB\x0b\n\t_end_dateB\x0b\n\t_owner_idB\x0c\n\n_venue_feeB\x0c\n\n_time_zone"K\n\x0bPageContent\x12\n\n\x02id\x18\x01 \x01(\t\x12\r\n\x05index\x18\x02 \x01(\x05\x12\r\n\x05title\x18\x03 \x01(\t\x12\x12\n\ncontent_md\x18\x04 \x01(\t"x\n\x12MutablePageContent\x12\x12\n\x05index\x18\x01 \x01(\x05H\x00\x88\x01\x01\x12\x12\n\x05title\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x17\n\ncontent_md\x18\x03 \x01(\tH\x02\x88\x01\x01B\x08\n\x06_indexB\x08\n\x06_titleB\r\n\x0b_content_md"\xb1\x01\n\x16TournamentRegistration\x12\x15\n\rtournament_id\x18\x01 \x01(\t\x12\x16\n\x0epaid_venue_fee\x18\x03 \x01(\x08\x12>\n\x13event_registrations\x18\x04 \x03(\x0b2!.parrygg.models.EventRegistration\x12"\n\x04user\x18\x05 \x01(\x0b2\x14.parrygg.models.UserJ\x04\x08\x02\x10\x03"\x9e\x01\n\x1eTournamentRegistrationMutation\x12\x1b\n\x0epaid_venue_fee\x18\x01 \x01(\x08H\x00\x88\x01\x01\x12F\n\x13event_registrations\x18\x02 \x03(\x0b2).parrygg.models.EventRegistrationMutationB\x11\n\x0f_paid_venue_feeJ\x04\x08\x03\x10\x04"|\n#BatchTournamentRegistrationMutation\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12D\n\x0cregistration\x18\x02 \x01(\x0b2..parrygg.models.TournamentRegistrationMutation"i\n\x12TournamentAttendee\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.parrygg.models.User\x12/\n\x06events\x18\x02 \x03(\x0b2\x1f.parrygg.models.EventAttendance"M\n\x14TournamentIdentifier\x12\x0c\n\x02id\x18\x01 \x01(\tH\x00\x12\x19\n\x0ftournament_slug\x18\x02 \x01(\tH\x00B\x0c\n\nidentifier"d\n\x1dTournamentPermissionsMetadata\x12C\n\x15tournament_permission\x18\x01 \x01(\x0e2$.parrygg.models.TournamentPermission*\xaf\x01\n\x0fTournamentState\x12 \n\x1cTOURNAMENT_STATE_UNSPECIFIED\x10\x00\x12\x1c\n\x18TOURNAMENT_STATE_PENDING\x10\x01\x12\x1a\n\x16TOURNAMENT_STATE_READY\x10\x02\x12 \n\x1cTOURNAMENT_STATE_IN_PROGRESS\x10\x03\x12\x1e\n\x1aTOURNAMENT_STATE_COMPLETED\x10\x04*\x91\x01\n\x14TournamentPermission\x12 \n\x1cPERMISSION_LEVEL_UNSPECIFIED\x10\x00\x12\x1a\n\x16PERMISSION_LEVEL_ADMIN\x10\x01\x12\x1c\n\x18PERMISSION_LEVEL_MANAGER\x10\x02\x12\x1d\n\x19PERMISSION_LEVEL_REPORTER\x10\x03B\x18\n\x14gg.parry.grpc.modelsP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'models.tournament_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x14gg.parry.grpc.modelsP\x01'
    _globals['_TOURNAMENTSTATE']._serialized_start = 2048
    _globals['_TOURNAMENTSTATE']._serialized_end = 2223
    _globals['_TOURNAMENTPERMISSION']._serialized_start = 2226
    _globals['_TOURNAMENTPERMISSION']._serialized_end = 2371
    _globals['_TOURNAMENT']._serialized_start = 155
    _globals['_TOURNAMENT']._serialized_end = 618
    _globals['_TOURNAMENTMUTATION']._serialized_start = 621
    _globals['_TOURNAMENTMUTATION']._serialized_end = 1091
    _globals['_PAGECONTENT']._serialized_start = 1093
    _globals['_PAGECONTENT']._serialized_end = 1168
    _globals['_MUTABLEPAGECONTENT']._serialized_start = 1170
    _globals['_MUTABLEPAGECONTENT']._serialized_end = 1290
    _globals['_TOURNAMENTREGISTRATION']._serialized_start = 1293
    _globals['_TOURNAMENTREGISTRATION']._serialized_end = 1470
    _globals['_TOURNAMENTREGISTRATIONMUTATION']._serialized_start = 1473
    _globals['_TOURNAMENTREGISTRATIONMUTATION']._serialized_end = 1631
    _globals['_BATCHTOURNAMENTREGISTRATIONMUTATION']._serialized_start = 1633
    _globals['_BATCHTOURNAMENTREGISTRATIONMUTATION']._serialized_end = 1757
    _globals['_TOURNAMENTATTENDEE']._serialized_start = 1759
    _globals['_TOURNAMENTATTENDEE']._serialized_end = 1864
    _globals['_TOURNAMENTIDENTIFIER']._serialized_start = 1866
    _globals['_TOURNAMENTIDENTIFIER']._serialized_end = 1943
    _globals['_TOURNAMENTPERMISSIONSMETADATA']._serialized_start = 1945
    _globals['_TOURNAMENTPERMISSIONSMETADATA']._serialized_end = 2045
