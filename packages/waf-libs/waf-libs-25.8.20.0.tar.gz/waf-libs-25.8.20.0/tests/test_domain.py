#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import unittest

from waflibs import domain


class TestDomain(unittest.TestCase):
    pass


class TestIDNA(TestDomain):
    def test_idna(self):
        orig = "カラ"
        result = "xn--lckwg"

        self.assertEqual(domain.idna(orig), result)


if __name__ == "__main__":
    unittest.main()
