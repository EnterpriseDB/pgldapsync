###############################################################################
#
# pgldapsync
#
# Synchronise Postgres roles with users in an LDAP directory.
#
# Copyright 2018 - 2021, EnterpriseDB Corporation
#
###############################################################################

"""pgldapsync package creation."""

import sys
import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

# Get the requirements list for the current version of Python
    with open('requirements.txt', 'r', encoding='utf-8') as reqf:
        required = reqf.read().splitlines()

setuptools.setup(
    name="pgldapsync",
    version="2.0.0",
    author="Dave Page",
    author_email="dave.page@enterprisedb.com",
    description="Synchronise LDAP users to Postgres",
    license='PostgreSQL',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/enterprisedb/pgldapsync",
    packages=setuptools.find_packages(),
    install_requires=required,
    python_requires='>=3.5',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "License :: OSI Approved :: PostgreSQL License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': ['pgldapsync=pgldapsync.__init__:main'],
    },
    include_package_data=True
)
