#!/usr/bin/env python

import os
import pathlib
import tempfile
import unittest

from waflibs import filedir


class Testfiledir(unittest.TestCase):
    def test_dest_location_dotfile_single_path(self):
        dest = filedir.get_dest_location("fake")

        self.assertEqual(pathlib.Path(f"/tmp/.fake"), dest)

    def test_dest_location_dotfile_path(self):
        dest = filedir.get_dest_location("something/real/fake")

        self.assertEqual(pathlib.Path(f"/tmp/.something/real/fake"), dest)

    def test_dest_location_single_path(self):
        filename = "nothomefake"
        dest = filedir.get_dest_location(filename, dotfile=False)

        self.assertEqual(pathlib.Path(f"/tmp/{filename}"), dest)

    def test_dest_location_target_dir(self):
        dest = filedir.get_dest_location(
            "nothomefake", target_dir="/something/else", dotfile=False
        )

        self.assertEqual(pathlib.Path("/something/else/nothomefake"), dest)

    def test_dest_location_target_dir_dotfile_single(self):
        dest = filedir.get_dest_location("nothomefake", target_dir="/something/else")

        self.assertEqual(pathlib.Path("/something/else/.nothomefake"), dest)

    def test_dest_location_target_dir_dotfile_multiple(self):
        filename = "not/omefake"
        target_dir = "/something/else"
        dest = filedir.get_dest_location(filename, target_dir=target_dir)

        self.assertEqual(pathlib.Path(f"{target_dir}/.{filename}"), dest)

    def test_dest_location_path(self):
        dest = filedir.get_dest_location("rel/sub/not/omefake", dotfile=False)

        self.assertEqual(pathlib.Path(f"/tmp/rel/sub/not/omefake"), dest)
