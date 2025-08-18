"""Script to generate a new project using the Sthali Core cookiecutter template.

This script clones the template, applies the project name and year, copies the generated content, and cleans up the
temporary directory.
"""

import datetime

import cookiecutter.main  # type: ignore
import typer

from ..commons import TEMPLATES_PATH, to_snake_case


def main(project_name: str) -> None:
    """Generate a new project using the Sthali Core cookiecutter template.

    Args:
        project_name: The name of the new project to generate.
    """
    typer.echo(f"Generating project with name: {project_name}")

    typer.echo("Cloning template")
    cookiecutter.main.cookiecutter(  # type: ignore
        str(TEMPLATES_PATH / "cookiecutter"),
        no_input=True,
        extra_context={
            "project_name": project_name,
            "project_slug": to_snake_case(project_name),
            "year": datetime.datetime.now(datetime.timezone.utc).year,
        },
        overwrite_if_exists=True,
    )
