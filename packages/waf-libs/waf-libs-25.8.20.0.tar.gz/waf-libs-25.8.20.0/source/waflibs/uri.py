"""
uri utils
"""

import ipaddress
import urllib

from waflibs import dns, log

logger = log.logger().get_logger()


def uri_result(result, full_uri=False):
    if full_uri:
        return result
    else:
        return dns.get_domain(result)


def convert_uri(uri, full_uri=False):
    try:
        ipaddress.ip_address(uri)

        result = uri
    except ValueError as e:
        logger.debug(f"exception caught - not an ip address: {e}")

        parse_result = urllib.parse.urlparse(uri)
        logger.debug(f"parse result: {parse_result}")

        if parse_result.netloc:
            result = uri_result(parse_result.hostname, full_uri=full_uri)
        elif parse_result.scheme and not parse_result.netloc:
            result = uri_result(parse_result.scheme, full_uri=full_uri)
        else:
            result = uri_result(parse_result.path, full_uri=full_uri)

    return result
