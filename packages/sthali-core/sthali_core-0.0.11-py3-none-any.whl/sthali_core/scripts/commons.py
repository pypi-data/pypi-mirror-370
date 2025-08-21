"""Common utility functions and classes used across the CLI scripts.

Variables:
    ROOT_PATH (pathlib.Path): The root path of the project.
    DOCS_PATH (pathlib.Path): The path to the docs directory.
    TEMPLATES_PATH (pathlib.Path): The path to the templates directory.
    TEMPLATES (fastapi.templating.Jinja2Templates): Jinja2 templates for rendering documentation.

Functions:
    to_snake_case(string: str) -> str: Converts a given string to snake case.
    read_pyproject(path: pathlib.Path | None) -> dict[str, typing.Any]: Reads the pyproject.toml file and returns its
        content as a dictionary.
    get_imports_from_module(module: types.ModuleType, level: int) -> list[Doc]: Recursively extract documentation
        metadata from a module's __all__ exports.
    recursive_writer(doc: Doc) -> str: Recursively write documentation for a Doc object and its sub-objects.
"""

import pathlib
import re
import types
import typing

import fastapi.templating
import pydantic
import tomli
import typer

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
    with pathlib.Path.open(path) as pyproject_file:
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


@pydantic.dataclasses.dataclass
class Doc:
    """Represents documentation metadata for an object.

    Attributes:
        name (str): The name of the object.
        path (pathlib.Path): The output file path for the documentation.
        docstring (str): The docstring or description.
        level (int): The Markdown heading level.
        sub (list["Doc"]): List of Doc objects for sub-objects.
    """

    name: str
    path: pathlib.Path
    docstring: str
    level: int
    sub: list["Doc"]


def recursive_writer(doc: Doc) -> str:
    """Recursively write documentation for a Doc object and its sub-objects.

    Args:
        doc (Doc): The Doc object to write.

    Returns:
        str: The rendered Markdown string for this Doc and its children.
    """

    def _render(name: str, docstring: str, level: int = 3, sub: str | None = None) -> str:
        template = TEMPLATES.get_template("docstring.md")  # type: ignore
        return template.render(  # type: ignore
            name=name,
            docstring=docstring,
            heading_level=level * "#",
            sub=sub,
        )

    typer.echo(f"Writing docstring from import: {doc.name}")

    to_render = _render(doc.name, doc.docstring, doc.level, "\n".join([recursive_writer(s) for s in doc.sub]))
    with pathlib.Path.open(doc.path, "w") as doc_file:
        doc_file.write(to_render)

    return to_render


TypesMapping = typing.Literal["module", "function", "class"]


def get_imports_from_module(module: types.ModuleType, level: int) -> list[Doc]:
    """Recursively extract documentation metadata from a module's __all__ exports.

    Args:
        module (types.ModuleType): The module to inspect.
        level (int): The Markdown heading level.

    Returns:
        list[Doc]: A list of Doc objects representing the module's exports.
    """

    def _get_import_type_mapping(_import: typing.Any) -> TypesMapping | None:
        import_type: typing.Any = type(_import)  # type: ignore
        match import_type:
            case types.ModuleType:
                return "module"
            case types.FunctionType:
                return "function"
            case _ if isinstance(_import, type):
                return "class"
            case _:
                return None

    def _get_docstring(obj: typing.Any) -> str:
        def _get_metadata(obj: typing.Any) -> str | None:
            metadata: list[typing.Any] = getattr(obj, "__metadata__", [])
            field_info = next(filter(lambda x: isinstance(x, pydantic.fields.FieldInfo), metadata), None)
            if field_info:
                return field_info.description
            return None

        def _get_doc(obj: typing.Any) -> str | None:
            return getattr(obj, "__doc__", None)

        metadata = _get_metadata(obj)
        doc = _get_doc(obj)
        return metadata or doc or ""

    typer.echo(f"Getting imports from {module.__name__} module")

    docs: list[Doc] = []
    for i in getattr(module, "__all__", []):
        typer.echo(f"Getting metadata from {i} import")

        _import = getattr(module, i)
        name = _import.__name__
        filename = _import.__name__
        sub = []
        import_type = _get_import_type_mapping(_import) or ""
        api_path = DOCS_PATH / "api"
        if import_type == "module":
            name = _import.__spec__.name
            sub = get_imports_from_module(_import, level + 1)
            filename = to_snake_case(i)

        docs.append(
            Doc(
                name=name,
                path=api_path / f"{import_type}_{filename}.md",
                docstring=_get_docstring(_import),
                level=level,
                sub=sub,
            ),
        )
    return docs


class BaseDocsGenerator:
    """Base class for documentation generators."""

    def __init__(
        self,
        pyproject_content: dict[str, typing.Any],
        organization_name: str | None = None,
        project_name: str | None = None,
    ) -> None:
        """Initialize the documentation generator.

        Args:
            pyproject_content (dict[str, typing.Any]): The content of pyproject.toml.
            organization_name (str | None): The name of the organization. Defaults to None.
            project_name (str | None): The name of the project. Defaults to None.
        """
        self.pyproject_content = pyproject_content
        self.organization_name = organization_name or "project-sthali"
        self.project_name = project_name

    def concatenate(self, file: str, path: pathlib.Path | None = None) -> None:
        """Generate the README file by concatenating documentation files.

        Args:
            file (str): The name of the file to generate (e.g., "index.md").
            path (pathlib.Path | None): The path where the file will be saved. Defaults to DOCS_PATH.
        """
        typer.echo(f"Generating {file}")

        typer.echo(f"Writing {file}")
        path = path or DOCS_PATH
        full_path = path / file
        with pathlib.Path.open(full_path, "w") as f:
            for file_to_concatenate in [
                DOCS_PATH / f"{i}.md" for i in ["index", "requirements", "installation", "usage"]
            ]:
                typer.echo(f"Concatenating doc: {file_to_concatenate.name}")
                with pathlib.Path.open(file_to_concatenate) as _f:
                    f.write(_f.read())
                    f.write("\n")

        typer.echo(f"Generated {full_path}")

    def render(
        self,
        file: str,
        path: pathlib.Path | None = None,
        new_file: str | None = None,
        **kwargs: typing.Any,
    ) -> None:
        """Generate documentation file.

        This method renders a template file with the provided data and writes it to the specified path.

        Args:
            file (str): The name of the file to generate (e.g., "index.md").
            path (pathlib.Path | None): The path where the file will be saved. Defaults to DOCS_PATH.
            new_file (str | None): If provided, the content will be written to this new file instead of `file`.
            **kwargs (typing.Any): Additional keyword arguments to pass to the template rendering.
        """
        typer.echo(f"Generating {file}")

        typer.echo("Rendering the template with the data")
        template = TEMPLATES.get_template(file)  # type: ignore
        content: str = template.render(  # type: ignore
            **self.pyproject_content,
            organization_name=self.organization_name,
            project_name=self.project_name,
            **kwargs or {},
        )

        file = new_file or file
        path = path or DOCS_PATH
        full_path = path / file
        typer.echo(f"Writing {full_path}")
        with pathlib.Path.open(full_path, "w") as f:
            f.write(content)  # type: ignore

        typer.echo(f"Generated {full_path}")
