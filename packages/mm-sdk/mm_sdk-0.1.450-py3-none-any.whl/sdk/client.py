"""
    Typed http client with error handling.

    # >>> import logging, pydantic
    # >>> logging.basicConfig(level=logging.DEBUG)
    # >>> client = SDKClient(connection_timeout=10, io_timeout=10, silent=True)
    # >>> class UserAgent(pydantic.BaseModel):
    # ...     user_agent: str = pydantic.Field(None, alias='user-agent')
    # >>> response = client.get('http://httpbin.org/user-agent', UserAgent)
    # >>> response
    # SDKResponse[Union[List[sdk.client.UserAgent], UserAgent]](data=UserAgent(user_agent='mobil-sdk/0.0.1'), error=None)
    #
    # >>> response = client.get('http://httpbin.org/post', UserAgent)
    # >>> response
    # SDKResponse[str](data=None, error=Error(code=405, message='METHOD NOT ALLOWED', detail='<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\\n<title>405 Method Not Allowed</title>\\n<h1>Method Not Allowed</h1>\\n<p>The method is not allowed for the requested URL.</p>\\n'))

"""
import inspect
import json
import logging
import uuid

from http import HTTPStatus
from typing import (
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from httpx import Client, Response, Timeout
from pydantic import BaseModel, HttpUrl
from pydantic.generics import GenericModel

from sdk.base import BytesResponse


logger = logging.getLogger("sdk")


DataT = TypeVar("DataT")


class Error(BaseModel):
    code: int
    message: str
    detail: Optional[str] = None


class SDKResponse(GenericModel, Generic[DataT]):
    data: Optional[DataT]
    error: Optional[Error]


class Empty(BaseModel):
    pass


class SDKClient:
    def __init__(
        self,
        connection_timeout: Union[int, float] = None,  # seconds, required
        io_timeout: Union[int, float] = None,  # seconds, required
        client: Optional[Client] = None,
        headers: Union[Dict, Callable] = None,
        acceptable_status_codes: Sequence = (
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            HTTPStatus.ACCEPTED,
        ),
        silent: bool = True,
        content_slice_size: int = 256,
        is_django: bool = True,
    ):
        assert client is not None or io_timeout, "Please provide io_timeout explicitly"
        assert (
            client is not None or connection_timeout is not None
        ), "session or connection_timeout must be provided"

        self._connection_timeout = connection_timeout
        self._io_timeout = io_timeout
        self._headers = headers or {}
        self._acceptable_status_codes = acceptable_status_codes

        self._client = client or self.create_default_client(
            self._connection_timeout, self._io_timeout
        )
        self._silent = silent
        self._content_slice_size = content_slice_size
        self._is_django = is_django

    def __del__(self):
        self.close()

    @staticmethod
    def create_default_client(
        connection_timeout: Union[float, int, None], io_timeout: Union[float, int, None]
    ) -> Client:
        timeout = Timeout(io_timeout, connect=connection_timeout)
        return Client(
            headers={"user-agent": "mobil-sdk/0.0.1"}, timeout=timeout, verify=False
        )

    def _update_request_parameters(self, params: dict) -> dict:
        kwargs = params.copy()
        if callable(self._headers):
            default_headers = self._headers()
        else:
            default_headers = self._headers
        if "headers" in kwargs:
            new_headers = default_headers.copy()

            new_headers.update(kwargs["headers"])
            kwargs["headers"] = new_headers
        else:
            kwargs["headers"] = default_headers.copy()

        kwargs["headers"].update(self._prepare_request_id(kwargs["headers"]))
        kwargs.setdefault("timeout", self._io_timeout)

        return kwargs

    def _prepare_request_id(self, headers):
        if headers.get("X-Request-Id"):
            # already have one
            return {}
        if self._is_django:
            from .utils.django_request_id import get_request_id_header

            request_id_header = get_request_id_header()
            if request_id_header:
                return request_id_header
        return {"X-Request-Id": uuid.uuid4().hex}

    def request(
        self, method: str, url: HttpUrl, response_class: Type[BaseModel], **kwargs
    ) -> SDKResponse:
        try:
            params = self._update_request_parameters(kwargs)

            logger.info(
                "~~~> HTTP request method=%s, url=%s, params=%s",
                method,
                url,
                self._log_kwargs(params),
            )

            response = self._client.request(method, url, **params)

            logger.info(
                "<~~~ HTTP response status_code=%s, url=%s content=%s",
                response.status_code,
                response.url,
                response.content[: self._content_slice_size],
            )

        except Exception as ex:
            if not self._silent:
                raise

            logger.error(
                "<~~~ Request error: %s method: %s  url: %s  kwargs: %s",
                ex,
                method,
                url,
                self._log_kwargs(kwargs),
                exc_info=True,
            )
            return SDKResponse[str](
                error={
                    "code": ex.status_code  # type: ignore
                    if hasattr(ex, "status_code")
                    else HTTPStatus.INTERNAL_SERVER_ERROR,
                    "message": str(ex),
                }
            )

        if (
            self._acceptable_status_codes
            and response.status_code not in self._acceptable_status_codes
        ):
            if not self._silent:
                response.raise_for_status()
            logger.error(
                "<~~~ Unexpected status_code=%s received from %s url=%s kwargs: %s",
                response.status_code,
                method,
                url,
                self._log_kwargs(params),
                exc_info=True,
            )
            return SDKResponse[str](
                error={
                    "code": response.status_code,
                    "message": response.reason_phrase or "",
                    "detail": response.content
                    if hasattr(response, "content")
                    else None,
                }
            )

        return SDKResponse[Union[List[response_class], response_class]](
            data=self._to_sdk_response(response, response_class)
        )

    def _log_kwargs(self, params):
        log_params = params.copy()
        log_params.pop("headers", None)
        log_params.pop("files", None)
        return json.dumps(log_params, default=str)[: self._content_slice_size]

    @staticmethod
    def _to_sdk_response(
        response: Response, response_class: Type[BaseModel]
    ) -> Union[List[BaseModel], BaseModel]:
        if response_class == Empty:
            return None

        if inspect.isclass(response_class) and issubclass(
            response_class, BytesResponse
        ):
            return response_class(bytes=response.content)
        else:
            response_json = json.loads(response.content)
            if isinstance(response_json, list):
                if len(response_json) and isinstance(response_json[0], dict):
                    return [response_class(**x) for x in response_json]
                else:
                    return response_json
            else:
                return response_class(**response_json)

    def get(
        self, url, response_class: Union[Type[BaseModel], Type[List]], **kwargs
    ) -> SDKResponse:
        return self.request("GET", url, response_class, **kwargs)

    def post(self, url, response_class: Type[BaseModel], **kwargs) -> SDKResponse:
        return self.request("POST", url, response_class, **kwargs)

    def put(self, url, response_class: Type[BaseModel], **kwargs) -> SDKResponse:
        return self.request("PUT", url, response_class, **kwargs)

    def patch(self, url, response_class: Type[BaseModel], **kwargs) -> SDKResponse:
        return self.request("PATCH", url, response_class, **kwargs)

    def delete(self, url, response_class: Type[BaseModel], **kwargs) -> SDKResponse:
        return self.request("DELETE", url, response_class, **kwargs)

    def close(self):
        if hasattr(self, "_client"):
            self._client.close()


if __name__ == "__main__":
    from doctest import testmod

    testmod(verbose=False)
