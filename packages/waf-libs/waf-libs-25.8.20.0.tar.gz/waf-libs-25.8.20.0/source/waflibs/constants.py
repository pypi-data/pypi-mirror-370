"""
constants
"""

import os
import pathlib
import sys

PROGRAM_NAME = os.path.basename(sys.argv[0])

PERSONAL_DOMAINS = [
    "fawong.com",
    "hlx.tw",
    "waf.hk",
    "xilef.org",
    "xn--i8s3q.xn--j6w193g",
]
DEV_DOMAINS = [
    "faw.gg",
    "gyx.io",
    "waf.sexy",
]
COMMUNITY_DOMAINS = [
    "fastandfungible.com",
    "kirinas.com",
    "seris-choice.com",
    "xn--ij2bx6jt8qgte.com",
    "xn--lckwg.net",
]
PUBLIC_DOMAINS = [
    "fantasticrealty.uk",
    "orientelectronic.net",
    "waf.gg",
]
PROJECT_DOMAINS = [
    "mylists.cc",
    "mymovielist.org",
    "mytvlist.org",
]
ADMIN_DOMAINS = [
    "aatf.us",
]
ALL_DOMAINS = (
    PERSONAL_DOMAINS
    + DEV_DOMAINS
    + COMMUNITY_DOMAINS
    + PUBLIC_DOMAINS
    + ADMIN_DOMAINS
    + PROJECT_DOMAINS
)

IP_CIDRS = []

HOME_DIR = os.environ.get("HOME", "/home/waf")

VERSION = (
    open(pathlib.Path(pathlib.Path(__file__).parent, "VERSION"), "r").read().strip()
)
USER_AGENT = f"waflibs python v{VERSION}"
