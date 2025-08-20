#!/usr/bin/env python

import os
import pathlib
import tempfile
import unittest

from waflibs import dns


class Testdns(unittest.TestCase):
    def test_origin_full_domain_shared_two(self):
        origin = dns.convert_origin("test.foo.example.com", "example.com", shared=True)

        self.assertEqual(origin, r"test.foo.")

    def test_origin_full_domain_shared_multiple(self):
        origin = dns.convert_origin(
            "test.foo.bar.example.com", "example.com", shared=True
        )

        self.assertEqual(origin, r"test.foo.bar.")

    def test_origin_full_domain(self):
        origin = dns.convert_origin("test.example.com", "example.com")

        self.assertEqual(origin, r"test.example.com.example.com.")

    def test_origin(self):
        origin = dns.convert_origin("test", "example.com")

        self.assertEqual(origin, r"test.example.com.")

    def test_origin_two(self):
        origin = dns.convert_origin("test.foo", "example.com")

        self.assertEqual(origin, r"test.foo.example.com.")

    def test_origin_multiple(self):
        origin = dns.convert_origin("test.foo.bar.baz", "example.com")

        self.assertEqual(origin, r"test.foo.bar.baz.example.com.")

    def test_origin_shared_single(self):
        origin = dns.convert_origin("test", "example.com", shared=True)

        self.assertEqual(origin, r"test")

    def test_origin_shared_multiple(self):
        origin = dns.convert_origin("test.foo.bar.baz", "example.com", shared=True)

        self.assertEqual(origin, r"test.foo.bar.baz")

    def test_origin_shared_two(self):
        origin = dns.convert_origin("test.foo", "example.com", shared=True)

        self.assertEqual(origin, r"test.foo")
