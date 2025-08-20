
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'models/slug.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11models/slug.proto\x12\x0eparrygg.models"<\n\x04Slug\x12\x0c\n\x04slug\x18\x01 \x01(\t\x12&\n\x04type\x18\x02 \x01(\x0e2\x18.parrygg.models.SlugType"C\n\x0bMutableSlug\x12\x0c\n\x04slug\x18\x01 \x01(\t\x12&\n\x04type\x18\x02 \x01(\x0e2\x18.parrygg.models.SlugType*j\n\x08SlugType\x12\x19\n\x15SLUG_TYPE_UNSPECIFIED\x10\x00\x12\x15\n\x11SLUG_TYPE_PRIMARY\x10\x01\x12\x16\n\x12SLUG_TYPE_OUTDATED\x10\x02\x12\x14\n\x10SLUG_TYPE_CUSTOM\x10\x03B\x18\n\x14gg.parry.grpc.modelsP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'models.slug_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x14gg.parry.grpc.modelsP\x01'
    _globals['_SLUGTYPE']._serialized_start = 168
    _globals['_SLUGTYPE']._serialized_end = 274
    _globals['_SLUG']._serialized_start = 37
    _globals['_SLUG']._serialized_end = 97
    _globals['_MUTABLESLUG']._serialized_start = 99
    _globals['_MUTABLESLUG']._serialized_end = 166
