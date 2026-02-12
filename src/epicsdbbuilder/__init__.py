"""Top level API.

.. data:: __version__
    :type: str

    Version number as calculated by https://github.com/pypa/setuptools_scm
"""

# All these have an __all__ so rely on that
from epicsdbbuilder.const_array import *  # noqa: F403
from epicsdbbuilder.dbd import *  # noqa: F403
from epicsdbbuilder.fanout import *  # noqa: F403
from epicsdbbuilder.parameter import *  # noqa: F403
from epicsdbbuilder.recordbase import *  # noqa: F403
from epicsdbbuilder.recordnames import *  # noqa: F403
from epicsdbbuilder.recordset import *  # noqa: F403

from ._version import __version__ as __version__
