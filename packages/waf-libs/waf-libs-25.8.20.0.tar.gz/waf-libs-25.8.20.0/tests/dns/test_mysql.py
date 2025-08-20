#!/usr/bin/env python

import os
import random
import string
import unittest
import unittest.mock

from waflibs import config, database, error
from waflibs.dns import mysql


def random_string():
    return "".join(
        random.choice(string.ascii_lowercase) for i in range(random.randint(10, 51))
    )


class TestMysql(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = unittest.mock.MagicMock()
        cls.ignored_ips = ["1.7.3.0/22"]
        cls.domains = ["example.com"]


class TestAddDnsToMysql(TestMysql):
    def test_wikipedia(self):
        mysql.add_dns_to_mysql(
            self.db,
            random_string(),
            self.ignored_ips,
            self.domains,
            wikipedia_link=random_string(),
        )

    def test_valid_hostname(self):
        mysql.add_dns_to_mysql(
            self.db,
            random_string(),
            self.ignored_ips,
            self.domains,
        )

    def test_no_hostname(self):
        with self.assertRaises(error.ValidationError) as e:
            mysql.add_dns_to_mysql(
                self.db,
                None,
                self.ignored_ips,
                self.domains,
            )

        self.assertRegex(e.exception.message, r"hostname")

    def test_no_domains(self):
        mysql.add_dns_to_mysql(
            self.db,
            random_string(),
            self.ignored_ips,
        )

    def test_add_cname(self):
        mysql.add_dns_to_mysql(
            self.db,
            random_string(),
            self.ignored_ips,
            record_type="CNAME",
            content=random_string(),
        )

    def test_add_existing_cname(self):
        string = random_string()
        name = "EXISTINGCNAME"
        mysql.add_dns_to_mysql(
            self.db,
            name,
            self.ignored_ips,
            record_type="CNAME",
            content=string,
        )
        cursor = self.db.cursor(buffered=True, dictionary=True)
        cursor.execute(
            "SELECT * FROM non_numeric_records \
                WHERE name = '{}'".format(
                name
            )
        )
        results = cursor.fetchall()
        self.assertEqual(len(results), 0)
