"""Common utility functions and classes used across the CLI scripts.

Variables:
    ROOT_PATH (pathlib.Path): The root path of the project.
    DOCS_PATH (pathlib.Path): The path to the docs directory.
    TEMPLATES (fastapi.templating.Jinja2Templates): Jinja2 templates for rendering documentation.

Functions:
    to_snake_case(string: str) -> str: Converts a given string to snake case.
    read_pyproject(path: pathlib.Path | None) -> dict[str, typing.Any]: Reads the pyproject.toml file and returns its
        content as a dictionary.

Classes:
    File: A context manager class to handle file operations.
"""

import pathlib
import re
import typing

import fastapi.templating
import tomli

ROOT_PATH = pathlib.Path()
DOCS_PATH = ROOT_PATH / "docs" / "docs"
TEMPLATES_PATH = pathlib.Path(__file__).parent / "templates"
TEMPLATES = fastapi.templating.Jinja2Templates(TEMPLATES_PATH)


def read_pyproject(path: pathlib.Path | None = None) -> dict[str, typing.Any]:
    """Reads the pyproject.toml file and returns its content as a dictionary.

    Args:
        path (pathlib.Path): The path to the pyproject.toml file. Defaults to None.

    Returns:
        dict[str, typing.Any]: The content of the pyproject.toml file as a dictionary
    """
    path = ROOT_PATH / "pyproject.toml" or path
    with File(path) as pyproject_file:
        return tomli.loads(pyproject_file.read())


def to_snake_case(string: str) -> str:
    """Converts a given string to snake case.

    Args:
        string (str): The string to be converted.

    Returns:
        str: The converted string in snake case.
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return re.sub(r"-", "_", s2).lower()


class File:
    """A context manager class to handle file operations.

    Args:
        file_path (Path): The path to the file.
        mode (typing.Literal["r", "w"], optional): The mode in which the file should be opened.
            Defaults to "r".

    Methods:
        reset: Resets the file at the specified file path.
    """

    def __init__(self, file_path: pathlib.Path, mode: typing.Literal["r", "w"] = "r") -> None:
        """Initializes an instance of the class.

        Args:
            file_path (Path): The path to the file.
            mode (typing.Literal["r", "w"], optional): The mode in which the file should be opened.
                Defaults to "r".
        """
        self.file_path = file_path
        self.mode = mode

    def __enter__(self) -> typing.IO[typing.Any]:
        """Context manager method that is called when entering a `with` statement.

        Returns:
            file object (typing.IO[typing.Any]): The opened file object.
        """
        return pathlib.Path(self.file_path).open(self.mode)

    def __exit__(self, *args: object, **kwargs: typing.Any) -> None:
        """Exit the context manager.

        Args:
            args (object): The positional arguments passed to the __exit__ method.
            kwargs (typing.Any): The keyword arguments passed to the __exit__ method.
        """

    def reset(self) -> None:
        """Resets the file at the specified file path."""
        with pathlib.Path(self.file_path).open():
            pass
