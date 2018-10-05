import ldap

from pgldapsync import config


def get_ldap_users(conn):
    users = []

    try:
        res = conn.search(config.LDAP_BASE_DN, config.LDAP_SEARCH_SCOPE,
                          '(cn=*)')

        while 1:
            types, data = conn.result(res, 0)

            if not data:
                break

            record = data[0][1]

            users.append(record[config.LDAP_USERNAME_ATTRIBUTE][0])

    except ldap.LDAPError, e:
        sys.stderr.write("Error retrieving LDAP users: %s" %
                         e.message['desc'])
        return None

    return users


def get_filtered_ldap_users(conn):
    users = get_ldap_users(conn)
    if users is None:
        return None

    # Remove ignored users
    for user in config.LDAP_IGNORE_USERS:
        try:
            users.remove(user)
        except:
            pass

    return users