"""
text utils
"""

import sys

from waflibs import log

logger = log.logger().get_logger()

TIMES = 77
logger.debug(f"default number of times is {TIMES}")


def divider(char="=", times=TIMES):
    """generate text divider"""

    return char * times


def print_divider(char="=", times=TIMES, stderr=False):
    """print text divider"""

    output = divider(char, times)

    if stderr:
        print(output, file=sys.stderr)
    else:
        print(output)


def stderrprint(*args, **kwargs):
    logger.debug(f"original kwargs: {kwargs}")

    output = sys.stderr
    if "stdout" in kwargs and kwargs["stdout"]:
        output = sys.stdout
        kwargs.pop("stdout")
    logger.debug(f"file output is {output.name}")

    if "newline" in kwargs and not kwargs["newline"]:
        kwargs["flush"] = True
        kwargs["end"] = ""
        kwargs.pop("newline")
    logger.debug(f"after kwargs: {kwargs}")

    print(*args, **kwargs, file=output)


eprint = stderrprint
errprint = stderrprint
errorprint = stderrprint
