"""Utilities to handle appdirs and store application data."""

import logging
import os
from pathlib import Path

from platformdirs import user_data_dir

APP_NAME = 'SDV-Installer'
APP_AUTHOR = 'DataCebo'
LOGGER = logging.getLogger(__name__)
CONFIG_PATH = Path(__file__).resolve().parent


def store_package_name(package):
    """Store the installed package name in a text file in a platform-specific directory.

    Args:
        packages (str):
            A string representing the package name.
    """
    storage_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))

    try:
        storage_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # No access to user data dir, fall back if possible
        if os.access(CONFIG_PATH, os.W_OK):
            storage_dir = CONFIG_PATH
        else:
            # Nowhere to write
            return

    except OSError:
        # Filesystem might be read-only or inaccessible
        return

    package_file = storage_dir / 'installed_packages.txt'
    try:
        with package_file.open('a') as installed_packages:
            installed_packages.write(package + '\n')

    except (PermissionError, OSError) as error:
        LOGGER.error(f"Failed to write installed package '{package}' to '{package_file}': {error}")


def read_stored_packages():
    """Read the list of installed packages from the platform-specific data file.

    Returns:
        list[str]:
            A list of installed package names.

    Raises:
        FileNotFoundError:
            If the file does not exist.
    """
    storage_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    package_file = storage_dir / 'installed_packages.txt'

    if not package_file.exists():
        raise FileNotFoundError('No stored package file found.')

    with package_file.open('r') as installed_packages:
        return set([line.strip() for line in installed_packages if line.strip()])


def remove_package_name(package):
    """Remove a single package name from the installed packages file.

    Args:
        package (str):
            A string representing the package name to remove.
    """
    storage_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    package_file = storage_dir / 'installed_packages.txt'

    if not package_file.exists():
        return

    # Read all packages and filter out the one to remove
    with package_file.open('r') as package_reader:
        packages = [line.strip() for line in package_reader if line.strip() != package]

    with package_file.open('w') as package_writer:
        package_writer.write('\n'.join(packages) if packages else '')
