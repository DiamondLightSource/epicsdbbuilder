'''Support for default record name configurations.'''

import parameter


__all__ = [
    'SimpleRecordNames',
    'SetSimpleRecordNames', 'SetTemplateRecordNames',
    'RecordName', 'SetRecordNames', 'GetRecordNames', 'SetPrefix']


# Default record name support: each record is created with precisely the name
# it is given.
class SimpleRecordNames(object):
    # Maximum record name length for EPICS 3.14
    maxLength = 61

    def __init__(self, prefix = '', separator = '', check = True):
        self.prefix = prefix
        self.separator = separator
        self.check = check

    def __call__(self, name):
        assert self.prefix is not None, 'Record name prefix is undefined'
        name = '%s%s%s' % (self.prefix, self.separator, name)
        assert not self.check or 0 < len(name) <= self.maxLength, \
            'Record name "%s" too long' % name
        return name

    def SetPrefix(self, prefix):
        self.prefix = prefix

def SetSimpleRecordNames(prefix = '', separator = ''):
    SetRecordNames(SimpleRecordNames(prefix, separator))

def SetTemplateRecordNames(prefix = None, separator = ':'):
    if prefix is None:
        prefix = parameter.Parameter('DEVICE', 'Device name')
    SetRecordNames(SimpleRecordNames(prefix, separator, False))


# By default record names are unmodified.
_RecordNames = lambda name: name

def SetRecordNames(names):
    global _RecordNames
    current = _RecordNames
    _RecordNames = names
    return current

def GetRecordNames():
    return _RecordNames

def RecordName(name):
    return _RecordNames(name)

def SetPrefix(prefix):
    _RecordNames.SetPrefix(prefix)
