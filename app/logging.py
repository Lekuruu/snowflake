
from logging import StreamHandler, Formatter

import logging

class ColorFormatter(Formatter):

    GREY = "\x1b[38;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    CYAN = "\x1b[96m"
    RESET = "\x1b[0m"

    FORMAT_PREFIX = '[%(asctime)s] - <%(name)s> '
    FORMAT = '%(levelname)s: %(message)s'

    FORMATS = {
        logging.NOTSET:   GREY + FORMAT_PREFIX            + FORMAT + RESET,
        logging.DEBUG:    GREY + FORMAT_PREFIX            + FORMAT + RESET,
        logging.INFO:     GREY + FORMAT_PREFIX + CYAN     + FORMAT + RESET,
        logging.WARNING:  GREY + FORMAT_PREFIX + YELLOW   + FORMAT + RESET,
        logging.ERROR:    GREY + FORMAT_PREFIX + RED      + FORMAT + RESET,
        logging.CRITICAL: GREY + FORMAT_PREFIX + BOLD_RED + FORMAT + RESET,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        return Formatter(log_fmt).format(record)

Console = StreamHandler()
Console.setFormatter(ColorFormatter())
