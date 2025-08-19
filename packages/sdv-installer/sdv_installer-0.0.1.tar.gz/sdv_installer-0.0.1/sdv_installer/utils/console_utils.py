"""Utility functions for securely handling password input with character masking."""

import sys
import time
from urllib.parse import urlparse, urlunparse

from sdv_installer.config import API_VALIDATE
from sdv_installer.constants import (
    ACTION_ERROR_MESSAGE,
    ACTION_SUCCESS_ALREADY_INSTALLED,
    ACTION_SUCCESS_ALREADY_UPDATED,
    ACTION_SUCCESS_MESSAGE,
    ADDITIONAL_DEPS_MESSAGE_PREFIX,
    BACKSPACE_KEYS,
    ENTER_KEY,
    NEWLINE_KEY,
    SUMMARY_PARTIAL_SUCCESS_MESSAGE,
    SUMMARY_SUCCESS_MESSAGE,
    SUMMARY_WARNING_MESSAGE,
    ExitCode,
)
from sdv_installer.utils.package_utils import is_version_bigger, is_version_equal


def print_with_flush(text):
    """Helper function to print text and flush the output immediately."""
    sys.stdout.write(text)
    sys.stdout.flush()


def handle_keypress(character, password):
    """Handles user keypresses: backspace and normal characteracter input."""
    if character in BACKSPACE_KEYS:
        if password:
            password = password[:-1]
            print_with_flush('\b \b')

    else:
        password += character
        print_with_flush('*')

    return password


def get_password(prompt, get_char_func):
    """Generic password input handler."""
    print_with_flush(prompt)
    password = ''
    while True:
        char = get_char_func()
        char = char.decode('utf-8') if isinstance(char, bytes) else char
        if char in [ENTER_KEY, NEWLINE_KEY]:
            print_with_flush('\n')
            break
        password = handle_keypress(char, password)

    return password


def get_char_win():
    """Windows-specific character reading function."""
    import msvcrt

    return msvcrt.getch()


def get_char_unix():
    """Unix-specific character reading function."""
    import termios
    import tty

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def get_password_input(prompt='License Key: '):
    """Password getter with stars."""
    if sys.platform == 'win32':
        return get_password(prompt, get_char_win)

    return get_password(prompt, get_char_unix)


def print_message(message):
    """Function to be used to print messages across the library."""
    print(message)  # noqa


def handle_process_exit_code(
    process,
    package,
    printable_package,
    version=None,
    action=None,
    installed_packages=None,
    upgrade=False,
):
    """Handle and display messages based on a subprocess exit code.

    Determines the appropriate success or error message to display
    based on the exit code of a subprocess and the package installation context.

    Args:
        process (subprocess.Process):
            A completed subprocess with a `returncode` attribute.
        package (str):
            The internal package name.
        printable_package (str):
            The user-friendly package name for display.
        version (str, optional):
            The target version of the package. Defaults to None.
        action (str, optional):
            The action performed (e.g., 'install', 'upgrade'). Defaults to None.
        installed_packages (dict, optional):
            A mapping of package names to installed versions. Defaults to None.
        upgrade (bool, optional):
            Indicates whether this is an upgrade operation. Defaults to False.
    """
    if process.returncode == ExitCode.SUCCESS:
        msg = ACTION_SUCCESS_MESSAGE.get(action)
        if action == 'install':
            installed_version = installed_packages.get(package) if installed_packages else None
            if installed_version:
                is_installed_bigger = is_version_bigger(installed_version, version)
                is_installed_equal = is_version_equal(installed_version, version)
                if upgrade and is_installed_bigger or is_installed_equal:
                    msg = ACTION_SUCCESS_ALREADY_UPDATED.get(action)
                elif installed_version and is_installed_equal:
                    msg = ACTION_SUCCESS_ALREADY_INSTALLED.get(action)

    elif process.returncode >= ExitCode.ERROR:
        msg = ACTION_ERROR_MESSAGE.get(action)

    sys.stdout.write(f'\r{printable_package} - {msg}\n')
    sys.stdout.flush()


def display_progress_animation(
    process,
    package,
    version=None,
    action=None,
    installed_packages=None,
    upgrade=False,
    show_version=False,
):
    """Display an animated progress indicator while a subprocess is running.

    This function continuously displays an animated progress message
    (e.g., "package .", "package ..", "package ...") until the given
    subprocess finishes. Once completed, it prints a final message
    based on the process's exit code.

    Args:
        process (subprocess.Popen):
            The subprocess to monitor.
        package (str):
            The name of the package being processed.
        version (str, optional):
            An optional version string to display with the package name.
        action (str, optional):
            The action being performed (e.g., "install", "download"). Used to determine
            the appropriate success or error message.
    """
    printable_package = f'{package} (version {version})' if show_version and version else package

    frames = [f'{printable_package} .  ', f'{printable_package} .. ', f'{printable_package} ...']
    while True:
        for frame in frames:
            sys.stdout.write(f'\r{frame}')
            sys.stdout.flush()
            time.sleep(0.3)
            if process.poll() is not None:
                handle_process_exit_code(
                    process,
                    package,
                    printable_package,
                    version,
                    action,
                    installed_packages,
                    upgrade,
                )
                return


def print_invalid_credentials():
    """Print an error message for invalid or expired SDV Enterprise credentials."""
    print_message(
        'Error installing SDV Enterprise. This may be due to an invalid '
        'username/license key combo, or because your license key has expired. '
        "Please double-check that you're providing the right credentials. If "
        "you're continuing to experience issues, please reach out to the "
        'DataCebo team. '
    )


def print_failed_to_connect():
    """Print an error message indicating failure to connect to the authentication server."""
    print_message(
        'Failed to connect to the authentication server.\n'
        'Please check your internet connection or firewall settings and that the API server '
        f'{API_VALIDATE} is reachable.'
    )


def print_warning_base_connector_package_installed():
    """Print a 'warning' message indicating that the base connector package will be installed."""
    print_message(
        "\nWarning: In order to use AI Connectors, you'll need to install "
        'database-specific packages. Please use the `--options` '
        'flag to specify your database variants.'
    )


def print_additional_dependencies_installed(additional_dependencies):
    """Print a message indicating that additional enterprise-related packages were installed.

    Args:
        action (list[str]):
            The list of additional packages that were installed.
    """
    if len(additional_dependencies) == 0:
        return
    message = f'{ADDITIONAL_DEPS_MESSAGE_PREFIX} ('
    message += ', '.join(additional_dependencies) + ').'
    print_message('\n' + message)


def print_package_summary(action, package_status, sdv_included):
    """Print a summary message indicating that whether or not the installation was successful.

    Args:
        action (str):
            The action that was performed (download or install).
        package_status (dict):
            A dictionary with the packages and whether or not the action was successfully performed.
        sdv_included (bool):
            Whether sdv-enterprise was included in the successful result.
    """
    all_success = all(package_status.values())

    if all_success and sdv_included:
        print_message('\n' + SUMMARY_SUCCESS_MESSAGE[action])

    elif all_success and not sdv_included:
        print_message('\n' + SUMMARY_PARTIAL_SUCCESS_MESSAGE[action])
    else:
        print_message('\n' + SUMMARY_WARNING_MESSAGE[action])


def mask_license_key(url):
    """Mask the license key in a URL with stars.

    This function takes a URL that contains embedded basic authentication
    credentials (username and password/license key) and replaces the
    license key with a masked value ("****") for safe logging or display.

    Args:
        url (str):
            The URL containing basic auth credentials.

    Returns:
        str:
            The URL with the license key masked. If no username is present,
            the original URL is returned.
    """
    parsed = urlparse(url)
    if parsed.username:
        netloc = f'{parsed.username}:****@{parsed.hostname}'
        return urlunparse(parsed._replace(netloc=netloc))

    return url
