from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

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

class HelloReply(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class HelloRequest(_message.Message):
    __slots__ = ["message", "user"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    message: str
    user: str
    def __init__(self, user: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

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
    __slots__ = ["errormessage", "message", "status", "user"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    errormessage: str
    message: _containers.RepeatedScalarFieldContainer[str]
    status: int
    user: str
    def __init__(self, status: _Optional[int] = ..., errormessage: _Optional[str] = ..., user: _Optional[str] = ..., message: _Optional[_Iterable[str]] = ...) -> None: ...

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

class UnreadMessage(_message.Message):
    __slots__ = ["message", "receiver", "sender"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_FIELD_NUMBER: _ClassVar[int]
    SENDER_FIELD_NUMBER: _ClassVar[int]
    message: str
    receiver: str
    sender: str
    def __init__(self, sender: _Optional[str] = ..., message: _Optional[str] = ..., receiver: _Optional[str] = ...) -> None: ...
