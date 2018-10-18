################################################################################
#
# pgldapsync
#
# Synchronise Postgres roles with users in an LDAP directory.
#
# pgldapsync/ldaputils/connection.py - LDAP connection functions
#
# Copyright 2018, EnterpriseDB Corporation
#
################################################################################

from ldap3 import Connection, Server
from ldap3.core.exceptions import *
import sys

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def connect_ldap_server(config):
    """Setup the connection to the LDAP server.

    Args:
        config (ConfigParser): The application configuration

    Returns:
        ldap3.core.connection.Connection: The LDAP connection object
    """
    # Parse the server URI
    uri = urlparse(config.get('ldap', 'server_uri'))

    # Create the server object
    tls = None
    server = Server(uri.hostname, port=uri.port, tls=tls)

    # Create the connection
    conn = None
    try:
        if config.get('ldap', 'bind_username') == '':
            conn = Connection(server, auto_bind=True)
        else:
            conn = Connection(server,
                              config.get('ldap', 'bind_username'),
                              config.get('ldap', 'bind_password'),
                              auto_bind=True)
    except LDAPSocketOpenError, e:
        sys.stderr.write("Error connecting to the LDAP server: %s\n" % e)
    except LDAPBindError, e:
        sys.stderr.write("Error binding to the LDAP server: %s\n" % e)

    return conn
