import asyncio
import random
import time
from itertools import chain
from typing import Any, ClassVar, Dict, Optional, Type

from aiohttp import ClientResponse, ClientSession, ClientTimeout, TCPConnector


class BaseInteractionError(Exception):
    default_message = 'Backend interaction error'

    def __init__(self, *, service, method, message=None):
        self.message = message or self.default_message
        self.service = service
        self.method = method

    @property
    def name(self):
        return self.__class__.__name__

    def __str__(self):
        return f'{self.__class__.__name__}({self.service}, {self.method}): {self.message}'


class InteractionResponseError(BaseInteractionError):
    default_message = 'Backend unexpected response'

    def __init__(
        self, *,
        status_code: int,
        method: str,
        service: str,
        message: Optional[str] = None,
        response_status: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ):
        """
        :param status_code: HTTP status code
        :param method: HTTP method
        :param response_status: статус ответа, который обычно приходит в JSON-теле ответа
            в ключе "status", например:
            >>> {"status": "failure", ... }
            >>> {"status": "success", ... }
        :param service: имя сервиса (просто строчка с человекочитаемым названием сервиса, в который делается запрос)
        :param params: какие-то структурированные параметры из тела ответа с ошибкой
        :param message: строка с сообщение об ошибке. в свободной форме
        """
        self.status_code = status_code
        self.response_status = response_status
        self.params = params
        super().__init__(service=service, method=method, message=message)

    def __str__(self):
        return (f'{self.__class__.__name__}({self.service}.{self.method}): '
                f'status={self.status_code} response_status={self.response_status} '
                f'params={self.params} {self.message}')


class AbstractInteractionClient:
    CONNECTOR: ClassVar[TCPConnector]

    REQUEST_TIMEOUT: ClassVar[Optional[float]] = None
    CONNECT_TIMEOUT: ClassVar[Optional[float]] = None

    SERVICE: ClassVar[str]
    BASE_URL: ClassVar[str]
    REQUEST_RETRY_TIMEOUTS = (0.1, 0.2, 0.4)

    _session: Optional[ClientSession] = None

    def __init__(self) -> None:
        self.default_timeout: Optional[ClientTimeout] = None
        if self.REQUEST_TIMEOUT:
            self.default_timeout = ClientTimeout(total=self.REQUEST_TIMEOUT, connect=self.CONNECT_TIMEOUT)

    def _get_session_cls(self) -> Type[ClientSession]:
        return ClientSession

    def _get_session_kwargs(self) -> Dict[str, Any]:
        """Returns kwargs necessary for creating a session instance."""
        kwargs = {
            'connector': self.CONNECTOR,
            'connector_owner': False,
            'trust_env': True,
        }
        if self.default_timeout:
            kwargs['timeout'] = self.default_timeout
        return kwargs

    @property
    def session(self) -> ClientSession:
        if self._session is None:
            self._session = self.create_session()
        return self._session

    def create_session(self) -> ClientSession:
        session_cls = self._get_session_cls()
        kwargs = self._get_session_kwargs()
        return session_cls(**kwargs)

    async def _handle_response_error(self, response: ClientResponse) -> None:
        raise InteractionResponseError(
            status_code=response.status,
            method=response.method,
            service=self.SERVICE,
            params=None,
        )

    async def _process_response(self, response: ClientResponse, interaction_method: str) -> Dict[str, Any]:
        if response.status >= 400:
            await self._handle_response_error(response)
        return await response.json()

    async def _make_request(
        self,
        interaction_method: str,
        method: str,
        url: str,
        **kwargs: Any
    ) -> ClientResponse:
        """Wraps ClientSession.request allowing retries, updating metrics."""

        kwargs.setdefault('headers', {})

        response_time = 0.0
        response = exc = None
        for retry_number, retry_delay in enumerate(chain((0.0,), self.REQUEST_RETRY_TIMEOUTS)):
            if retry_delay:
                delay = retry_delay - response_time
                await asyncio.sleep(delay + random.uniform(-delay / 2, delay / 2))

            exc = None
            response = None
            before = time.monotonic()
            try:
                response = await self.session.request(method, url, **kwargs)

                assert response is not None
                success = True
            except Exception as e:
                exc = e
                success = False

            response_time = time.monotonic() - before

            if success or isinstance(exc, asyncio.TimeoutError):
                break

        if exc:
            raise exc

        return response  # type: ignore

    async def _request(  # noqa: C901
        self,
        interaction_method: str,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:

        response = await self._make_request(interaction_method, method, url, **kwargs)
        processed = await self._process_response(response, interaction_method)

        return processed

    async def get(self, interaction_method: str, url: str, **kwargs: Any) -> Dict[str, Any]:
        return await self._request(interaction_method, 'GET', url, **kwargs)

    async def post(self, interaction_method: str, url: str, **kwargs: Any) -> Dict[str, Any]:
        return await self._request(interaction_method, 'POST', url, **kwargs)

    async def put(self, interaction_method: str, url: str, **kwargs: Any) -> Dict[str, Any]:
        return await self._request(interaction_method, 'PUT', url, **kwargs)

    async def patch(self, interaction_method: str, url: str, **kwargs: Any) -> Dict[str, Any]:
        return await self._request(interaction_method, 'PATCH', url, **kwargs)

    async def delete(self, interaction_method: str, url: str, **kwargs: Any) -> Dict[str, Any]:
        return await self._request(interaction_method, 'DELETE', url, **kwargs)

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    def endpoint_url(self, relative_url: str, base_url_override: Optional[str] = None) -> str:
        base_url = (base_url_override or self.BASE_URL).rstrip('/')
        relative_url = relative_url.lstrip('/')
        return f'{base_url}/{relative_url}'