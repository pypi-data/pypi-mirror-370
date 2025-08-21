"""The module that contains the CLI commands.

Classes:
    Command: The commands that can be executed by the CLI.
    Generate: The class that executes the commands based on the provided arguments.
"""

import datetime
import enum
import importlib
import pathlib

import cookiecutter.main  # type: ignore
import typer
import yaml

from .commons import (
    DOCS_PATH,
    ROOT_PATH,
    TEMPLATES_PATH,
    BaseDocsGenerator,
    get_imports_from_module,
    read_pyproject,
    recursive_writer,
    to_snake_case,
)


class Generate:
    """The class that executes the options based on the provided arguments.

    Methods:
        execute: Executes the option based on the provided arguments.
    """

    class GenerateOptionsEnum(str, enum.Enum):
        """The options that can be executed by the CLI.

        Options:
            docs
            docstring
            index-file
            installation
            licence
            logo
            mkdocs
            project
            readme
            requirements
            usage
        """

        docs = "docs"
        docstring = "docstring"
        index_file = "index-file"
        installation = "installation"
        licence = "licence"
        logo = "logo"
        mkdocs = "mkdocs"
        project = "project"
        readme = "readme"
        requirements = "requirements"
        usage = "usage"

    @staticmethod
    def execute(option: GenerateOptionsEnum, project_name: str | None = None) -> None:
        """Executes the option based on the provided arguments."""
        match option:
            case Generate.GenerateOptionsEnum.docs:
                Generate.execute(Generate.GenerateOptionsEnum.licence)

                Generate.execute(Generate.GenerateOptionsEnum.index_file)
                Generate.execute(Generate.GenerateOptionsEnum.requirements)
                Generate.execute(Generate.GenerateOptionsEnum.installation)
                Generate.execute(Generate.GenerateOptionsEnum.usage)
                Generate.execute(Generate.GenerateOptionsEnum.readme)

                Generate.execute(Generate.GenerateOptionsEnum.docstring)
                Generate.execute(Generate.GenerateOptionsEnum.mkdocs)

            case Generate.GenerateOptionsEnum.docstring:
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

            case Generate.GenerateOptionsEnum.index_file:
                pyproject_content = read_pyproject()
                docs_generator = BaseDocsGenerator(pyproject_content, project_name=project_name)

                docs_generator.render("index.md")

            case Generate.GenerateOptionsEnum.installation:
                pyproject_content = read_pyproject()
                docs_generator = BaseDocsGenerator(pyproject_content, project_name=project_name)

                docs_generator.render("installation.md")

            case Generate.GenerateOptionsEnum.licence:
                pyproject_content = read_pyproject()
                docs_generator = BaseDocsGenerator(pyproject_content, project_name=project_name)

                year = datetime.datetime.now(datetime.timezone.utc).year
                docs_generator.render("license.md", year=year)
                docs_generator.render("license.md", ROOT_PATH, "LICENSE", year=year)

            case Generate.GenerateOptionsEnum.logo:
                pyproject_content = read_pyproject()
                docs_generator = BaseDocsGenerator(pyproject_content, project_name=project_name)

                assert project_name is not None, "Project name is required for project"
                path = DOCS_PATH / "images"
                docs_generator.render("logo.svg", path, f"{project_name}.svg")

            case Generate.GenerateOptionsEnum.mkdocs:
                pyproject_content = read_pyproject()
                docs_generator = BaseDocsGenerator(pyproject_content, project_name=project_name)

                Generate.execute(Generate.GenerateOptionsEnum.docstring)

                # prerender mkdocs.yml
                docs_generator.render("mkdocs.yml", ROOT_PATH / "docs")

                # append API references to mkdocs.yml
                typer.echo("Generating API Reference")

                typer.echo("Reading temp mkdocs")
                with pathlib.Path.open(ROOT_PATH / "docs" / "mkdocs.yml") as mkdocs_file:
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
                with pathlib.Path.open(ROOT_PATH / "docs" / "mkdocs.yml", "w") as mkdocs_file:
                    yaml.dump(mkdocs_dict, mkdocs_file)

                typer.echo("Generated API Reference")

            case Generate.GenerateOptionsEnum.project:
                assert project_name is not None, "Project name is required for project"

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

                Generate.execute(Generate.GenerateOptionsEnum.logo, project_name)
                Generate.execute(Generate.GenerateOptionsEnum.licence)

            case Generate.GenerateOptionsEnum.readme:
                pyproject_content = read_pyproject()
                docs_generator = BaseDocsGenerator(pyproject_content, project_name=project_name)

                Generate.execute(Generate.GenerateOptionsEnum.index_file)
                Generate.execute(Generate.GenerateOptionsEnum.requirements)
                Generate.execute(Generate.GenerateOptionsEnum.installation)
                Generate.execute(Generate.GenerateOptionsEnum.usage)

                docs_generator.concatenate("README.md", ROOT_PATH)

            case Generate.GenerateOptionsEnum.requirements:
                pyproject_content = read_pyproject()
                docs_generator = BaseDocsGenerator(pyproject_content, project_name=project_name)

                docs_generator.render("requirements.md")

            case Generate.GenerateOptionsEnum.usage:
                pyproject_content = read_pyproject()
                docs_generator = BaseDocsGenerator(pyproject_content, project_name=project_name)

                docs_generator.render("usage.md")
