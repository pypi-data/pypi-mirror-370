
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'services/hierarchy_service.proto')
_sym_db = _symbol_database.Default()
from ..models import hierarchy_pb2 as models_dot_hierarchy__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n services/hierarchy_service.proto\x12\x10parrygg.services\x1a\x16models/hierarchy.proto"v\n\x18GetEventHierarchyRequest\x12\x12\n\x08event_id\x18\x01 \x01(\tH\x00\x128\n\x0fevent_slug_path\x18\x02 \x01(\x0b2\x1d.parrygg.models.EventSlugPathH\x00B\x0c\n\nidentifier"I\n\x19GetEventHierarchyResponse\x12,\n\thierarchy\x18\x01 \x01(\x0b2\x19.parrygg.models.Hierarchy"v\n\x18GetPhaseHierarchyRequest\x12\x12\n\x08phase_id\x18\x01 \x01(\tH\x00\x128\n\x0fphase_slug_path\x18\x02 \x01(\x0b2\x1d.parrygg.models.PhaseSlugPathH\x00B\x0c\n\nidentifier"I\n\x19GetPhaseHierarchyResponse\x12,\n\thierarchy\x18\x01 \x01(\x0b2\x19.parrygg.models.Hierarchy"~\n\x1aGetBracketHierarchyRequest\x12\x14\n\nbracket_id\x18\x01 \x01(\tH\x00\x12<\n\x11bracket_slug_path\x18\x02 \x01(\x0b2\x1f.parrygg.models.BracketSlugPathH\x00B\x0c\n\nidentifier"K\n\x1bGetBracketHierarchyResponse\x12,\n\thierarchy\x18\x01 \x01(\x0b2\x19.parrygg.models.Hierarchy2\xe8\x02\n\x10HierarchyService\x12n\n\x11GetEventHierarchy\x12*.parrygg.services.GetEventHierarchyRequest\x1a+.parrygg.services.GetEventHierarchyResponse"\x00\x12n\n\x11GetPhaseHierarchy\x12*.parrygg.services.GetPhaseHierarchyRequest\x1a+.parrygg.services.GetPhaseHierarchyResponse"\x00\x12t\n\x13GetBracketHierarchy\x12,.parrygg.services.GetBracketHierarchyRequest\x1a-.parrygg.services.GetBracketHierarchyResponse"\x00B\x1a\n\x16gg.parry.grpc.servicesP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'services.hierarchy_service_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x16gg.parry.grpc.servicesP\x01'
    _globals['_GETEVENTHIERARCHYREQUEST']._serialized_start = 78
    _globals['_GETEVENTHIERARCHYREQUEST']._serialized_end = 196
    _globals['_GETEVENTHIERARCHYRESPONSE']._serialized_start = 198
    _globals['_GETEVENTHIERARCHYRESPONSE']._serialized_end = 271
    _globals['_GETPHASEHIERARCHYREQUEST']._serialized_start = 273
    _globals['_GETPHASEHIERARCHYREQUEST']._serialized_end = 391
    _globals['_GETPHASEHIERARCHYRESPONSE']._serialized_start = 393
    _globals['_GETPHASEHIERARCHYRESPONSE']._serialized_end = 466
    _globals['_GETBRACKETHIERARCHYREQUEST']._serialized_start = 468
    _globals['_GETBRACKETHIERARCHYREQUEST']._serialized_end = 594
    _globals['_GETBRACKETHIERARCHYRESPONSE']._serialized_start = 596
    _globals['_GETBRACKETHIERARCHYRESPONSE']._serialized_end = 671
    _globals['_HIERARCHYSERVICE']._serialized_start = 674
    _globals['_HIERARCHYSERVICE']._serialized_end = 1034
