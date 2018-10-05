import psycopg2

from pgldapsync import config


def get_pg_login_roles(conn):

    cur = conn.cursor()

    try:
        cur.execute("SELECT rolname FROM pg_authid WHERE rolcanlogin;")
        rows = cur.fetchall()
    except psycopg2.Error, e:
        print ("Error retrieving Postgres login roles: %s" % e)
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