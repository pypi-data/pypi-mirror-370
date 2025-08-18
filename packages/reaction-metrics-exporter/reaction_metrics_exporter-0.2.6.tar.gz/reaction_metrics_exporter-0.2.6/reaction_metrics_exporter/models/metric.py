# for forward references
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
import dataclasses
from typing import Self

import jinja2
import structlog

from ..reaction import Reaction
from .config import Config
from .event import Action, Command, Event, Match, Start, Stop, StreamEvent


logger = structlog.get_logger()
config = Config.get_config()


@dataclass(frozen=True)
class MatchMetric:
    stream: str
    filter: str
    # each element of pattern has its match at same index in matches
    patterns: tuple[str, ...]
    matches: tuple[str, ...]

    # to render matches values
    _env = jinja2.Environment()

    @property
    def labels(self) -> tuple[str, ...]:
        return ("stream", "filter", *self.patterns)

    @property
    def values(self) -> tuple[str, ...]:
        return (self.stream, self.filter, *self.matches)

    @classmethod
    def add(cls, match: Match, metrics: ReactionMetrics) -> MatchMetric:
        patterns: tuple[str, ...] = Reaction.patterns(match.stream, match.filter, match.matches)
        matches: tuple[str, ...] = config.render(match.stream, match.filter, patterns, match.matches)
        metric = cls(match.stream, match.filter, patterns, matches)
        # actions need patterns anyway
        metrics.last_match[(match.stream, match.filter)] = metric
        # remove patterns
        if not config.matches_extra:
            metric = MatchMetric(metric.stream, metric.filter, (), ())
        logger.debug(f"new match: stream {metric.stream}, filter {metric.filter}, patterns {metric.patterns}, matches {metric.matches}")
        metrics.matches[metric] += 1
        return metric


@dataclass(frozen=True)
class ActionMetric:
    stream: str
    filter: str
    action: str
    patterns: tuple[str, ...]
    matches: tuple[str, ...]
    status: bool

    @property
    def labels(self) -> tuple[str, ...]:
        return ("stream", "filter", "action", *self.patterns)

    @property
    def values(self) -> tuple[str, ...]:
        return (self.stream, self.filter, self.action, *self.matches)

    @classmethod
    def add(cls, action: Action, metrics: ReactionMetrics) -> ActionMetric:
        # get last corresponding match to fetch patterns
        if config.actions_extra:
            if last_match := metrics.last_match.get((action.stream, action.filter)):
                patterns, matches = last_match.patterns, last_match.matches
            else:
                logger.debug(
                    f"cannot extract patterns from previous match for {action.action=}, {action.stream=}, {action.filter=}; this is normal for a delayed action with reaction having restarted."
                )
                patterns, matches = (), ()
        else:
            patterns, matches = (), ()
        metric = ActionMetric(action.stream, action.filter, action.action, patterns, matches, action.status)
        logger.debug(
            f"new action: stream {metric.stream}, filter {metric.filter}, patterns {metric.patterns}, matches {metric.matches}, action {metric.action}, status {metric.status}"
        )
        metrics.actions[metric] += 1
        return metric


@dataclass(frozen=True)
class PendingAction:
    stream: str
    filter: str
    action: str
    patterns: tuple[str, ...]
    matches: tuple[str, ...]

    @property
    def labels(self) -> tuple[str, ...]:
        return ("stream", "filter", "action", *self.patterns)

    @property
    def values(self) -> tuple[str, ...]:
        return (self.stream, self.filter, self.action, *self.matches)

    @classmethod
    def from_show(cls, stream: str, filter: str, matches_str: str, action: str) -> PendingAction:
        # reaction show uses space to delimitate matches
        # won't work if space in match
        matches = tuple(matches_str.split(" "))
        if config.pending_extra:
            patterns = Reaction.patterns(stream, filter, matches)
            matches = config.render(stream, filter, patterns, matches)
        else:
            patterns, matches = (), ()
        return cls(stream, filter, action, patterns, matches)


@dataclass(frozen=True)
class CommandMetric:
    state: str
    command: str
    status: bool
    code: int

    @property
    def labels(self) -> tuple[str, ...]:
        return tuple(dataclasses.asdict(self))

    @property
    def values(self) -> tuple[str, ...]:
        return tuple(str(value) for value in dataclasses.asdict(self).values())

    @classmethod
    def add(cls, command: Command, metrics: ReactionMetrics) -> Self:
        match command:
            case Start():
                state = "start"
            case Stop():
                state = "stop"
            case _:
                raise TypeError(f"unsupported command type: {type(command)}")
        inst = cls(state, command.command[0], command.status, command.code)
        logger.debug(f"new command: state {state}, command {command.command[0]}, status {command.status}, code {command.code}")
        metrics.commands[inst] += 1
        return inst


@dataclass(frozen=True)
class StreamMetric:
    stream: str
    type: str

    @property
    def labels(self) -> tuple[str, ...]:
        return tuple(dataclasses.asdict(self))

    @property
    def values(self) -> tuple[str, ...]:
        return tuple(dataclasses.asdict(self).values())

    @classmethod
    def add(cls, event: StreamEvent, metrics: ReactionMetrics) -> Self:
        metric = cls(event.stream, event.type)
        logger.debug(f"new stream event: stream {event.stream}, type {event.type}")
        metrics.streams[metric] += 1
        return metric


class ReactionMetrics:
    def __init__(self) -> None:
        # meant to be monotonic counters
        self.matches: dict[MatchMetric, int] = defaultdict(int)
        self.actions: dict[ActionMetric, int] = defaultdict(int)
        self.commands: dict[CommandMetric, int] = defaultdict(int)
        self.streams: dict[StreamMetric, int] = defaultdict(int)

        # holds the last match for the given (stream, filter) pair.
        # the next action for (stream, filter) is considered to be
        # triggered by match. this is true if the logs are well-ordered.
        self.last_match: dict[tuple[str, str], MatchMetric] = {}

    def add(self, event: Event):
        match event:
            case Action():
                if config.actions:
                    ActionMetric.add(event, self)
            case Match():
                if config.matches:
                    MatchMetric.add(event, self)
            case Command():
                if config.commands:
                    CommandMetric.add(event, self)
            case StreamEvent():
                if config.streams:
                    StreamMetric.add(event, self)
            case _:
                raise TypeError(f"unsupported event type: {type(event)}")

    @property
    def n_matches(self) -> int:
        return sum(self.matches.values())

    @property
    def n_actions(self) -> int:
        return sum(self.actions.values())

    @property
    def n_commands(self) -> int:
        return sum(self.commands.values())

    @property
    def n_streams(self) -> int:
        return sum(self.streams.values())

    def clear(self):
        # reset metrics af if is was first launch
        self.matches.clear()
        self.actions.clear()
        self.last_match.clear()
        self.commands.clear()
        self.streams.clear()

    def __repr__(self):
        return str(self.__dict__)
