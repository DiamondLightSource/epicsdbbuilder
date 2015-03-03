import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from epicsdbbuilder import *

InitialiseDbd(os.environ['EPICS_BASE'])

tmpl_names = SetTemplateRecordNames()
dls_names = BasicRecordNames('XX-YY-ZZ-01')

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


SetRecordNames(tmpl_names)

t = records.ai('TEST',
    INP = '@%s' % P, VAL = Q, SCAN = '1 second')
records.bi('BOO', INP = s)

WriteRecords('/dev/stdout')
