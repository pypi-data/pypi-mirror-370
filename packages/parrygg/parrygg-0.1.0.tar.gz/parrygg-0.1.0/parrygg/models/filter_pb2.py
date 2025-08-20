
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'models/filter.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13models/filter.proto\x12\x0eparrygg.models"0\n\x0cEventsFilter\x12\x14\n\x07user_id\x18\x01 \x01(\tH\x00\x88\x01\x01B\n\n\x08_user_id"\xa2\x01\n\x11TournamentsFilter\x12\x14\n\x07user_id\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x15\n\x08owner_id\x18\x02 \x01(\tH\x01\x88\x01\x01\x126\n\x0cadmin_filter\x18\x03 \x01(\x0b2\x1b.parrygg.models.AdminFilterH\x02\x88\x01\x01B\n\n\x08_user_idB\x0b\n\t_owner_idB\x0f\n\r_admin_filter"3\n\x0bUsersFilter\x12\x16\n\tgamer_tag\x18\x01 \x01(\tH\x00\x88\x01\x01B\x0c\n\n_gamer_tag"Y\n\x0bAdminFilter\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x129\n\npermission\x18\x02 \x01(\x0e2%.parrygg.models.AdminFilterPermission*\xa6\x01\n\x15AdminFilterPermission\x12\x1f\n\x1bADMIN_FILTER_PERMISSION_ANY\x10\x00\x12!\n\x1dADMIN_FILTER_PERMISSION_ADMIN\x10\x01\x12#\n\x1fADMIN_FILTER_PERMISSION_MANAGER\x10\x02\x12$\n ADMIN_FILTER_PERMISSION_REPORTER\x10\x03B\x18\n\x14gg.parry.grpc.modelsP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'models.filter_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x14gg.parry.grpc.modelsP\x01'
    _globals['_ADMINFILTERPERMISSION']._serialized_start = 399
    _globals['_ADMINFILTERPERMISSION']._serialized_end = 565
    _globals['_EVENTSFILTER']._serialized_start = 39
    _globals['_EVENTSFILTER']._serialized_end = 87
    _globals['_TOURNAMENTSFILTER']._serialized_start = 90
    _globals['_TOURNAMENTSFILTER']._serialized_end = 252
    _globals['_USERSFILTER']._serialized_start = 254
    _globals['_USERSFILTER']._serialized_end = 305
    _globals['_ADMINFILTER']._serialized_start = 307
    _globals['_ADMINFILTER']._serialized_end = 396
