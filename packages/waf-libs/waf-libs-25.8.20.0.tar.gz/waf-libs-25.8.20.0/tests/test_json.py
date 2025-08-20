#!/usr/bin/env python

import tempfile
import unittest

from waflibs import shell, json


class TestShell(unittest.TestCase):
    def test_shell_command_capture_output_strip(self):
        stdout, stderr, _ = shell.shell_command(["echo", "hello\nthere\n\n\n\n"])

        self.assertEqual(stdout, "hello\nthere")
        self.assertEqual(stderr, "")

    def test_shell_command_capture_output(self):
        stdout, stderr, _ = shell.shell_command(
            ["echo", "hello", "there"],
        )

        self.assertEqual(stdout, "hello there")
        self.assertEqual(stderr, "")

    def test_shell_command_no_capture_output(self):
        proc = shell.shell_command(
            ["echo", "hello", "there"],
            capture_output=False,
        )

        self.assertEqual(proc.stdout, None)
        self.assertEqual(proc.stderr, None)

    def test_json_write(self):
        tf = tempfile.NamedTemporaryFile()
        filename = tf.name

        json_string = """{
  "test": "yes",
  "no": "stuff"
}"""
        json_dict = {
            "test": "yes",
            "no": "stuff",
        }

        json.write_json_file(json_dict, filename)
        tf.seek(0)

        f = open(filename, "r")
        self.assertEqual(f.read(), json_string)


if __name__ == "__main__":
    unittest.main()
