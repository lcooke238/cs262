from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

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
    __slots__ = ["name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class HelloReply(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class HelloRequest(_message.Message):
    __slots__ = ["message", "name"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    message: str
    name: str
    def __init__(self, name: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

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
    __slots__ = ["name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

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
    __slots__ = ["name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

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
    __slots__ = ["message", "name", "target"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    message: str
    name: str
    target: str
    def __init__(self, name: _Optional[str] = ..., message: _Optional[str] = ..., target: _Optional[str] = ...) -> None: ...
