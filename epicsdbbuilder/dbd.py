'''Implements the set of records provided by a dbd'''

import os
import os.path
import ctypes
import platform

from . import mydbstatic   # Pick up interface to EPICS dbd files

from .recordbase import Record


__all__ = ['InitialiseDbd', 'LoadDbdFile', 'records']


# This class contains all the record types current supported by the loaded
# dbd, and is published to the world as epics.records.  As records are added
# (in response to calls to LoadDbdFile) they are automatically available to
# all targets.
class RecordTypes(object):
    def __init__(self):
        self.__RecordTypes = set()

    def GetRecords(self):
        return sorted(self.__RecordTypes)

    def _PublishRecordType(self, on_use, recordType, validate):
        # Publish this record type as a method
        self.__RecordTypes.add(recordType)
        setattr(
            self, recordType,
            Record.CreateSubclass(on_use, recordType, validate))

    # Checks whether the given recordType names a known valid record type.
    def __contains__(self, recordType):
        return recordType in self.__RecordTypes


# Every record type loaded from a DBD is present as an attribute of this
# class with the name of the record type.
#
# For example, to create an ai record, simply write
#
#   records.ai('NAME', DESC = 'A test ai record', EGU = 'V')
#
records = RecordTypes()


# This class uses a the static database to validate whether the associated
# record type allows a given value to be written to a given field.
class ValidateDbField:
    def __init__(self, dbEntry):
        self.dbEntry = mydbstatic.dbCopyEntry(dbEntry)
        self.__FieldInfo = None

    # Computes list of valid names and creates associated arginfo
    # definitions.  This is postponed quite late to try and ensure the menus
    # are fully populated, in other words we don't want to fire this until
    # all the dbd files have been loaded.
    def __ProcessDbd(self):
        # ordered dict of field_name -> arginfo
        self.__FieldInfo = set()
        status = mydbstatic.dbFirstField(self.dbEntry, 0)
        while status == 0:
            name = mydbstatic.dbGetFieldName(self.dbEntry)
            if name != 'NAME':
                self.__FieldInfo.add(name)
            status = mydbstatic.dbNextField(self.dbEntry, 0)


    # This method raises an attribute error if the given field name is
    # invalid.
    def ValidFieldName(self, name):
        if self.__FieldInfo is None:
            self.__ProcessDbd()
        if name not in self.__FieldInfo:
            raise AttributeError('Invalid field name %s' % name)

    # This method raises an exeption if the given field name does not exist
    # or if the value cannot be validly written.
    def ValidFieldValue(self, name, value):
        # First check the field name is valid
        self.ValidFieldName(name)
        value = str(value)

        # Set the database cursor to the field
        status = mydbstatic.dbFirstField(self.dbEntry, 0)
        while status == 0:
            if mydbstatic.dbGetFieldName(self.dbEntry) == name:
                break
            status = mydbstatic.dbNextField(self.dbEntry, 0)

        # Now see if we can write the value to it
        message = mydbstatic.dbVerify(self.dbEntry, value)
        assert message is None, \
            'Can\'t write "%s" to field %s: %s' % (value, name, message)



# The same database pointer is used for all DBD files: this means that all
# the DBD entries are accumulated into a single large database.
_db = ctypes.c_void_p()

def LoadDbdFile(dbdfile, on_use = None):
    dirname, filename = os.path.split(dbdfile)

    # Read the specified dbd file into the current database.  This allows
    # us to see any new definitions.
    curdir = os.getcwd()
    if dirname:
        os.chdir(dirname)

    # We add <epics_base>/dbd to the path so that dbd includes can be resolved.
    separator = ':'
    if platform.system() == 'Windows':
        separator = ';'

    status = mydbstatic.dbReadDatabase(
        ctypes.byref(_db), filename,
        separator.join(['.', os.path.join(_epics_base, 'dbd')]), None)
    os.chdir(curdir)
    assert status == 0, 'Error reading database %s (status %d)' % \
        (dbdfile, status)


    # Enumerate all the record types and build a record generator class
    # for each one that we've not seen before.
    entry = mydbstatic.dbAllocEntry(_db)
    status = mydbstatic.dbFirstRecordType(entry)
    while status == 0:
        recordType = mydbstatic.dbGetRecordTypeName(entry)
        if not hasattr(records, recordType):
            validate = ValidateDbField(entry)
            records._PublishRecordType(on_use, recordType, validate)
        status = mydbstatic.dbNextRecordType(entry)
    mydbstatic.dbFreeEntry(entry)


def InitialiseDbd(epics_base = None, host_arch = None):
    global _epics_base
    if epics_base:
        # Import from given location
        mydbstatic.ImportFunctions(epics_base, host_arch)
        _epics_base = epics_base
    else:
        # Import from epicscorelibs installed libs
        from epicscorelibs import path
        mydbstatic.ImportFunctionsFrom(path.get_lib('dbCore'))
        _epics_base = path.base_path
    LoadDbdFile('base.dbd')
