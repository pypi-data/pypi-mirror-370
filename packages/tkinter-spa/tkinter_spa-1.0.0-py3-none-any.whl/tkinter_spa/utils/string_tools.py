import re


def module_to_class_name(module_name):
    """
        Converts a snake_case module name into a CamelCase class name
        (e.g. module_name => ModuleName).

        Parameters
        ----------
        module_name : str

        Returns
        -------
        str
    """

    return ''.join([word.capitalize() for word in module_name.split('_')])

def title_snake_case(title):
    """
        Converts a string to snake_case by normalizing whitespaces, removing symbols
        and handling camelCase or PascaleCase.

        Parameters
        ----------
        title : str

        Returns
        -------
        str
    """
    title = re.sub(r'([a-z])([A-Z])', r'\1_\2', title)
    title = re.sub(r'[\W_]+', ' ', title)
    return '_'.join(title.lower().split())
