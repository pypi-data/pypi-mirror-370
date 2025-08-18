import asyncio
from collections import OrderedDict
from typing import Any

from asyncio_simple_http_server import HttpHeaders, HttpResponse, uri_mapping
import prometheus_client
from prometheus_client.core import GaugeMetricFamily, Metric, REGISTRY
from prometheus_client.registry import Collector
import structlog

from reaction_metrics_exporter import __version__

from .models.config import Config
from .models.metric import PendingAction, ReactionMetrics
from .reaction import Reaction

logger = structlog.get_logger()
config = Config.get_config()


class MetricsHandler:
    HEADERS = HttpHeaders().set("Content-Type", "text/plain; charset=UTF-8")

    def __init__(self, metrics: ReactionMetrics):
        self._collector = ReactionCollector(metrics)
        self._metrics = metrics
        # registry is a singleton holding multiple collector

        if not config.internals:
            REGISTRY._collector_to_names = {}
        REGISTRY.register(self._collector)

    @uri_mapping("/metrics")
    async def metrics(self):
        # calls collect on every collector
        logger.debug("got a request on /metrics")
        async with asyncio.Lock():
            await self._collector.generate()
            openmetrics = prometheus_client.generate_latest(REGISTRY)
            self._metrics.clear()
        return HttpResponse(200, self.HEADERS, openmetrics)


class ReactionCollector(Collector):
    def __init__(self, metrics: ReactionMetrics) -> None:
        super().__init__()
        self._metrics = metrics
        # filled by async func to be collected by sync registry
        self.collected = ()

    def collect(self) -> tuple[Metric, ...]:
        return self.collected

    async def generate(self) -> None:
        logger.debug("start metrics collection")
        n_match, n_action, n_command, n_stream = 0, 0, 0, 0
        collected: list[Metric] = []

        # all the metrics we are going to export
        # they do not accumulate: one object per collection
        build_info = GaugeMetricFamily(
            "reaction_exporter_build_info",
            "A metric with a constant '1' value labelled by version of reaction_metrics_exporter.",
            labels=("version",),
        )
        collected.append(build_info)
        build_info.add_metric((__version__,), 1.0)

        reaction_info = GaugeMetricFamily(
            "reaction_status_info",
            "A metric with a constant '1' value labelled by version of reaction and its status.",
            labels=("version", "status"),
        )
        collected.append(reaction_info)
        up = "1" if await Reaction.up() else "0"
        version = await Reaction.version()
        reaction_info.add_metric((version, up), 1.0)

        if self._metrics.commands:
            commands = GaugeMetricFamily(
                "reaction_commands_count", "Number of commands launched by reaction, labelled with moment, success status and exit code."
            )
            collected.append(commands)
            for command, count in self._metrics.commands.items():
                commands._labelnames = command.labels
                commands.add_metric(command.values, count)
            n_command = len(commands.samples)

        if self._metrics.streams:
            streams = GaugeMetricFamily("reaction_stream_event_count", "Number of stream events, labelled by stream name and type of event.")
            collected.append(streams)
            for stream, count in self._metrics.streams.items():
                streams._labelnames = stream.labels
                streams.add_metric(stream.values, count)
            n_stream = len(streams.samples)

        if self._metrics.matches:
            match_count = GaugeMetricFamily(
                "reaction_match_count",
                "Number of matches, labelled by stream and filter names, with pattern=match extra labels.",
            )
            collected.append(match_count)
            # labels can vary with patterns and action names
            # we need to change global setting everytime because
            # the way the prometheus lib is made
            for match, count in self._metrics.matches.items():
                match_count._labelnames = match.labels
                match_count.add_metric(match.values, count)
            n_match = len(match_count.samples)

        if self._metrics.actions:
            action_count = GaugeMetricFamily(
                "reaction_action_count",
                "Number of actions, labelled by stream, filter and action names, with pattern=match extra labels.",
            )
            collected.append(action_count)
            for action, count in self._metrics.actions.items():
                action_count._labelnames = action.labels
                action_count.add_metric(action.values, count)
            n_action = len(action_count.samples)

        n_pending = 0
        if config.pending:

            pending_count = GaugeMetricFamily(
                "reaction_pending_count",
                "Number of pending actions, labelled by stream, filter and action names, with pattern=match extra labels.",
            )
            collected.append(pending_count)
            # pending actions cannot easily be inferred from logs: use `reaction show`
            for pending, count in self._collect_pending():
                pending_count._labelnames = pending.labels
                pending_count.add_metric(pending.values, count)
            n_pending = len(pending_count.samples)

        logger.debug(f"metrics collected: {n_match=}, {n_action=}, {n_pending=}, {n_command=}, {n_stream=}")

        self.collected = tuple(collected)

    def _collect_pending(self):
        show: OrderedDict[str, Any] = Reaction.show()
        for stream, filters in show.items():
            for filter, state in filters.items():
                for matches, data in state.items():
                    # i.e. action pending for this (stream, filter)
                    if "actions" in data:
                        for action, _ in data["actions"].items():
                            metric = PendingAction.from_show(stream, filter, matches, action)
                            yield metric, len(data["actions"])
