
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'services/phase_service.proto')
_sym_db = _symbol_database.Default()
from ..models import phase_pb2 as models_dot_phase__pb2
from ..models import entrant_pb2 as models_dot_entrant__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1cservices/phase_service.proto\x12\x10parrygg.services\x1a\x12models/phase.proto\x1a\x14models/entrant.proto"]\n\x0fGetPhaseRequest\x12\x0c\n\x02id\x18\x01 \x01(\tH\x00\x12.\n\x07slug_id\x18\x02 \x01(\x0b2\x1b.parrygg.models.PhaseSlugIdH\x00B\x0c\n\nidentifier"8\n\x10GetPhaseResponse\x12$\n\x05phase\x18\x01 \x01(\x0b2\x15.parrygg.models.Phase"\'\n\x19GetPhasePlacementsRequest\x12\n\n\x02id\x18\x01 \x01(\t"K\n\x1aGetPhasePlacementsResponse\x12-\n\nplacements\x18\x01 \x03(\x0b2\x19.parrygg.models.Placement"\x1f\n\x11ResetPhaseRequest\x12\n\n\x02id\x18\x01 \x01(\t"\x14\n\x12ResetPhaseResponse2\xd6\x01\n\x0cPhaseService\x12S\n\x08GetPhase\x12!.parrygg.services.GetPhaseRequest\x1a".parrygg.services.GetPhaseResponse"\x00\x12q\n\x12GetPhasePlacements\x12+.parrygg.services.GetPhasePlacementsRequest\x1a,.parrygg.services.GetPhasePlacementsResponse"\x00B\x1a\n\x16gg.parry.grpc.servicesP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'services.phase_service_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x16gg.parry.grpc.servicesP\x01'
    _globals['_GETPHASEREQUEST']._serialized_start = 92
    _globals['_GETPHASEREQUEST']._serialized_end = 185
    _globals['_GETPHASERESPONSE']._serialized_start = 187
    _globals['_GETPHASERESPONSE']._serialized_end = 243
    _globals['_GETPHASEPLACEMENTSREQUEST']._serialized_start = 245
    _globals['_GETPHASEPLACEMENTSREQUEST']._serialized_end = 284
    _globals['_GETPHASEPLACEMENTSRESPONSE']._serialized_start = 286
    _globals['_GETPHASEPLACEMENTSRESPONSE']._serialized_end = 361
    _globals['_RESETPHASEREQUEST']._serialized_start = 363
    _globals['_RESETPHASEREQUEST']._serialized_end = 394
    _globals['_RESETPHASERESPONSE']._serialized_start = 396
    _globals['_RESETPHASERESPONSE']._serialized_end = 416
    _globals['_PHASESERVICE']._serialized_start = 419
    _globals['_PHASESERVICE']._serialized_end = 633
