from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Type

from pydantic import ValidationError

from ..filters.base import BaseFilter
from .handler import CallbackType, FilterObject, FilterType, HandlerObject

if TYPE_CHECKING:
    from aiogram.dispatcher.router import Router


class SkipHandler(Exception):
    pass


class EventObserver:
    """
    Base events observer
    """

    def __init__(self):
        self.handlers: List[HandlerObject] = []

    def register(self, callback: CallbackType, *filters: FilterType):
        """
        Register callback with filters

        :param callback:
        :param filters:
        :return:
        """
        self.handlers.append(
            HandlerObject(
                callback=callback, filters=[FilterObject(filter_) for filter_ in filters]
            )
        )

    async def trigger(self, *args, **kwargs):
        for handler in self.handlers:
            result, data = await handler.check(*args, **kwargs)
            if result:
                try:
                    yield await handler.call(*args, **data)
                except SkipHandler:
                    continue

    def __call__(self, *args: FilterType):
        def wrapper(callback: CallbackType):
            self.register(callback, *args)
            return callback

        return wrapper


class TelegramEventObserver(EventObserver):
    """
    Event observer for Telegram events
    """

    def __init__(self, router: Router, event_name: str):
        super().__init__()

        self.router: Router = router
        self.event_name: str = event_name
        self.filters: List[Type[BaseFilter]] = []

    def bind_filter(self, bound_filter: Type[BaseFilter]) -> None:
        if not isinstance(bound_filter, BaseFilter):
            pass
        self.filters.append(bound_filter)

    def _resolve_filters_chain(self):
        registry: List[FilterType] = []
        routers: List[Router] = []

        router = self.router
        while router and router not in routers:
            observer = router.observers[self.event_name]
            routers.append(router)
            router = router.parent_router

            for filter_ in observer.filters:
                if filter_ in registry:
                    continue
                yield filter_
                registry.append(filter_)

    def register(self, callback: CallbackType, *filters: FilterType, **bound_filters):
        resolved_filters = self.resolve_filters(bound_filters)
        return super().register(callback, *filters, *resolved_filters)

    async def trigger(self, *args, **kwargs):
        async for result in super(TelegramEventObserver, self).trigger(*args, **kwargs):
            yield result
            break

    def resolve_filters(self, full_config: Dict[str, Any]) -> List[BaseFilter]:
        filters: List[BaseFilter] = []
        if not full_config:
            return filters

        for bound_filter in self._resolve_filters_chain():
            # Try to initialize filter.
            try:
                f = bound_filter(**full_config)
            except ValidationError:
                continue

            # Clean full config to prevent to re-initialize another filter with the same configuration
            for key in f.__fields__:
                full_config.pop(key)

            filters.append(f)

        if full_config:
            raise ValueError(f"Unknown filters: {set(full_config.keys())}")

        return filters

    def __call__(self, *args: FilterType, **bound_filters):
        def wrapper(callback: CallbackType):
            self.register(callback, *args, **bound_filters)
            return callback

        return wrapper
