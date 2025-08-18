"""Script to generate Markdown documentation files from Python docstrings.

This script introspects modules, classes, and functions in the project, extracts their docstrings and metadata, and
writes them as Markdown files to the API reference directory.
"""

import importlib
import pathlib
import types
import typing

import pydantic
import typer

from ..commons import DOCS_PATH, ROOT_PATH, TEMPLATES, File, to_snake_case


def get_metadata(obj: typing.Any) -> str | None:
    """Retrieve the Pydantic metadata description from an object, if available.

    Args:
        obj (typing.Any): The object to inspect.

    Returns:
        str | None: The description from Pydantic FieldInfo metadata, or None if not found.
    """
    metadata: list[typing.Any] = getattr(obj, "__metadata__", [])
    field_info = next(filter(lambda x: isinstance(x, pydantic.fields.FieldInfo), metadata), None)
    if field_info:
        return field_info.description
    return None


def get_doc(obj: typing.Any) -> str | None:
    """Get the __doc__ attribute of an object.

    Args:
        obj (typing.Any): The object to inspect.

    Returns:
        str | None: The docstring of the object, or None if not present.
    """
    return getattr(obj, "__doc__", None)


def get_docstring(obj: typing.Any) -> str:
    """Get the best available docstring for an object.

    Prefers Pydantic metadata description, then __doc__, or empty string.

    Args:
        obj (typing.Any): The object to inspect.

    Returns:
        str: The docstring or description.
    """
    metadata = get_metadata(obj)
    doc = get_doc(obj)
    return metadata or doc or ""


def render(name: str, docstring: str, level: int = 3, sub: str | None = None) -> str:
    """Render a Markdown documentation block using Jinja2 template.

    Args:
        name (str): The name of the object.
        docstring (str): The docstring to include.
        level (int): The Markdown heading level. Defaults to 3.
        sub (str | None): Rendered documentation for sub-objects. Defaults to None.

    Returns:
        str: The rendered Markdown string.
    """
    template = TEMPLATES.get_template("docstring.md")  # type: ignore
    return template.render(  # type: ignore
        name=name,
        docstring=docstring,
        heading_level=level * "#",
        sub=sub,
    )


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
    typer.echo(f"Writing docstring from import: {doc.name}")

    to_render = render(doc.name, doc.docstring, doc.level, "\n".join([recursive_writer(s) for s in doc.sub]))
    with File(doc.path, "w") as doc_file:
        doc_file.write(to_render)

    return to_render


TypesMapping = typing.Literal["module", "function", "class"]


def get_import_type_mapping(_import: typing.Any) -> TypesMapping | None:
    """Determine the type of an imported object.

    Args:
        _import (typing.Any): The imported object.

    Returns:
        TypesMapping | None: A string indicating the type: "module", "function", or "class", or None if unknown.
    """
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


def get_imports_from_module(module: types.ModuleType, level: int) -> list[Doc]:
    """Recursively extract documentation metadata from a module's __all__ exports.

    Args:
        module (types.ModuleType): The module to inspect.
        level (int): The Markdown heading level.

    Returns:
        list[Doc]: A list of Doc objects representing the module's exports.
    """
    typer.echo(f"Getting imports from {module.__name__} module")

    docs: list[Doc] = []
    for i in getattr(module, "__all__", []):
        typer.echo(f"Getting metadata from {i} import")

        _import = getattr(module, i)
        name = _import.__name__
        filename = _import.__name__
        sub = []
        import_type = get_import_type_mapping(_import) or ""
        api_path = DOCS_PATH / "api"
        if import_type == "module":
            name = _import.__spec__.name
            sub = get_imports_from_module(_import, level + 1)
            filename = to_snake_case(i)

        docs.append(
            Doc(
                name=name,
                path=api_path / f"{import_type}_{filename}.md",
                docstring=get_docstring(_import),
                level=level,
                sub=sub,
            ),
        )
    return docs


def main() -> None:
    """Generate Markdown documentation files for the project.

    This function imports the project module, extracts docstrings from its exports,
    clears the API reference directory, and writes new documentation files.
    """
    project_slug = to_snake_case(str(ROOT_PATH.absolute()).split("/")[-1])
    typer.echo(f"Generating docs for {project_slug}")

    project_module = importlib.import_module(project_slug)
    heading_level = 3
    imports_from_module = get_imports_from_module(project_module, heading_level)

    typer.echo("Clearing API Reference folder")
    api_path = DOCS_PATH / "api"
    for doc in api_path.glob("*"):
        doc.unlink()

    for doc in imports_from_module:
        recursive_writer(doc)

    typer.echo(f"Generated docs for {project_slug}")
