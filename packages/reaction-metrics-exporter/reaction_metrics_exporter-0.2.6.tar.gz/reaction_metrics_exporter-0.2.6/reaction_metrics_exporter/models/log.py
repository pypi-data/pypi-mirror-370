from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    # Syslog-like
    EMER = 0
    ALERT = 1
    CRIT = 2
    ERROR = 3
    WARN = 4
    NOTICE = 5
    INFO = 6
    DEBUG = 7
    # Additionnal field
    UNKNOWN = 8


@dataclass
class Log:
    time: datetime
    level: LogLevel
    message: str
