import ldap


def connect_ldap_server(ldap_url):
    try:
        conn = ldap.initialize(ldap_url)
        conn.protocol_version = ldap.VERSION3

    except ldap.LDAPError, e:
        print("Error connecting to the LDAP server: %s" % e)
        return None

    return conn