'''Support for default record name configurations.'''

from . import parameter


__all__ = [
    'SimpleRecordNames', 'TemplateRecordNames',
    'SetSimpleRecordNames', 'SetTemplateRecordNames',
    'RecordName', 'SetRecordNames', 'GetRecordNames',
    'PushPrefix', 'PopPrefix', 'SetPrefix', 'SetSeparator']


# Default record name support: each record is created with precisely the name
# it is given.
class SimpleRecordNames(object):
    # Maximum record name length for EPICS 3.14
    maxLength = 61

    def __init__(self, prefix = '', separator = ':', check = True):
        self.prefix = [prefix] if prefix else []
        self.separator = separator
        self.check = check

    def __call__(self, name):
        name = self.separator.join(map(str, self.prefix + [name]))
        assert not self.check or 0 < len(name) <= self.maxLength, \
            'Record name "%s" too long' % name
        return name

    def PushPrefix(self, prefix):
        self.prefix.append(prefix)

    def PopPrefix(self):
        return self.prefix.pop()

    def SetPrefix(self, prefix):
        if prefix:
            if self.prefix:
                self.PopPrefix()
            self.PushPrefix(prefix)
        else:
            self.PopPrefix()

    def SetSeparator(self, separator):
        self.separator = separator


class TemplateRecordNames(SimpleRecordNames):
    def __init__(self, prefix = None, separator = ':'):
        if prefix is None:
            prefix = parameter.Parameter('DEVICE', 'Device name')
        SimpleRecordNames.__init__(self, prefix, separator, False)


def SetSimpleRecordNames(prefix = '', separator = ''):
    SetRecordNames(SimpleRecordNames(prefix, separator))

def SetTemplateRecordNames(prefix = None, separator = ':'):
    SetRecordNames(TemplateRecordNames(prefix, separator))


# By default record names are unmodified.
def _RecordNames(name):
    return name

def SetRecordNames(names):
    global _RecordNames
    current = _RecordNames
    _RecordNames = names
    return current

def GetRecordNames():
    return _RecordNames

def RecordName(name):
    return _RecordNames(name)

def PushPrefix(prefix):
    _RecordNames.PushPrefix(prefix)

def PopPrefix():
    return _RecordNames.PopPrefix()

def SetPrefix(prefix):
    _RecordNames.SetPrefix(prefix)

def SetSeparator(separator):
    _RecordNames.SetSeparator(separator)
