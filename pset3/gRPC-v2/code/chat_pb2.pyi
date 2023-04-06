from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BackupReply(_message.Message):
    __slots__ = ["errormessage", "serverinfo", "status"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    SERVERINFO_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    errormessage: str
    serverinfo: _containers.RepeatedCompositeFieldContainer[ServerInfo]
    status: int
    def __init__(self, status: _Optional[int] = ..., errormessage: _Optional[str] = ..., serverinfo: _Optional[_Iterable[_Union[ServerInfo, _Mapping]]] = ...) -> None: ...

class BackupRequest(_message.Message):
    __slots__ = ["serverinfo"]
    SERVERINFO_FIELD_NUMBER: _ClassVar[int]
    serverinfo: _containers.RepeatedCompositeFieldContainer[ServerInfo]
    def __init__(self, serverinfo: _Optional[_Iterable[_Union[ServerInfo, _Mapping]]] = ...) -> None: ...

class DeleteReply(_message.Message):
    __slots__ = ["errormessage", "status", "user"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    errormessage: str
    status: int
    user: str
    def __init__(self, status: _Optional[int] = ..., errormessage: _Optional[str] = ..., user: _Optional[str] = ...) -> None: ...

class DeleteRequest(_message.Message):
    __slots__ = ["user"]
    USER_FIELD_NUMBER: _ClassVar[int]
    user: str
    def __init__(self, user: _Optional[str] = ...) -> None: ...

class GetReply(_message.Message):
    __slots__ = ["errormessage", "message", "status"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    errormessage: str
    message: _containers.RepeatedCompositeFieldContainer[UnreadMessage]
    status: int
    def __init__(self, status: _Optional[int] = ..., errormessage: _Optional[str] = ..., message: _Optional[_Iterable[_Union[UnreadMessage, _Mapping]]] = ...) -> None: ...

class GetRequest(_message.Message):
    __slots__ = ["user"]
    USER_FIELD_NUMBER: _ClassVar[int]
    user: str
    def __init__(self, user: _Optional[str] = ...) -> None: ...

class JaredMessage(_message.Message):
    __slots__ = ["content", "errormessage", "status"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    content: str
    errormessage: str
    status: int
    def __init__(self, status: _Optional[int] = ..., errormessage: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class ListReply(_message.Message):
    __slots__ = ["errormessage", "status", "user", "wildcard"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    WILDCARD_FIELD_NUMBER: _ClassVar[int]
    errormessage: str
    status: int
    user: _containers.RepeatedScalarFieldContainer[str]
    wildcard: str
    def __init__(self, status: _Optional[int] = ..., errormessage: _Optional[str] = ..., wildcard: _Optional[str] = ..., user: _Optional[_Iterable[str]] = ...) -> None: ...

class ListRequest(_message.Message):
    __slots__ = ["args"]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    args: str
    def __init__(self, args: _Optional[str] = ...) -> None: ...

class LoginReply(_message.Message):
    __slots__ = ["errormessage", "status", "user"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    errormessage: str
    status: int
    user: str
    def __init__(self, status: _Optional[int] = ..., errormessage: _Optional[str] = ..., user: _Optional[str] = ...) -> None: ...

class LoginRequest(_message.Message):
    __slots__ = ["user"]
    USER_FIELD_NUMBER: _ClassVar[int]
    user: str
    def __init__(self, user: _Optional[str] = ...) -> None: ...

class LogoutReply(_message.Message):
    __slots__ = ["errormessage", "status", "user"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    errormessage: str
    status: int
    user: str
    def __init__(self, status: _Optional[int] = ..., errormessage: _Optional[str] = ..., user: _Optional[str] = ...) -> None: ...

class LogoutRequest(_message.Message):
    __slots__ = ["user"]
    USER_FIELD_NUMBER: _ClassVar[int]
    user: str
    def __init__(self, user: _Optional[str] = ...) -> None: ...

class SendReply(_message.Message):
    __slots__ = ["errormessage", "message", "status", "target", "user"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    errormessage: str
    message: str
    status: int
    target: str
    user: str
    def __init__(self, status: _Optional[int] = ..., errormessage: _Optional[str] = ..., user: _Optional[str] = ..., message: _Optional[str] = ..., target: _Optional[str] = ...) -> None: ...

class SendRequest(_message.Message):
    __slots__ = ["message", "target", "user"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    message: str
    target: str
    user: str
    def __init__(self, user: _Optional[str] = ..., message: _Optional[str] = ..., target: _Optional[str] = ...) -> None: ...

class ServerInfo(_message.Message):
    __slots__ = ["host", "port"]
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    host: str
    port: str
    def __init__(self, host: _Optional[str] = ..., port: _Optional[str] = ...) -> None: ...

class UnreadMessage(_message.Message):
    __slots__ = ["message", "receiver", "sender"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_FIELD_NUMBER: _ClassVar[int]
    SENDER_FIELD_NUMBER: _ClassVar[int]
    message: str
    receiver: str
    sender: str
    def __init__(self, sender: _Optional[str] = ..., message: _Optional[str] = ..., receiver: _Optional[str] = ...) -> None: ...
