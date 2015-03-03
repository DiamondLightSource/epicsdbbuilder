import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from epicsdbbuilder import *

InitialiseDbd(os.environ['EPICS_BASE'])

SetRecordNames(TemplateRecordNames())
names = DiamondRecordNames()
names.SetDeviceName('XX-YY-ZZ-01')
SetRecordNames(names)

P = Parameter('P', 'A parameter')

r = ImportRecord('SR-DI-DCCT-01:SIGNAL')

records.bi('TRIG',
    FLNK = create_fanout('FAN',
        records.longin('A', DESC = 'blah'),
        records.ai('B', INP = r)),
    SCAN = '1 second')

s = ImportName('TRIG')

PopRecordNames()

t = records.ai('TEST',
    INP = '@%s' % P, SCAN = '1 second')
records.bi('BOO', INP = s)

WriteRecords('/dev/stdout', '')
