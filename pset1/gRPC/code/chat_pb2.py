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




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nchat.proto\x12\nhelloworld\"-\n\x0cHelloRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\"\x1c\n\x0cLoginRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\"\x1b\n\x0bListRequest\x12\x0c\n\x04\x61rgs\x18\x01 \x01(\t\"C\n\x12SendMessageRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0e\n\x06target\x18\x03 \x01(\t\"\x1d\n\nHelloReply\x12\x0f\n\x07message\x18\x01 \x01(\t\"-\n\nLoginReply\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\x0e\n\x06status\x18\x02 \x01(\x05\"L\n\tListReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x10\n\x08wildcard\x18\x02 \x01(\t\x12\x0f\n\x07message\x18\x03 \x01(\t\x12\x0c\n\x04user\x18\x04 \x03(\t2\x90\x02\n\rClientHandler\x12>\n\x08SayHello\x12\x18.helloworld.HelloRequest\x1a\x16.helloworld.HelloReply\"\x00\x12\x43\n\rSayHelloAgain\x12\x18.helloworld.HelloRequest\x1a\x16.helloworld.HelloReply\"\x00\x12=\n\tListUsers\x12\x17.helloworld.ListRequest\x1a\x15.helloworld.ListReply\"\x00\x12;\n\x05Login\x12\x18.helloworld.LoginRequest\x1a\x16.helloworld.LoginReply\"\x00\x42\x36\n\x1bio.grpc.examples.helloworldB\x0fHelloWorldProtoP\x01\xa2\x02\x03HLWb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\033io.grpc.examples.helloworldB\017HelloWorldProtoP\001\242\002\003HLW'
  _HELLOREQUEST._serialized_start=26
  _HELLOREQUEST._serialized_end=71
  _LOGINREQUEST._serialized_start=73
  _LOGINREQUEST._serialized_end=101
  _LISTREQUEST._serialized_start=103
  _LISTREQUEST._serialized_end=130
  _SENDMESSAGEREQUEST._serialized_start=132
  _SENDMESSAGEREQUEST._serialized_end=199
  _HELLOREPLY._serialized_start=201
  _HELLOREPLY._serialized_end=230
  _LOGINREPLY._serialized_start=232
  _LOGINREPLY._serialized_end=277
  _LISTREPLY._serialized_start=279
  _LISTREPLY._serialized_end=355
  _CLIENTHANDLER._serialized_start=358
  _CLIENTHANDLER._serialized_end=630
# @@protoc_insertion_point(module_scope)
