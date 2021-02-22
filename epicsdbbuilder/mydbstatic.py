import os
import sys
from ctypes import *

import platform

if sys.version_info < (3,):
    auto_encode = c_char_p
    def auto_decode(result, func, args):
        return result
else:
    class auto_encode(c_char_p):
        @classmethod
        def from_param(cls, value):
            if value is None:
                return value
            else:
                return value.encode()
    def auto_decode(result, func, args):
        if result is None:
            return result
        else:
            return result.decode()


_FunctionList = (
    ('dbReadDatabase',      c_int, None,
        (c_void_p, auto_encode, auto_encode, auto_encode)),
    ('dbAllocEntry',        c_void_p, None, (c_void_p,)),
    ('dbFirstRecordType',   c_int, None, (c_void_p,)),
    ('dbGetRecordTypeName', c_char_p, auto_decode, (c_void_p,)),
    ('dbNextRecordType',    c_int, None, (c_void_p,)),
    ('dbFreeEntry',         None, None, (c_void_p,)),
    ('dbCopyEntry',         c_void_p, None, (c_void_p,)),
    ('dbFirstField',        c_int, None, (c_void_p,)),
    ('dbGetFieldName',      c_char_p, auto_decode, (c_void_p,)),
    ('dbNextField',         c_int, None, (c_void_p,)),
    ('dbVerify',            c_char_p, auto_decode, (c_void_p, auto_encode)),
)


# Fallback implementation for dbVerify.  Turns out not to be present in EPICS
# 3.16, which is rather annoying.  In this case we just allow all writes to
# succeed.
def dbVerify(entry, value):
    return None


# This function is called late to complete the process of importing all the
# exports from this module.  This is done late so that paths.EPICS_BASE can be
# configured late.
def ImportFunctions(epics_base, host_arch):
    if host_arch is None:
        # Mapping from host architecture to EPICS host architecture name can be
        # done with a little careful guesswork.  As EPICS architecture names are
        # a little arbitrary this isn't guaranteed to work.
        system_map = {
            ('Linux',   '32bit'):   'linux-x86',
            ('Linux',   '64bit'):   'linux-x86_64',
            ('Darwin',  '32bit'):   'darwin-x86',
            ('Darwin',  '64bit'):   'darwin-x86',
            ('Windows', '32bit'):   'win32-x86',
            ('Windows', '64bit'):   'windows-x64',
        }
        bits = platform.architecture()[0]
        host_arch = system_map[(platform.system(), bits)]

    # So we can work with both EPICS 3.14 and 3.15, look for libdbCore.so first
    # before falling back to the older libdbStaticHost.so
    # On Windows, use dbCore.dll or dbStaticHost.dll instead
    library_name_format = 'lib{}.so'
    library_location = 'lib'
    if platform.system() == 'Windows':
        library_name_format = '{}.dll'
        library_location = 'bin'

    try:
        ImportFunctionsFrom(os.path.join(
            epics_base, library_location, host_arch,
            library_name_format.format('dbCore')))
    except OSError:
        ImportFunctionsFrom(os.path.join(
            epics_base, library_location, host_arch,
            library_name_format.format('dbStaticHost')))


def ImportFunctionsFrom(path):
    # Load the dbd static library using ctypes PyDLL convention instead of CDLL
    #
    # The difference is that this way we hold onto the Python GIL.  Mostly this
    # makes no difference, as these are very quick function calls, but it turns
    # out that if there is another Python thread running then contention for the
    # GIL can wreck performance here.
    #
    # The ctypes documentation is not particularly helpful, saying in particular
    # "this is only useful to call Python C api functions directly", which
    # doesn't seem to be correct.
    libdb = PyDLL(path)
    # Actually populate the functions in globals, split from ImportFunctions to
    # support legacy API
    for name, restype, errcheck, argtypes in _FunctionList:
        try:
            function = getattr(libdb, name)
        except AttributeError:
            # Check for global fallback function
            if name not in globals():
                raise
        else:
            function.restype = restype
            function.argtypes = argtypes
            if errcheck:
                function.errcheck = errcheck
            globals()[name] = function
