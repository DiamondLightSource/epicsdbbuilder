EPICS Database Builder
======================

This Python module is designed to make it easy to build complex EPICS databases
by writing a Python script.  While writing record templates the corresponding
dbd entries are checked to reduce the number of errors in the database.

A simple example of the use of this library is the following::

    from epicsdbbuilder import *
    InitialiseDbd('/dls_sw/epics/R3.14.12.3/base/')
    SetTemplateRecordNames()

    a = records.ao('TEST')
    c = records.calc('CALC', CALC = 'A+B', SCAN = '1 second', INPA = a.VAL)
    c.INPB = c

    WriteRecords('output.db')

See the ``docs`` directory for more detailed documentation.
