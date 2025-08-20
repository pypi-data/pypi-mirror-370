#!/usr/bin/env python

import unittest

from waflibs import shell


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


if __name__ == "__main__":
    unittest.main()
