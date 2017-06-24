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
#     ('dbFreeBase',          None, (c_void_p,)),
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
    ('dbGetPrompt',         c_char_p, auto_decode, (c_void_p,)),
    ('dbGetPromptGroup',    c_int, None, (c_void_p,)),
    ('dbGetFieldType',      c_int, None, (c_void_p,)),
    ('dbGetNMenuChoices',   c_int, None, (c_void_p,)),
    ('dbGetMenuChoices',    c_void_p, None, (c_void_p,)),
    ('dbNextField',         c_int, None, (c_void_p,)),
#     ('dbGetString',         c_char_p, auto_decode, (c_void_p,)),
    ('dbVerify',            c_char_p, auto_decode, (c_void_p, auto_encode)),
)

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
    try:
        libdb = CDLL(os.path.join(
            epics_base, 'lib', host_arch, 'libdbCore.so'))
    except OSError:
        libdb = CDLL(os.path.join(
            epics_base, 'lib', host_arch, 'libdbStaticHost.so'))

    for name, restype, errcheck, argtypes in _FunctionList:
        function = getattr(libdb, name)
        function.restype = restype
        function.argtypes = argtypes
        if errcheck:
            function.errcheck = errcheck
        globals()[name] = function
