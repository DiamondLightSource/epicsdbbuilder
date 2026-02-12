"""Implements the set of records provided by a dbd"""

import ctypes
import os
import os.path
import platform

from . import mydbstatic  # Pick up interface to EPICS dbd files
from .recordbase import Record

__all__ = ["InitialiseDbd", "LoadDbdFile", "records"]


# This class contains all the record types current supported by the loaded
# dbd, and is published to the world as epics.records.  As records are added
# (in response to calls to LoadDbdFile) they are automatically available to
# all targets.
class RecordTypes:
    def __init__(self):
        self.__RecordTypes = set()

    def GetRecords(self):
        return sorted(self.__RecordTypes)

    def _PublishRecordType(self, on_use, record_type, validate):
        # Publish this record type as a method
        self.__RecordTypes.add(record_type)
        setattr(self, record_type, Record.CreateSubclass(on_use, record_type, validate))

    # Checks whether the given recordType names a known valid record type.
    def __contains__(self, record_type):
        return record_type in self.__RecordTypes


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
    def __init__(self, db_entry):
        # Copy the existing entry so it stays on the right record
        self.dbEntry = DBEntry(db_entry)
        self.__FieldInfo = None

    # Computes list of valid names and creates associated arginfo
    # definitions.  This is postponed quite late to try and ensure the menus
    # are fully populated, in other words we don't want to fire this until
    # all the dbd files have been loaded.
    def __ProcessDbd(self):
        # set of field names
        self.__FieldInfo = set()
        for field_name in self.dbEntry.iterate_fields():
            if field_name != "NAME":
                self.__FieldInfo.add(field_name)

    # This method raises an attribute error if the given field name is
    # invalid.
    def ValidFieldName(self, name):
        if self.__FieldInfo is None:
            self.__ProcessDbd()
        if name not in self.__FieldInfo:
            raise AttributeError(f"Invalid field name {name}")

    # This method raises an exeption if the given field name does not exist
    # or if the value cannot be validly written.
    def ValidFieldValue(self, name, value):
        # First check the field name is valid
        self.ValidFieldName(name)
        value = str(value)

        # Set the database cursor to the field
        for field_name in self.dbEntry.iterate_fields():
            if field_name == name:
                break

        # Now see if we can write the value to it
        message = mydbstatic.dbVerify(self.dbEntry, value)
        assert message is None, f"Can't write '{value}' to field {name}: {message}"


# The same database pointer is used for all DBD files: this means that all
# the DBD entries are accumulated into a single large database.
_db = ctypes.c_void_p()


class DBEntry:
    """Create a dbEntry instance within the current DBD.

    This is a stateful pointer that can be moved to different
    record types and fields within them with the iterate methods.

    If entry is specified on init and is a DBEntry instance, it
    will be copied so that its position is maintained.
    """

    def __init__(self, entry=None):
        assert _db, "LoadDdbFile not called yet"
        if entry is None:
            # No entry, so alloc a new one
            self._as_parameter_ = mydbstatic.dbAllocEntry(_db)
        else:
            # Existing entry, copy it so it stays on the same record
            self._as_parameter_ = mydbstatic.dbCopyEntry(entry)

    def iterate_records(self):
        """Iterate through the record types, yielding their names"""
        status = mydbstatic.dbFirstRecordType(self)
        while status == 0:
            yield mydbstatic.dbGetRecordTypeName(self)
            status = mydbstatic.dbNextRecordType(self)

    def iterate_fields(self, dct_only=0):
        """Iterate through a record's fields, yielding their names"""
        status = mydbstatic.dbFirstField(self, dct_only)
        while status == 0:
            yield mydbstatic.dbGetFieldName(self)
            status = mydbstatic.dbNextField(self, dct_only)

    def __del__(self):
        mydbstatic.dbFreeEntry(self._as_parameter_)


def LoadDbdFile(dbdfile, on_use=None):
    dirname, filename = os.path.split(dbdfile)

    # Read the specified dbd file into the current database.  This allows
    # us to see any new definitions.
    curdir = os.getcwd()
    if dirname:
        os.chdir(dirname)

    # We add <epics_base>/dbd to the path so that dbd includes can be resolved.
    separator = ":"
    if platform.system() == "Windows":
        separator = ";"

    status = mydbstatic.dbReadDatabase(
        ctypes.byref(_db),
        filename,
        separator.join([".", os.path.join(_epics_base, "dbd")]),
        None,
    )
    os.chdir(curdir)
    assert status == 0, f"Error reading database {dbdfile} (status {status})"

    # Enumerate all the record types and build a record generator class
    # for each one that we've not seen before.
    entry = DBEntry()
    for record_type in entry.iterate_records():
        if not hasattr(records, record_type):
            validate = ValidateDbField(entry)
            records._PublishRecordType(on_use, record_type, validate)  # noqa: SLF001


def InitialiseDbd(epics_base=None, host_arch=None):
    global _epics_base
    if epics_base:
        # Import from given location
        mydbstatic.ImportFunctions(epics_base, host_arch)
        _epics_base = epics_base
    else:
        # Import from epicscorelibs installed libs
        from epicscorelibs import path

        mydbstatic.ImportFunctionsFrom(path.get_lib("dbCore"))
        _epics_base = path.base_path
    LoadDbdFile("base.dbd")
