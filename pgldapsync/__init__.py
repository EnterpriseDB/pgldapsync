import argparse
import ConfigParser

from pgldapsync.ldaputils.connection import connect_ldap_server
from pgldapsync.ldaputils.users import *
from pgldapsync.pgutils.connection import connect_pg_server
from pgldapsync.pgutils.roles import *

global config


def get_create_login_roles(ldap_users, pg_roles):
    roles = []

    for user in ldap_users:
        if user not in pg_roles:
            roles.append(user)

    return roles


def get_drop_login_roles(ldap_users, pg_roles):
    roles = []

    for role in pg_roles:
        if role not in ldap_users:
            roles.append(role)

    return roles


def main():
    """
    The core structure of the app
    """

    # Command line arguments
    parser = argparse.ArgumentParser(
        description='Synchronise users and groups from LDAP/AD to PostgreSQL.')
    parser.add_argument("--dry-run", "-d", action='store_true',
                        help="don't apply changes to the database server, "
                             "dump the SQL to stdout instead")
    parser.add_argument("config", metavar="CONFIG_FILE",
                        help="the configuration file to read")

    args = parser.parse_args()

    if args.dry_run:
        print("-- This is an LDAP sync dry run.")
        print("-- The commands below can be manually executed if required.")

    # Set the config file path in builtins so config.py can find it
    config = ConfigParser.ConfigParser()
    try:
        config.read(args.config)
    except ConfigParser.Error, e:
        sys.stderr.write("Error reading configuration file: %s\n" % e)
        sys.exit(1)

    # Get the LDAP users
    ldap_conn = connect_ldap_server(config)
    if ldap_conn is None:
        sys.exit(1)

    ldap_users = get_filtered_ldap_users(config, ldap_conn)
    if ldap_users is None:
        sys.exit(1)

    # Get the Postgres users
    pg_conn = connect_pg_server(config.get('postgres', 'server_connstr'))
    if pg_conn is None:
        sys.exit(1)

    pg_login_roles = get_filtered_pg_login_roles(config, pg_conn)
    if pg_login_roles is None:
        sys.exit(1)

    login_roles_to_create = get_create_login_roles(ldap_users, pg_login_roles)
    login_roles_to_drop = get_drop_login_roles(ldap_users, pg_login_roles)

    # Create/drop roles if required
    have_work = ((config.getboolean('general',
                                    'add_ldap_users_to_postgres') and
                  len(login_roles_to_create) > 0) or
                 (config.getboolean('general',
                                    'remove_login_roles_from_postgres') and
                  len(login_roles_to_drop) > 0))

    login_roles_added = 0
    login_roles_dropped = 0
    login_roles_add_errors = 0
    login_roles_drop_errors = 0

    cur = None
    if have_work:
        if args.dry_run:
            print("BEGIN;")
        else:
            cur = pg_conn.cursor()
            cur.execute("BEGIN;")

    if config.getboolean('general', 'add_ldap_users_to_postgres'):
        # Generate the attribute list
        attribute_list = get_role_attributes(config)

        for role in login_roles_to_create:
            role_name = role.replace('\'', '\\\'')
            role_grants = get_role_grants(config, role_name)
            role_admin_grants = get_role_grants(config, role_name, True)

            if args.dry_run:
                print('CREATE ROLE "%s" LOGIN %s;' %
                      (role_name, attribute_list))
                print role_grants
                print role_admin_grants
            else:
                try:
                    # We can't use a real parameterised query here as we're
                    # working with an object, not data.
                    cur.execute('SAVEPOINT cr; CREATE ROLE "%s" LOGIN %s;%s%s'
                                % (role_name, attribute_list,
                                   role_grants, role_admin_grants))
                    login_roles_added = login_roles_added + 1
                except psycopg2.Error, e:
                    sys.stderr.write("Error creating role %s: %s" % (role, e))
                    login_roles_add_errors = login_roles_add_errors + 1
                    cur.execute('ROLLBACK TO SAVEPOINT cr;')

    if config.getboolean('general', 'remove_login_roles_from_postgres'):
        for role in login_roles_to_drop:
            if args.dry_run:
                print('DROP ROLE "%s";' % role.replace('\'', '\\\''))
            else:
                try:
                    # We can't use a real parameterised query here as we're
                    # working with an object, not data.
                    cur.execute('SAVEPOINT dr; DROP ROLE "%s";' %
                                role.replace('\'', '\\\''))
                    login_roles_dropped = login_roles_dropped + 1
                except psycopg2.Error, e:
                    sys.stderr.write("Error dropping role %s: %s" % (role, e))
                    login_roles_drop_errors = login_roles_drop_errors + 1
                    cur.execute('ROLLBACK TO SAVEPOINT dr;')

    if have_work:
        if args.dry_run:
            print("COMMIT;")
        else:
            cur.execute("COMMIT;")
            cur.close()
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
