from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CheckReply(_message.Message):
    __slots__ = ["errormessage", "sendupdate", "status"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    SENDUPDATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    errormessage: str
    sendupdate: bool
    status: int
    def __init__(self, status: _Optional[int] = ..., errormessage: _Optional[str] = ..., sendupdate: bool = ...) -> None: ...

class CheckRequest(_message.Message):
    __slots__ = ["clock", "hash", "user"]
    CLOCK_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    clock: int
    hash: bytes
    user: str
    def __init__(self, user: _Optional[str] = ..., hash: _Optional[bytes] = ..., clock: _Optional[int] = ...) -> None: ...

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

class Metadata(_message.Message):
    __slots__ = ["MAC", "clock", "filename", "filepath", "hash", "user"]
    CLOCK_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    FILEPATH_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    MAC: int
    MAC_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    clock: int
    filename: str
    filepath: str
    hash: bytes
    user: str
    def __init__(self, clock: _Optional[int] = ..., user: _Optional[str] = ..., hash: _Optional[bytes] = ..., MAC: _Optional[int] = ..., filename: _Optional[str] = ..., filepath: _Optional[str] = ...) -> None: ...

class SyncReply(_message.Message):
    __slots__ = ["file", "meta", "will_receive"]
    FILE_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    WILL_RECEIVE_FIELD_NUMBER: _ClassVar[int]
    file: bytes
    meta: Metadata
    will_receive: bool
    def __init__(self, will_receive: bool = ..., meta: _Optional[_Union[Metadata, _Mapping]] = ..., file: _Optional[bytes] = ...) -> None: ...

class SyncRequest(_message.Message):
    __slots__ = ["metadata", "user"]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    metadata: _containers.RepeatedCompositeFieldContainer[Metadata]
    user: str
    def __init__(self, user: _Optional[str] = ..., metadata: _Optional[_Iterable[_Union[Metadata, _Mapping]]] = ...) -> None: ...

class UnreadMessage(_message.Message):
    __slots__ = ["message", "receiver", "sender"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_FIELD_NUMBER: _ClassVar[int]
    SENDER_FIELD_NUMBER: _ClassVar[int]
    message: str
    receiver: str
    sender: str
    def __init__(self, sender: _Optional[str] = ..., message: _Optional[str] = ..., receiver: _Optional[str] = ...) -> None: ...

class UploadReply(_message.Message):
    __slots__ = ["errormessage", "status", "success"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    errormessage: str
    status: int
    success: bool
    def __init__(self, status: _Optional[int] = ..., errormessage: _Optional[str] = ..., success: bool = ...) -> None: ...

class UploadRequest(_message.Message):
    __slots__ = ["file", "meta"]
    FILE_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    file: bytes
    meta: Metadata
    def __init__(self, meta: _Optional[_Union[Metadata, _Mapping]] = ..., file: _Optional[bytes] = ...) -> None: ...
