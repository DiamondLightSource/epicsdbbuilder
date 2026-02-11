EPICS Database Builder
======================

|code_ci| |docs_ci| |coverage| |pypi_version| |license|

This Python module is designed to make it easy to build complex EPICS databases
by writing a Python script.  While writing record templates the corresponding
dbd entries are checked to reduce the number of errors in the database.

============== ==============================================================
PyPI           ``pip install epicsdbbuilder``
Source code    https://github.com/DiamondLightSource/epicsdbbuilder

Releases       https://github.com/DiamondLightSource/epicsdbbuilder/releases
============== ==============================================================

A simple example of the use of this library is the following:

.. code-block:: python

    from epicsdbbuilder import *
    InitialiseDbd('/dls_sw/epics/R3.14.12.3/base/')
    SetTemplateRecordNames()

    a = records.ao('TEST')
    c = records.calc('CALC', CALC = 'A+B', SCAN = '1 second', INPA = a.VAL)
    c.INPB = c

    WriteRecords('output.db')

.. |code_ci| image:: https://github.com/DiamondLightSource/epicsdbbuilder/actions/workflows/code.yml/badge.svg?branch=main
    :target: https://github.com/DiamondLightSource/epicsdbbuilder/actions/workflows/code.yml
    :alt: Code CI

.. |docs_ci| image:: https://github.com/DiamondLightSource/epicsdbbuilder/actions/workflows/docs.yml/badge.svg?branch=main
    :target: https://github.com/DiamondLightSource/epicsdbbuilder/actions/workflows/docs.yml
    :alt: Docs CI

.. |coverage| image:: https://codecov.io/gh/DiamondLightSource/epicsdbbuilder/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/DiamondLightSource/epicsdbbuilder
    :alt: Test Coverage

.. |pypi_version| image:: https://img.shields.io/pypi/v/epicsdbbuilder.svg
    :target: https://pypi.org/project/epicsdbbuilder
    :alt: Latest PyPI version

.. |license| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :target: https://opensource.org/licenses/Apache-2.0
    :alt: Apache License
