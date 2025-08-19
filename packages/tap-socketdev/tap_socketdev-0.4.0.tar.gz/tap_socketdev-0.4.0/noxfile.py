"""Nox configuration."""

from __future__ import annotations

import nox

PYPROJECT = nox.project.load_toml("pyproject.toml")
PYTHON_VERSIONS = nox.project.python_versions(PYPROJECT)

nox.needs_version = ">=2025.2.9"
nox.options.sessions = ("tests", "mypy", "ty")
nox.options.default_venv_backend = "uv"

UV_SYNC_COMMAND = (
    "uv",
    "sync",
    "--locked",
    "--no-dev",
)


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Execute pytest tests."""
    env = {
        "UV_PROJECT_ENVIRONMENT": session.virtualenv.location,
    }
    if isinstance(session.python, str):
        env["UV_PYTHON"] = session.python

    session.run_install(
        *UV_SYNC_COMMAND,
        "--group=ci",
        "--group=testing",
        env=env,
    )
    session.run("pytest", *session.posargs)


@nox.session(tags=["typing"])
def mypy(session: nox.Session) -> None:
    """Check types with mypy."""
    env = {
        "UV_PROJECT_ENVIRONMENT": session.virtualenv.location,
    }
    if isinstance(session.python, str):
        env["UV_PYTHON"] = session.python

    session.run_install(
        *UV_SYNC_COMMAND,
        "--group=testing",
        "--group=typing",
        env=env,
    )
    args = session.posargs or ("tap_socketdev", "tests")
    session.run("mypy", *args)


@nox.session(tags=["typing"])
def ty(session: nox.Session) -> None:
    """Check types with ty."""
    env = {
        "UV_PROJECT_ENVIRONMENT": session.virtualenv.location,
    }
    if isinstance(session.python, str):
        env["UV_PYTHON"] = session.python

    session.run_install(
        *UV_SYNC_COMMAND,
        "--group=typing",
        env=env,
    )
    args = session.posargs or ("tap_socketdev", "tests")
    session.run("ty", "check", *args)
