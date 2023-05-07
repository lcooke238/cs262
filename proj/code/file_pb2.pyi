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
    __slots__ = []
    def __init__(self) -> None: ...

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

class Clock(_message.Message):
    __slots__ = ["clock"]
    CLOCK_FIELD_NUMBER: _ClassVar[int]
    clock: int
    def __init__(self, clock: _Optional[int] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["clock", "files", "ownerships"]
    CLOCK_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    OWNERSHIPS_FIELD_NUMBER: _ClassVar[int]
    clock: Clock
    files: _containers.RepeatedCompositeFieldContainer[File]
    ownerships: _containers.RepeatedCompositeFieldContainer[Ownership]
    def __init__(self, clock: _Optional[_Union[Clock, _Mapping]] = ..., files: _Optional[_Iterable[_Union[File, _Mapping]]] = ..., ownerships: _Optional[_Iterable[_Union[Ownership, _Mapping]]] = ...) -> None: ...

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

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class File(_message.Message):
    __slots__ = ["MAC", "clock", "file", "filename", "filepath", "hash", "id", "src"]
    CLOCK_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    FILEPATH_FIELD_NUMBER: _ClassVar[int]
    FILE_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MAC: int
    MAC_FIELD_NUMBER: _ClassVar[int]
    SRC_FIELD_NUMBER: _ClassVar[int]
    clock: int
    file: bytes
    filename: str
    filepath: str
    hash: bytes
    id: int
    src: str
    def __init__(self, id: _Optional[int] = ..., filename: _Optional[str] = ..., filepath: _Optional[str] = ..., src: _Optional[str] = ..., file: _Optional[bytes] = ..., MAC: _Optional[int] = ..., hash: _Optional[bytes] = ..., clock: _Optional[int] = ...) -> None: ...

class ListReply(_message.Message):
    __slots__ = ["errormessage", "files", "status"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    errormessage: str
    files: _containers.RepeatedScalarFieldContainer[str]
    status: int
    def __init__(self, status: _Optional[int] = ..., errormessage: _Optional[str] = ..., files: _Optional[_Iterable[str]] = ...) -> None: ...

class ListRequest(_message.Message):
    __slots__ = ["user"]
    USER_FIELD_NUMBER: _ClassVar[int]
    user: str
    def __init__(self, user: _Optional[str] = ...) -> None: ...

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

class Ownership(_message.Message):
    __slots__ = ["file_id", "permissions", "username"]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    file_id: int
    permissions: int
    username: str
    def __init__(self, username: _Optional[str] = ..., file_id: _Optional[int] = ..., permissions: _Optional[int] = ...) -> None: ...

class ServerInfo(_message.Message):
    __slots__ = ["host", "port"]
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    host: str
    port: str
    def __init__(self, host: _Optional[str] = ..., port: _Optional[str] = ...) -> None: ...

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

class UploadAddNewRequest(_message.Message):
    __slots__ = ["id", "user"]
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    id: int
    user: str
    def __init__(self, user: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class UploadHelperRequest(_message.Message):
    __slots__ = ["file", "id", "meta", "src"]
    FILE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    SRC_FIELD_NUMBER: _ClassVar[int]
    file: bytes
    id: int
    meta: Metadata
    src: str
    def __init__(self, id: _Optional[int] = ..., meta: _Optional[_Union[Metadata, _Mapping]] = ..., src: _Optional[str] = ..., file: _Optional[bytes] = ...) -> None: ...

class UploadRemoveOldRequest(_message.Message):
    __slots__ = ["count_minus_2", "src"]
    COUNT_MINUS_2_FIELD_NUMBER: _ClassVar[int]
    SRC_FIELD_NUMBER: _ClassVar[int]
    count_minus_2: int
    src: str
    def __init__(self, src: _Optional[str] = ..., count_minus_2: _Optional[int] = ...) -> None: ...

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
