"""Base utilities for Sthali Core."""

import typing

import fastapi
import pydantic


class Config:
    """Manages application configuration."""

    app_specification: dict[str, typing.Any]

    def __init__(self, app_specification_file_path: str) -> None:
        """Initialize Config.

        Args:
            app_specification_file_path: Path to the application specification file.
        """


@pydantic.dataclasses.dataclass
class AppSpecification:
    """Represents the application specification."""


class App:
    """Represents the FastAPI application."""

    app: fastapi.FastAPI

    def __init__(self, app_specification: AppSpecification) -> None:
        """Initialize App.

        Args:
            app_specification: The application specification.
        """
