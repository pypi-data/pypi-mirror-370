from dataclasses import dataclass
from enum import Enum

from agentbox.envd.filesystem_agentbox.filesystem_pb2 import AgentBoxFileType


class AgentBoxFilesystemEventType(Enum):
    """
    Enum representing the type of filesystem event.
    """

    CHMOD = "chmod"
    """
    Filesystem object permissions were changed.
    """
    CREATE = "create"
    """
    Filesystem object was created.
    """
    REMOVE = "remove"
    """
    Filesystem object was removed.
    """
    RENAME = "rename"
    """
    Filesystem object was renamed.
    """
    WRITE = "write"
    """
    Filesystem object was written to.
    """


def map_event_type(event: AgentBoxFileType):
    if event == AgentBoxFileType.EVENT_TYPE_CHMOD:
        return AgentBoxFilesystemEventType.CHMOD
    elif event == AgentBoxFileType.EVENT_TYPE_CREATE:
        return AgentBoxFilesystemEventType.CREATE
    elif event == AgentBoxFileType.EVENT_TYPE_REMOVE:
        return AgentBoxFilesystemEventType.REMOVE
    elif event == AgentBoxFileType.EVENT_TYPE_RENAME:
        return AgentBoxFilesystemEventType.RENAME
    elif event == AgentBoxFileType.EVENT_TYPE_WRITE:
        return AgentBoxFilesystemEventType.WRITE


@dataclass
class AgentBoxFilesystemEvent:
    """
    Contains information about the filesystem event - the name of the file and the type of the event.
    """

    name: str
    """
    Relative path to the filesystem object.
    """
    type: AgentBoxFilesystemEventType
    """
    Filesystem operation event type.
    """
