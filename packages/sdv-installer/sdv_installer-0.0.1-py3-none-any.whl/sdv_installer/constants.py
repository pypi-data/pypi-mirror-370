"""Constants used across the SDV-Installer."""

from enum import IntEnum

try:
    from enum import StrEnum as StringEnum

except ImportError:
    from enum import Enum as StringEnum

from packaging.version import Version

from sdv_installer.config import PYPI_URL

MIN_PYTHON_VERSION = Version('3.8')
MAX_PYTHON_VERSION = Version('3.13')
REQUIRED_BITNESS = '64-bit'

SUPPORTED_PLATFORM_TAGS = [
    'macosx_10_9_x86_64',
    'macosx_11_0_universal2',
    'macosx_11_0_x86_64',
    'macosx_12_0_arm64',
    'macosx_12_0_x86_64',
    'macosx_13_0_arm64',
    'macosx_13_0_x86_64',
    'macosx_14_0_arm64',
    'macosx_14_0_x86_64',
    'manylinux2010_x86_64',
    'manylinux2014_x86_64',
    'manylinux_2_17_x86_64',
    'manylinux_2_28_x86_64',
    'musllinux_1_1_x86_64',
    'win_amd64',
]

EXPECTED_PACKAGES = set([
    'sdv-enterprise',
    'sdv-enterprise-full',
    'bundle-cag',
    'bundle-ai-connectors',
    'bundle-xsynthesizers',
    'bundle-differential-privacy',
])

TRUSTED_HOSTS = [
    'pypi.org',
    'pypi.python.org',
    'files.pythonhosted.org',
    PYPI_URL,
]

CONNECTORS_PACKAGES = [
    'bundle-ai-connectors',
]


ACTION_SUCCESS_MESSAGE = {
    'install': 'Installed!',
    'uninstall -y': 'Uninstalled!',
    'download': 'Downloaded!',
}

ACTION_SUCCESS_ALREADY_INSTALLED = {
    'install': 'N/A (already installed)',
}

ACTION_SUCCESS_ALREADY_UPDATED = {
    'install': 'N/A (already installed and up-to-date)',
}

ACTION_ERROR_MESSAGE = {
    'install': 'Installation failed. Use --debug for more details.',
    'uninstall -y': 'Uninstall failed. Use --debug for more details.',
    'download': 'Download failed. Use --debug for more details.',
}
ADDITIONAL_DEPS_MESSAGE_PREFIX = (
    'Note: This package has additional required dependencies that were also installed'
)

# Constants for keypresses
ENTER_KEY = '\r'
BACKSPACE_KEYS = ['\x08', '\x7f']
NEWLINE_KEY = '\n'

# Constants for Summary Messages
SUMMARY_SUCCESS_MESSAGE = {
    'install': ('Success! All packages have been installed. You are ready to use SDV Enterprise.'),
    'download': (
        'Success! All packages have been downloaded. '
        'Please install the packages to use SDV Enterprise.'
    ),
}

SUMMARY_PARTIAL_SUCCESS_MESSAGE = {
    'install': (
        'Notice! All packages were installed, but `sdv-enterprise` was not included.\n'
        'To use SDV Enterprise, please make sure it is installed.'
    ),
    'download': (
        'Notice! All packages were downloaded, but `sdv-enterprise` was not included.\n'
        'Please make sure that you have downloaded SDV-Enterprise in order to '
        'be able to install it later.'
    ),
}

SUMMARY_WARNING_MESSAGE = {
    'install': (
        'Warning! Some packages that you have access to could not be installed. '
        'Please check your setup and contact DataCebo to troubleshoot.'
    ),
    'download': (
        'Warning! Some packages that you have access to could not be downloaded. '
        'Please check your setup and contact DataCebo to troubleshoot.'
    ),
}


class ProductType(StringEnum):
    """Product type enum."""

    BASE = 'base'
    BUNDLE = 'bundle'


class ExitCode(IntEnum):
    """Exit Code Representation."""

    SUCCESS = 0
    ERROR = 1
