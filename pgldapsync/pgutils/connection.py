###############################################################################
#
# pgldapsync
#
# Synchronise Postgres roles with users in an LDAP directory.
#
# Copyright 2018 - 2021, EnterpriseDB Corporation
#
###############################################################################

"""Postgres connection functions."""

import sys
import psycopg2


def connect_pg_server(pg_connstr):
    """Setup the connection to the Postgres server.

    Args:
        pg_connstr (str): The Postgres connection string

    Returns:
        connection: The psycopg2 connection object
    """
    try:
        conn = psycopg2.connect(pg_connstr)
    except psycopg2.Error as exception:
        sys.stderr.write("Error connecting to the Postgres server: %s\n" %
                         exception)
        return None

    return conn
