import asyncio
from datetime import datetime, timezone
import signal
import sys

import structlog

from .models.config import Config

logger = structlog.get_logger()
config = Config.get_config()


class StateMeta(type):
    # as long as dates are localized, comparison works even
    # when tz are different, e.g. Docker and host
    _last_log: datetime = datetime.now(timezone.utc)
    _wait_until: datetime = datetime.now(timezone.utc)

    @property
    def last_log(cls) -> datetime:
        return cls._last_log

    @last_log.setter
    def last_log(cls, value: datetime):
        cls._last_log = value

    @property
    def wait_until(cls) -> datetime:
        return cls._wait_until

    @wait_until.setter
    def wait_until(cls, value: datetime):
        cls._wait_until = value


class State(metaclass=StateMeta):
    """singleton-ish to manage app's state."""

    # which signals means terminate for us
    _SIGNALS = ["SIGINT", "SIGTERM"]
    _inst = None

    @classmethod
    def init(cls):
        cls._last_file = f"{config.restore_dir}/last_log"
        cls._wait_file = f"{config.restore_dir}/wait_until"

        cls._load_last_log()
        cls._load_wait_until()

        for sig in cls._SIGNALS:
            asyncio.get_running_loop().add_signal_handler(getattr(signal, sig), lambda sig=sig: cls._quit(sig))
        logger.debug(f"installed handlers for signals {cls._SIGNALS}")

    # a bit verbose but less error-prone to me
    @classmethod
    def _load_last_log(cls):
        if not config.restore:
            return
        try:
            with open(cls._last_file, "r") as f:
                cls.last_log = datetime.fromtimestamp(float(f.read()), timezone.utc)
                logger.debug(f"loaded datetime {cls.last_log} from {cls._last_file}")
        except FileNotFoundError:
            pass

    @classmethod
    def _load_wait_until(cls):
        try:
            with open(cls._wait_file, "r") as f:
                cls.wait_until = datetime.fromtimestamp(float(f.read()), timezone.utc)
                logger.debug(f"loaded datetime {cls.wait_until} from {cls._wait_file}")
        except FileNotFoundError:
            pass

    @classmethod
    def _save_last_log(cls):
        if not config.restore:
            return
        with open(cls._last_file, "w") as f:
            ts = cls.last_log.timestamp()
            f.write(str(ts))
            logger.debug(f"saved last log datetime {cls.last_log} into {cls._last_file}")

    @classmethod
    def _save_wait_until(cls):
        if not config.restore:
            return
        with open(cls._wait_file, "w") as f:
            ts = cls.wait_until.timestamp()
            f.write(str(ts))
            logger.debug(f"saved wait until datetime {cls.wait_until} into {cls._wait_file}")

    @classmethod
    def _quit(cls, sig: str):
        try:
            if config.restore:
                logger.info(f"signal {sig} catched, save state before exiting")
                cls._save_last_log()
                cls._save_wait_until()
            logger.info("exiting.")
        except Exception as e:
            # catch anything so process can exit
            logger.exception(e)
        finally:
            sys.exit(0)
