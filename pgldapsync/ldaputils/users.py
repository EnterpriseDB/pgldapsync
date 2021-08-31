###############################################################################
#
# pgldapsync
#
# Synchronise Postgres roles with users in an LDAP directory.
#
# pgldapsync/ldaputils/users.py - LDAP user functions
#
# Copyright 2018 - 2021, EnterpriseDB Corporation
#
###############################################################################

from ldap3.core.exceptions import *
import sys


def get_ldap_users(config, conn, admin):
    """Get a list of users from the LDAP server.

    Args:
        config (ConfigParser): The application configuration
        conn (ldap3.core.connection.Connection): The LDAP connection object
        admin (bool): Return users in the admin group?
    Returns:
        str[]: A list of user names
    """
    users = []

    if admin:
        base_dn = config.get('ldap', 'admin_base_dn')
        search_filter = config.get('ldap', 'admin_filter_string')
    else:
        base_dn = config.get('ldap', 'base_dn')
        search_filter = config.get('ldap', 'filter_string')

    try:
        conn.search(base_dn,
                    search_filter,
                    config.get('ldap', 'search_scope'),
                    attributes=[config.get('ldap', 'username_attribute')]
                          )
    except LDAPInvalidScopeError as e:
        sys.stderr.write("Error searching the LDAP directory: %s\n" % e)
        sys.exit(1)
    except LDAPAttributeError as e:
        sys.stderr.write("Error searching the LDAP directory: %s\n" % e)
        sys.exit(1)
    except LDAPInvalidFilterError as e:
        sys.stderr.write("Error searching the LDAP directory: %s\n" % e)
        sys.exit(1)

    for entry in conn.entries:
        users.append(entry[config.get('ldap', 'username_attribute')].value)

    return users


def get_filtered_ldap_users(config, conn, admin):
    """Get a filtered list of users from the LDAP server, having removed users
    to be ignored.

    Args:
        config (ConfigParser): The application configuration
        conn (ldap3.core.connection.Connection): The LDAP connection object
        admin (bool): Return users in the admin group?
    Returns:
        str[]: A filtered list of user names
    """
    users = get_ldap_users(config, conn, admin)
    if users is None:
        return None

    # Remove ignored users
    for user in config.get('ldap', 'ignore_users').split(','):
        try:
            users.remove(user)
        except:
            pass

    return users
