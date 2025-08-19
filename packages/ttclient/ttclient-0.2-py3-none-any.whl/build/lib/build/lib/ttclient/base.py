import logging
from collections.abc import Awaitable
from contextlib import suppress
from typing import Any

import httpx

from .exceptions import (InputDataError, MethodError, NoAccessError,
                         NotFoundError, RedirectError, ServerError,
                         TooManyRequestsError, UnauthorizedError)


class BaseClient:
    __secret__: str = ''
    host: str = ''
    log: logging.Logger = logging.getLogger('ttclient')

    def __init__(self, secret: str, host: str) -> None:
        self.__secret__ = secret
        self.host = f'https://{host}'

    def __repr__(self) -> str:
        return f'Client [{self.host}]' + (' with ' if self.__secret__ else ' no ') + 'secret'

    def http_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(headers={'X-APIToken': self.__secret__})

    async def api_call(self, method: str, uri: str, **data: Any) -> dict:
        async with self.http_client() as client:
            result = {}

            if method in {'POST', 'PUT'}:
                resp = await client.request(method, f'{self.host}{uri}', json=data or {})
            else:
                resp = await client.request(method, f'{self.host}{uri}', params=data or {})

            self.log.info('CALL API %s %s: %s', method, uri, resp.status_code)

            with suppress(Exception):
                result = resp.json()

            match resp.status_code:
                case 400:
                    raise InputDataError(method, uri, data, result, resp.status_code)
                case 401:
                    raise UnauthorizedError(method, uri, data, result, resp.status_code)
                case 403:
                    raise NoAccessError(method, uri, data, result, resp.status_code)
                case 404:
                    raise NotFoundError(method, uri, data, result, resp.status_code)
                case 405:
                    raise MethodError(method, uri, data, result, resp.status_code)
                case 429:
                    raise TooManyRequestsError(method, uri, data, result, resp.status_code)
                case 301 | 302:
                    raise RedirectError(method, uri, data, result, resp.status_code)
                case 500 | 502 | 503 | 504:
                    raise ServerError(method, uri, data, result, resp.status_code)

            return result

    def __call__(self, method: str, uri: str, *uri_args: int | str, **data: Any) -> Awaitable[dict]:
        return self.api_call(method, uri.format(*uri_args), **data)

    def get(self, uri: str, *uri_args: int | str, **data: Any) -> Awaitable[dict]:
        return self.api_call('GET', uri.format(*uri_args), **data)

    def post(self, uri: str, *uri_args: int | str, **data: Any) -> Awaitable[dict]:
        return self.api_call('POST', uri.format(*uri_args), **data)

    def put(self, uri: str, *uri_args: int | str, **data: Any) -> Awaitable[dict]:
        return self.api_call('PUT', uri.format(*uri_args), **data)

    def delete(self, uri: str, *uri_args: int | str, **data: Any) -> Awaitable[dict]:
        return self.api_call('DELETE', uri.format(*uri_args), **data)
