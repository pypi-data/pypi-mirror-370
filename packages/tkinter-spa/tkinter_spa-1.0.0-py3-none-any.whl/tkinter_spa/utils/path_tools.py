from pathlib import Path


def locate_directory(directory_name = 'views'):
    """
        Locates the view directory created by the developper.

        Parameters
        ----------
        directory_name : str
            The name of the directory to locate. Defaults to 'views'.

        Returns
        -------
        str
            The relative path to the 'views' directory, converted into
            a Python module path.

        Raises
        ------
        RuntimeError
            If the 'views' directory cannot be found within the project directory tree.
    """

    # path from where python has been executed
    python_source = Path.cwd()

    for path in python_source.glob(f'**/{directory_name}'):
        if path.is_dir():
            return '.'.join(path.relative_to(python_source).parts)

    raise RuntimeError(
        f'{directory_name} directory not found since the project entrypoint.'
    )
