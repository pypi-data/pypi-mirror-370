#!/usr/bin/python
"""helpers to manipulate config file"""

import copy
import json
import pathlib

import yaml
from waflibs import log

wl_logger = log.logger()
logger = wl_logger.get_logger()
logger.debug = logger.info


def sanitize(config, deep_copy=True):
    """remove secrets from config file"""

    if deep_copy:
        config_copy = copy.deepcopy(config)
    else:
        config_copy = config

    secret_text = [
        "password",
        "passwords",
        "api-token",
        "api-tokens",
        "api_token",
        "api_tokens",
        "api-key",
        "api-keys",
        "api_key",
        "api_keys",
        "token",
        "tokens",
    ]

    if hasattr(config_copy, "items"):
        config_dict = config_copy
    else:
        config_dict = vars(config_copy)
    for k, v in config_dict.items():
        if isinstance(v, dict):
            sanitize(v, deep_copy=False)
        else:
            for text in secret_text:
                if text in k:
                    config_dict[k] = "REDACTED"

    return config_dict


def get_config_filename(
    fname,
    ignore_suffix=False,
):
    """get config filename"""

    logger.debug(f"orig config filename: {fname}")

    file = pathlib.Path(fname)
    if ignore_suffix:
        logger.debug("ignore_suffix flag set to true... ignoring suffix")
    else:
        exts = [
            "ini",
            "json",
            "yml",
            "yaml",
        ]

        for ext in exts:
            suffix = f".{ext}"
            logger.debug(f"suffix: {suffix}")
            file_suffix = file.suffix
            logger.debug(f"file suffix: {file_suffix}")

            if not file_suffix:
                logger.debug("file suffix is empty")

                file_path = pathlib.Path(f"{file}{suffix}")
                logger.debug(f"file path is {file_path}")
                if file_path.is_file():
                    logger.debug(f"real file found at {file_path}")
                    file = file_path
            elif file_suffix == suffix:
                logger.debug(f"found file suffix {file_suffix} with suffix {suffix}")
                file = file.with_suffix(suffix)

    logger.debug(f"filename: {file}")
    return file


def parse_yaml_file(
    fname,
    ignore_suffix=False,
):
    """parse yaml config by filename"""

    filename = get_config_filename(fname, ignore_suffix)
    logger.debug(f"yaml filename: {filename}")

    if not filename:
        raise Exception(f"no yaml config file found at {fname}")
    else:
        with open(pathlib.Path(filename)) as f:
            config = parse_yaml(f.read())

        return config


def parse_yaml(config):
    """parse yaml config"""

    return yaml.load(config, Loader=yaml.FullLoader)


def parse_json_file(filename):
    """parse json config by filename"""

    f = open(filename)
    config = parse_json(f.read())
    f.close()

    return config


def parse_json(config):
    """parse json config"""

    return json.loads(config)
