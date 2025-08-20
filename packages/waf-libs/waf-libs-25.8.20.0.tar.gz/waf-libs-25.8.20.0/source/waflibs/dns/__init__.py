"""
general utils
"""

import os
import shutil
import sys

from waflibs import log
from waflibs.dns import bind, mysql

import dns.resolver

logger = log.logger().get_logger()


def get_cloudflare_credentials(config, real_domain=None):
    """get cloudflare credentials"""

    if real_domain:
        domain = real_domain.replace(".", "_")

        return config["cloudflare_credentials"][domain]
    else:
        return config["cloudflare_credentials"]["default"]


def get_default_domains(config, zone_type="public"):
    """get default domains"""

    try:
        zones = config["zones"]["default_domains"]
    except (KeyError, TypeError) as e:
        logger.debug(f"key error - {e}")
        zones = {}

    if zone_type in zones:
        return zones[zone_type]
    else:
        return DEFAULT_DOMAINS


get_cloudflare_config = get_cloudflare_credentials


def convert_origin(orig_name, orig_domain, shared=False):
    """convert domain origin to standard form"""

    full_name = orig_name.strip(".").strip()
    domain = orig_domain.strip(".").strip()

    if shared:
        return full_name.replace(domain, "")

    if full_name == domain:
        return "{}.".format(full_name)
    if full_name == "@":
        return "{}.".format(domain)

    split_name = full_name.split(".")[0:-2]
    if not split_name:
        return "{}.{}.".format(full_name, domain)
    else:
        hostname = ".".join(split_name)
        if domain:
            return "{}.{}.".format(full_name, domain)
        else:
            return "{}.".format(hostname)


def print_cloudflare_errors(error):
    """print full cloudflare errors"""

    if len(error) > 0:
        for err in error:
            print(err)
    else:
        print(error)


print_cf_error = print_cloudflare_errors
print_cf_errors = print_cloudflare_errors


def dns_lookup(record, record_type):
    """lookup dns record"""

    return dns.resolver.query(record, record_type)


def get_domain(hostname):
    logger.debug(f"hostname: {hostname}")

    return ".".join(hostname.split(".")[-2:])
