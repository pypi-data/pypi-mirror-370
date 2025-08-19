"""Utility functions for package and virtual env."""

import os
import pathlib
import subprocess
import sys
from importlib.metadata import distributions
from typing import Dict, Tuple

from packaging.requirements import Requirement
from packaging.utils import parse_sdist_filename, parse_wheel_filename
from packaging.version import InvalidVersion, Version

from sdv_installer.constants import EXPECTED_PACKAGES, ProductType

BASE_PREFIX = 'sdv-enterprise'


def list_current_installed_packages():
    """Returns a list of currently installed package names.

    Uses `importlib.metadata.distributions()` to retrieve metadata for all installed
    distributions and extracts their package names.

    Returns:
        List[str]:
            A list of package names currently installed in the environment.
    """
    return [dist.metadata['Name'] for dist in distributions()]


def list_current_installed_packages_with_their_version():
    """Returns a list of currently installed package names.

    Uses `importlib.metadata.distributions()` to retrieve metadata for all installed
    distributions and extracts their package names.

    Returns:
        List[str]:
            A list of package names currently installed in the environment.
    """
    return {dist.metadata['Name']: dist.metadata['Version'] for dist in distributions()}


def clean_path(path: str):
    """Cleans a file path by stripping leading/trailing whitespace and converting to lowercase.

    Args:
        path (str):
            The input file path as a string.

    Returns:
        str:
            The cleaned file path.
    """
    return path.strip().lower()


def get_package_name(file_path: str):
    """Extracts the package name from a given file path.

    Supports `.whl`, `.tar.gz`, and other archive formats. For wheel and source distribution
    files, the name is parsed using appropriate helper functions. For other file types,
    the base file name is returned.

    Args:
        file_path (str):
            Path to the package file.

    Returns:
        str or None:
            The extracted package name, or None if the path is invalid.
    """
    package_name = None
    if not file_path or not file_path.strip():
        return None

    file_path = clean_path(file_path)
    if file_path.endswith('.whl') or file_path.endswith('.tar.gz'):
        filename = os.path.basename(file_path)
        if file_path.endswith('.whl'):
            package_name, _, _, _ = parse_wheel_filename(filename)
        else:
            package_name, _ = parse_sdist_filename(filename)
    else:
        package_name = pathlib.PurePath(file_path).name

    return package_name


def get_latest_package_version(package_name, index_url=None):
    """Returns a sorted list of available versions for a given package.

    This function invokes `pip index versions` via subprocess to retrieve the
    list of available versions for a specified package from the given Python
    package index (PyPI or a custom index).

    Args:
        package_name (str):
            The name of the package to query.
        index_url (str, optional):
            The base URL of the package index to use. If not provided, the default PyPI
            index is used.

    Returns:
        str:
            Returns a string representing the highest version available.
            Returns None if the pip command fails.
    """
    cmd = [sys.executable, '-m', 'pip', 'index', 'versions', package_name]
    if index_url:
        cmd += ['--index-url', index_url]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None

    for line in result.stdout.splitlines():
        if line.startswith('Available versions: '):
            text_versions = line.replace('Available versions: ', '')
            text_versions = text_versions.split(',')
            break

    return text_versions[0]


def split_base_and_bundles(
    packages: Dict[str, str], use_product_type: bool = True
) -> Tuple[str, list]:
    """Split base sdv-enterprise packages from bundles.

    Args:
        packages (dict): List of package dicts. Each dict has the keys 'package_name' and
        'package_type'.
        use_product_type (bool): Whether or not to use the product type attribute to figure out
        if a package is a base package or bundle. If false, fall back to using the package name.

    Returns:
        tuple (list[str], list[str]). A list of base packages and a list of bundle packages.
    """
    base_packages = []
    bundles = []
    if use_product_type:
        for package, product_type in packages.items():
            if product_type == ProductType.BASE.value:
                base_packages.append(package)
            elif product_type == ProductType.BUNDLE.value:
                bundles.append(package)
    else:
        for package in packages:
            if package.startswith(BASE_PREFIX):
                base_packages.append(package)
            else:
                bundles.append(package)

    return sorted(base_packages), sorted(bundles)


def is_version_bigger(installed_version, requested_version):
    """Check if the installed version is greater than the requested version."""
    if isinstance(installed_version, str) and isinstance(requested_version, str):
        try:
            return Version(installed_version) > Version(requested_version)
        except InvalidVersion:
            return False

    return False


def is_version_equal(installed_version, requested_version):
    """Check if the installed version is equal to the requested version."""
    if isinstance(installed_version, str) and isinstance(requested_version, str):
        try:
            return Version(installed_version) == Version(requested_version)
        except InvalidVersion:
            return False

    return False


def convert_to_set(obj):
    """Convert a list, tuple, str, int, float, or dictionary to a set."""
    if isinstance(obj, (list, tuple)):
        obj = set(obj)
    elif isinstance(obj, (str, int, float)):
        obj = {obj}
    elif isinstance(obj, dict):
        obj = set(obj.keys())
    return obj


def get_requirement_name(requirement_name):
    """Get the name of a requirement, useful to remove extra_requires, specifiers, markers."""
    if isinstance(requirement_name, str):
        return Requirement(requirement_name).name
    return requirement_name


def is_none_or_empty_iterate(obj):
    """Check if object is None or an empty list/dict/iterate."""
    return obj is None or (hasattr(obj, '__len__') and len(obj) == 0)


def determine_additional_sdv_enterprise_deps(
    packages_before_install,
    packages_after_install,
    user_requested_packages,
    all_sdv_enterprise_related_pkgs=EXPECTED_PACKAGES,
):
    """Determine the additional sdv-enterprise related packages installed, given before & after.

    Args:
        packages_before_install (set, list[str]):
            All packages before installation with sdv-installer.

        packages_after_install (set, list[str]):
            All packages after installation with sdv-installer.

        user_requested_packages (set, list[str], dict[str, str], str, None)
            The user requested packages to install. If it is an itert

        all_sdv_enterprise_related_pkgs (set, list[str])
            The package names of all base packages and bundle packages
            that could be installed by the user.
            Defaults to EXPECTED_PACKAGES

    Returns:
        (set): The additional sdv-enterprise related packages that were installed.
    """
    if is_none_or_empty_iterate(user_requested_packages):
        # User did not say a specific package to install
        # Return empty list to specify no additional deps were installed (everything installed)
        return {}

    packages_before_install = convert_to_set(packages_before_install)
    packages_after_install = convert_to_set(packages_after_install)

    user_requested_packages = convert_to_set(user_requested_packages)
    user_requested_packages = {get_requirement_name(pkg) for pkg in user_requested_packages}

    all_sdv_enterprise_related_pkgs = convert_to_set(all_sdv_enterprise_related_pkgs)

    all_installed_pkgs = packages_after_install.difference(packages_before_install)
    installed_pkgs_related_to_sdv_enterprise = all_installed_pkgs.intersection(
        all_sdv_enterprise_related_pkgs
    )
    additional_dependencies_installed = installed_pkgs_related_to_sdv_enterprise.difference(
        user_requested_packages
    )
    return additional_dependencies_installed


def check_is_sdv_enterprise_included(packages):
    """Check if any of the given package names includes 'sdv-enterprise'.

    Args:
        packages (list of str):
            A list of package names.

    Returns:
        bool:
            True if 'sdv-enterprise' is found in any package name, False otherwise.
    """
    for package in packages:
        if package.startswith(BASE_PREFIX):
            return True

    return False
