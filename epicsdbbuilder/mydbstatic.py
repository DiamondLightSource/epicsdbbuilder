import os
from ctypes import *

import platform


_FunctionList = (
#     ('dbFreeBase',          None, (c_void_p,)),
    ('dbReadDatabase',      c_int, (c_void_p, c_char_p, c_char_p, c_char_p)),
    ('dbAllocEntry',        c_void_p, (c_void_p,)),
    ('dbFirstRecordType',   c_int, (c_void_p,)),
    ('dbGetRecordTypeName', c_char_p, (c_void_p,)),
    ('dbNextRecordType',    c_int, (c_void_p,)),
    ('dbFreeEntry',         None, (c_void_p,)),
    ('dbCopyEntry',         c_void_p, (c_void_p,)),
    ('dbFirstField',        c_int, (c_void_p,)),
    ('dbGetFieldName',      c_char_p, (c_void_p,)),
    ('dbGetPrompt',         c_char_p, (c_void_p,)),
    ('dbGetPromptGroup',    c_int, (c_void_p,)),
    ('dbGetFieldType',      c_int, (c_void_p,)),
    ('dbGetNMenuChoices',   c_int, (c_void_p,)),
    ('dbGetMenuChoices',    c_void_p, (c_void_p,)),
    ('dbNextField',         c_int, (c_void_p,)),
#     ('dbGetString',         c_char_p, (c_void_p,)),
    ('dbVerify',            c_char_p, (c_void_p, c_char_p)),
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

    libdb = CDLL(os.path.join(
        epics_base, 'lib', host_arch, 'libdbStaticHost.so'))

    for name, restype, argtypes in _FunctionList:
        function = getattr(libdb, name)
        function.restype = restype
        function.argtypes = argtypes
        globals()[name] = function
