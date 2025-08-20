#!/usr/bin/env python

import datetime
import tempfile
import unittest

from waflibs.dns import bind
from waflibs import text


class TestDns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bind_dir = tempfile.TemporaryDirectory()

        cls.serial = int(datetime.datetime.now().strftime("%Y%m%d00"))
        cls.bind_dir = bind_dir
        cls.domain = "test.com"
        cls.records = [
            {
                "name": "fullname.record.",
                "type": "CNAME",
                "content": "nodot",
                "proxied": False,
            },
            {
                "name": "shortname",
                "type": "CNAME",
                "content": "hasadot.",
                "proxied": False,
            },
            {
                "name": "test",
                "type": "A",
                "content": "1.2.3.4",
                "proxied": False,
            },
            {
                "name": "longtest.",
                "type": "AAAA",
                "content": "123:ABC::4",
                "proxied": False,
            },
            {
                "name": "sigh.test.com.",
                "type": "A",
                "content": "2.3.4.5",
                "proxied": False,
            },
            {
                "name": "test.com.",
                "type": "MX",
                "content": "mx.garbage",
                "proxied": False,
                "priority": 99,
            },
            {
                "name": "nameserver",
                "type": "NS",
                "content": "name.server.",
                "proxied": False,
            },
        ]
        cls.result = """; HEADER

$ORIGIN test.com

{}

fullname.record. IN CNAME nodot
shortname IN CNAME hasadot.
test IN A 1.2.3.4
longtest. IN AAAA 123:ABC::4
sigh.test.com. IN A 2.3.4.5
test.com. IN MX 99 mx.garbage
nameserver IN NS name.server.

; 7 total records found

"""

    @classmethod
    def tearDownClass(cls):
        cls.bind_dir.cleanup()

    def setUp(self):
        tf = tempfile.NamedTemporaryFile()
        tf.write(b"; HEADER\n\n$ORIGIN {zone}\n\n{serial}\n")
        tf.seek(0)

        self.template_file = tf

        dtf = tempfile.NamedTemporaryFile()
        dtf.write(b"{records}\n")
        dtf.seek(0)

        self.domain_template_file = dtf

        s = open(f"{self.bind_dir.name}/serial", "w")
        s.write(str(self.serial))
        s.write("\n")
        s.seek(0)

        self.serial_file = s

    def test_generate_serial(self):
        serial_filename = tempfile.NamedTemporaryFile()

        serial = bind.generate_serial(
            serial_number=self.serial,
            serial_file=serial_filename.name,
        )
        self.assertEqual(serial, self.serial)

    def test_generate_serial_filename(self):
        serial_filename = tempfile.NamedTemporaryFile()

        serial = bind.generate_serial(
            serial_file=serial_filename.name,
        )
        self.assertEqual(serial, self.serial)

    def test_generate_bind_file_serial(self):
        zone_file_name = bind.generate_bind_file(
            self.records,
            self.domain,
            serial_number=self.serial,
            serial_file=self.serial_file.name,
            bind_dir=self.bind_dir.name,
            template_file_name=self.template_file.name,
            domain_template_file_name=self.domain_template_file.name,
        )

        with open(zone_file_name) as f:
            self.assertEqual(f.read(), self.result.format(self.serial))

    def test_generate_bind_file_no_serial(self):
        zone_file_name = bind.generate_bind_file(
            self.records,
            self.domain,
            bind_dir=self.bind_dir.name,
            template_file_name=self.template_file.name,
            domain_template_file_name=self.domain_template_file.name,
            serial_file=self.serial_file.name,
        )

        with open(zone_file_name) as f:
            self.assertEqual(f.read(), self.result.format(self.serial + 1))


if __name__ == "__main__":
    unittest.main()
