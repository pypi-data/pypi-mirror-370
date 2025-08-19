"""Installer of SDV-Enterprise."""

import glob
import json
import logging
import subprocess
import sys
from typing import Dict, List, Optional, Union
from urllib.parse import quote_plus

import requests
from requests.exceptions import RequestException

from sdv_installer import config
from sdv_installer.authentication import authenticate
from sdv_installer.constants import (
    CONNECTORS_PACKAGES,
    EXPECTED_PACKAGES,
    TRUSTED_HOSTS,
    ExitCode,
    ProductType,
)
from sdv_installer.utils import (
    check_is_sdv_enterprise_included,
    determine_additional_sdv_enterprise_deps,
    display_progress_animation,
    get_latest_package_version,
    get_package_name,
    list_current_installed_packages,
    list_current_installed_packages_with_their_version,
    mask_license_key,
    print_additional_dependencies_installed,
    print_failed_to_connect,
    print_invalid_credentials,
    print_message,
    print_package_summary,
    print_warning_base_connector_package_installed,
    read_stored_packages,
    remove_package_name,
    split_base_and_bundles,
    store_package_name,
)

LOGGER = logging.getLogger(__name__)


def _perform_pip_action(
    action,
    packages,
    version=None,
    index_url=None,
    extra_options=None,
    show_version=False,
    debug=False,
    upgrade=False,
    package_status=None,
):
    """Performs pip actions (e.g., install, uninstall) on a list of packages.

    This function builds and executes pip commands using subprocess for each package
    provided. It supports custom package indexes and additional pip options.

    Args:
        action (str):
            The pip action to perform (e.g., 'install', 'uninstall').
        packages (list[str]):
            A list of package names to process.
        index_url (str, optional):
            Custom PyPI index URL. Defaults to None.
        extra_options (list[str], optional):
            Additional pip CLI options. Defaults to None.
        debug (bool, optional):
            If True, prints pip commands instead of suppressing output.
            Defaults to False.
    """
    package_status = package_status or {}
    extra_options = extra_options or []
    installed_packages_with_versions = list_current_installed_packages_with_their_version()
    package_version = None
    was_successful = False

    for package_name in packages:
        package = package_name
        use_version = bool(version or index_url) and package not in CONNECTORS_PACKAGES
        online_access = '--no-index' not in extra_options

        if use_version and online_access:
            package_version = version or get_latest_package_version(package_name, index_url)
            if upgrade is False:
                package = f'{package_name}=={package_version}' if package_version else package_name

        elif package in CONNECTORS_PACKAGES and online_access:
            package_version = get_latest_package_version(package_name, index_url)

        command = f'{sys.executable} -m pip {action} {package or package_name}'
        printable_command = f'\npip {action} {package or package_name}'
        if index_url:
            command = f'{command} --index-url {index_url}'
            printable_command = f'{printable_command} --index-url {mask_license_key(index_url)}'
            trusted_hosts_str = ' '.join(f'--trusted-host {host}' for host in TRUSTED_HOSTS)
            command = f'{command} {trusted_hosts_str}'
            printable_command = f'{printable_command} {trusted_hosts_str}'

        if upgrade:
            command = f'{command} --upgrade'
            printable_command = f'{printable_command} --upgrade'

        if extra_options:
            command = f'{command} {" ".join(extra_options)}'
            printable_command = f'{printable_command} {" ".join(extra_options)}'

        LOGGER.debug('Launching subprocess with: %s', printable_command)
        if debug:
            print_message(printable_command)
            process = subprocess.run(command.split())

        else:
            process = subprocess.Popen(
                command.split(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            display_progress_animation(
                process=process,
                package=package_name,
                version=package_version,
                action=action,
                upgrade=upgrade,
                installed_packages=installed_packages_with_versions,
                show_version=show_version,
            )

        was_successful = process.returncode == ExitCode.SUCCESS
        package_status[package_name] = was_successful

        if action == 'install' and not extra_options and was_successful:
            store_package_name(package_name)

        if 'uninstall' in action:
            remove_package_name(package_name)

    return package_status


def _print_and_perform_action(
    action: str,
    packages: Dict[str, str],
    index_url: Union[str, None],
    debug: bool,
    version: Union[str, None],
    pip_options: Optional[List[str]] = None,
    upgrade: bool = False,
    use_product_type: bool = True,
):
    """Print and perform pip action (install/download) for base and bundle packages.

    Args:
        action (str):
            The pip action to perform (eg. 'install' or 'download').
        packages (dict):
            A dictionary mapping package name to the product type.
        index_url (str):
            The index url to use for pip.
        debug (bool):
            Whether or not to show full print out from pip.
        version (str):
            The version of the package to do the action on.
        pip_options (list):
            List of pip options (eg. --python-version).
        upgrade (bool):
            Whether or not to use upgrade option with pip.
        use_product_type (bool):
            Whether or not to use the product type to aid in messages that get printed.
    """
    base_packages, bundles = split_base_and_bundles(packages, use_product_type)
    action_cap = action.capitalize()
    package_status = {}

    if base_packages:
        print_message(f'\n{action_cap}ing SDV Enterprise:')
        base_package_statuses = _perform_pip_action(
            action=action,
            packages=base_packages,
            index_url=index_url,
            debug=debug,
            version=version,
            extra_options=pip_options,
            show_version=True,
            upgrade=upgrade,
            package_status=package_status,
        )
        package_status.update(base_package_statuses)

    if bundles:
        print_message(f'\n{action_cap}ing Bundles:')
        bundle_package_statuses = _perform_pip_action(
            action=action,
            packages=bundles,
            index_url=index_url,
            debug=debug,
            version=version,
            extra_options=pip_options,
            show_version=False,
            upgrade=upgrade,
        )
        package_status.update(bundle_package_statuses)

    if set(CONNECTORS_PACKAGES).intersection(packages):
        print_warning_base_connector_package_installed()

    # Determine if sdv-enterprise is actually present
    if action == 'install':
        successful_packages = list_current_installed_packages()
    else:
        successful_packages = [pkg for pkg, status in package_status.items() if status]

    sdv_included = check_is_sdv_enterprise_included(successful_packages)
    print_package_summary(action, package_status, sdv_included)


def _uninstall_packages_action(packages, debug=False):
    """Uninstall the packages using subprocess / Popen with ``pip``."""
    print_message('Uninstalling:')
    _perform_pip_action('uninstall -y', packages, index_url=None, debug=debug)


def _install_packages_action(
    username, license_key, user_requested_packages, version=None, debug=False, upgrade=False
):
    """Install the packages using subprocess / Popen with ``pip``."""
    username_quoted = quote_plus(username, encoding='utf-8')
    index_url = f'https://{username_quoted}:{license_key}@{config.PYPI_URL}/'

    _print_and_perform_action(
        action='install',
        packages=user_requested_packages,
        index_url=index_url,
        debug=debug,
        version=version,
        pip_options=None,
        upgrade=upgrade,
    )


def _download_packages_action(
    username, license_key, packages, python_version, platform, folder, version=None, debug=False
):
    """Download the packages using subprocess / Popen with ``pip download``."""
    username = quote_plus(username, encoding='utf-8')
    index_url = f'https://{username}:{license_key}@{config.PYPI_URL}/'
    pip_options = [
        '--dest',
        folder,
    ]
    if platform:
        pip_options.append('--only-binary=:all:')
        for item in platform:
            pip_options.extend(['--platform', item])

    if python_version:
        if '--only-binary=:all:' not in pip_options:
            pip_options.append('--only-binary=:all:')

        pip_options.extend(['--python-version', python_version])

    _print_and_perform_action(
        action='download',
        packages=packages,
        index_url=index_url,
        debug=debug,
        version=version,
        pip_options=pip_options,
    )


def _get_accessible_packages(username, license_key):
    """Get a dictionary mapping all packages the user can access to their product type."""
    post_data = {'username': username, 'license_key': license_key}

    try:
        response = requests.post(
            config.API_PACKAGE_PERMISSIONS,
            data=json.dumps(post_data),
            headers=config.HEADERS,
            timeout=config.TIMEOUT,
        )
    except RequestException:
        print_failed_to_connect()
        return None

    if response.status_code != requests.codes.ok:
        print_invalid_credentials()
        return None

    parsed_response = response.json()
    LOGGER.debug('Active packages user %s has access to: %s', username, parsed_response)
    accessible_packages = parsed_response.get('packages', [])
    package_to_product_type = {
        pkg['package_name']: pkg['product_type'] for pkg in accessible_packages
    }
    return package_to_product_type


def _get_packages(username, license_key, package=None, options=None):
    """Retrieve a list of available packages to install."""
    package_to_product_type = _get_accessible_packages(username, license_key)
    if not package_to_product_type:
        return

    if package in package_to_product_type and options:
        options = options if isinstance(options, list) else [options]
        bundle_available_packages = {
            f'{package}[{option}]': ProductType.BUNDLE.value for option in options
        }
        return bundle_available_packages

    elif package and package not in package_to_product_type:
        print_message(f'Invalid package {package} or no access to the given package.')
        return

    if package and package in package_to_product_type:
        return {package: package_to_product_type[package]}

    return package_to_product_type


@authenticate
def install_packages(
    username=None,
    license_key=None,
    package=None,
    options=None,
    debug=False,
    version=None,
    upgrade=False,
    **kwargs,
):
    """Install packages in the current environment (online)."""
    all_sdv_enterprise_related_pkgs = _get_accessible_packages(username, license_key)
    packages_before_install = list_current_installed_packages()

    user_requested_packages = _get_packages(
        username=username,
        license_key=license_key,
        package=package,
        options=options,
    )

    _install_packages_action(
        username,
        license_key,
        user_requested_packages=user_requested_packages,
        version=version,
        debug=debug,
        upgrade=upgrade,
    )
    packages_after_install = list_current_installed_packages()
    additional_dependencies_installed = determine_additional_sdv_enterprise_deps(
        packages_before_install=packages_before_install,
        packages_after_install=packages_after_install,
        user_requested_packages=user_requested_packages,
        all_sdv_enterprise_related_pkgs=all_sdv_enterprise_related_pkgs,
    )
    print_additional_dependencies_installed(additional_dependencies_installed)


def install_packages_from_folder(folder, package=None, options=None, debug=False):
    """Install packages from a folder (offline)."""
    wheels = glob.glob(f'{folder}/*.whl')
    packages = set()
    for wheel in wheels:
        package_name = get_package_name(wheel)
        if package_name in EXPECTED_PACKAGES:
            packages.add(package_name)

    if package:
        if package not in packages:
            print_message(
                f"\nWarning: We couldn’t find the requested package: '{package}' in the provided "
                'folder, no packages were installed.'
            )
            return
        else:
            packages = [package]
            if options:
                packages = [f'{package}[{option}]' for option in options]

    pip_options = ['--no-index', f'--find-links {folder}']
    packages_before_install = list_current_installed_packages()
    packages = dict.fromkeys(packages)

    _print_and_perform_action(
        'install',
        packages=packages,
        pip_options=pip_options,
        version=None,
        index_url=None,
        debug=debug,
        use_product_type=False,
    )
    packages_after_install = list_current_installed_packages()

    additional_dependencies_installed = determine_additional_sdv_enterprise_deps(
        packages_before_install=packages_before_install,
        packages_after_install=packages_after_install,
        user_requested_packages=package,
        all_sdv_enterprise_related_pkgs=EXPECTED_PACKAGES,
    )
    print_additional_dependencies_installed(additional_dependencies_installed)


@authenticate
def _auth_get_packages(username=None, license_key=None, package=None, **kwargs):
    """Wrapper around `_get_packages` to authenticate before using it."""
    return _get_packages(username=username, license_key=license_key, package=package, **kwargs)


def uninstall_packages(
    all_packages=False,
    debug=False,
    **kwargs,
):
    """Uninstall previously installed packages or all accessible packages."""
    packages = []
    try:
        packages = read_stored_packages()

    except (FileNotFoundError, PermissionError, OSError, ValueError):
        print_message('Fetching package list from license server...')
        packages = _auth_get_packages()

    if not packages:
        print_message('No packages found to uninstall.')
        return

    current_packages = list_current_installed_packages()
    if set(packages).intersection(set(current_packages)):
        _uninstall_packages_action(packages, debug=debug)
    else:
        print_message('No packages found to uninstall.')


@authenticate
def download_packages(
    username=None,
    license_key=None,
    package=None,
    python_version=None,
    platform=None,
    folder=None,
    version=None,
    options=None,
    debug=False,
    **kwargs,
):
    """Download packages into a local folder for offline installation."""
    packages = _get_packages(
        username=username, license_key=license_key, package=package, options=options
    )

    if not packages:
        print_message('No packages available for download.')
        return

    _download_packages_action(
        username=username,
        license_key=license_key,
        packages=packages,
        python_version=python_version,
        platform=platform,
        folder=folder,
        version=version,
        debug=debug,
    )


@authenticate
def list_packages(username: str, license_key: str):
    """List all packages the user has access to."""
    package_to_product_type = _get_accessible_packages(username, license_key)

    # Filter bundles
    base_packages, bundles = split_base_and_bundles(package_to_product_type)
    bases_message = '\n'.join(base_packages)
    print_message(f'\nSDV Enterprise:\n{bases_message}')
    if bundles:
        bundles_message = '\n'.join(bundles)
        print_message(f'\nSDV Bundles:\n{bundles_message}')

    return package_to_product_type
