import json
import logging
import random
import time
from enum import Enum
from typing import Any, Mapping, Optional, Type, Union

from requests import Request, Response
from requests.exceptions import HTTPError, JSONDecodeError, RequestException
from requests.models import PreparedRequest
from requests.sessions import Session

from .exceptions import DixaAPIError, DixaHTTPError, DixaRequestException

REDACTED_HEADERS = ["Authorization"]


class DixaCustomFormatter(logging.Formatter):
    standard_attributes = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "message",
        "asctime",
        "taskName",
    }

    def format(self, record):
        base_message = super().format(record)
        extra_fields = {
            key: value
            for key, value in record.__dict__.items()
            if key not in self.standard_attributes
        }
        if extra_fields:
            extra_message = json.dumps(extra_fields, indent=4)
            return f"{base_message}\n{extra_message}"
        else:
            return base_message


class RequestMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class DixaClient:
    def __init__(
        self,
        api_key: str,
        api_secret: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: int = 10,
        session: Optional[Session] = None,
        logger: Optional[logging.Logger] = None,
        logging_level: int = logging.DEBUG,
    ):
        self._api_secret = api_secret
        self._max_retries = max_retries
        self._base_retry_delay = retry_delay
        self._retry_delay = retry_delay
        self._retries = 0
        self._logger = logger or self._create_default_logger(logging_level)
        self._session = session or Session()
        self._session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": api_key,
            }
        )

    def _create_default_logger(
        self, logging_level: int = logging.DEBUG
    ) -> logging.Logger:
        logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = DixaCustomFormatter(
            "%(asctime)s - %(levelname)s - %(message)s - %(name)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging_level)
        return logger

    def _redact_auth(self, request: PreparedRequest) -> PreparedRequest:
        temp_request = request.copy()
        for header in REDACTED_HEADERS:
            if header in temp_request.headers:
                temp_request.headers[header] = "REDACTED"
        return temp_request

    def _retry(self, request: PreparedRequest) -> Response:
        redacted_request = self._redact_auth(request)
        if self._retries >= self._max_retries:
            self._logger.error(
                "Max retries reached",
                extra={
                    "retries": self._retries,
                    "max_retries": self._max_retries,
                    "url": redacted_request.url,
                    "headers": dict(redacted_request.headers),
                },
            )
            self._reset_retry_logic()
            raise DixaAPIError("Max retries reached")
        self._increase_retry_logic()
        self._logger.info(
            "Retrying",
            extra={
                "retries": self._retries,
                "max_retries": self._max_retries,
                "delay": self._retry_delay,
                "url": redacted_request.url,
                "headers": dict(redacted_request.headers),
            },
        )
        time.sleep(self._retry_delay)
        return self._send(request)

    def _increase_retry_logic(self):
        self._retries += 1
        self._retry_delay *= 2
        self._retry_delay += random.uniform(0, 1)

    def _reset_retry_logic(self):
        self._retries = 0
        self._retry_delay = self._base_retry_delay

    def _extract_error_message(self, response: Response) -> str:
        try:
            error_response = response.json()
        except JSONDecodeError:
            self._logger.error(
                "Failed to decode JSON response", extra={"response": response.text}
            )
            return response.text
        return error_response.get("message", response.text)

    def _send(self, request: PreparedRequest) -> Response:
        redacted_request = self._redact_auth(request)
        self._logger.debug(
            "Sending request",
            extra={
                "url": redacted_request.url,
                "headers": dict(redacted_request.headers),
            },
        )
        try:
            response = self._session.send(request)
            if response.status_code == 429:
                self._logger.warning("Rate limited, retrying...")
                return self._retry(request)
            if response.status_code >= 500:
                self._logger.error(
                    "Server error, retrying...",
                    extra={
                        "response": response.text,
                        "status_code": response.status_code,
                    },
                )
                return self._retry(request)
            self._reset_retry_logic()
            response.raise_for_status()
            self._logger.debug("Request successful", extra={"response": response.text})
            return response
        except HTTPError as http_error:
            self._logger.error(
                "HTTP error",
                extra={
                    "error": http_error.response.text,
                },
            )
            raise DixaHTTPError(
                self._extract_error_message(http_error.response)
            ) from http_error
        except RequestException as request_error:
            self._logger.error(
                "Request failed",
                extra={
                    "error": "An ambiguous error occured",
                },
            )
            raise DixaRequestException("Request failed") from request_error

    def _extract_data(
        self, response: Response, expected: Type[Union[dict, list]]
    ) -> Union[dict, list]:
        try:
            data = response.json().get("data", {})
        except JSONDecodeError:
            self._logger.error(
                "Failed to decode JSON response, expect missing data",
                extra={"response": response.text},
            )
            return expected()

        if not isinstance(data, expected):
            self._logger.error(
                "Invalid data type",
                extra={
                    "expected": expected.__name__,
                    "got": type(data).__name__,
                    "data": data,
                },
            )
            raise DixaAPIError(
                f"Expected {expected.__name__}, got {type(data).__name__}"
            )

        return data

    def _request(
        self,
        method: RequestMethod,
        url: str,
        query: Mapping[str, Any] | None = None,
        json: Mapping[str, Any] | None = None,
    ) -> Response:
        request = Request(method.value, url, params=query, json=json)
        prepared_request = self._session.prepare_request(request)
        return self._send(prepared_request)

    def _has_next_page(self, data: dict) -> bool:
        return data.get("meta", {}).get("next") is not None

    def paginate(self, url: str, query: Mapping[str, Any] | None = None) -> list:
        pages, data = 0, []
        while url:
            pages += 1
            self._logger.debug(
                "Fetching page", extra={"page": pages, "url": url, "query": query}
            )
            response = self._request(RequestMethod.GET, url, query=query)
            if not isinstance(response, Response):
                return data
            try:
                response = response.json()
                data.extend(response.get("data", []))
            except JSONDecodeError:
                self._logger.error(
                    "Failed to decode JSON response, expect missing data",
                    extra={"response": response.text},
                )
                break
            meta = response.get("meta", {})
            url = meta.get("next") if meta is not None else ""
        self._logger.debug(
            "Fetched all pages", extra={"pages": pages, "records": len(data)}
        )
        return data

    def get(
        self,
        url: str,
        query: Union[Mapping[str, Any], None] = None,
        expected: Type[Union[dict, list]] = dict,
    ) -> Union[dict, list]:
        response = self._request(RequestMethod.GET, url, query=query)
        return self._extract_data(response, expected)

    def post(
        self,
        url: str,
        json: Union[Mapping[str, Any], None] = None,
        expected: Type[Union[dict, list]] = dict,
    ) -> Union[dict, list]:
        response = self._request(RequestMethod.POST, url, json=json)
        return self._extract_data(response, expected)

    def put(
        self,
        url: str,
        json: Union[Mapping[str, Any], None] = None,
        expected: Type[Union[dict, list]] = dict,
    ) -> Union[dict, list]:
        response = self._request(RequestMethod.PUT, url, json=json)
        return self._extract_data(response, expected)

    def delete(
        self,
        url: str,
        json: Union[Mapping[str, Any], None] = None,
        expected: Type[Union[dict, list]] = dict,
    ) -> Union[dict, list]:
        response = self._request(RequestMethod.DELETE, url, json=json)
        return self._extract_data(response, expected)

    def patch(
        self,
        url: str,
        json: Union[Mapping[str, Any], None] = None,
        expected: Type[Union[dict, list]] = dict,
    ) -> Union[dict, list]:
        response = self._request(RequestMethod.PATCH, url, json=json)
        return self._extract_data(response, expected)
