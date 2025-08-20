#!/usr/bin/env/python

import os
import unittest
import unittest.mock

from waflibs import config, database


class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        creds = {
            "host": "blah",
            "username": "blah",
            "password": "blah",
            "database": "blah",
        }
        cls.config = {
            "postgres_credentials": creds,
            "mysql_credentials": creds,
        }


class TestMysql(TestDatabase):
    @unittest.mock.patch("mysql.connector.connect")
    def test_mysql_connect(self, external):
        mysql_config = self.config["mysql_credentials"]

        database.mysql_connect(
            mysql_config["host"],
            mysql_config["username"],
            mysql_config["password"],
            mysql_config["database"],
        )


class TestPostgresql(TestDatabase):
    @unittest.mock.patch("psycopg.connect")
    def test_postgresql_connect(self, external):
        postgres_config = self.config["postgres_credentials"]

        database.postgresql_connect(
            postgres_config["host"],
            postgres_config["username"],
            postgres_config["password"],
            postgres_config["database"],
        )


if __name__ == "__main__":
    unittest.main()
