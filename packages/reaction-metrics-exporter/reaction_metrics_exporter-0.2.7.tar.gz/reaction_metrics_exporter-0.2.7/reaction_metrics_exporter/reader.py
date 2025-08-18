from abc import ABC, abstractmethod
import asyncio
from collections.abc import AsyncGenerator
from contextlib import closing
from datetime import datetime, timezone
from typing import Any

import aiofiles
import aionotify
import structlog
from systemd import journal
from systemd.journal import Reader

from .models.config import Config
from .models.exception import UnsupportedLine
from .models.log import Log, LogLevel
from .state import State

logger = structlog.get_logger()
config = Config.get_config()


class LogReader(ABC):
    """
    Asynchonously yield reaction logs.

    path is "abstract" (e.g. it is the unit to be read specific to subclasses).
    """

    @abstractmethod
    def __init__(self, path: str) -> None:
        self._path = path

    @abstractmethod
    def logs(self) -> AsyncGenerator[Log]:
        pass

    @abstractmethod
    def _to_log(self, entry: Any) -> Log:
        pass


class FileReader(LogReader):
    def __init__(self, path: str) -> None:
        super().__init__(path)

    async def logs(self) -> AsyncGenerator[Log]:
        async with aiofiles.open(self._path, "a+") as file:
            # go to the end of the file
            with closing(aionotify.Watcher()) as watcher:
                # register inotify watcher
                watcher.watch(self._path, flags=aionotify.Flags.MODIFY)
                await watcher.setup()
                while True:
                    # watch for changes
                    _ = await watcher.get_event()
                    # consume new lines
                    async for line in file:
                        yield self._to_log(line)

    def _to_log(self, entry: str) -> Log:
        entry = entry.strip()
        try:
            # split only first space
            level, _ = entry.split(" ", 1)
        except ValueError as e:
            raise UnsupportedLine(f"cannot parse loglevel in line {entry}: {e}")
        try:
            loglevel: LogLevel = LogLevel[level]
            # note that loglevel is part of the message
            return Log(datetime.now().astimezone(), loglevel, entry)
        except (ValueError, KeyError) as e:
            raise UnsupportedLine(f"unrecognized loglevel {level} found in line {entry}: {e}")


class JournalReader(LogReader):
    def __init__(self, path: str):
        super().__init__(path)
        # when mounting in Docker, without the path logs are not read because
        # they come from "another" computer. in that case the path points
        # mounted journal files, otherwise None will be transparent
        journal_path = "/var/log/journal" if config.docker else None
        self._jd: Reader = journal.Reader(path=journal_path)
        self._jd.this_boot()
        self._jd.log_level(journal.LOG_INFO)
        # no nice way to check for existence, but no exception if it doesn't
        self._jd.add_match(_SYSTEMD_UNIT=path)

        # current log time
        self._jd.seek_tail()
        last_entry = self._jd.get_previous()
        if not last_entry:
            logger.error(f"no journald entry found: check your permissions unless you just started reaction")
        else:
            logger.debug(f"successfully read last reaction entry")
            tail_date = self._to_log(last_entry).time
            if State.last_log < tail_date:
                logger.debug(f"last recorded log {State.last_log} behind last journald log ({tail_date}), seek back")
                # the problem here is that we use UTC timezone everywhere for simplicity,
                # but the systemd library calls .astimezone() on the passed datetime,
                # which adjust the datetime as if it represents a local time.
                # removing the timezone makes Python .astimezone() idempotent.
                self._jd.seek_realtime(State.last_log.replace(tzinfo=None))
                self._jd.get_next()

        logger.info(f"started listening journald entries")

    async def logs(self) -> AsyncGenerator[Log]:
        for entry in self._jd:
            yield self._to_log(entry)

        while True:
            # evaluate to true when a new entry (at least) appears
            if await self._wait_entries() == journal.APPEND:
                for entry in self._jd:
                    log = self._to_log(entry)
                    yield log

    async def _wait_entries(self) -> int:
        # Reader.wait() is synchronous, execute in another thread
        loop = asyncio.get_running_loop()
        # back to polling with 1s non-blocking timeout
        res: int = await loop.run_in_executor(None, self._jd.wait, 1)
        return res

    def _to_log(self, entry: dict[str, Any]) -> Log:
        return Log(entry["__REALTIME_TIMESTAMP"].astimezone(), entry["PRIORITY"], entry["MESSAGE"].strip())
