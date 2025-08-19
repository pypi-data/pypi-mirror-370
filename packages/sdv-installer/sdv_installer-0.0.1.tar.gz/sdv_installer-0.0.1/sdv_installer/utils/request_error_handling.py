"""Utility functions to handle requests HTTP errors."""


class NotFoundError(ValueError):
    """Error to be raised when an end point is not found (404)."""


def handle_http_error_response(response):
    """Handle HTTP error responses and raises appropriate exceptions with error messages.

    The function attempts to parse the error details from the response as JSON. If the content
    cannot be parsed as JSON, the raw response text will be used.

    Args:
        response (requests.Response):
            The HTTP response object that contains the status code and error details.

    Raises:
        ValueError:
            If the status code is 400 (Bad Request) or 422 (Validation Error).
        PermissionError:
            If the status code is 401 (Unauthorized) or 403 (Forbidden).
        NotFoundError:
            If the status code is 404 (Not Found).
        RuntimeError:
            If the status code is 405 (Method Not Allowed) or 5xx (Server Error).
        Exception:
            For any unexpected status code.
    """
    status = response.status_code
    try:
        error_detail = response.json()
    except ValueError:
        error_detail = response.text

    error_map = {
        400: (ValueError, f'Bad Request: {error_detail}'),
        401: (PermissionError, f'Invalid Credentials or Expired License Key: {error_detail}.'),
        403: (PermissionError, 'Forbidden: You don’t have permission to access this resource.'),
        404: (NotFoundError, 'Not Found: The requested endpoint does not exist.'),
        405: (RuntimeError, 'Method Not Allowed: Check the HTTP method.'),
        422: (ValueError, f'Validation Error: {error_detail}'),
    }

    if status >= 500:
        exception, message = RuntimeError, f'Server Error ({status}): {error_detail}'

    else:
        exception, message = error_map.get(
            status, (Exception, f'Unexpected Error ({status}): {error_detail}')
        )

    raise exception(message)
