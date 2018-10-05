import psycopg2


def connect_pg_server(pg_connstr):
    try:
        conn = psycopg2.connect(pg_connstr)
    except psycopg2.Error, e:
        print("Error connecting to the Postgres server: %s" % e)
        return None

    return conn