"""Script to update the API Reference section in mkdocs.yml.

This function scans the API reference directory, updates the 'API Reference' section in the mkdocs.yml navigation, and
writes the changes back to the file.
"""

import pathlib

import typer
import yaml

from ..commons import DOCS_PATH, ROOT_PATH, File


def main() -> None:
    """Update the API Reference section in mkdocs.yml.

    This function scans the API reference directory, updates the 'API Reference' section in the mkdocs.yml navigation,
    and writes the changes back to the file.
    """
    typer.echo("Generating API Reference")

    typer.echo("Reading temp mkdocs")
    with File(ROOT_PATH / "docs" / "mkdocs.yml") as mkdocs_file:
        mkdocs_dict = yaml.safe_load(mkdocs_file.read())

    typer.echo("Getting references")
    api_references = sorted([i.name for i in pathlib.Path.iterdir(DOCS_PATH / "api")])

    typer.echo("Rendering mkdocs_dict with the data")
    for section in mkdocs_dict["nav"]:
        if "API Reference" in section:
            section["API Reference"] = [
                {"_".join(i.split("_")[1:]).rsplit(".", 1)[0]: f"api/{i}"} for i in api_references
            ]

    typer.echo("Writing mkdocs")
    with File(ROOT_PATH / "docs" / "mkdocs.yml", "w") as mkdocs_file:
        yaml.dump(mkdocs_dict, mkdocs_file)

    typer.echo("Generated API Reference")
