from __future__ import annotations

import nox

PYTHON_VERSIONS: list[str] = ["3.13", "3.14"]


@nox.session(venv_backend="uv", tags=["lint", "fix"])
def coverage(session: nox.Session) -> None:
    """Run tests with coverage reporting."""
    session.install("coverage[toml]", "pytest", "pytest-cov")
    session.install("-e", ".")

    session.run(
        "pytest",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-config=config/coverage.ini",
    )

    session.log("Coverage HTML report generated in htmlcov/")


@nox.session(venv_backend="uv", tags=["lint"])
def ruff_check(session: nox.Session) -> None:
    """Run ruff linting and formatting checks (CI-friendly, no changes)."""
    session.install("ruff")
    session.run(
        "ruff",
        "check",
        ".",
        "--fix",
        "--config",
        "config/ruff.toml",
    )
    session.run(
        "ruff",
        "check",
        ".",
        "--config",
        "config/ruff.toml",
    )
    session.run(
        "ruff",
        "format",
        ".",
        "--check",
        "--config",
        "config/ruff.toml",
    )


@nox.session(venv_backend="uv", tags=["lint", "fix"])
def ruff_fix(session: nox.Session) -> None:
    """Run ruff linting and formatting with auto-fix (development)."""
    session.install("ruff")
    session.run(
        "ruff",
        "check",
        ".",
        "--fix",
        "--config",
        "config/ruff.toml",
    )
    session.run(
        "ruff",
        "format",
        ".",
        "--config",
        "config/ruff.toml",
    )


@nox.session(venv_backend="uv", tags=["typecheck"])
def pyright(session: nox.Session) -> None:
    """Run static type checks."""
    session.install("pyright")
    session.run("pyright")


@nox.session(python=PYTHON_VERSIONS, venv_backend="uv")
def tests(session: nox.Session) -> None:
    """Run the unit test suite."""
    session.install("-e", ".")
    session.install("pytest")
    session.run("pytest")
