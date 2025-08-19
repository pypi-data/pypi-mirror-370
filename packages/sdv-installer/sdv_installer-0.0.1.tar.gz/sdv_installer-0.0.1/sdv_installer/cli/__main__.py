"""SDV-Installer command line interface."""

import argparse
import sys

from sdv_installer.installation import (
    download_packages,
    install_packages,
    install_packages_from_folder,
    list_packages,
    uninstall_packages,
)
from sdv_installer.utils.system_requirements import print_check_results


def install_action(args):
    """Install the `SDV-Enterprise` packages."""
    if args.folder:
        install_packages_from_folder(
            folder=args.folder,
            package=args.package,
            options=args.options,
            debug=args.debug,
        )

    else:
        install_packages(
            package=args.package,
            options=args.options,
            debug=args.debug,
            version=args.version,
            upgrade=args.upgrade,
        )


def uninstall_action(args):
    """Uninstall the `SDV-Enterprise` packages."""
    uninstall_packages(debug=args.debug)


def download_action(args):
    """Download SDV-Enterprise packages for offline install."""
    download_packages(
        package=args.package,
        python_version=args.python_version,
        platform=args.platform,
        folder=args.folder,
        version=args.version,
        options=args.options,
        debug=args.debug,
    )


def list_action(args, parser=None):
    """List all packages the user has access to."""
    list_packages()


def perform_check_action(args):
    """Perform a check on the user's system to verify compatibility with SDV-Enterprise."""
    print_check_results()


def get_parser():
    """Return the argparser for the SDV-Installer application."""
    parser = argparse.ArgumentParser(description='SDV Installer.')
    parser.set_defaults(action=None)

    action = parser.add_subparsers(title='action')

    # Install
    install_parser = action.add_parser('install', help='Install your SDV Enterprise Packages.')
    install_parser.set_defaults(action=install_action)
    install_parser.add_argument(
        '--package',
        required=False,
        help='The package that you want to install.',
    )
    install_parser.add_argument(
        '--options', help='Optional dependencies to install.', required=False, nargs='+'
    )
    install_parser.add_argument('--folder', type=str, help='Install from a local folder.')
    install_parser.add_argument('--debug', action='store_true', help='Print pip install commands.')
    install_parser.add_argument(
        '-v', '--version', required=False, help='SDV-Enterprise version (e.g., 0.23.0).'
    )
    install_parser.add_argument(
        '-u',
        '--upgrade',
        required=False,
        help='Upgrade the current installed packages.',
        action='store_true',
    )

    # Uninstall
    uninstall_parser = action.add_parser(
        'uninstall', help='Uninstall your SDV Enterprise Packages.'
    )
    uninstall_parser.set_defaults(action=uninstall_action)
    uninstall_parser.add_argument(
        '--debug', action='store_true', help='Print pip install commands.'
    )

    # Download
    download_parser = action.add_parser(
        'download',
        help='Download your SDV Enterprise Packages for offline installation.',
    )
    download_parser.set_defaults(action=download_action)
    download_parser.add_argument(
        '--package',
        required=False,
        help=(
            'The package that you want to download. If not provided, all '
            'packages will be downloaded',
        ),
    )
    download_parser.add_argument(
        '--python-version', required=False, help='Python version (e.g., 39).'
    )
    download_parser.add_argument(
        '--platform',
        required=False,
        help='Platform tag(s) (e.g., macosx_14_0_arm64). You can specify this multiple times.',
        action='append',
    )
    download_parser.add_argument(
        '--folder', required=True, help='Destination folder for downloaded packages.'
    )
    download_parser.add_argument(
        '--debug', action='store_true', help='Print pip download commands.'
    )
    download_parser.add_argument(
        '--version', required=False, help='SDV-Enterprise version (e.g., 0.23).'
    )
    download_parser.add_argument(
        '--options', help='Optional dependencies to install.', required=False, nargs='+'
    )

    # List
    list_parser = action.add_parser('list-packages', help='List all packages you have access to.')
    list_parser.set_defaults(action=list_action)

    # Check Requirements
    check_parser = action.add_parser(
        'check-requirements', help='Check if your system meets SDV Enterprise requirements.'
    )
    check_parser.set_defaults(action=perform_check_action)

    return parser


def run_cli():
    """Run command line interface."""
    parser = get_parser()
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    args.action(args)


if __name__ == '__main__':
    run_cli()
