'''Support for generating epics records.'''

from __future__ import print_function

import string

from . import recordnames
from .recordset import recordset


__all__ = [
    'PP', 'CA', 'CP', 'CPP', 'NP',
    'MS', 'MSS', 'MSI', 'NMS',
    'ImportRecord']



# Quotes a single character if necessary
def quote_char(ch):
    if ord(ch) < ord(' '):
        return '\\x%02x' % ord(ch)
    elif ch in '"\\':
        return '\\' + ch
    else:
        return ch

# Converts a string into a safely quoted string with quotation marks
def quote_string(value):
    return '"' + ''.join(map(quote_char, value)) + '"'


# ---------------------------------------------------------------------------
#
#   Record class

# Base class for all record types.
#
# All record types known to the IOC builder (loaded from DBD files in EPICS
# support modules) are subclasses of this class.
class Record(object):

    # Creates a subclass of the record with the given record type and
    # validator bound to the subclass.  The device used to load the record is
    # remembered so that it can subsequently be instantiated if necessary.
    @classmethod
    def CreateSubclass(cls, on_use, recordType, validate):
        # Each record we publish is a class so that individual record
        # classes can be subclassed when convenient.
        class BuildRecord(Record):
            _validate = validate
            _type = recordType
            _on_use = on_use
        BuildRecord.__name__ = recordType

        # Perform any class extension required for this particular record type.
        from . import bits
        return bits.ExtendClass(BuildRecord)


    def __setattr(self, name, value):
        # Because we have hooked into __setattr__, we need to dance a little
        # to write names into our dictionary.
        if name[:2] == '__':
            self.__dict__['_Record' + name] = value
        else:
            self.__dict__[name] = value


    # Record constructor.  Needs to be told the type of record that this will
    # be, a field validation object (which will be used to check field names
    # and field value assignments), the name of the record being created, and
    # initialisations for any other fields.  Builds standard record name using
    # the currently configured RecordName hook.

    # Record constructor.
    #
    # This is used to construct a record of a particular record type.  The
    # record is added to database of the generated IOC, or can simply be
    # written out to a separate .db file, depending on the chosen IOC writer.
    #
    # record
    #   The name of the record being generated.  The detailed name of the
    #   record is determined by the configured record name convention, and
    #   normally the device part of the record name is not specified here.
    # **fields
    #   All of the fields supported by the record type appear as attributes
    #   of the class.  Values can be specified in the constructor, or can be
    #   assigned subsequently to the generated instance.
    #
    # For example, the following code generates a record which counts how
    # many times it has been processed:
    #
    #   cntr = records.calc('CNTR', CALC = 'A+1', VAL = 0)
    #   cntr.A = cntr
    #
    # This will generate a database somewhat like this:
    #
    # record(calc, "$(DEVICE):CNTR")
    # {
    #     field(A,    "$(DEVICE):CNTR")
    #     field(CALC, "A+1")
    #     field(VAL,  "0")
    # }
    #
    # Record links can be wrapped with PP(), CP(), MS() and NP() calls.
    def __init__(self, record, **fields):

        # Make sure the Device class providing this record is instantiated
        if self._on_use:
            self._on_use(self)

        # These assignment have to be directly into the dictionary to
        # bypass the tricksy use of __setattr__.
        self.__setattr('__fields', {})
        self.__setattr('__aliases', set())
        self.__setattr('__metadata', [])
        self.__setattr('name', recordnames.RecordName(record))

        # Support the special 'address' field as an alias for either INP or
        # OUT, depending on which of those exists.  We only set up this field
        # if exactly one of INP or OUT is present as a valid field.
        address = [
            field for field in ['INP', 'OUT'] if self.ValidFieldName(field)]
        if len(address) == 1:
            self.__setattr('__address', address[0])

        # Make sure all the fields are properly processed and validated.
        for name, value in fields.items():
            setattr(self, name, value)

        recordset.PublishRecord(self.name, self)


    def add_alias(self, alias):
        self.__aliases.add(alias)

    def add_metadata(self, metadata):
        self.__metadata.append(metadata)


    # Call to generate database description of this record.  Outputs record
    # definition in .db file format.  Hooks for meta-data can go here.
    def Print(self, output):
        print(file = output)
        for metadata in self.__metadata:
            print('#%', metadata, file = output)
        print('record(%s, "%s")' % (self._type, self.name), file = output)
        print('{', file = output)
        # Print the fields in alphabetical order.  This is more convenient
        # to the eye and has the useful side effect of bypassing a bug
        # where DTYPE needs to be specified before INP or OUT fields.
        for k in sorted(self.__fields.keys()):
            value = self.__fields[k]
            if getattr(value, 'ValidateLater', False):
                self.__ValidateField(k, value)
            value = self.__FormatFieldForDb(k, value)
            padding = ''.ljust(4-len(k))  # To align field values
            print('    field(%s, %s%s)' % (k, padding, value), file = output)
        for alias in sorted(list(self.__aliases)):
            print('    alias("%s")' % alias, file = output)
        print('}', file = output)


    # The string for a record is just its name.
    def __str__(self):
        return self.name

    # The representation string for a record identifies its type and name,
    # but we can't do much more.
    def __repr__(self):
        return '<record %s "%s">' % (self._type, self.name)

    # Calling the record generates a self link with a list of specifiers.
    def __call__(self, *specifiers):
        return _Link(self, None, *specifiers)


    # Assigning to a record attribute updates a field.
    def __setattr__(self, fieldname, value):
        if fieldname == 'address':
            fieldname = self.__address
        if value is None:
            # Treat assigning None to a field the same as deleting that field.
            # This is convenient for default arguments.
            if fieldname in self.__fields:
                del self.__fields[fieldname]
        else:
            # If the field is callable we call it first: this is used to
            # ensure we convert record pointers into links.  It's unlikely
            # that this will have unfortunate side effects elsewhere, but it's
            # always possible...
            if callable(value):
                value = value()
            if not getattr(value, 'ValidateLater', False):
                self.__ValidateField(fieldname, value)
            self.__fields[fieldname] = value

    # Field validation
    def __ValidateField(self, fieldname, value):
        # If the field can validate itself then ask it to, otherwise use our
        # own validation routine.  This is really just a hook for parameters
        # so that they can do their own validation.
        if hasattr(value, 'Validate'):
            value.Validate(self, fieldname)
        else:
            self._validate.ValidFieldValue(fieldname, str(value))

    # Field formatting
    def __FormatFieldForDb(self, fieldname, value):
        if hasattr(value, 'FormatDb'):
            return value.FormatDb(self, fieldname)
        else:
            return quote_string(str(value))


    # Allow individual fields to be deleted from the record.
    def __delattr__(self, fieldname):
        if fieldname == 'address':
            fieldname = self.__address
        del self.__fields[fieldname]


    # Reading a record attribute returns a link to the field.
    def __getattr__(self, fieldname):
        if fieldname == 'address':
            fieldname = self.__address
        self._validate.ValidFieldName(fieldname)
        return _Link(self, fieldname)

    def _FieldValue(self, fieldname):
        return self.__fields[fieldname]

    # Can be called to validate the given field name, returns True iff this
    # record type supports the given field name.
    @classmethod
    def ValidFieldName(cls, fieldname):
        try:
            # The validator is specified to raise an AttributeError exception
            # if the field name cannot be validated.  We translate this into
            # a boolean here.
            cls._validate.ValidFieldName(fieldname)
        except AttributeError:
            return False
        else:
            return True

    # When a record is pickled for export it will reappear as an ImportRecord
    # instance.  This makes more sense (as the record has been fully generated
    # already), and avoids a lot of trouble.
    def __reduce__(self):
        return (ImportRecord, (self.name, self._type))



# Records can be imported by name.  An imported record has no specification
# of its type, and so no validation can be done: all that can be done to an
# imported record is to link to it.
class ImportRecord:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<external record "%s">' % self.name

    def __call__(self, *specifiers):
        return _Link(self, None, *specifiers)

    def __getattr__(self, fieldname):
        # Brain-dead minimal validation: just check for all uppercase!
        ValidChars = set(string.ascii_uppercase + string.digits)
        if not set(fieldname) <= ValidChars:
            raise AttributeError('Invalid field name %s' % fieldname)
        return _Link(self, fieldname)

    def add_alias(self, name):
        recordset.AddBodyLine('alias("%s", "%s")' % (self.name, name))


# A link is a class to encapsulate a process variable link.  It remembers
# the record, the linked field, and a list of specifiers (such as PP, CP,
# etcetera).
class _Link:
    def __init__(self, record, field, *specifiers):
        self.record = record
        self.field = field
        self.specifiers = specifiers

    def __str__(self):
        result = self.record.name
        if self.field:
            result = '%s.%s' % (result, self.field)
        for specifier in self.specifiers:
            result = '%s %s' % (result, specifier)
        return result

    def __call__(self, *specifiers):
        return _Link(self.record, self.field, *self.specifiers + specifiers)

    # Returns the value currently assigned to this field.
    def Value(self):
        return self.record._FieldValue(self.field)


# Some helper routines for building links

def PP(record):
    """ "Process Passive": any record update through a PP output link will be
    processed if its scan is Passive.

    Example (Python source)
    -----------------------
    `my_record.INP = PP(other_record)`

    Example (Generated DB)
    ----------------------
    `field(INP, "other PP")`
    """
    return record('PP')

def CA(record):
    """ "Channel Access": a CA (input or output) link will be treated as
    a channel access link regardless whether it is a DB link or not.

    Example (Python source)
    -----------------------
    `my_record.INP = CA(other_record)`

    Example (Generated DB)
    ----------------------
    `field(INP, "other CA")`
    """
    return record('CA')


def CP(record):
    """ "Channel Process": a CP input link will cause the linking record
    to process any time the linked record is updated.

    Example (Python source)
    -----------------------
    `my_record.INP = CP(other_record)`

    Example (Generated DB)
    ----------------------
    `field(INP, "other CP")`
    """
    return record('CP')

def CPP(record):
    """ "Channel Process if Passive": a CP input link will be treated as
    a channel access link and if the linking record is passive,
    the linking passive record will be processed any time the linked record
    is updated.

    Example (Python source)
    -----------------------
    `my_record.INP = CPP(other_record)`

    Example (Generated DB)
    ----------------------
    `field(INP, "other CPP")`
    """
    return record('CPP')


def MS(record):
    """ "Maximise Severity": any alarm state on the linked record is propagated
    to the linking record. When propagated, the alarm status will become
    `LINK_ALARM`.

    Example (Python source)
    -----------------------
    `my_record.INP = MS(other_record)`

    Example (Generated DB)
    ----------------------
    `field(INP, "other MS")`
    """
    return record('MS')


def MSS(record):
    """ "Maximise Status and Severity": both alarm status and alarm severity
    on the linked record are propagated to the linking record.

    Example (Python source)
    -----------------------
    `my_record.INP = MSS(other_record)`

    Example (Generated DB)
    ----------------------
    `field(INP, "other MSS")`
    """
    return record('MSS')


def MSI(record):
    """ "Maximise Severity if Invalid": propagate an alarm state on the linked
    record only if the alarm severity is `INVALID_ALARM`.
    When propagated, the alarm status will become `LINK_ALARM`.

    Example (Python source)
    -----------------------
    `my_record.INP = MSI(other_record)`

    Example (Generated DB)
    ----------------------
    `field(INP, "other MSI")`
    """
    return record('MSI')


def NMS(record):
    """ "Non-Maximise Severity": no alarm is propagated.
    This is the default behavior of EPICS links.

    Example (Python source)
    -----------------------
    `my_record.INP = NMS(other_record)`

    Example (Generated DB)
    ----------------------
    `field(INP, "other NMS")`
    """
    return record('NMS')


def NP(record):
    """ "No Process": the linked record is not processed.
    This is the default behavior of EPICS links.

    Example (Python source)
    -----------------------
    `my_record.INP = NP(other_record)`

    Example (Generated DB)
    ----------------------
    `field(INP, "other NPP")`
    """
    return record('NPP')
