from setuptools import setup

# these lines allow the version to be specified in Makefile.private
import os
version = os.environ.get("MODULEVER", "development")

setup(
    name = 'epicsdbbuilder',
    version = version,
    description = 'EPICS Database Builder',
    long_description = open('README.rst', 'rt').read(),
    url = 'https://github.com/Araneidae/epicsdbbuilder',
    author = 'Michael Abbott',
    author_email = 'Michael.Abbott@diamond.ac.uk',
    packages = ['epicsdbbuilder'])
