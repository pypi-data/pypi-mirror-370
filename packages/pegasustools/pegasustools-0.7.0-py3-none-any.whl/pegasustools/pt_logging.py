"""Logging utilities for PegasusTools."""

import logging
import sys
import typing


def setup_pt_logger(
    logging_level: int = logging.INFO,
    log_stream: typing.TextIO = sys.stdout,
) -> logging.Logger:
    """Create a logger for PegasusTools under the name pt.logger.

    Parameters
    ----------
    logging_level : int, optional
        The logging level to use, by default logging.INFO
    log_stream : typing.TextIO, optional
        The stream to send the logs to, by default sys.stdout

    Returns
    -------
    logging.Logger
        A Logger object that is fully setup.
    """
    logger = logging.getLogger("pt.logger")

    logging.basicConfig(
        stream=log_stream,
        level=logging_level,
        format="%(levelname)s:%(name)s:%(asctime)s: %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
    )

    return logger
