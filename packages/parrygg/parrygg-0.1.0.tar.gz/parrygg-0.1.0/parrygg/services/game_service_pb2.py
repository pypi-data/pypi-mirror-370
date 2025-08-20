
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'services/game_service.proto')
_sym_db = _symbol_database.Default()
from ..models import game_pb2 as models_dot_game__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1bservices/game_service.proto\x12\x10parrygg.services\x1a\x11models/game.proto"\x11\n\x0fGetGamesRequest"7\n\x10GetGamesResponse\x12#\n\x05games\x18\x01 \x03(\x0b2\x14.parrygg.models.Game2b\n\x0bGameService\x12S\n\x08GetGames\x12!.parrygg.services.GetGamesRequest\x1a".parrygg.services.GetGamesResponse"\x00B\x1a\n\x16gg.parry.grpc.servicesP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'services.game_service_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x16gg.parry.grpc.servicesP\x01'
    _globals['_GETGAMESREQUEST']._serialized_start = 68
    _globals['_GETGAMESREQUEST']._serialized_end = 85
    _globals['_GETGAMESRESPONSE']._serialized_start = 87
    _globals['_GETGAMESRESPONSE']._serialized_end = 142
    _globals['_GAMESERVICE']._serialized_start = 144
    _globals['_GAMESERVICE']._serialized_end = 242
