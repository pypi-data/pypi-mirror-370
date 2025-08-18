"""Dynamically creates an Enum for available clients."""

import enum
import importlib
import pathlib
import types


class Clients:
    """Discovers and provides an Enum for client modules."""

    def __init__(self, parent_path: pathlib.Path, package: str | None = None) -> None:
        """Initialize Clients.

        Args:
            parent_path: The parent directory path where the 'clients' subdirectory resides.
            package: The package name to use for relative imports. Defaults to the parent_path's name.
        """
        self.clients_directory = parent_path / pathlib.Path("clients")
        self.package = package or parent_path.name

    @property
    def _clients_file_path(self) -> list[pathlib.Path]:
        return list(filter(lambda file: file.stem != "__init__", self.clients_directory.glob("*.py")))

    @property
    def _src_path(self) -> pathlib.Path:
        return next(filter(lambda x: x.name in ["src", "site-packages"], self.clients_directory.parents))

    @property
    def clients_map(self) -> dict[str, types.ModuleType]:
        """Return a map of client names to their imported modules.

        Returns:
            A dictionary where keys are client names (derived from filenames)
            and values are the corresponding imported client modules.
        """
        return {
            file_path.stem: importlib.import_module(self._relative_to_formatted(file_path), package=self.package)
            for file_path in self._clients_file_path
        }

    @property
    def enum(self) -> type[enum.Enum]:
        """Dynamically create an Enum representing available clients.

        The Enum members will have names and values corresponding to the client names.

        Returns:
            An Enum type where members are the discovered client names.
        """
        client_enum_map = {key: key for key in self.clients_map}
        return enum.Enum("ClientEnum", client_enum_map)

    def _relative_to_formatted(self, path: pathlib.Path) -> str:
        """Return the relative path to the clients directory."""
        return str(path.relative_to(self._src_path)).strip(".py").replace("/", ".")
