# pgldapsync

This Python module allows you to synchronise Postgres login roles
with users in an LDAP directory.

In order to use it, you will need to create a _config_local.py_ 
file alongside _config.py_ containing the site-specific 
configuration you require. See _config.py_ for a complete list
of all the available configuration options.

Once configured, simply run pgldapsync like so:

    python pgldapsync.py
    
In order to test the configuration (and dump the SQL that would
be executed to stdout), run it like this:

    python pgldapsync.py --dry-run

## Creating a virtual environment for dev/test

Assuming you have the virtualenv package installed:

    venv pgldapsync
    source pgldapsync/bin/activate.sh
    pip install -r requirements.txt
    
Adapt the first command as required for your environment/Python
version.

## Creating a package

To create a package (wheel), run the following in your virtual 
environment:

    python setup.py sdist bdist_wheel

Copyright 2018, EnterpriseDB Corporation