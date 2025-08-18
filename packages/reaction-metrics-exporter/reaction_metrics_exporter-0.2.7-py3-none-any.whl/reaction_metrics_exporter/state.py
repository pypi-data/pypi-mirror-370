import asyncio
from datetime import datetime, timedelta, timezone
import os
import pickle
import signal
import sys

import structlog

from .models.config import Config
from .models.metric import ReactionMetrics

logger = structlog.get_logger()
config = Config.get_config()


class StateMeta(type):
    # as long as dates are localized, comparison works even
    # when tz are different, e.g. Docker and host
    _last_log: datetime = datetime.now().astimezone()
    _wait_until: datetime = datetime.now().astimezone()

    # meant to be short-lived and keep unexported metrics across restarts
    _metrics = ReactionMetrics()

    # don't recall anything beyond 15 minutes
    _limit = 15
    _start: datetime = datetime.now().astimezone()

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

    @property
    def metrics(cls) -> ReactionMetrics:
        return cls._metrics

    @metrics.setter
    def metrics(cls, value: ReactionMetrics):
        cls._metrics = value


class State(metaclass=StateMeta):
    """singleton-ish to manage app's state."""

    # which signals means terminate for us
    _SIGNALS = ["SIGINT", "SIGTERM"]
    _inst = None

    @classmethod
    def init(cls):
        cls._last_file = f"{config.restore_dir}/last_log"
        cls._wait_file = f"{config.restore_dir}/wait_until"
        cls._metrics_file = f"{config.restore_dir}/metrics.pickle"

        cls._load_last_log()
        cls._load_wait_until()
        cls._load_metrics()

        for sig in cls._SIGNALS:
            asyncio.get_running_loop().add_signal_handler(getattr(signal, sig), lambda sig=sig: cls._quit(sig))
        logger.debug(f"installed handlers for signals {cls._SIGNALS}")

    # a bit verbose but less error-prone to me
    @classmethod
    def _load_last_log(cls):
        if not os.path.isfile(cls._last_file):
            return
        with open(cls._last_file, "r") as f:
            last_log = datetime.fromtimestamp(float(f.read())).astimezone()
            logger.debug(f"loaded datetime {last_log} from {cls._last_file}")
            if cls._recall(last_log):
                cls.last_log = last_log
            else:
                logger.info(f"ignoring last log date older than {cls._limit} minutes")

    @classmethod
    def _load_wait_until(cls):
        if not os.path.isfile(cls._wait_file):
            return
        with open(cls._wait_file, "r") as f:
            wait_until = datetime.fromtimestamp(float(f.read())).astimezone()
            logger.debug(f"loaded datetime {wait_until} from {cls._wait_file}")
            if cls._recall(wait_until):
                cls.wait_until = wait_until

    @classmethod
    def _load_metrics(cls):
        if not os.path.isfile(cls._metrics_file):
            return
        try:
            with open(cls._metrics_file, "rb") as f:
                cls.metrics: ReactionMetrics = pickle.load(f)
                logger.debug(f"loaded {cls.metrics.n_metrics} metrics from previous session")
                if not cls._recall(cls.last_log):
                    logger.info(f"discarding loaded metrics as they are older than 15 minutes")
                    cls.metrics.clear()
        except (pickle.PickleError, EOFError):
            pass

    @classmethod
    def _save_last_log(cls):
        with open(cls._last_file, "w") as f:
            ts = cls.last_log.timestamp()
            f.write(str(ts))
            logger.debug(f"saved last log datetime {cls.last_log} into {cls._last_file}")

    @classmethod
    def _save_wait_until(cls):
        with open(cls._wait_file, "w") as f:
            ts = cls.wait_until.timestamp()
            f.write(str(ts))
            logger.debug(f"saved wait until datetime {cls.wait_until} into {cls._wait_file}")

    @classmethod
    def _save_metrics(cls):
        with open(cls._metrics_file, "wb") as f:
            pickle.dump(cls.metrics, f)
            logger.debug(f"saved {cls.metrics.n_metrics} unexported metrics for 15 minutes")

    @classmethod
    def _quit(cls, sig: str):
        try:
            logger.info(f"signal {sig} catched, save state before exiting")
            cls._save_last_log()
            cls._save_wait_until()
            cls._save_metrics()
            logger.info("exiting.")
        except Exception as e:
            # catch anything so process can exit
            logger.exception(e)
        finally:
            sys.exit(0)

    @classmethod
    def _recall(cls, start: datetime) -> bool:
        return cls._start - timedelta(minutes=cls._limit) < start
