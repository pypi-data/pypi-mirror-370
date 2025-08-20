
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'services/user_service.proto')
_sym_db = _symbol_database.Default()
from ..models import user_pb2 as models_dot_user__pb2
from ..models import image_pb2 as models_dot_image__pb2
from ..models import filter_pb2 as models_dot_filter__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1bservices/user_service.proto\x12\x10parrygg.services\x1a\x11models/user.proto\x1a\x12models/image.proto\x1a\x13models/filter.proto",\n\x0eGetUserRequest\x12\x0c\n\x02id\x18\x01 \x01(\tH\x00B\x0c\n\nidentifier"5\n\x0fGetUserResponse\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.parrygg.models.User">\n\x0fGetUsersRequest\x12+\n\x06filter\x18\x01 \x01(\x0b2\x1b.parrygg.models.UsersFilter"7\n\x10GetUsersResponse\x12#\n\x05users\x18\x01 \x03(\x0b2\x14.parrygg.models.User"J\n\x11UpdateUserRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12)\n\x04user\x18\x02 \x01(\x0b2\x1b.parrygg.models.MutableUser"8\n\x12UpdateUserResponse\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.parrygg.models.User2\x8f\x02\n\x0bUserService\x12P\n\x07GetUser\x12 .parrygg.services.GetUserRequest\x1a!.parrygg.services.GetUserResponse"\x00\x12S\n\x08GetUsers\x12!.parrygg.services.GetUsersRequest\x1a".parrygg.services.GetUsersResponse"\x00\x12Y\n\nUpdateUser\x12#.parrygg.services.UpdateUserRequest\x1a$.parrygg.services.UpdateUserResponse"\x00B\x1a\n\x16gg.parry.grpc.servicesP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'services.user_service_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x16gg.parry.grpc.servicesP\x01'
    _globals['_GETUSERREQUEST']._serialized_start = 109
    _globals['_GETUSERREQUEST']._serialized_end = 153
    _globals['_GETUSERRESPONSE']._serialized_start = 155
    _globals['_GETUSERRESPONSE']._serialized_end = 208
    _globals['_GETUSERSREQUEST']._serialized_start = 210
    _globals['_GETUSERSREQUEST']._serialized_end = 272
    _globals['_GETUSERSRESPONSE']._serialized_start = 274
    _globals['_GETUSERSRESPONSE']._serialized_end = 329
    _globals['_UPDATEUSERREQUEST']._serialized_start = 331
    _globals['_UPDATEUSERREQUEST']._serialized_end = 405
    _globals['_UPDATEUSERRESPONSE']._serialized_start = 407
    _globals['_UPDATEUSERRESPONSE']._serialized_end = 463
    _globals['_USERSERVICE']._serialized_start = 466
    _globals['_USERSERVICE']._serialized_end = 737
