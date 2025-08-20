from __future__ import annotations

from dataclasses import dataclass
import importlib.metadata
from importlib.metadata import PackageNotFoundError, metadata, version
import os
import platform
import sys

from pydantic import BaseModel, Field, field_validator

from bear_utils._internal._version import __version__
from bear_utils.logger_manager import LogConsole

__PACKAGE_NAME__ = "bear-utils"


class _ProjectMetadata(BaseModel):
    """Dataclass to store project metadata."""

    name: str = Field(default=__PACKAGE_NAME__, description="Project name of the package.")
    version: str = Field(default=__version__, description="Project version.")
    description: str = Field(default="No description available.", description="Project description.")

    def __str__(self) -> str:
        """String representation of the project metadata."""
        return f"{self.name} v{self.version}: {self.description}"

    @field_validator("version", mode="before")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate the version string."""
        if not isinstance(v, str) or "0.0.0" in v:
            try:
                v = version(__PACKAGE_NAME__)
            except PackageNotFoundError:
                v = "0.0.0"
        return v


_metadata = _ProjectMetadata()


@dataclass
class _Package:
    """Dataclass to store package information."""

    name: str
    """Package name."""
    version: str = ""
    """Package version."""
    description: str = ""
    """Package description."""

    def __post_init__(self) -> None:
        """Post-initialization to ensure version is a string."""
        if not isinstance(self.version, str) or "0.0.0" in self.version:
            self.version = version(self.name) if self.name else "0.0.0"
        if not self.description:
            try:
                self.description = metadata(self.name)["Summary"]
            except PackageNotFoundError:
                self.description = "No description available."

    def __str__(self) -> str:
        """String representation of the package information."""
        return f"{self.name} v{self.version}: {self.description}"


@dataclass(frozen=True)
class _Variable:
    """Dataclass describing an environment variable."""

    name: str
    """Variable name."""
    value: str
    """Variable value."""


@dataclass(frozen=True)
class _Environment:
    """Dataclass to store environment information."""

    interpreter_name: str
    """Python interpreter name."""
    interpreter_version: str
    """Python interpreter version."""
    interpreter_path: str
    """Path to Python executable."""
    platform: str
    """Operating System."""
    packages: list[_Package]
    """Installed packages."""
    variables: list[_Variable]
    """Environment variables."""


def _interpreter_name_version() -> tuple[str, str]:
    if hasattr(sys, "implementation"):
        impl = sys.implementation.version
        version = f"{impl.major}.{impl.minor}.{impl.micro}"
        kind = impl.releaselevel
        if kind != "final":
            version += kind[0] + str(impl.serial)
        return sys.implementation.name, version
    return "", "0.0.0"


def _get_package_info(dist: str = _metadata.name) -> _Package:
    """Get package information for the given distribution.

    Parameters:
        dist: A distribution name.

    Returns:
        Package information with version, name, and description.
    """
    try:
        pkg_version = version(dist)
        pkg_description = metadata(dist)["Summary"] or "No description available."
        return _Package(
            name=dist,
            version=pkg_version,
            description=pkg_description,
        )
    except PackageNotFoundError:
        return _Package(name=dist, version="0.0.0", description="Package not found.")


def _get_name(dist: str = __PACKAGE_NAME__) -> str:
    """Get name of the given distribution.

    Parameters:
        dist: A distribution name.

    Returns:
        A package name.
    """
    return _metadata.name if dist == __PACKAGE_NAME__ else _get_package_info(dist).name


def _get_version(dist: str = __PACKAGE_NAME__) -> str:
    """Get version of the given distribution.

    Parameters:
        dist: A distribution name.

    Returns:
        A version number.
    """
    return _metadata.version if dist == __PACKAGE_NAME__ else _get_package_info(dist).version


def _get_description(dist: str = __PACKAGE_NAME__) -> str:
    """Get description of the given distribution.

    Parameters:
        dist: A distribution name.

    Returns:
        A description string.
    """
    return _metadata.description if dist == __PACKAGE_NAME__ else _get_package_info(dist).description


def _get_debug_info() -> _Environment:
    """Get debug/environment information.

    Returns:
        Environment information.
    """
    py_name, py_version = _interpreter_name_version()
    packages: list[str] = [
        _metadata.name,
        "diskcache",
        "pyglm",
        "sqlalchemy",
        "pillow",
        "rich",
        "pydantic",
        "pathspec",
        "prompt-toolkit",
        "pyyaml",
        "singleton-base",
        "httpx",
        "toml",
        "tinydb",
        "fastapi",
        "uvicorn",
        "typer",
        "pyfiglet",
        "bear-epoch-time",
    ]
    variables: list[str] = [
        "PYTHONPATH",
        *[var for var in os.environ if var.startswith(_metadata.name.replace("-", "_"))],
    ]
    return _Environment(
        interpreter_name=py_name,
        interpreter_version=py_version,
        interpreter_path=sys.executable,
        platform=platform.platform(),
        variables=[_Variable(var, val) for var in variables if (val := os.getenv(var))],
        packages=[_Package(pkg, _get_version(pkg)) for pkg in packages],
    )


def get_installed_packages() -> list[_Package]:
    """Get all installed packages in current environment"""
    packages = []
    for dist in importlib.metadata.distributions():
        packages.append({"name": dist.metadata["Name"], "version": dist.version})
    return packages


def _print_debug_info(no_color: bool = False) -> None:
    """Print debug/environment information with minimal clean formatting."""
    info: _Environment = _get_debug_info()
    sections = [
        (
            "SYSTEM",
            [
                ("Platform", info.platform),
                ("Python", f"{info.interpreter_name} {info.interpreter_version}"),
                ("Location", info.interpreter_path),
            ],
        ),
        ("ENVIRONMENT", [(var.name, var.value) for var in info.variables]),
        ("PACKAGES", [(pkg.name, f"v{pkg.version}") for pkg in info.packages]),
    ]
    console = LogConsole(highlight=not no_color, markup=True, force_terminal=not no_color)

    for i, (section_name, items) in enumerate(sections):
        if items:
            console.print(f"{section_name}", style="bold red")
            for key, value in items:
                console.print(key, style="bold blue", end=": ")
                console.print(value, style="bold green")
            if i != len(sections) - 1:
                console.print()


if __name__ == "__main__":
    print(_print_debug_info())
