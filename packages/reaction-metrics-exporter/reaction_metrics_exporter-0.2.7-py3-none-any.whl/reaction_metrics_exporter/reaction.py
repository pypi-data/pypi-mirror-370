import asyncio
from collections import OrderedDict
from functools import cache
import os
import re
import subprocess
from typing import Any, Never, Self

from ruamel.yaml import YAML
import structlog

from .models.exception import ReactionCommandFailed, UnmatchedPattern

from .models.config import Config


logger = structlog.get_logger()
config = Config.get_config()


class Reaction:
    _inst = None
    _reader = YAML()

    # patterns are written as <name> in regexps
    PATTERN_REGEXP = re.compile(r"<(?P<pattern>\w+)>")

    def __init__(self):
        if not os.path.exists(config.socket):
            logger.warn(f"socket {config.socket} does not exist, is reaction running?")
        # ensure config is known after initialization
        self._set_config()
        # launch background task to watch for config changes
        asyncio.get_running_loop().create_task(self._poll_config())

    @classmethod
    def init(cls) -> Self:
        if cls._inst is None:
            cls._inst = cls()
        return cls._inst

    @classmethod
    def config(cls) -> OrderedDict[str, Any]:
        return cls.init()._conf

    @classmethod
    def show(cls) -> OrderedDict[str, Any]:
        try:
            stdout = subprocess.run(
                ["reaction", "show", "--socket", config.socket],
                check=True,
                capture_output=True,
            ).stdout
            return cls._reader.load(stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"error while invoking `reaction show`: {e}. stderr: {e.stderr}")
            # not a fatal error: new pending actions will not be exported
            return OrderedDict()

    @classmethod
    async def version(cls) -> str:
        try:
            version = (await cls._exec_async_command(f"reaction -V")).decode("utf-8")
        except ReactionCommandFailed:
            logger.warning(f"exported N/A for reaction's version")
            return "N/A"

        try:
            n_version = version.split(" ")[1].strip()
            logger.debug(f"exported {n_version=} for reaction")
            return n_version
        except IndexError:
            logger.warning(f"cannot extract version of reaction from {version}: has format changed?")
            return version

    @classmethod
    async def up(cls) -> bool:
        try:
            await cls._exec_async_command(f"reaction show --socket {config.socket}")
            return True
        except ReactionCommandFailed:
            return False

    @classmethod
    @cache
    def patterns(cls, stream: str, filter: str, matches: tuple[str]) -> tuple[str, ...]:
        """
        get unique and sorted patterns which are involved in all the regexps of a filter.
        matches are current those of a log and are checked for consistency.
        """
        conf = cls.config()
        patterns: set[str] = set()
        try:
            for regex in conf["streams"][stream]["filters"][filter]["regex"]:
                for pattern in re.findall(cls.PATTERN_REGEXP, regex):
                    patterns.add(pattern)
        except KeyError as e:
            raise UnmatchedPattern(f"cannot find filter or regexs at {stream}.{filter} (key {e}) for matches {matches}: has config changed?")
        if len(patterns) != len(matches):
            raise UnmatchedPattern(f"different number of matches {matches} and patterns {patterns} for filter {stream}.{filter}")
        return tuple(sorted(patterns))

    async def _poll_config(self) -> Never:
        # refresh configuration every 10 seconds
        while True:
            await asyncio.sleep(10)
            await self._async_set_config()

    async def _async_set_config(self):
        stdout = await self._exec_async_command(f'reaction test-config -c "{config.reaction_config}"')
        logger.debug("reaction's configuration updated successfully")
        conf = self._reader.load(stdout)
        if conf == self._conf:
            return
        self._conf = conf
        self.patterns.cache_clear()

    def _set_config(self):
        # synchronous so initialization and checks can be done outside of async contexts
        stdout = subprocess.run(
            ["reaction", "test-config", "-c", config.reaction_config],
            check=True,
            capture_output=True,
        ).stdout
        logger.debug("reaction's configuration updated successfully")
        self._conf = self._reader.load(stdout)

    @staticmethod
    async def _exec_async_command(cmd: str) -> bytes:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise ReactionCommandFailed(f"reaction failed to execute command {cmd}: {stderr}")
        return stdout
