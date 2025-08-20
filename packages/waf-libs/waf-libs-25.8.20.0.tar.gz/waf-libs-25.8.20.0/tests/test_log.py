#!/usr/bin/env python

import argparse
import unittest

from waflibs import log


class TestLog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v_parser = argparse.ArgumentParser(description="test verbose logger")
        v_parser.add_argument("-v", "--verbose", action="store_true", help="verbose")
        cls.v_args = v_parser.parse_args(["-v"])

        parser = argparse.ArgumentParser(description="test logger")
        cls.args = parser.parse_args({})


class TestLogger(TestLog):
    def tearDownModule(self):
        self.logging.shutdown()

    def test_create_verbose_logger(self):
        logger = log.logger(self.v_args).get_logger()
        logger.handlers.clear()

    def test_create_logger(self):
        logger = log.logger(self.args).get_logger()
        logger.handlers.clear()

    def test_one_logger(self):
        logger = log.logger(self.v_args).get_logger()

        with self.assertLogs(logger, level="DEBUG") as cm:
            logger.debug("test")
        self.assertRegex(str(cm.output), r".*test.*test")

        logger.handlers.clear()


if __name__ == "__main__":
    unittest.main()
