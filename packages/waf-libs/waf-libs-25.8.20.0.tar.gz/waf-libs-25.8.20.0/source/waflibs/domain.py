#!/usr/bin/env python
"""utils for manipulating text"""


def idna(domain_name):
    """convert unicode domain name to punycode"""

    return domain_name.encode("idna").decode("utf-8")


idn = idna
i_d_n = idna
i_d_na = idna
