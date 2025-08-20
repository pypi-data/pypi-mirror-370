
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'models/image.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12models/image.proto\x12\x0eparrygg.models"I\n\x05Image\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0b\n\x03url\x18\x02 \x01(\t\x12\'\n\x04type\x18\x03 \x01(\x0e2\x19.parrygg.models.ImageType*k\n\tImageType\x12\x1a\n\x16IMAGE_TYPE_UNSPECIFIED\x10\x00\x12\x15\n\x11IMAGE_TYPE_BANNER\x10\x01\x12\x15\n\x11IMAGE_TYPE_AVATAR\x10\x02\x12\x14\n\x10IMAGE_TYPE_COVER\x10\x03B\x18\n\x14gg.parry.grpc.modelsP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'models.image_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x14gg.parry.grpc.modelsP\x01'
    _globals['_IMAGETYPE']._serialized_start = 113
    _globals['_IMAGETYPE']._serialized_end = 220
    _globals['_IMAGE']._serialized_start = 38
    _globals['_IMAGE']._serialized_end = 111
