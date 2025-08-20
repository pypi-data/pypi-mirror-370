#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import unittest

from waflibs import text

DEFAULT_TIMES = text.TIMES
TIMES = 33


class TestText(unittest.TestCase):
    pass


class TestDivider(TestText):
    def test_divider_default(self):
        self.assertEqual(text.divider(), "=" * DEFAULT_TIMES)

    def test_divider_char(self):
        self.assertEqual(text.divider(char="-"), "-" * DEFAULT_TIMES)

    def test_divider_times(self):
        self.assertEqual(text.divider(times=TIMES), "=" * TIMES)

    def test_divider_all(self):
        self.assertEqual(text.divider(char="_", times=TIMES), "_" * TIMES)


if __name__ == "__main__":
    unittest.main()
