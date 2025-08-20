
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'models/user.proto')
_sym_db = _symbol_database.Default()
from ..models import image_pb2 as models_dot_image__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11models/user.proto\x12\x0eparrygg.models\x1a\x12models/image.proto"\x88\x02\n\x04User\x12\n\n\x02id\x18\x01 \x01(\t\x12\x11\n\tgamer_tag\x18\x02 \x01(\t\x12\x12\n\nfirst_name\x18\x03 \x01(\t\x12\x11\n\tlast_name\x18\x04 \x01(\t\x12\x0e\n\x06bio_md\x18\x05 \x01(\t\x12\x10\n\x08pronouns\x18\x06 \x01(\t\x12\x12\n\navatar_url\x18\x07 \x01(\t\x12\x14\n\x0cbanner_color\x18\x08 \x01(\t\x12\x18\n\x10location_country\x18\t \x01(\t\x12\x16\n\x0elocation_state\x18\n \x01(\t\x12\x15\n\rlocation_city\x18\x0b \x01(\t\x12%\n\x06images\x18\x0c \x03(\x0b2\x15.parrygg.models.Image"\xb5\x03\n\x0bMutableUser\x12\x16\n\tgamer_tag\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x17\n\nfirst_name\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x16\n\tlast_name\x18\x03 \x01(\tH\x02\x88\x01\x01\x12\x13\n\x06bio_md\x18\x04 \x01(\tH\x03\x88\x01\x01\x12\x15\n\x08pronouns\x18\x05 \x01(\tH\x04\x88\x01\x01\x12\x1c\n\x0favatar_image_id\x18\x06 \x01(\tH\x05\x88\x01\x01\x12\x19\n\x0cbanner_color\x18\x07 \x01(\tH\x06\x88\x01\x01\x12\x1d\n\x10location_country\x18\x08 \x01(\tH\x07\x88\x01\x01\x12\x1b\n\x0elocation_state\x18\t \x01(\tH\x08\x88\x01\x01\x12\x1a\n\rlocation_city\x18\n \x01(\tH\t\x88\x01\x01B\x0c\n\n_gamer_tagB\r\n\x0b_first_nameB\x0c\n\n_last_nameB\t\n\x07_bio_mdB\x0b\n\t_pronounsB\x12\n\x10_avatar_image_idB\x0f\n\r_banner_colorB\x13\n\x11_location_countryB\x11\n\x0f_location_stateB\x10\n\x0e_location_cityB\x18\n\x14gg.parry.grpc.modelsP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'models.user_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x14gg.parry.grpc.modelsP\x01'
    _globals['_USER']._serialized_start = 58
    _globals['_USER']._serialized_end = 322
    _globals['_MUTABLEUSER']._serialized_start = 325
    _globals['_MUTABLEUSER']._serialized_end = 762
