"""
json utils
"""

import json

from waflibs import log

logger = log.logger().get_logger()


def write_json_file(contents, filename):
    """write json file to disk"""

    if type(filename) == str:
        f = open(filename, "w")
    else:
        f = filename
    f.write(json.dumps(contents, indent=2))
    f.close()
