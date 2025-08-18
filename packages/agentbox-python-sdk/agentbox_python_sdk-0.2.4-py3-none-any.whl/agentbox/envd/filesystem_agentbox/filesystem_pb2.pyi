from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AgentBoxFileType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILE_TYPE_UNSPECIFIED: _ClassVar[AgentBoxFileType]
    FILE_TYPE_FILE: _ClassVar[AgentBoxFileType]
    FILE_TYPE_DIRECTORY: _ClassVar[AgentBoxFileType]

class AgentBoxEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_TYPE_UNSPECIFIED: _ClassVar[AgentBoxEventType]
    EVENT_TYPE_CREATE: _ClassVar[AgentBoxEventType]
    EVENT_TYPE_WRITE: _ClassVar[AgentBoxEventType]
    EVENT_TYPE_REMOVE: _ClassVar[AgentBoxEventType]
    EVENT_TYPE_RENAME: _ClassVar[AgentBoxEventType]
    EVENT_TYPE_CHMOD: _ClassVar[AgentBoxEventType]
FILE_TYPE_UNSPECIFIED: AgentBoxFileType
FILE_TYPE_FILE: AgentBoxFileType
FILE_TYPE_DIRECTORY: AgentBoxFileType
EVENT_TYPE_UNSPECIFIED: AgentBoxEventType
EVENT_TYPE_CREATE: AgentBoxEventType
EVENT_TYPE_WRITE: AgentBoxEventType
EVENT_TYPE_REMOVE: AgentBoxEventType
EVENT_TYPE_RENAME: AgentBoxEventType
EVENT_TYPE_CHMOD: AgentBoxEventType

class AgentBoxMoveRequest(_message.Message):
    __slots__ = ("source", "destination")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    source: str
    destination: str
    def __init__(self, source: _Optional[str] = ..., destination: _Optional[str] = ...) -> None: ...

class AgentBoxMoveResponse(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: AgentBoxEntryInfo
    def __init__(self, entry: _Optional[_Union[AgentBoxEntryInfo, _Mapping]] = ...) -> None: ...

class AgentBoxMakeDirRequest(_message.Message):
    __slots__ = ("path",)
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class AgentBoxMakeDirResponse(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: AgentBoxEntryInfo
    def __init__(self, entry: _Optional[_Union[AgentBoxEntryInfo, _Mapping]] = ...) -> None: ...

class AgentBoxRemoveRequest(_message.Message):
    __slots__ = ("path",)
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class AgentBoxRemoveResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AgentBoxStatRequest(_message.Message):
    __slots__ = ("path",)
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class AgentBoxStatResponse(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: AgentBoxEntryInfo
    def __init__(self, entry: _Optional[_Union[AgentBoxEntryInfo, _Mapping]] = ...) -> None: ...

class AgentBoxEntryInfo(_message.Message):
    __slots__ = ("name", "type", "path", "size", "mode", "permissions", "owner", "group", "modified_time", "symlink_target")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_TIME_FIELD_NUMBER: _ClassVar[int]
    SYMLINK_TARGET_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: AgentBoxFileType
    path: str
    size: int
    mode: int
    permissions: str
    owner: str
    group: str
    modified_time: _timestamp_pb2.Timestamp
    symlink_target: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[_Union[AgentBoxFileType, str]] = ..., path: _Optional[str] = ..., size: _Optional[int] = ..., mode: _Optional[int] = ..., permissions: _Optional[str] = ..., owner: _Optional[str] = ..., group: _Optional[str] = ..., modified_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., symlink_target: _Optional[str] = ...) -> None: ...

class AgentBoxListDirRequest(_message.Message):
    __slots__ = ("path", "depth")
    PATH_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    path: str
    depth: int
    def __init__(self, path: _Optional[str] = ..., depth: _Optional[int] = ...) -> None: ...

class AgentBoxListDirResponse(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[AgentBoxEntryInfo]
    def __init__(self, entries: _Optional[_Iterable[_Union[AgentBoxEntryInfo, _Mapping]]] = ...) -> None: ...

class AgentBoxWatchDirRequest(_message.Message):
    __slots__ = ("path", "recursive")
    PATH_FIELD_NUMBER: _ClassVar[int]
    RECURSIVE_FIELD_NUMBER: _ClassVar[int]
    path: str
    recursive: bool
    def __init__(self, path: _Optional[str] = ..., recursive: bool = ...) -> None: ...

class AgentBoxFilesystemEvent(_message.Message):
    __slots__ = ("name", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: AgentBoxEventType
    def __init__(self, name: _Optional[str] = ..., type: _Optional[_Union[AgentBoxEventType, str]] = ...) -> None: ...

class AgentBoxWatchDirResponse(_message.Message):
    __slots__ = ("start", "filesystem", "keepalive")
    class AgentBoxStartEvent(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class AgentBoxKeepAlive(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    START_FIELD_NUMBER: _ClassVar[int]
    FILESYSTEM_FIELD_NUMBER: _ClassVar[int]
    KEEPALIVE_FIELD_NUMBER: _ClassVar[int]
    start: AgentBoxWatchDirResponse.AgentBoxStartEvent
    filesystem: AgentBoxFilesystemEvent
    keepalive: AgentBoxWatchDirResponse.AgentBoxKeepAlive
    def __init__(self, start: _Optional[_Union[AgentBoxWatchDirResponse.AgentBoxStartEvent, _Mapping]] = ..., filesystem: _Optional[_Union[AgentBoxFilesystemEvent, _Mapping]] = ..., keepalive: _Optional[_Union[AgentBoxWatchDirResponse.AgentBoxKeepAlive, _Mapping]] = ...) -> None: ...

class AgentBoxCreateWatcherRequest(_message.Message):
    __slots__ = ("path", "recursive")
    PATH_FIELD_NUMBER: _ClassVar[int]
    RECURSIVE_FIELD_NUMBER: _ClassVar[int]
    path: str
    recursive: bool
    def __init__(self, path: _Optional[str] = ..., recursive: bool = ...) -> None: ...

class AgentBoxCreateWatcherResponse(_message.Message):
    __slots__ = ("watcher_id",)
    WATCHER_ID_FIELD_NUMBER: _ClassVar[int]
    watcher_id: str
    def __init__(self, watcher_id: _Optional[str] = ...) -> None: ...

class AgentBoxGetWatcherEventsRequest(_message.Message):
    __slots__ = ("watcher_id",)
    WATCHER_ID_FIELD_NUMBER: _ClassVar[int]
    watcher_id: str
    def __init__(self, watcher_id: _Optional[str] = ...) -> None: ...

class AgentBoxGetWatcherEventsResponse(_message.Message):
    __slots__ = ("events",)
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[AgentBoxFilesystemEvent]
    def __init__(self, events: _Optional[_Iterable[_Union[AgentBoxFilesystemEvent, _Mapping]]] = ...) -> None: ...

class AgentBoxRemoveWatcherRequest(_message.Message):
    __slots__ = ("watcher_id",)
    WATCHER_ID_FIELD_NUMBER: _ClassVar[int]
    watcher_id: str
    def __init__(self, watcher_id: _Optional[str] = ...) -> None: ...

class AgentBoxRemoveWatcherResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
