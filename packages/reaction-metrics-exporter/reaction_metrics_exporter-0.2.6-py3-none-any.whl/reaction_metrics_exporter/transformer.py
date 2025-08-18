from abc import ABC
from ast import literal_eval
from datetime import datetime
import json
import re

import structlog

from .models.config import Config
from .models.event import (
    Action,
    Event,
    Exit,
    LogEvent,
    Match,
    Start,
    Stop,
    StreamExit,
    StreamStart,
    StreamTimeout,
    StreamUnexecutable,
    StreamUnreadable,
)
from .models.exception import UnsupportedLine, UnsupportedLog
from .models.log import Log

logger = structlog.get_logger()
config = Config.get_config()


class Transformer(ABC):
    REGEX_EVENT = re.compile(
        r"""
        (?P<status>INFO|ERROR)\s
        (?P<stream>.+?)
        \.
        (?P<filter>.+?)
        (?P<sep>\.)? # optional dot if event is an action (in which case we have filter.action)
        (?(sep)(?P<action>.+?)) # if dot found, match action name
        :\s(?P<type>match|run) # back to generic match
        \s(?P<params>\[.+?\])
        """,
        re.VERBOSE,
    )

    REGEX_COMMAND = re.compile(
        r"""
        (?P<status>INFO|ERROR)\s
        (?P<state>.+?)\s
        command:\srun\s
        (?P<command>\[.+?\])
        (?P<sep>:\s)? # only found if action failed
        (?(sep)exit\scode:\s)
        (?(sep)(?P<code>\d+))
        """,
        re.VERBOSE,
    )

    REGEX_STREAM_EXEC = re.compile(r"ERROR could not execute stream (?P<stream>.+?) cmd:.+")
    REGEX_STREAM_EXIT = re.compile(r"ERROR stream (?P<stream>.+?) exited:.+")
    REGEX_STREAM_TERMINATE = re.compile(r"ERROR child process of stream (?P<stream>.+?) did not terminate")
    REGEX_STREAM_READ = re.compile(r"ERROR impossible to read output from stream (?P<stream>.+?):.+")
    REGEX_STREAM_START = re.compile(r"INFO (?P<stream>.+?): start.+")

    REGEX_REACTION_EXIT = re.compile("INFO received SIGTERM, closing streams...")

    @classmethod
    def to_event(cls, log: Log) -> Event:
        message = log.message.strip()
        # test different type of logs
        if m := cls.REGEX_EVENT.match(message):
            return cls._to_log_event(log.time, m)
        if m := cls.REGEX_COMMAND.match(message):
            return cls._to_command_event(log.time, m)

        stream_event = None
        if m := cls.REGEX_STREAM_EXEC.match(message):
            stream_event = StreamUnexecutable(log.time, m.groupdict()["stream"])
        elif m := cls.REGEX_STREAM_EXIT.match(message):
            stream_event = StreamExit(log.time, m.groupdict()["stream"])
        elif m := cls.REGEX_STREAM_TERMINATE.match(message):
            stream_event = StreamTimeout(log.time, m.groupdict()["stream"])
        elif m := cls.REGEX_STREAM_READ.match(message):
            stream_event = StreamUnreadable(log.time, m.groupdict()["stream"])
        elif m := cls.REGEX_STREAM_START.match(message):
            stream_event = StreamStart(log.time, m.groupdict()["stream"])
        if stream_event:
            logger.debug(f'parsed log at "{stream_event.time}": got {stream_event.stream=}, {stream_event.type}')
            return stream_event

        if m := cls.REGEX_REACTION_EXIT.match(message):
            return Exit(log.time)

        raise UnsupportedLog(f"unmatched: {log.message.strip()}")

    @classmethod
    def _to_log_event(cls, t: datetime, m: re.Match[str]) -> LogEvent:
        groups: dict[str, str] = m.groupdict()
        stream_name: str = groups["stream"].strip()
        filter_name: str = groups["filter"].strip()
        action_name: str = groups["action"]
        event_type: str = groups["type"].strip()
        params: str = groups["params"].strip()

        logger.debug(f'parsed log at "{t}"; got {stream_name=}, {filter_name=}, {action_name=}, {event_type=}, {params=}')
        # run = action
        if event_type == "run":
            # command format is is ["cmd" "arg0"...] with no commas
            # transform to array manually
            cmd_line: str = params.lstrip('["').rstrip('"]')
            command: tuple[str, ...] = tuple([part for part in cmd_line.split('" "')])

            action = Action(t, stream_name, filter_name, action_name, command, True)
            return action

        if event_type == "match":
            # expected format is ["match1", "match2"]
            # not perfectly safe (can e.g. overload memory) but not subject to eval-like stuff
            try:
                matches: tuple[str] = tuple(json.loads(params))
                return Match(t, stream_name, filter_name, matches)
            except json.JSONDecodeError as e:
                raise UnsupportedLog(f"cannot parse matches {params}: {e}")

        raise UnsupportedLog(f"type: {event_type}")

    @classmethod
    def _to_command_event(cls, t: datetime, m: re.Match[str]) -> Event:
        groups = m.groupdict()
        state = groups["state"]
        command = groups["command"]
        status = cls._to_status(groups["status"])
        # return code is not in logs in no errors
        code = 0 if status else int(groups["code"])
        logger.debug(f'parsed log at "{t}"; got {state=}, {command=}, {status=}, {code=}')
        match state:
            case "start":
                event_class = Start
            case "stop":
                event_class = Stop
            case _:
                raise UnsupportedLog(f"state: {state}")
        try:
            command_args = tuple(literal_eval(command))
        except (SyntaxError, ValueError) as e:
            raise UnsupportedLog(f"cannot parse command {command}: {e}")
        return event_class(t, command_args, status, code)

    @staticmethod
    def _to_status(status: str):
        match status:
            case "INFO":
                return True
            case "ERROR":
                return False
            case _:
                raise UnsupportedLine(f"unknown status: {status}")
