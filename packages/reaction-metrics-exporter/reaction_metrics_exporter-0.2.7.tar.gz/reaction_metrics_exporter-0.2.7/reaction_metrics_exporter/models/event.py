from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Event(ABC):
    """
    describe events as shown in the logs
    """

    time: datetime


@dataclass
class Exit(Event):
    """a shadow class to indicate reaction has stopped"""


@dataclass
class Command(Event):
    """describe commands launched when reaction's state changes"""

    command: tuple[str]
    status: bool
    code: int


@dataclass
class Start(Command):
    pass


@dataclass
class Stop(Command):
    pass


@dataclass
class StreamEvent(Event, ABC):
    """
    events that can happen to stream; mostly errors.
    possible errors can be found in reaction code; limit errors to stream and filter stuff.
    for example corrupted database is not included.
    """

    stream: str
    type: str = field(init=False)


@dataclass
class StreamStart(StreamEvent):
    def __post_init__(self):
        self.type = "start"


@dataclass
class StreamExit(StreamEvent):
    def __post_init__(self):
        self.type = "exit"


@dataclass
class StreamTimeout(StreamEvent):
    def __post_init__(self):
        self.type = "timeout"


@dataclass
class StreamUnreadable(StreamEvent):
    def __post_init__(self):
        self.type = "read"


@dataclass
class StreamUnexecutable(StreamEvent):
    def __post_init__(self):
        self.type = "exec"


@dataclass
class LogEvent(Event):
    """
    describe something done by reaction regarding logs
    """

    stream: str
    filter: str


@dataclass
class Match(LogEvent):
    matches: tuple[str, ...]


@dataclass
class Action(LogEvent):
    action: str
    command: tuple[str, ...]
    status: bool
