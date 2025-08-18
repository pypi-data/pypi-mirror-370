import os
import pytest

from pathlib import Path

from tkinter_spa.tk_root import TkinterApp

from app.views.home_view import HomeView


@pytest.fixture
def root():
    root = TkinterApp().initialize(startup_view = HomeView)

    return root

@pytest.fixture
def cwd_tmp_path(tmp_path):
    """
        locate_directory() uses Path.cwd() as the root to search for
        the target directory. Since pytest creates temporary directories
        using tmp_path *outside* the project tree, we must temporarily
        change the working directory to tmp_path for the function to succeed.
    """

    old_cwd = Path.cwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(old_cwd)
