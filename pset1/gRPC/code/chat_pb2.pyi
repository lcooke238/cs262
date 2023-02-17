from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

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
    __slots__ = ["message", "status", "user", "wildcard"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    WILDCARD_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: int
    user: _containers.RepeatedScalarFieldContainer[str]
    wildcard: str
    def __init__(self, status: _Optional[int] = ..., wildcard: _Optional[str] = ..., message: _Optional[str] = ..., user: _Optional[_Iterable[str]] = ...) -> None: ...

class ListRequest(_message.Message):
    __slots__ = ["args"]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    args: str
    def __init__(self, args: _Optional[str] = ...) -> None: ...

class LoginReply(_message.Message):
    __slots__ = ["message", "status"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: int
    def __init__(self, message: _Optional[str] = ..., status: _Optional[int] = ...) -> None: ...

class LoginRequest(_message.Message):
    __slots__ = ["name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class SendMessageRequest(_message.Message):
    __slots__ = ["message", "name", "target"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    message: str
    name: str
    target: str
    def __init__(self, name: _Optional[str] = ..., message: _Optional[str] = ..., target: _Optional[str] = ...) -> None: ...
