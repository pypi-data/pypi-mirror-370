import asyncio

import structlog

from .app import ExporterApp

logger = structlog.get_logger()
try:
    asyncio.run(ExporterApp.run())
except Exception as e:
    # pretty-print any exception before quitting
    logger.exception(f"{e.__class__.__name__}: {e}")
