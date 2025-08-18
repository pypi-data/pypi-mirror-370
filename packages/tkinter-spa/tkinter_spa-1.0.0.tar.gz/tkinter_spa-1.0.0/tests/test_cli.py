import pytest
import subprocess
import sys

from tkinter_spa.cli import main_cli
from tkinter_spa._version import __version__


# py -B -m pytest -rA -k "test_main_cli"
def test_main_cli():

    with pytest.raises(SystemExit):
        sys.argv = ['tkinter_spa']
        main_cli()

# py -B -m pytest -rA -k "test_cli_version"
def test_cli_version():

    result = subprocess.run(
        ['tkinter_spa', '--version'],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    version = result.stdout.lstrip('tkinter_spa').strip()

    assert version == __version__
