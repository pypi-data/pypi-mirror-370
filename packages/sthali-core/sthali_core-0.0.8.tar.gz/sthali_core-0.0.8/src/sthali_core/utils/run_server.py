"""Utilities for running the FastAPI server."""

import os

import fastapi
import uvicorn

from .base import App, AppSpecification, Config


def run(config: type[Config], app_spec: type[AppSpecification], app: type[App]) -> fastapi.FastAPI:
    """Initialize and return the FastAPI application.

    Args:
        config: The configuration class.
        app_spec: The application specification class.
        app: The application class.

    Returns:
        The configured FastAPI application instance.
    """
    app_specification_file_path = os.getenv("APP_SPECIFICATION_FILE_PATH") or "volume/app_specification_sample.json"
    client_config = config(app_specification_file_path)
    client_app = app(app_spec(**client_config.app_specification))
    return client_app.app


def main(app: fastapi.FastAPI, port: int = 8000) -> None:
    """Run the FastAPI application using Uvicorn.

    Args:
        app: The FastAPI application instance to run.
        port: The port number to run the server on. Defaults to 8000.
    """
    uvicorn.run(app, host="0.0.0.0", port=port)
