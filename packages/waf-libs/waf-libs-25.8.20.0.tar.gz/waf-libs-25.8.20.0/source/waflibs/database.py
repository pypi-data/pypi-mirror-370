#!/usr/bin/env python
"""utils for mysql stuffs"""

import mysql.connector
import psycopg


def mysql_connect(host, user, password, database, buffered=False):
    """mysql connector"""

    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        db=database,
        buffered=buffered,
    )


def postgresql_connect(host, user, password, database):
    """postgresql connector"""

    return psycopg.connect(
        dbname=database,
        user=user,
        password=password,
        host=host,
    )


postgres_connect = postgresql_connect
