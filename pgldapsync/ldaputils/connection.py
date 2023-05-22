###############################################################################
#
# pgldapsync
#
# Synchronise Postgres roles with users in an LDAP directory.
#
# Copyright 2018 - 2023, EnterpriseDB Corporation
#
###############################################################################

"""LDAP connection functions."""

# FIX THIS!
# pylint: disable=too-many-branches

import ssl
import sys

from ldap3 import Connection, Server, Tls
from ldap3.core.exceptions import LDAPBindError, LDAPSocketOpenError, \
    LDAPStartTLSError


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

    # Create the TLS configuration object if required
    tls = None

    if uri.scheme == 'ldaps' or config.getboolean('ldap', 'use_starttls'):

        ca_cert_file = None
        if config.get('ldap', 'ca_cert_file') != '':
            ca_cert_file = config.get('ldap', 'ca_cert_file')

        cert_file = None
        if config.get('ldap', 'cert_file') != '':
            cert_file = config.get('ldap', 'cert_file')

        key_file = None
        if config.get('ldap', 'key_file') != '':
            key_file = config.get('ldap', 'key_file')

        tls = Tls(
            local_private_key_file=key_file,
            local_certificate_file=cert_file,
            validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1,
            ca_certs_file=ca_cert_file)

    # Debug
    if config.getboolean('ldap', 'debug'):
        sys.stderr.write("TLS/SSL configuration:   %s\n" % tls)

    # Create the server object
    server = Server(uri.hostname,
                    port=uri.port,
                    tls=tls,
                    use_ssl=(uri.scheme == 'ldaps'))

    # Debug
    if config.getboolean('ldap', 'debug'):
        sys.stderr.write("LDAP server config:      %s\n" % server)

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
    except LDAPSocketOpenError as exception:
        sys.stderr.write("Error connecting to the LDAP server: %s\n" %
                         exception)
    except LDAPBindError as exception:
        sys.stderr.write("Error binding to the LDAP server: %s\n" % exception)

    # Debug
    if config.getboolean('ldap', 'debug'):
        sys.stderr.write("Initial LDAP connection: %s\n" % conn)

    # Enable TLS if STARTTLS is configured
    if uri.scheme != 'ldaps' and config.getboolean('ldap', 'use_starttls'):
        try:
            conn.start_tls()
        except LDAPStartTLSError as exception:
            sys.stderr.write("Error starting TLS: %s\n" % exception)
            return None

    # Debug
    if config.getboolean('ldap', 'debug'):
        sys.stderr.write("Final LDAP connection:   %s\n" % conn)

    return conn
