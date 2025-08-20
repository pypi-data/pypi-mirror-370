#!/usr/bin/env python
"""errors and exceptions"""


class ValidationError(Exception):
    """generic validation error"""

    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message
