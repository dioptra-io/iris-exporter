import logging
from logging import getLogger

logger = getLogger("iris-exporter")


def configure_logging() -> None:
    logging.basicConfig(
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        format="level={levelname} time={asctime} process={processName} thread={threadName} file={filename}:{lineno} function={funcName} {message}",
        level=logging.INFO,
        style="{",
    )
