"""
utils for logging
"""

import logging
import os
import random
import sys
import time

import loguru

from waflibs.constants import PROGRAM_NAME

DEBUG = logging.DEBUG
VERBOSE = DEBUG

INFO = logging.INFO


class logger:
    def get_logger(self, name=PROGRAM_NAME):
        """get current logger"""

        return logging.getLogger(name)

    def is_verbose(self, args):
        """check whether verbosity is set"""

        return "verbose" in args and args.verbose

    has_verbose = is_verbose

    def set_all_logger_levels(self, level):
        self.set_level(level)

        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        loggers.append(logging.getLogger())
        for logger in loggers:
            logger.setLevel(level)

    def set_level(self, level):
        self.logger.setLevel(level)

    def __init__(
        self,
        args={},
        verbose=False,
        program_name=PROGRAM_NAME,
        log_format=None,
    ):
        """create logger"""

        self.logger = self.get_logger()

        divider = "#" * 55

        if log_format is None:
            log_format = f"""{divider}
timestamp: %(asctime)s
name: %(name)s
filename: %(filename)s
path name: %(pathname)s
module: %(module)s
function name: %(funcName)s()
line num: %(lineno)s
level name: %(levelname)s
level num: %(levelno)s

START LOG
%(message)s
END LOG
{divider}"""
        elif log_format == "simple":
            log_format = None
        formatter = logging.Formatter(log_format)

        if self.is_verbose(args) or verbose:
            self.set_all_logger_levels(VERBOSE)

            sh = logging.StreamHandler()
            sh.setFormatter(formatter)
            self.logger.addHandler(sh)

            fh = logging.FileHandler(
                f"/tmp/{program_name}.{time.time()}.log", mode="a+"
            )
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
        else:
            self.set_all_logger_levels(INFO)
