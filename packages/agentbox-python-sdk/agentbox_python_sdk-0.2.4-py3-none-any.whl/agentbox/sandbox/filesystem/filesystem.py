from dataclasses import dataclass
from enum import Enum
from typing import IO, Optional, Union

from agentbox.envd.filesystem_agentbox import filesystem_pb2


class AgentBoxFileType(Enum):
    """
    Enum representing the type of filesystem object.
    """

    FILE = "file"
    """
    Filesystem object is a file.
    """
    DIR = "dir"
    """
    Filesystem object is a directory.
    """


def map_file_type(ft: filesystem_pb2.AgentBoxFileType):
    if ft == filesystem_pb2.AgentBoxFileType.FILE_TYPE_FILE:
        return AgentBoxFileType.FILE
    elif ft == filesystem_pb2.AgentBoxFileType.FILE_TYPE_DIRECTORY:
        return AgentBoxFileType.DIR


@dataclass
class AgentBoxEntryInfo:
    """
    Sandbox filesystem object information.
    """

    name: str
    """
    Name of the filesystem object.
    """
    type: Optional[AgentBoxFileType]
    """
    Type of the filesystem object.
    """
    path: str
    """
    Path to the filesystem object.
    """


@dataclass
class AgentBoxWriteEntry:
    """
    Contains path and data of the file to be written to the filesystem.
    """

    path: str
    data: Union[str, bytes, IO]
