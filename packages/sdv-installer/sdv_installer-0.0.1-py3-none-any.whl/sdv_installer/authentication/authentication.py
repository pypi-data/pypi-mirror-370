"""Licensing authentication module."""

from functools import wraps

import requests
from requests.exceptions import RequestException

from sdv_installer import config
from sdv_installer.utils import (
    get_password_input,
    print_failed_to_connect,
    print_invalid_credentials,
)


def authenticate_user_and_license_key(username, license_key):
    """Authenticate the user and license key by sending a request to the authentication API.

    Constructs an authentication request using the provided username and license key,
    sends it to the appropriate API endpoint, and returns a boolean indicating whether
    the authentication was successful.

    Args:
        username (str):
            The username to authenticate.
        license_key (str):
            The license key to authenticate.

    Raises:
        InvalidLoginCredentials:
            If the user has provided invalid login credentials.

    Returns:
        bool:
            True if authentication is successful, False otherwise.
    """
    post_data = {'username': username, 'license_key': license_key}
    try:
        response = requests.post(
            config.API_VALIDATE, json=post_data, headers=config.HEADERS, timeout=config.TIMEOUT
        )
    except RequestException:
        print_failed_to_connect()
        return False

    response_dict = response.json()
    valid = response_dict.get('valid', False)
    authenticated = bool(response.status_code == requests.codes.ok and valid)
    if not authenticated:
        print_invalid_credentials()

    return authenticated


def authenticate(function):
    """Authenticate wrapper to be used by other functions."""

    @wraps(function)
    def wrapper(*args, **kwargs):
        if kwargs.get('username') and kwargs.get('license_key'):
            username = kwargs['username']
            license_key = kwargs['license_key']

        else:
            username = input('Username: ')
            license_key = get_password_input('License Key: ')
            kwargs['username'] = username
            kwargs['license_key'] = license_key

        authenticated = authenticate_user_and_license_key(username, license_key)
        if authenticated:
            return function(*args, **kwargs)

    return wrapper
