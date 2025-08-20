"""
environment utils
"""

import json
import os

from waflibs import log

logger = log.logger().get_logger()


def get_env_var(var, default=None):
    env_var = os.environ.get(var, default)
    logger.debug(f"env var: {env_var}")

    return env_var


get_env = get_env_var
