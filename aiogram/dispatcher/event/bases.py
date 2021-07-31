from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, NoReturn, Optional, Union
from unittest.mock import sentinel

from ...types import TelegramObject
from ..middlewares.base import BaseMiddleware

NextMiddlewareType = Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]]
MiddlewareType = Union[
    BaseMiddleware, Callable[[NextMiddlewareType, TelegramObject, Dict[str, Any]], Awaitable[Any]]
]

UNHANDLED = sentinel.UNHANDLED
REJECTED = sentinel.REJECTED


class SkipHandler(Exception):
    pass


class CancelHandler(Exception):
    pass


def skip(message: Optional[str] = None) -> NoReturn:
    """
    Raise an SkipHandler
    """
    raise SkipHandler(message or "Event skipped")
