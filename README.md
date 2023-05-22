# pgldapsync

This Python module allows you to synchronise Postgres login roles
with users in an LDAP directory.

*pgldapsync is supported on Python 3.7 or later.*

In order to use it, you will need to create a _config.ini_ 
file containing the site-specific configuration you require. 
See _config.ini.example_ for a complete list of all the 
available configuration options. This file should be copied to
create your own configuration.

Once configured, simply run pgldapsync like so:

    python3 pgldapsync.py /path/to/config.ini
    
In order to test the configuration (and dump the SQL that would
be executed to stdout), run it like this:

    python3 pgldapsync.py --dry-run /path/to/config.ini

## Creating a virtual environment for dev/test

    python3 -m venv /path/to/pgldapsync
    source /path/to/pgldapsync/bin/activate.sh
    pip install -r requirements.txt
    
Adapt the first command as required for your environment/Python
version.

## Creating a package

To create a package (wheel), run the following in your virtual 
environment:

    python3 setup.py sdist bdist_wheel --universal

Copyright 2018 - 2023, EnterpriseDB Corporation
