###############################################################################
#
# pgldapsync
#
# Synchronise Postgres roles with users in an LDAP directory.
#
# pgldapsync/pgutils/connection.py - Postgres connection functions
#
# Copyright 2018 - 2021, EnterpriseDB Corporation
#
###############################################################################

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
    except psycopg2.Error as e:
        sys.stderr.write("Error connecting to the Postgres server: %s\n" % e)
        return None

    return conn
