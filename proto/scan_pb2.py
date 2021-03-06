# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: scan.proto

from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import service as _service
from google.protobuf import service_reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


import app_pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='scan.proto',
  package='scan',
  serialized_pb='\n\nscan.proto\x12\x04scan\x1a\tapp.proto\"n\n\x10\x43ompatibleDetail\x12\x1d\n\x07\x61\x63\x63ount\x18\x01 \x01(\x0b\x32\x0c.app.Account\x12\x0f\n\x07proxies\x18\x02 \x01(\t\x12*\n\rscanAppDetail\x18\x03 \x01(\x0b\x32\x13.app.DetailResponse\">\n\x0c\x41\x64\x61ptRequest\x12\x0f\n\x07package\x18\x01 \x01(\t\x12\x1d\n\x04type\x18\x02 \x01(\x0e\x32\x0f.scan.AdaptType\"7\n\rAdaptResponse\x12&\n\x06\x64\x65tail\x18\x01 \x01(\x0b\x32\x16.scan.CompatibleDetail\"&\n\x13MultiVersionRequest\x12\x0f\n\x07package\x18\x01 \x01(\t\"?\n\x14MultiVersionResponse\x12\'\n\x07\x64\x65tails\x18\x01 \x03(\x0b\x32\x16.scan.CompatibleDetail*%\n\tAdaptType\x12\x0c\n\x08\x44OWNLOAD\x10\x01\x12\n\n\x06\x44\x45TAIL\x10\x02\x32\xa1\x01\n\x0bScanService\x12\x41\n\x16\x41\x64\x61ptCompatibleAccount\x12\x12.scan.AdaptRequest\x1a\x13.scan.AdaptResponse\x12O\n\x16GetMultiVersionAccount\x12\x19.scan.MultiVersionRequest\x1a\x1a.scan.MultiVersionResponseB\x03\x90\x01\x01')

_ADAPTTYPE = _descriptor.EnumDescriptor(
  name='AdaptType',
  full_name='scan.AdaptType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='DOWNLOAD', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DETAIL', index=1, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=369,
  serialized_end=406,
)

AdaptType = enum_type_wrapper.EnumTypeWrapper(_ADAPTTYPE)
DOWNLOAD = 1
DETAIL = 2



_COMPATIBLEDETAIL = _descriptor.Descriptor(
  name='CompatibleDetail',
  full_name='scan.CompatibleDetail',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='account', full_name='scan.CompatibleDetail.account', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='proxies', full_name='scan.CompatibleDetail.proxies', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='scanAppDetail', full_name='scan.CompatibleDetail.scanAppDetail', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=31,
  serialized_end=141,
)


_ADAPTREQUEST = _descriptor.Descriptor(
  name='AdaptRequest',
  full_name='scan.AdaptRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='package', full_name='scan.AdaptRequest.package', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='type', full_name='scan.AdaptRequest.type', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=143,
  serialized_end=205,
)


_ADAPTRESPONSE = _descriptor.Descriptor(
  name='AdaptResponse',
  full_name='scan.AdaptResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='detail', full_name='scan.AdaptResponse.detail', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=207,
  serialized_end=262,
)


_MULTIVERSIONREQUEST = _descriptor.Descriptor(
  name='MultiVersionRequest',
  full_name='scan.MultiVersionRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='package', full_name='scan.MultiVersionRequest.package', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=264,
  serialized_end=302,
)


_MULTIVERSIONRESPONSE = _descriptor.Descriptor(
  name='MultiVersionResponse',
  full_name='scan.MultiVersionResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='details', full_name='scan.MultiVersionResponse.details', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=304,
  serialized_end=367,
)

_COMPATIBLEDETAIL.fields_by_name['account'].message_type = app_pb2._ACCOUNT
_COMPATIBLEDETAIL.fields_by_name['scanAppDetail'].message_type = app_pb2._DETAILRESPONSE
_ADAPTREQUEST.fields_by_name['type'].enum_type = _ADAPTTYPE
_ADAPTRESPONSE.fields_by_name['detail'].message_type = _COMPATIBLEDETAIL
_MULTIVERSIONRESPONSE.fields_by_name['details'].message_type = _COMPATIBLEDETAIL
DESCRIPTOR.message_types_by_name['CompatibleDetail'] = _COMPATIBLEDETAIL
DESCRIPTOR.message_types_by_name['AdaptRequest'] = _ADAPTREQUEST
DESCRIPTOR.message_types_by_name['AdaptResponse'] = _ADAPTRESPONSE
DESCRIPTOR.message_types_by_name['MultiVersionRequest'] = _MULTIVERSIONREQUEST
DESCRIPTOR.message_types_by_name['MultiVersionResponse'] = _MULTIVERSIONRESPONSE

class CompatibleDetail(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _COMPATIBLEDETAIL

  # @@protoc_insertion_point(class_scope:scan.CompatibleDetail)

class AdaptRequest(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _ADAPTREQUEST

  # @@protoc_insertion_point(class_scope:scan.AdaptRequest)

class AdaptResponse(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _ADAPTRESPONSE

  # @@protoc_insertion_point(class_scope:scan.AdaptResponse)

class MultiVersionRequest(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _MULTIVERSIONREQUEST

  # @@protoc_insertion_point(class_scope:scan.MultiVersionRequest)

class MultiVersionResponse(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _MULTIVERSIONRESPONSE

  # @@protoc_insertion_point(class_scope:scan.MultiVersionResponse)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), '\220\001\001')

_SCANSERVICE = _descriptor.ServiceDescriptor(
  name='ScanService',
  full_name='scan.ScanService',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=409,
  serialized_end=570,
  methods=[
  _descriptor.MethodDescriptor(
    name='AdaptCompatibleAccount',
    full_name='scan.ScanService.AdaptCompatibleAccount',
    index=0,
    containing_service=None,
    input_type=_ADAPTREQUEST,
    output_type=_ADAPTRESPONSE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='GetMultiVersionAccount',
    full_name='scan.ScanService.GetMultiVersionAccount',
    index=1,
    containing_service=None,
    input_type=_MULTIVERSIONREQUEST,
    output_type=_MULTIVERSIONRESPONSE,
    options=None,
  ),
])

class ScanService(_service.Service):
  __metaclass__ = service_reflection.GeneratedServiceType
  DESCRIPTOR = _SCANSERVICE
class ScanService_Stub(ScanService):
  __metaclass__ = service_reflection.GeneratedServiceStubType
  DESCRIPTOR = _SCANSERVICE

# @@protoc_insertion_point(module_scope)
