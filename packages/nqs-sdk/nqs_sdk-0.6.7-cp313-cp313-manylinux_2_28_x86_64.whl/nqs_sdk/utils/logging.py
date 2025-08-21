import logging
from datetime import datetime
from typing import Any


def _format_time(self, record, datefmt=None):  # type: ignore[no-untyped-def]
    return datetime.fromtimestamp(record.created).isoformat(timespec="microseconds")


logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)5s %(name)s: %(message)s")
logging.Formatter.formatTime = _format_time  # type: ignore[method-assign]


def local_logger(name: str) -> Any:
    return logging.getLogger(name)


def global_logger(name: str) -> Any:
    # Clear existing handlers from the root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set up the formatter with the desired format
    formatter = logging.Formatter("%(asctime)sZ %(levelname)5s %(name)s: %(message)s", "%Y-%m-%dT%H:%M:%S.%f")

    # Create a console handler and set its formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Add the handler to the root logger
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.DEBUG)

    return logging.getLogger(__name__)
