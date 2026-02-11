import subprocess
import sys

from epicsdbbuilder import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "epicsdbbuilder", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
