import logging
import sys
from pathlib import Path


def set_logger(log_level):
    message_format = (
        (
            "%(asctime)s | %(levelname)-5.5s | %(name)-15s | %(funcName)-17s | %(message)s"
        )
        if log_level == logging.DEBUG
        else ("%(asctime)s | %(levelname)-5.5s | %(message)s")
    )
    file_log_formatter = logging.Formatter(message_format)
    log_dir = "."
    file_name = "dynamofl_output.log"

    fileHandler = logging.FileHandler(Path(log_dir, file_name), mode="a")
    fileHandler.setFormatter(file_log_formatter)

    console_log_formatter = logging.Formatter(
        message_format,
        datefmt="%H:%M:%S",
    )
    consoleHandler = logging.StreamHandler(stream=sys.stdout)
    consoleHandler.setFormatter(console_log_formatter)

    logging.basicConfig(
        level=log_level,
        handlers=[fileHandler, consoleHandler],
    )
