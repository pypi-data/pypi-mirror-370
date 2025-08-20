#!/usr/bin/env python

import logging
import pathlib
import random
import string
import sys
import tempfile
import unittest

from waflibs import config


def random_word(length=29):
    return "".join(random.choice(string.ascii_lowercase) for i in range(length))


class TestConfig(unittest.TestCase):
    pass


class TestConfigFilename(TestConfig):
    @classmethod
    def setUpClass(cls):
        cls.ntf = tempfile.NamedTemporaryFile(
            suffix=".yaml",
            delete=False,
        )
        cls.expected = pathlib.Path(cls.ntf.name)

    @classmethod
    def tearDownClass(cls):
        cls.ntf.close()

    def test_no_ext_ignore(self):
        fname = self.expected.with_suffix("")
        expected = self.expected.with_suffix("")

        self.assertEqual(
            config.get_config_filename(
                fname,
                ignore_suffix=True,
            ),
            expected,
        )

    def test_no_ext_no_ignore(self):
        fname = self.expected.with_suffix("")

        self.assertEqual(config.get_config_filename(fname), self.expected)

    def test_ext_ignore(self):
        fname = self.expected

        self.assertEqual(
            config.get_config_filename(
                fname,
                ignore_suffix=True,
            ),
            self.expected,
        )

    def test_ext_no_ignore(self):
        fname = self.expected

        self.assertEqual(config.get_config_filename(fname), self.expected)


class TestParseConfig(TestConfig):
    json = b"""
{
  "a": "b",
  "c": {
    "d": "e"
  },
  "f": {
    "g": {
      "h": "i"
    }
  }
}
"""

    yaml = b"""
---
a: b
c:
  d: e
f:
  g:
    h: i
"""

    result_yaml_dict = {"a": "b", "c": {"d": "e"}, "f": {"g": {"h": "i"}}}
    result_json_dict = {"a": "b", "c": {"d": "e"}, "f": {"g": {"h": "i"}}}

    def test_parse_yaml(self):
        self.assertEqual(config.parse_yaml(self.yaml), self.result_yaml_dict)

    def test_parse_yaml_file_error(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(
                b"""this
is: badness"""
            )
            f.seek(0)

            with self.assertRaises(Exception):
                config.parse_yaml_file(f.name)

    def test_parse_bad_yaml_ext_file(self):
        with tempfile.NamedTemporaryFile(suffix=".bad") as f:
            f.write(self.yaml)
            f.seek(0)

            self.assertEqual(config.parse_yaml_file(f.name), self.result_yaml_dict)

    def test_parse_yaml_ext_file(self):
        with tempfile.NamedTemporaryFile(suffix=".yaml") as f:
            f.write(self.yaml)
            f.seek(0)

            self.assertEqual(config.parse_yaml_file(f.name), self.result_yaml_dict)

    def test_parse_json(self):
        self.assertEqual(config.parse_json(self.json), self.result_json_dict)

    def test_parse_json_file(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(self.json)
            f.seek(0)

            self.assertEqual(config.parse_json_file(f.name), self.result_json_dict)


class TestSanitizeConfig(TestConfig):
    def test_orig_dict_not_modified(self):
        orig_dict = {
            "real": "should not change",
            "token": "kozxokawekowaefokijwef",
        }
        result_dict = {"real": "should not change", "token": "REDACTED"}

        self.assertEqual(config.sanitize(orig_dict), result_dict)

    def test_empty_dict(self):
        orig_dict = {}
        result_dict = {}

        self.assertEqual(config.sanitize(orig_dict), result_dict)

    def test_single_dict(self):
        orig_dict = {
            "merp_token": "walfj",
            "fail_password": "lwfjealkwef",
            "password": "supersecretalfjeawoefjk",
            "token": "awfjeoawkfj",
            "real": "should not change",
        }
        result_dict = {
            "merp_token": "REDACTED",
            "fail_password": "REDACTED",
            "password": "REDACTED",
            "token": "REDACTED",
            "real": "should not change",
        }

        self.assertEqual(config.sanitize(orig_dict), result_dict)

    def test_single_multi_dict(self):
        orig_dict = {"asdf": {"password": "laksdjflkasdjfk"}}
        result_dict = {"asdf": {"password": "REDACTED"}}

        self.assertEqual(config.sanitize(orig_dict), result_dict)

    def test_single_multi_dict_entries(self):
        orig_dict = {
            "asdf": {
                "password": "laksdjflkasdjfk",
                "more_token": "zxocvuoxcbiuzoxcibu",
            }
        }
        result_dict = {"asdf": {"password": "REDACTED", "more_token": "REDACTED"}}

        self.assertEqual(config.sanitize(orig_dict), result_dict)

    def test_multi_multi_dict(self):
        orig_dict = {
            "asdf": {
                "password": "laksdjflkasdjfk",
                "more_token": "zxocvuoxcbiuzoxcibu",
            },
            "oiuzxc": {
                "tokens": "uoyioiyuuoiot",
                "real": "should not change",
            },
        }
        result_dict = {
            "asdf": {"password": "REDACTED", "more_token": "REDACTED"},
            "oiuzxc": {"tokens": "REDACTED", "real": "should not change"},
        }

        self.assertEqual(config.sanitize(orig_dict), result_dict)

    def test_multi_tokens_dict(self):
        orig_dict = {
            "asdf": {
                "password": random_word(),
                "more_token": random_word(),
            },
            "oiuzxc": {
                "tokens": [
                    random_word(),
                    random_word(),
                ],
                "real": "should not change",
                "token": random_word(),
            },
        }
        result_dict = {
            "asdf": {"password": "REDACTED", "more_token": "REDACTED"},
            "oiuzxc": {
                "tokens": "REDACTED",
                "real": "should not change",
                "token": "REDACTED",
            },
        }

        self.assertEqual(config.sanitize(orig_dict), result_dict)


if __name__ == "__main__":
    unittest.main()
