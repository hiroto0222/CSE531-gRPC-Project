# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: branch.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0c\x62ranch.proto\"t\n\x12MsgDeliveryRequest\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x10\n\x08\x65vent_id\x18\x02 \x01(\x05\x12\x11\n\tinterface\x18\x03 \x01(\t\x12\r\n\x05money\x18\x04 \x01(\x05\x12\x0f\n\x07\x62\x61lance\x18\x05 \x01(\x05\x12\r\n\x05\x63lock\x18\x06 \x01(\x05\"c\n\x13MsgDeliveryResponse\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x10\n\x08\x65vent_id\x18\x02 \x01(\x05\x12\x0f\n\x07\x62\x61lance\x18\x03 \x01(\x05\x12\x0e\n\x06result\x18\x04 \x01(\t\x12\r\n\x05\x63lock\x18\x05 \x01(\x05\x32\x44\n\x06\x42ranch\x12:\n\x0bMsgDelivery\x12\x13.MsgDeliveryRequest\x1a\x14.MsgDeliveryResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'branch_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_MSGDELIVERYREQUEST']._serialized_start=16
  _globals['_MSGDELIVERYREQUEST']._serialized_end=132
  _globals['_MSGDELIVERYRESPONSE']._serialized_start=134
  _globals['_MSGDELIVERYRESPONSE']._serialized_end=233
  _globals['_BRANCH']._serialized_start=235
  _globals['_BRANCH']._serialized_end=303
# @@protoc_insertion_point(module_scope)
