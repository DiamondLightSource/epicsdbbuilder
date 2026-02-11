# EPICS Database Building Framework

# All these have an __all__ so rely on that
import sys

from epicsdbbuilder.const_array import *
from epicsdbbuilder.dbd import *
from epicsdbbuilder.fanout import *
from epicsdbbuilder.parameter import *
from epicsdbbuilder.recordbase import *
from epicsdbbuilder.recordnames import *
from epicsdbbuilder.recordset import *

if sys.version_info < (3, 8):
    from importlib_metadata import version  # noqa
else:
    from importlib.metadata import version  # noqa

__version__ = version("epicsdbbuilder")
del version

__all__ = ["__version__"]
