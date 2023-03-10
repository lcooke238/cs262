# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chat.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nchat.proto\"\x1c\n\x0cLoginRequest\x12\x0c\n\x04user\x18\x01 \x01(\t\"\x1d\n\rLogoutRequest\x12\x0c\n\x04user\x18\x01 \x01(\t\"\x1b\n\x0bListRequest\x12\x0c\n\x04\x61rgs\x18\x01 \x01(\t\"<\n\x0bSendRequest\x12\x0c\n\x04user\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0e\n\x06target\x18\x03 \x01(\t\"\x1d\n\rDeleteRequest\x12\x0c\n\x04user\x18\x01 \x01(\t\"\x1a\n\nGetRequest\x12\x0c\n\x04user\x18\x01 \x01(\t\"@\n\nLoginReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrormessage\x18\x02 \x01(\t\x12\x0c\n\x04user\x18\x03 \x01(\t\"A\n\x0bLogoutReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrormessage\x18\x02 \x01(\t\x12\x0c\n\x04user\x18\x03 \x01(\t\"Q\n\tListReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrormessage\x18\x02 \x01(\t\x12\x10\n\x08wildcard\x18\x03 \x01(\t\x12\x0c\n\x04user\x18\x04 \x03(\t\"A\n\x0b\x44\x65leteReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrormessage\x18\x02 \x01(\t\x12\x0c\n\x04user\x18\x03 \x01(\t\"`\n\tSendReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrormessage\x18\x02 \x01(\t\x12\x0c\n\x04user\x18\x03 \x01(\t\x12\x0f\n\x07message\x18\x04 \x01(\t\x12\x0e\n\x06target\x18\x05 \x01(\t\"B\n\rUnreadMessage\x12\x0e\n\x06sender\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x10\n\x08receiver\x18\x03 \x01(\t\"Q\n\x08GetReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrormessage\x18\x02 \x01(\t\x12\x1f\n\x07message\x18\x03 \x03(\x0b\x32\x0e.UnreadMessage\"E\n\x0cJaredMessage\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrormessage\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t2\x80\x02\n\rClientHandler\x12\'\n\tListUsers\x12\x0c.ListRequest\x1a\n.ListReply\"\x00\x12%\n\x05Login\x12\r.LoginRequest\x1a\x0b.LoginReply\"\x00\x12(\n\x06Logout\x12\x0e.LogoutRequest\x1a\x0c.LogoutReply\"\x00\x12\"\n\x04Send\x12\x0c.SendRequest\x1a\n.SendReply\"\x00\x12\'\n\x0bGetMessages\x12\x0b.GetRequest\x1a\t.GetReply\"\x00\x12(\n\x06\x44\x65lete\x12\x0e.DeleteRequest\x1a\x0c.DeleteReply\"\x00\x42\x06\xa2\x02\x03HLWb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\242\002\003HLW'
  _LOGINREQUEST._serialized_start=14
  _LOGINREQUEST._serialized_end=42
  _LOGOUTREQUEST._serialized_start=44
  _LOGOUTREQUEST._serialized_end=73
  _LISTREQUEST._serialized_start=75
  _LISTREQUEST._serialized_end=102
  _SENDREQUEST._serialized_start=104
  _SENDREQUEST._serialized_end=164
  _DELETEREQUEST._serialized_start=166
  _DELETEREQUEST._serialized_end=195
  _GETREQUEST._serialized_start=197
  _GETREQUEST._serialized_end=223
  _LOGINREPLY._serialized_start=225
  _LOGINREPLY._serialized_end=289
  _LOGOUTREPLY._serialized_start=291
  _LOGOUTREPLY._serialized_end=356
  _LISTREPLY._serialized_start=358
  _LISTREPLY._serialized_end=439
  _DELETEREPLY._serialized_start=441
  _DELETEREPLY._serialized_end=506
  _SENDREPLY._serialized_start=508
  _SENDREPLY._serialized_end=604
  _UNREADMESSAGE._serialized_start=606
  _UNREADMESSAGE._serialized_end=672
  _GETREPLY._serialized_start=674
  _GETREPLY._serialized_end=755
  _JAREDMESSAGE._serialized_start=757
  _JAREDMESSAGE._serialized_end=826
  _CLIENTHANDLER._serialized_start=829
  _CLIENTHANDLER._serialized_end=1085
# @@protoc_insertion_point(module_scope)
