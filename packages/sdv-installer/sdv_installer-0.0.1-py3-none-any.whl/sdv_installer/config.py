"""Configuration module for SDV-Installer."""

import os

# Default API URL that will be used
LKS_URL = os.getenv('LKS_URL', 'https://lks.datacebo.com')

# Endpoints
API_PACKAGE_PERMISSIONS = f'{LKS_URL}/api/v1/package_permissions/active'
API_VALIDATE = f'{LKS_URL}/api/v1/licenses/validate'

# Pypi Server to be used
PYPI_URL = os.getenv('PYPI_URL', 'pypi.datacebo.com')

# Headers
HEADERS = {'accept': 'application/json', 'Content-Type': 'application/json'}

# Timeout Value for API Calls
TIMEOUT = os.getenv('SDV_API_TIMEOUT', 10)
