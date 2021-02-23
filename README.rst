EPICS Database Builder
======================

|code_ci| |docs_ci| |coverage| |pypi_version| |license|

This Python module is designed to make it easy to build complex EPICS databases
by writing a Python script.  While writing record templates the corresponding
dbd entries are checked to reduce the number of errors in the database.

============== ==============================================================
PyPI           ``pip install epicsdbbuilder``
Source code    https://github.com/dls-controls/epicsdbbuilder
Documentation  https://dls-controls.github.io/epicsdbbuilder
============== ==============================================================

A simple example of the use of this library is the following:

.. code:: python

    from epicsdbbuilder import *
    InitialiseDbd('/dls_sw/epics/R3.14.12.3/base/')
    SetTemplateRecordNames()

    a = records.ao('TEST')
    c = records.calc('CALC', CALC = 'A+B', SCAN = '1 second', INPA = a.VAL)
    c.INPB = c

    WriteRecords('output.db')

.. |code_ci| image:: https://github.com/dls-controls/epicsdbbuilder/workflows/Code%20CI/badge.svg?branch=master
    :target: https://github.com/dls-controls/epicsdbbuilder/actions?query=workflow%3A%22Code+CI%22
    :alt: Code CI

.. |docs_ci| image:: https://github.com/dls-controls/epicsdbbuilder/workflows/Docs%20CI/badge.svg?branch=master
    :target: https://github.com/dls-controls/epicsdbbuilder/actions?query=workflow%3A%22Docs+CI%22
    :alt: Docs CI

.. |coverage| image:: https://codecov.io/gh/dls-controls/epicsdbbuilder/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/dls-controls/epicsdbbuilder
    :alt: Test Coverage

.. |pypi_version| image:: https://img.shields.io/pypi/v/epicsdbbuilder.svg
    :target: https://pypi.org/project/epicsdbbuilder
    :alt: Latest PyPI version

.. |license| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :target: https://opensource.org/licenses/Apache-2.0
    :alt: Apache License

..
    Anything below this line is used when viewing README.rst and will be replaced
    when included in index.rst

See https://dls-controls.github.io/epicsdbbuilder for more detailed documentation.


