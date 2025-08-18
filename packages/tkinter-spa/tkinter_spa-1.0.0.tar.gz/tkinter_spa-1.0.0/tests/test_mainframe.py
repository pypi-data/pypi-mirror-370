import pytest
import sys

from tkinter_spa.main_frame import MainFrame
from tkinter_spa.utils.path_tools import locate_directory


# py -B -m pytest -rA -k "test_swap_mainframes"
def test_swap_mainframes(cwd_tmp_path, root, monkeypatch):
    """
        Tests raise TypeError if the class written in module stored
        in views is not a subclass of View.
    """

    # TestView class creation in pytest tmp_path
    tmp_view_directory = cwd_tmp_path / 'tmp_views'
    tmp_view_directory.mkdir(parents=True)
    file_path = tmp_view_directory / 'test_view.py'

    with open(f'{str(file_path)}', 'w', encoding = 'utf-8') as file:
        file.write('class TestView():\n')
        file.write('\tdef __init__(self, master):\n')
        file.write('\t\tself.master = master\n')
        file.write("\t\tself.title = 'home'")

    # Add pytest tmp_path in the import scope
    sys.path.insert(0, str(cwd_tmp_path))

    # Patch the constant in main_frame module
    patched_view_directory = locate_directory('tmp_views')
    monkeypatch.setattr('tkinter_spa.main_frame.view_directory', patched_view_directory)

    a = MainFrame(root, 'test')
    with pytest.raises(TypeError) as error:
        a.swap_mainframes('test_view')

    assert "TestView in 'test_view.py' must subclass View." == str(error.value)

    # Clean the test session
    sys.path.pop(0)
    root.destroy()
