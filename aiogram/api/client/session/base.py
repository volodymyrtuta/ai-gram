from __future__ import annotations

import abc
import datetime
import json
from types import TracebackType
from typing import Any, AsyncGenerator, Callable, Optional, Type, TypeVar, Union

from aiogram.utils.exceptions import TelegramAPIError

from ...methods import Response, TelegramMethod
from ..telegram import PRODUCTION, TelegramAPIServer

T = TypeVar("T")
_JSON_LOADS = Callable[..., Any]
_JSON_DUMPS = Callable[..., str]


class BaseSession(abc.ABC):
    _api: TelegramAPIServer
    _json_loads: _JSON_LOADS
    _json_dumps: _JSON_DUMPS

    @property
    def api(self) -> TelegramAPIServer:
        return getattr(self, "_api", PRODUCTION)  # type: ignore

    @api.setter
    def api(self, value: TelegramAPIServer) -> None:
        self._api = value

    @property
    def json_loads(self) -> _JSON_LOADS:
        return getattr(self, "_json_loads", json.loads)  # type: ignore

    @json_loads.setter
    def json_loads(self, value: _JSON_LOADS) -> None:
        self._json_loads = value  # type: ignore

    @property
    def json_dumps(self) -> _JSON_DUMPS:
        return getattr(self, "_json_dumps", json.dumps)  # type: ignore

    @json_dumps.setter
    def json_dumps(self, value: _JSON_DUMPS) -> None:
        self._json_dumps = value  # type: ignore

    @classmethod
    def raise_for_status(cls, response: Response[T]) -> None:
        if response.ok:
            return
        raise TelegramAPIError(response.description)

    @abc.abstractmethod
    async def close(self) -> None:  # pragma: no cover
        pass

    @abc.abstractmethod
    async def make_request(self, token: str, method: TelegramMethod[T]) -> T:  # pragma: no cover
        pass

    @abc.abstractmethod
    async def stream_content(
        self, url: str, timeout: int, chunk_size: int
    ) -> AsyncGenerator[bytes, None]:  # pragma: no cover
        yield b""

    def prepare_value(self, value: Any) -> Union[str, int, bool]:
        if isinstance(value, str):
            return value
        if isinstance(value, (list, dict)):
            return self.json_dumps(self.clean_json(value))
        if isinstance(value, datetime.timedelta):
            now = datetime.datetime.now()
            return str(round((now + value).timestamp()))
        if isinstance(value, datetime.datetime):
            return str(round(value.timestamp()))
        else:
            return str(value)

    def clean_json(self, value: Any) -> Any:
        if isinstance(value, list):
            return [self.clean_json(v) for v in value if v is not None]
        elif isinstance(value, dict):
            return {k: self.clean_json(v) for k, v in value.items() if v is not None}
        return value

    async def __aenter__(self) -> BaseSession:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.close()
