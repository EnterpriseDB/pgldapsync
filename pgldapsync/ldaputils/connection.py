import sys
import ldap

from pgldapsync import config


def connect_ldap_server(ldap_url):
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

    try:
        conn = ldap.initialize(ldap_url)
        conn.protocol_version = ldap.VERSION3

    except ldap.LDAPError, e:
        sys.stderr.write("Error connecting to the LDAP server: %s\n" % e)
        return None

    # Setup LDAP options
    conn.protocol_version = 3
    conn.set_option(ldap.OPT_REFERRALS, 0)

    # Enable TLS if required
    if (config.LDAP_USE_STARTTLS and not
        config.LDAP_SERVER_URI[:5].lower() == 'ldaps'):
        try:
            conn.start_tls_s()
        except ldap.LDAPError, e:
            sys.stderr.write("Error starting TLS: %s\n" % e.message['info'])
            return None

    # Bind, if configured to do so
    if config.LDAP_BIND_USERNAME != "":
        try:
            conn.simple_bind_s(config.LDAP_BIND_USERNAME,
                               config.LDAP_BIND_PASSWORD)
        except ldap.LDAPError, e:
            sys.stderr.write("Error binding to the LDAP server: %s\n" % e)
            return None

    return conn
