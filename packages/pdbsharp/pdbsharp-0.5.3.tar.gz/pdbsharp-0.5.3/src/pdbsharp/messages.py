import enum
from typing import Iterable

from textual.message import Message


class PdbState(enum.Enum):
    Unattached = enum.auto()
    Attached = enum.auto()
    Attaching = enum.auto()


class PdbMessageType(enum.Enum):
    COMMAND = enum.auto()
    EOF = enum.auto()
    INT = enum.auto()


class MessageToRepl(Message):
    def __init__(self, type: PdbMessageType, content: str | None = None) -> None:
        self.type = type
        self.content = content
        super().__init__()


class MessageFromRepl(Message):
    def __init__(self, text):
        self.text = text
        super().__init__()


class StdoutMessageFromRepl(Message):
    def __init__(self, text: str):
        self.text = text
        super().__init__()


class TabAddMessage(Message):
    def __init__(
        self,
        pid: int,
        capture_io=False,
        commands: Iterable[str] | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.pid = pid
        self.capture_io = capture_io
        self.commands = commands


class TabFocusMessage(Message):
    def __init__(self, tab_id: str, query: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tab_id = tab_id
        self.query = query


class TabDeleteMessage(Message):
    # Represents a message to the main app to remove an existing tab
    def __init__(self, tab_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tab_id = tab_id
