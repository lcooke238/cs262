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




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nchat.proto\"\x07\n\x05\x45mpty\"0\n\x10SetStatusRequest\x12\x0c\n\x04user\x18\x01 \x01(\t\x12\x0e\n\x06status\x18\x02 \x01(\x08\"(\n\nServerInfo\x12\x0c\n\x04host\x18\x01 \x01(\t\x12\x0c\n\x04port\x18\x02 \x01(\t\"\x0f\n\rBackupRequest\"T\n\x0b\x42\x61\x63kupReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrormessage\x18\x02 \x01(\t\x12\x1f\n\nserverinfo\x18\x03 \x03(\x0b\x32\x0b.ServerInfo\"\x1c\n\x0cLoginRequest\x12\x0c\n\x04user\x18\x01 \x01(\t\"\x1d\n\rLogoutRequest\x12\x0c\n\x04user\x18\x01 \x01(\t\"\x1b\n\x0bListRequest\x12\x0c\n\x04\x61rgs\x18\x01 \x01(\t\"<\n\x0bSendRequest\x12\x0c\n\x04user\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0e\n\x06target\x18\x03 \x01(\t\"\x1d\n\rDeleteRequest\x12\x0c\n\x04user\x18\x01 \x01(\t\"\x1a\n\nGetRequest\x12\x0c\n\x04user\x18\x01 \x01(\t\"@\n\nLoginReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrormessage\x18\x02 \x01(\t\x12\x0c\n\x04user\x18\x03 \x01(\t\"A\n\x0bLogoutReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrormessage\x18\x02 \x01(\t\x12\x0c\n\x04user\x18\x03 \x01(\t\"Q\n\tListReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrormessage\x18\x02 \x01(\t\x12\x10\n\x08wildcard\x18\x03 \x01(\t\x12\x0c\n\x04user\x18\x04 \x03(\t\"A\n\x0b\x44\x65leteReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrormessage\x18\x02 \x01(\t\x12\x0c\n\x04user\x18\x03 \x01(\t\"`\n\tSendReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrormessage\x18\x02 \x01(\t\x12\x0c\n\x04user\x18\x03 \x01(\t\x12\x0f\n\x07message\x18\x04 \x01(\t\x12\x0e\n\x06target\x18\x05 \x01(\t\"B\n\rUnreadMessage\x12\x0e\n\x06sender\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x10\n\x08receiver\x18\x03 \x01(\t\"Q\n\x08GetReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrormessage\x18\x02 \x01(\t\x12\x1f\n\x07message\x18\x03 \x03(\x0b\x32\x0e.UnreadMessage\"E\n\x0cJaredMessage\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrormessage\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t2\xf7\x03\n\rClientHandler\x12\'\n\tListUsers\x12\x0c.ListRequest\x1a\n.ListReply\"\x00\x12%\n\x05Login\x12\r.LoginRequest\x1a\x0b.LoginReply\"\x00\x12(\n\x06Logout\x12\x0e.LogoutRequest\x1a\x0c.LogoutReply\"\x00\x12\"\n\x04Send\x12\x0c.SendRequest\x1a\n.SendReply\"\x00\x12\'\n\x0bGetMessages\x12\x0b.GetRequest\x1a\t.GetReply\"\x00\x12(\n\x06\x44\x65lete\x12\x0e.DeleteRequest\x1a\x0c.DeleteReply\"\x00\x12,\n\nGetBackups\x12\x0e.BackupRequest\x1a\x0c.BackupReply\"\x00\x12\"\n\x07\x41\x64\x64User\x12\r.LoginRequest\x1a\x06.Empty\"\x00\x12&\n\nRemoveUser\x12\x0e.DeleteRequest\x1a\x06.Empty\"\x00\x12,\n\rSetUserStatus\x12\x11.SetStatusRequest\x1a\x06.Empty\"\x00\x12$\n\nAddMessage\x12\x0c.SendRequest\x1a\x06.Empty\"\x00\x12\'\n\x0e\x44\x65leteMessages\x12\x0b.GetRequest\x1a\x06.Empty\"\x00\x42\x06\xa2\x02\x03HLWb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\242\002\003HLW'
  _EMPTY._serialized_start=14
  _EMPTY._serialized_end=21
  _SETSTATUSREQUEST._serialized_start=23
  _SETSTATUSREQUEST._serialized_end=71
  _SERVERINFO._serialized_start=73
  _SERVERINFO._serialized_end=113
  _BACKUPREQUEST._serialized_start=115
  _BACKUPREQUEST._serialized_end=130
  _BACKUPREPLY._serialized_start=132
  _BACKUPREPLY._serialized_end=216
  _LOGINREQUEST._serialized_start=218
  _LOGINREQUEST._serialized_end=246
  _LOGOUTREQUEST._serialized_start=248
  _LOGOUTREQUEST._serialized_end=277
  _LISTREQUEST._serialized_start=279
  _LISTREQUEST._serialized_end=306
  _SENDREQUEST._serialized_start=308
  _SENDREQUEST._serialized_end=368
  _DELETEREQUEST._serialized_start=370
  _DELETEREQUEST._serialized_end=399
  _GETREQUEST._serialized_start=401
  _GETREQUEST._serialized_end=427
  _LOGINREPLY._serialized_start=429
  _LOGINREPLY._serialized_end=493
  _LOGOUTREPLY._serialized_start=495
  _LOGOUTREPLY._serialized_end=560
  _LISTREPLY._serialized_start=562
  _LISTREPLY._serialized_end=643
  _DELETEREPLY._serialized_start=645
  _DELETEREPLY._serialized_end=710
  _SENDREPLY._serialized_start=712
  _SENDREPLY._serialized_end=808
  _UNREADMESSAGE._serialized_start=810
  _UNREADMESSAGE._serialized_end=876
  _GETREPLY._serialized_start=878
  _GETREPLY._serialized_end=959
  _JAREDMESSAGE._serialized_start=961
  _JAREDMESSAGE._serialized_end=1030
  _CLIENTHANDLER._serialized_start=1033
  _CLIENTHANDLER._serialized_end=1536
# @@protoc_insertion_point(module_scope)
