###############################################################################
#
# pgldapsync
#
# Synchronise Postgres roles with users in an LDAP directory.
#
# pgldapsync/__init__.py - Main entry point
#
# Copyright 2018 - 2021, EnterpriseDB Corporation
#
###############################################################################

import argparse
import os

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

from pgldapsync.ldaputils.connection import connect_ldap_server
from pgldapsync.ldaputils.users import *
from pgldapsync.pgutils.connection import connect_pg_server
from pgldapsync.pgutils.roles import *


def read_command_line():
    """Read the command line arguments.

    Returns:
        ArgumentParser: The parsed arguments object
    """
    parser = argparse.ArgumentParser(
        description='Synchronise users and groups from LDAP/AD to PostgreSQL.')
    parser.add_argument("--dry-run", "-d", action='store_true',
                        help="don't apply changes to the database server, "
                             "dump the SQL to stdout instead")
    parser.add_argument("config", metavar="CONFIG_FILE",
                        help="the configuration file to read")

    args = parser.parse_args()

    return args


def read_config(file):
    """Read the config file.

    Args:
        file (str): The config file to read
        pg_roles (str[]): A list of roles in Postgres

    Returns:
        ConfigParser: The config object
    """
    config = ConfigParser.ConfigParser()

    # Read the default config
    defaults = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'config_default.ini')

    try:
        config.read(defaults)
    except ConfigParser.Error as e:
        sys.stderr.write(
            "Error reading default configuration file (%s): %s\n" %
            (defaults, e))
        sys.exit(1)

    try:
        config.read(file)
    except ConfigParser.Error as e:
        sys.stderr.write(
            "Error reading user configuration file (%s): %s\n" %
            (file, e))
        sys.exit(1)

    return config


def main():
    """The core structure of the app."""

    # Read the command line options
    args = read_command_line()

    # Read the config file
    config = read_config(args.config)

    # Connect to LDAP and get the users we care about
    ldap_conn = connect_ldap_server(config)
    if ldap_conn is None:
        sys.exit(1)

    ldap_users = get_filtered_ldap_users(config, ldap_conn, False)
    if ldap_users is None:
        sys.exit(1)

    # Get the LDAP admin users, if the base DN and filter are configured
    if config.get('ldap', 'admin_base_dn') == '' or \
            config.get('ldap', 'admin_filter_string') == '':
        ldap_admin_users = []
    else:
        ldap_admin_users = get_ldap_users(config, ldap_conn, True)
    if ldap_admin_users is None:
        sys.exit(1)

    # Connect to Postgres and get the roles we care about
    pg_conn = connect_pg_server(config.get('postgres', 'server_connstr'))
    if pg_conn is None:
        sys.exit(1)

    pg_login_roles = get_filtered_pg_login_roles(config, pg_conn)
    if pg_login_roles is None:
        sys.exit(1)

    # Compare the LDAP users and Postgres roles and get the lists of roles
    # to add and drop.
    login_roles_to_create = get_create_login_roles(ldap_users, pg_login_roles)
    login_roles_to_drop = get_drop_login_roles(ldap_users, pg_login_roles)

    # Create/drop roles if required
    have_work = ((config.getboolean('general',
                                    'add_ldap_users_to_postgres') and
                  len(login_roles_to_create) > 0) or
                 (config.getboolean('general',
                                    'remove_login_roles_from_postgres') and
                  len(login_roles_to_drop) > 0))

    # Initialise the counters for operations/errors
    login_roles_added = 0
    login_roles_dropped = 0
    login_roles_add_errors = 0
    login_roles_drop_errors = 0

    # Warn the user we're in dry run mode
    if args.dry_run:
        print("-- This is an LDAP sync dry run.")
        print("-- The commands below can be manually executed if required.")

    cur = None
    if have_work:

        # Begin the transaction
        if args.dry_run:
            print("BEGIN;")
        else:
            cur = pg_conn.cursor()
            cur.execute("BEGIN;")

    # If we need to add roles to Postgres, then do so
    if config.getboolean('general', 'add_ldap_users_to_postgres'):

        # For each role, get the required attributes and SQL snippets
        for role in login_roles_to_create:
            role_name = role.replace('\'', '\\\'')
            role_grants = get_role_grants(config, role_name)
            role_admin_grants = get_role_grants(config, role_name, True)
            attribute_list = get_role_attributes(config,
                                                 (role in ldap_admin_users))
            guc_list = get_guc_list(config, role_name)

            if args.dry_run:

                # It's a dry run, so just print the output
                print('CREATE ROLE "%s" LOGIN %s;' %
                      (role_name, attribute_list))
                print(role_grants)
                print(role_admin_grants)
                print(guc_list)
            else:

                # This is a live run, so directly execute the SQL generated.
                # For each statement, create a savepoint so we can rollback
                # to it if there's an error. That allows us to fail only
                # a single role rather than all of them.
                try:
                    # We can't use a real parameterised query here as we're
                    # working with an object, not data.
                    cur.execute('SAVEPOINT cr; CREATE ROLE "%s" LOGIN %s;%s%s%s'
                                % (role_name, attribute_list,
                                   role_grants, role_admin_grants, guc_list))
                    login_roles_added = login_roles_added + 1
                except psycopg2.Error as e:
                    sys.stderr.write("Error creating role %s: %s" % (role, e))
                    login_roles_add_errors = login_roles_add_errors + 1
                    cur.execute('ROLLBACK TO SAVEPOINT cr;')

    # If we need to drop roles from Postgres, then do so
    if config.getboolean('general', 'remove_login_roles_from_postgres'):

        # For each role to drop, just run the DROP statement
        for role in login_roles_to_drop:

            if args.dry_run:

                # It's a dry run, so just print the output
                print('DROP ROLE "%s";' % role.replace('\'', '\\\''))
            else:

                # This is a live run, so directly execute the SQL generated.
                # For each statement, create a savepoint so we can rollback
                # to it if there's an error. That allows us to fail only
                # a single role rather than all of them.
                try:
                    # We can't use a real parameterised query here as we're
                    # working with an object, not data.
                    cur.execute('SAVEPOINT dr; DROP ROLE "%s";' %
                                role.replace('\'', '\\\''))
                    login_roles_dropped = login_roles_dropped + 1
                except psycopg2.Error as e:
                    sys.stderr.write("Error dropping role %s: %s" % (role, e))
                    login_roles_drop_errors = login_roles_drop_errors + 1
                    cur.execute('ROLLBACK TO SAVEPOINT dr;')

    if have_work:

        # Commit the transaction
        if args.dry_run:
            print("COMMIT;")
        else:
            cur.execute("COMMIT;")
            cur.close()

            # Print the summary of work completed
            print("Login roles added to Postgres:     %d" % login_roles_added)
            print("Login roles dropped from Postgres: %d" % login_roles_dropped)
            if login_roles_add_errors > 0:
                print("Errors adding login roles:         %d" %
                      login_roles_add_errors)
            if login_roles_drop_errors > 0:
                print("Errors dropping login roles:       %d" %
                      login_roles_drop_errors)
    else:
        print("No login roles were added or dropped.")
