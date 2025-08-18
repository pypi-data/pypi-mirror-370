import pytest

from tkinter_spa.utils.path_tools import locate_directory
from tkinter_spa.utils.string_tools import module_to_class_name, title_snake_case


class TestLocateDirectory:

    # py -B -m pytest -rA -k "test_locate_directory"
    def test_locate_directory(self, cwd_tmp_path):

        directory_name = 'test_views'

        directories = cwd_tmp_path / 'a'/ 'nested' / 'directory' / directory_name
        directories.mkdir(parents=True)

        path_to_directory = locate_directory(directory_name)

        assert path_to_directory == 'a.nested.directory.test_views'
        assert directory_name == path_to_directory.split('.')[-1]

    # py -B -m pytest -rA -k "test_locate_directory_missing"
    def test_locate_directory_missing(self, cwd_tmp_path):

        directory_name = 'views'

        with pytest.raises(RuntimeError, match=f"{directory_name} directory not found"):
            locate_directory(directory_name)

class TestModuleToClassName:

    test_module_to_class_name_cases = [
        {
            'input': '',
            'expected': ''
        },
        {
            'input': 'view',
            'expected': 'View'
        },
        {
            'input': 'first_view',
            'expected': 'FirstView'
        },
        {
            'input': 'my_very_first_view',
            'expected': 'MyVeryFirstView'
        },
    ]

    # py -B -m pytest -rA -k "test_module_to_class_name"
    @pytest.mark.parametrize('test_case_', test_module_to_class_name_cases)
    def test_module_to_class_name(self, test_case_):

        module_name = test_case_['input']

        class_name = module_to_class_name(module_name)

        assert class_name == test_case_['expected']

class TestTitleSnakeCase:

    test_title_snake_case_cases = [
        {
            'input': 'pageOne'
        },
        {
            'input': 'Page One!'
        },
        {
            'input': 'Page   One'
        },
        {
            'input': 'PageOne'
        },
    ]

    for test_case in test_title_snake_case_cases:
        test_case.update({
            'expected': 'page_one'
        })

    # py -B -m pytest -rA -k "test_title_snake_case"
    @pytest.mark.parametrize('test_case_', test_title_snake_case_cases)
    def test_title_snake_case(self, test_case_):

        title = test_case_['input']

        class_name = title_snake_case(title)

        assert class_name == test_case_['expected']
