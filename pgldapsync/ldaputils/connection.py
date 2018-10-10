import sys
import ldap


def connect_ldap_server(config):
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

    try:
        conn = ldap.initialize(config.get('ldap', 'server_uri'))
        conn.protocol_version = ldap.VERSION3

    except ldap.LDAPError, e:
        sys.stderr.write("Error connecting to the LDAP server: %s\n" % e)
        return None

    # Setup LDAP options
    conn.protocol_version = 3
    conn.set_option(ldap.OPT_REFERRALS, 0)

    # Enable TLS if required
    if (config.getboolean('ldap', 'use_starttls') and not
        config.get('ldap', 'server_uri')[:5].lower() == 'ldaps'):
        try:
            conn.start_tls_s()
        except ldap.LDAPError, e:
            sys.stderr.write("Error starting TLS: %s\n" % e.message['info'])
            return None

    # Bind, if configured to do so
    if config.get('ldap', 'bind_username') != "":
        try:
            conn.simple_bind_s(config.get('ldap', 'bind_username'),
                               config.get('ldap', 'bind_password'))
        except ldap.LDAPError, e:
            sys.stderr.write("Error binding to the LDAP server: %s\n" % e)
            return None

    return conn
