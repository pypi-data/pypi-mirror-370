from requests.exceptions import HTTPError, RequestException


class DixaRequestException(RequestException):
    """Dixa request exception."""

    pass


class DixaHTTPError(HTTPError):
    """Dixa HTTP error."""

    pass


class DixaAPIError(Exception):
    """Dixa API error."""

    pass
