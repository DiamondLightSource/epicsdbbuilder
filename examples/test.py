import os
import sys
import platform
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from epicsdbbuilder import *

InitialiseDbd(os.environ['EPICS_BASE'], os.environ.get('EPICS_HOST_ARCH', None))

tmpl_names = TemplateRecordNames()
dls_names = SimpleRecordNames('XX-YY-ZZ-01', ':')

SetRecordNames(dls_names)

P = Parameter('P', 'A parameter')
Q = Parameter('Q', 'A number')

r = ImportRecord('SR-DI-DCCT-01:SIGNAL')

records.bi('TRIG',
    FLNK = create_fanout('FAN',
        records.longin('A', DESC = 'blah'),
        records.ai('B', INP = r)),
    SCAN = '1 second')

s = ImportRecord(RecordName('TRIG'))

PushPrefix('ABC')

records.ai('TEST')


SetRecordNames(tmpl_names)

t = records.ai('TEST',
    INP = '@%s' % P, VAL = Q, SCAN = '1 second')
records.bi('BOO', INP = s)

if platform.system() == 'Windows':
    WriteRecords(os.path.join(os.path.dirname(__file__), 'test_output.db'))
else:
    WriteRecords('/dev/stdout')
