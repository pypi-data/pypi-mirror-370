#!/usr/bin/env python3
"""utils for arg_parse"""

import argparse
import os
import sys


class parser:
    def __init__(
        self,
        description=None,
        prog=None,
    ):
        if not prog:
            prog = os.path.basename(sys.argv[0])

        self.ap = argparse.ArgumentParser(
            description=description,
            prog=prog,
        )

    def get_parser(
        self,
    ):
        return self.ap

    def use_config_file(self, filename, help_text=None):
        """enable argument for passing in config file"""

        if not help_text:
            help_text = f"Config file (default: %(default)s)"

        self.get_parser().add_argument(
            "-c",
            "--config",
            "--config-file",
            type=str,
            default=filename,
            help=help_text,
        )

    enable_config = use_config_file
    enable_config_file = use_config_file
    use_config = use_config_file

    def enable_verbose_logging(self, count=False):
        """enable verbose logger"""

        other_args = {}
        if count:
            action = "count"
            other_args = {
                "default": 0,
            }
        else:
            action = "store_true"

        self.get_parser().add_argument(
            "-d",
            "-v",
            "--verbose",
            "--debug",
            action=action,
            help="verbose logging",
            **other_args,
        )

    use_verbose_logger = enable_verbose_logging
    use_verbose_logging = enable_verbose_logging
    use_logger = enable_verbose_logging
    enable_logger = enable_verbose_logging
    enable_verbose_logger = enable_verbose_logging

    def enable_dry_run(self, count=False, help_text=None):
        """enable dry run mode"""

        if not help_text:
            help_text = "dry run"

        if count:
            action = "count"
        else:
            action = "store_true"

        self.get_parser().add_argument(
            "-r",
            "--dry-run",
            "--dryrun",
            action=action,
            help=help_text,
            default=0,
        )

    use_dry_run = enable_dry_run
