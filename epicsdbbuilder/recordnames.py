'''Support for default record name configurations.'''

import parameter


__all__ = [
    'BasicRecordNames', 'SetTemplateRecordNames',
    'RecordName', 'SetRecordNames', 'GetRecordNames']


# Default record name support: each record is created with precisely the name
# it is given.
class BasicRecordNames(object):
    # Maximum record name length for EPICS 3.14
    maxLength = 61

    def __init__(self, prefix = '', separator = '', check = True):
        self.prefix = prefix
        self.separator = separator
        self.check = check

    def RecordName(self, name):
        name = '%s%s%s' % (self.prefix, self.separator, name)
        assert not self.check or 0 < len(name) <= self.maxLength, \
            'Record name "%s" too long' % name
        return name


def SetTemplateRecordNames(prefix = None, separator = ':'):
    if prefix is None:
        prefix = parameter.Parameter('DEVICE', 'Device name')

    names = BasicRecordNames(prefix, separator, False)
    SetRecordNames(names)
    return names


# One record name mechanism is configured, by default a BasicRecordNames
# instance with no prefix.
_RecordNames = BasicRecordNames()

def SetRecordNames(names):
    global _RecordNames
    current = _RecordNames
    _RecordNames = names
    return current

def GetRecordNames():
    return _RecordNames

def RecordName(name):
    return _RecordNames.RecordName(name)
