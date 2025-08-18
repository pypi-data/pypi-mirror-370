"""Documentation generation scripts for Sthali Core.

This package contains scripts to generate and update documentation files such as API references, README, license, and
requirements.
"""

import pathlib
import typing

import typer

from ..commons import DOCS_PATH, TEMPLATES, File

ORGANIZATION_NAME = "project-sthali"


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
        self.organization_name = organization_name or ORGANIZATION_NAME
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
        with File(full_path, "w") as f:
            for file_to_concatenate in [
                DOCS_PATH / f"{i}.md" for i in ["index", "requirements", "installation", "usage"]
            ]:
                typer.echo(f"Concatenating doc: {file_to_concatenate.name}")
                with File(file_to_concatenate) as _f:
                    f.write(_f.read())
                    f.write("\n")

        typer.echo(f"Generated {full_path}")

    def render(
        self, file: str, path: pathlib.Path | None = None, new_file: str | None = None, **kwargs: typing.Any,
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
        with File(full_path, "w") as f:
            f.write(content)

        typer.echo(f"Generated {full_path}")
