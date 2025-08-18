from collections import OrderedDict
from functools import cache
import os
import re
from typing import Any, Self

import jinja2
from ruamel.yaml import YAML
from schema import And, Optional, Or, Schema, Use
import structlog

logger = structlog.get_logger()


class Config:
    """
    singleton-ish holding the exporter's configuration.
    does validation and expose most of its configuration as public attributes.
    """

    _inst: Self | None = None
    _reader = YAML()
    _env = jinja2.Environment()

    # forget is written "\d+{d,w,m,y,H,M}, e.g. 12w or 12H"
    _REGEX_DURATION = re.compile(r"(?P<unit>\d+)(?P<kind>\w)")
    # to call timedelta constructor
    _DELTA_MAP = {
        "u": "microseconds",
        "S": "seconds",
        "M": "minutes",
        "H": "hours",
        "d": "days",
        "w": "weeks",
        "m": "months",
        "y": "years",
    }

    _listen_schema = Schema(
        {
            Optional("address", default="127.0.0.1"): str,
            Optional("port", default=8080): int,
        }
    )

    _reaction_schema = Schema(
        {
            Optional("config", default="/etc/reaction"): os.path.exists,
            # choose systemd by default, and accept only one of "systemd" or "file" key
            Optional("logs", default={"systemd": "reaction.service"}): Or(
                {
                    Optional("systemd", default="reaction.service"): And(
                        # a way to set default value if key exists but value is None.
                        Use(lambda v: "reaction.service" if v is None else v),  # pyright: ignore[reportArgumentType]
                        str,
                    )
                },
                {
                    Optional("file", default="/var/log/reaction.log"): And(
                        Use(lambda v: "/var/log/reaction.log" if v is None else v), str  # pyright: ignore[reportArgumentType]
                    )
                },
            ),
            Optional("socket", default="/run/reaction/reaction.sock"): str,
            Optional("hold", default=60): int,
        }
    )

    # a bit complex because we want to handle keys whose presence acts as bool,
    # so they cannot have a default value and can contains additionnal dictionaries with defaults
    _extra_schema = And(
        # set default value if None, then validate
        Use(lambda export: {"extra": True} if export is None else export),  # pyright: ignore[reportArgumentType]
        # can be False (don't export) or extra option for labels
        Or(
            bool,
            {Optional("extra", default=True): bool},  # pyright: ignore[reportArgumentType]
        ),
    )
    _export_schema = Schema(
        {
            Optional("matches", default=_extra_schema.validate({})): _extra_schema,
            Optional("actions", default=_extra_schema.validate({})): _extra_schema,
            Optional("pending", default=_extra_schema.validate({})): _extra_schema,
            Optional("commands", default=None): Or(bool, None),
            Optional("streams", default=None): Or(bool, None),
            Optional("internals"): Or(bool, None),
        }
    )
    _metrics_schema = Schema(
        {
            # if None or True, export as-is, if str, render template, if False, don't exporter
            Optional("all", default={}): Or({str: Or(str, None, bool)}, {}),  # pyright: ignore[reportArgumentType]
            Optional("for", default={}): Or({str: {str: {str: Or(str, None, bool)}}}, {}),  # pyright: ignore[reportArgumentType]
            Optional("export", default=_export_schema.validate({})): _export_schema,
        }
    )
    # Schema is made of subschema, allowing for complex default values
    _schema = Schema(
        {
            Optional("loglevel", default="INFO"): And(
                str,
                lambda s: s.upper() in ["DEBUG", "INFO", "WARNING", "ERROR"],
            ),
            Optional("listen", default=_listen_schema.validate({})): _listen_schema,
            Optional("reaction", default=_reaction_schema.validate({})): _reaction_schema,
            Optional("metrics", default=_metrics_schema.validate({})): _metrics_schema,
        }
    )

    def __init__(self):
        self._conf = OrderedDict()

    @classmethod
    def get_config(cls) -> Self:
        # use defaults
        if cls._inst is None:
            cls._inst = cls()
        return cls._inst

    @classmethod
    def from_file(cls, config_path: str) -> Self:
        inst = cls.get_config()
        logger.debug(f"using config file: {config_path}")
        with open(config_path, "r") as file:
            content = cls._reader.load(file.read())
            if not content:
                # to get default values
                content = {}
        inst._set_conf(content)
        return inst

    @classmethod
    def from_default(cls) -> Self:
        inst = cls.get_config()
        logger.debug(f"using no config file")
        inst._set_conf({})
        return inst

    def _set_conf(self, content: dict[str, Any]) -> None:
        logger.debug(f"initial configuration: {content}")
        self._conf: OrderedDict[str, Any] = self._schema.validate(content)
        logger.info(f"using configuration: {self._conf}")
        logger.debug(
            f"will export: matches: {self.matches} (labels: {self.matches_extra}); actions: {self.actions} (labels: {self.actions_extra}); pending: {self.pending} (labels: {self.pending_extra})"
        )
        if self.docker:
            logger.info(f"detected running in a Docker environment")

    @property
    def listen(self) -> tuple[str, int]:
        return (
            self._conf["listen"]["address"],
            self._conf["listen"]["port"],
        )

    @property
    def log_level(self) -> str:
        return self._conf["loglevel"]

    @property
    def socket(self) -> str:
        return self._conf["reaction"]["socket"]

    @property
    def reaction_config(self) -> str:
        return self._conf["reaction"]["config"]

    @property
    def type(self) -> str:
        return list(self._conf["reaction"]["logs"])[0]

    @property
    def path(self) -> str:
        return self._conf["reaction"]["logs"][self.type]

    @property
    def actions(self) -> bool:
        return self._use_metric("actions")

    @property
    def actions_extra(self) -> bool:
        return self._use_labels("actions")

    @property
    def matches(self) -> bool:
        return self._use_metric("matches")

    @property
    def matches_extra(self) -> bool:
        return self._use_labels("matches")

    @property
    def pending(self) -> bool:
        return self._use_metric("pending")

    @property
    def pending_extra(self) -> bool:
        return self._use_labels("pending")

    @property
    def commands(self) -> bool:
        return self._use_metric("commands")

    @property
    def streams(self) -> bool:
        return self._use_metric("streams")

    @property
    def hold(self) -> int:
        return self._conf["reaction"]["hold"]

    @property
    def internals(self) -> bool:
        return self._conf["metrics"]["export"].get("internals") == True

    @property
    def docker(self) -> bool:
        return os.environ.get("DOCKER") is not None

    @property
    def restore_dir(self) -> str:
        # unnamed volume declared in Dockerfile
        if self.docker:
            return f"/data"
        # if running in systemd, will be StateDirectory,
        # otherwise the directory from which the command has been launched
        return os.getcwd()

    @cache
    def render(self, stream: str, filter: str, patterns: tuple[str, ...], matches: tuple[str, ...]) -> tuple[str, ...]:
        """filter and render patterns according to conf"""
        res: list[str] = []
        for pattern, match in zip(patterns, matches):
            match template := self.transforms(stream, filter).get(pattern):
                case str():
                    try:
                        res.append(self._env.from_string(template, {pattern: match}).render())
                    except jinja2.exceptions.TemplateSyntaxError as e:
                        logger.warn(f"cannot use match {match} for pattern {pattern} with template {template}: {e}")
                case None:
                    # absence of value means use as-is
                    res.append(match)
                case False:
                    # explicitly don't export
                    pass
                case _:
                    raise ValueError(f"unauthorized templating value: {template}")
        return tuple(res)

    @cache
    def transforms(self, stream: str, filter: str) -> dict[str, str | bool]:
        """
        returns jinja2 templates for given stream and filter, according to conf.
        absence of value means export as-is, False means don't export, template otherwise.
        """
        all = self._conf["metrics"]["all"]
        locals = self._conf["metrics"]["for"]
        # if duplicate key first one is overriden (i.e. global transform is overwriten)
        merge: dict[str, str | None | bool] = all | locals.get(stream, {}).get(filter, {})
        res: dict[str, str | bool] = {}
        for pattern, value in merge.items():
            # don't export label
            if value is False:
                res[pattern] = False
            # export as-is
            elif value is None or value is True:
                continue
            # export with custom template
            else:
                res[pattern] = value
        return res

    def __repr__(self) -> str:
        # useful for pytest
        return str(self._conf)

    def _use_metric(self, metric: str):
        return self._conf["metrics"]["export"].get(metric) != False

    def _use_labels(self, metric: str) -> bool:
        return self._use_metric(metric) and (
            # by default, we export labels
            self._conf["metrics"]["export"][metric] is None
            or self._conf["metrics"]["export"][metric].get("extra")
        )
