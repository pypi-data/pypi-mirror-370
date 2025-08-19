r"""Contain the main entry point."""

from __future__ import annotations

import sys

from feu.imports import is_click_available
from feu.install import install_package
from feu.package import find_closest_version as find_closest_version_
from feu.package import is_valid_version

if is_click_available():  # pragma: no cover
    import click


@click.group()
def cli() -> None:
    r"""Implement the main entrypoint."""


@click.command()
@click.option("-n", "--pkg-name", "pkg_name", help="Package name", required=True, type=str)
@click.option("-v", "--pkg-version", "pkg_version", help="Package version", required=True, type=str)
def install(pkg_name: str, pkg_version: str) -> None:
    r"""Install a package and associated packages.

    Args:
        pkg_name: The package name e.g. ``'pandas'``.
        pkg_version: The target version to install.

    Example usage:

    python -m feu install --pkg_name=numpy --pkg_version=2.0.2
    """
    version = find_closest_version_(
        pkg_name=pkg_name,
        pkg_version=pkg_version,
        python_version=f"{sys.version_info[0]}.{sys.version_info[1]}",
    )
    install_package(package=pkg_name, version=version)


@click.command()
@click.option("-n", "--pkg-name", "pkg_name", help="Package name", required=True, type=str)
@click.option("-v", "--pkg-version", "pkg_version", help="Package version", required=True, type=str)
@click.option(
    "-p", "--python-version", "python_version", help="Python version", required=True, type=str
)
def find_closest_version(pkg_name: str, pkg_version: str, python_version: str) -> None:
    r"""Print the closest valid version given the package name and
    version, and python version.

    Args:
        pkg_name: The package name.
        pkg_version: The package version to check.
        python_version: The python version.

    Example usage:

    python -m feu find-closest-version --pkg_name=numpy --pkg_version=2.0.2 --python_version=3.10
    """
    print(  # noqa: T201
        find_closest_version_(
            pkg_name=pkg_name, pkg_version=pkg_version, python_version=python_version
        )
    )


@click.command()
@click.option("-n", "--pkg-name", "pkg_name", help="Package name", required=True, type=str)
@click.option("-v", "--pkg-version", "pkg_version", help="Package version", required=True, type=str)
@click.option(
    "-p", "--python-version", "python_version", help="Python version", required=True, type=str
)
def check_valid_version(pkg_name: str, pkg_version: str, python_version: str) -> None:
    r"""Print if the specified package version is valid for the given
    Python version.

    Args:
        pkg_name: The package name.
        pkg_version: The package version to check.
        python_version: The python version.

    Example usage:

    python -m feu check-valid-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10
    """
    print(  # noqa: T201
        is_valid_version(pkg_name=pkg_name, pkg_version=pkg_version, python_version=python_version)
    )


cli.add_command(install)
cli.add_command(find_closest_version)
cli.add_command(check_valid_version)


if __name__ == "__main__":  # pragma: no cover
    cli()
