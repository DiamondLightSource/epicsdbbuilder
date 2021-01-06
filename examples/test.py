# vim: set fileencoding=UTF-8:

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

# Test link options
records.ai('OPTIONS:CA', INP = CA(t))
records.ai('OPTIONS:CP', INP = CP(t))
records.ai('OPTIONS:CPP', INP = CPP(t))

# Test multiple link options
records.ai('OPTIONS:PP:MS', INP = PP(MS(t)))

# Test custom field formatting
class CustomFieldWithPrint:
    def __init__(self, value):
        self.value = value

    def Validate(self, record, fieldname):
        return True

    def Print(self, record, fieldname):
        return f'["{self.value}"]'

    def __str__(self):
        return "you should not see me!"

records.ai('FIELD:CUSTOM_WITH_PRINT', INP = CustomFieldWithPrint('constant_link'))


class CustomFieldWithoutPrint:
    def __init__(self, value):
        self.value = value

    def Validate(self, record, fieldname):
        return True

    def __str__(self):
        return self.value

records.ai('FIELD:CUSTOM_WITHOUT_PRINT', INP = CustomFieldWithoutPrint('link'))

# A string constant with some evil character values
records.stringin('STRING', VAL = '"\n\\\x01€')


if platform.system() == 'Windows':
    WriteRecords(os.path.join(os.path.dirname(__file__), 'test_output.db'))
else:
    WriteRecords('/dev/stdout')
