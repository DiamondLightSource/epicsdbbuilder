[![CI](https://github.com/DiamondLightSource/epicsdbbuilder/actions/workflows/ci.yml/badge.svg)](https://github.com/DiamondLightSource/epicsdbbuilder/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/DiamondLightSource/epicsdbbuilder/branch/main/graph/badge.svg)](https://codecov.io/gh/DiamondLightSource/epicsdbbuilder)
[![PyPI](https://img.shields.io/pypi/v/epicsdbbuilder.svg)](https://pypi.org/project/epicsdbbuilder)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

# epicsdbbuilder

This Python module is designed to make it easy to build complex EPICS databases
by writing a Python script.  While writing record templates the corresponding
dbd entries are checked to reduce the number of errors in the database.


Source          | <https://github.com/DiamondLightSource/epicsdbbuilder>
:---:           | :---:
PyPI            | `pip install epicsdbbuilder`
Docker          | `docker run ghcr.io/diamondlightsource/epicsdbbuilder:latest`
Documentation   | <https://diamondlightsource.github.io/epicsdbbuilder>
Releases        | <https://github.com/DiamondLightSource/epicsdbbuilder/releases>

A simple example of the use of this library is the following:

```python

    from epicsdbbuilder import *
    InitialiseDbd('/dls_sw/epics/R3.14.12.3/base/')
    SetTemplateRecordNames()

    a = records.ao('TEST')
    c = records.calc('CALC', CALC = 'A+B', SCAN = '1 second', INPA = a.VAL)
    c.INPB = c

    WriteRecords('output.db')
```

<!-- README only content. Anything below this line won't be included in index.md -->

See https://diamondlightsource.github.io/epicsdbbuilder for more detailed documentation.
