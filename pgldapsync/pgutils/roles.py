import psycopg2
import sys

from pgldapsync import config


def get_pg_login_roles(conn):
    cur = conn.cursor()

    try:
        cur.execute("SELECT rolname FROM pg_authid WHERE rolcanlogin;")
        rows = cur.fetchall()
    except psycopg2.Error, e:
        sys.stderr.write("Error retrieving Postgres login roles: %s\n" % e)
        return None

    roles = []

    for row in rows:
        roles.append(row[0])

    cur.close()

    return roles


def get_filtered_pg_login_roles(conn):
    roles = get_pg_login_roles(conn)
    if roles is None:
        return None

    # Remove ignored roles
    for role in config.PG_IGNORE_LOGIN_ROLES:
        try:
            roles.remove(role)
        except:
            pass

    return roles


def get_role_attributes():
    attribute_list = ''
    if config.ROLE_ATTRIBUTE_SUPERUSER:
        attribute_list = attribute_list + 'SUPERUSER'
    else:
        attribute_list = attribute_list + 'NOSUPERUSER'

    if config.ROLE_ATTRIBUTE_CREATEDB:
        attribute_list = attribute_list + ' CREATEDB'
    else:
        attribute_list = attribute_list + ' NOCREATEDB'

    if config.ROLE_ATTRIBUTE_CREATEROLE:
        attribute_list = attribute_list + ' CREATEROLE'
    else:
        attribute_list = attribute_list + ' NOCREATEROLE'

    if config.ROLE_ATTRIBUTE_NOINHERIT:
        attribute_list = attribute_list + ' NOINHERIT'
    else:
        attribute_list = attribute_list + ' INHERIT'

    if config.ROLE_ATTRIBUTE_BYPASSRLS:
        attribute_list = attribute_list + ' BYPASSRLS'
    else:
        attribute_list = attribute_list + ' NOBYPASSRLS'

    if config.ROLE_ATTRIBUTE_CONNECTION_LIMIT is not None:
        attribute_list = attribute_list + ' CONNECTION LIMIT ' + \
                         str(config.ROLE_ATTRIBUTE_CONNECTION_LIMIT)

    return attribute_list
