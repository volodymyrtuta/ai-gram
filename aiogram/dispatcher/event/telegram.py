from __future__ import annotations

from inspect import isclass
from itertools import chain
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, List, Optional, Tuple, Type

from pydantic import ValidationError

from aiogram.dispatcher.middlewares.manager import MiddlewareManager

from ...exceptions import FiltersResolveError
from ...types import TelegramObject
from ..filters.base import BaseFilter
from .bases import REJECTED, UNHANDLED, MiddlewareType, SkipHandler
from .handler import CallbackType, FilterObject, FilterType, HandlerObject, HandlerType

if TYPE_CHECKING:
    from aiogram.dispatcher.router import Router


class TelegramEventObserver:
    """
    Event observer for Telegram events

    Here you can register handler with filters or bounded filters which can be used as keyword arguments instead of writing full references when you register new handlers.
    This observer will stops event propagation when first handler is pass.
    """

    def __init__(self, router: Router, event_name: str) -> None:
        self.router: Router = router
        self.event_name: str = event_name

        self.handlers: List[HandlerObject] = []
        self.filters: List[Type[BaseFilter]] = []

        self.middleware = MiddlewareManager()
        self.outer_middleware = MiddlewareManager()

        # Re-used filters check method from already implemented handler object
        # with dummy callback which never will be used
        self._handler = HandlerObject(callback=lambda: True, filters=[])

    def filter(self, *filters: FilterType, **bound_filters: Any) -> None:
        """
        Register filter for all handlers of this event observer

        :param filters: positional filters
        :param bound_filters: keyword filters
        """
        resolved_filters = self.resolve_filters(filters, bound_filters)
        if self._handler.filters is None:
            self._handler.filters = []
        self._handler.filters.extend(
            [FilterObject(filter_) for filter_ in chain(resolved_filters, filters)]
        )

    def bind_filter(self, bound_filter: Type[BaseFilter]) -> None:
        """
        Register filter class in factory

        :param bound_filter:
        """
        # TODO: This functionality should be deprecated in the future
        #  in due to bound filter has uncontrollable ordering and
        #  makes debugging process is harder that explicit using filters

        if not isclass(bound_filter) or not issubclass(bound_filter, BaseFilter):
            raise TypeError(
                "bound_filter() argument 'bound_filter' must be subclass of BaseFilter"
            )
        self.filters.append(bound_filter)

    def _resolve_filters_chain(self) -> Generator[Type[BaseFilter], None, None]:
        """
        Get all bounded filters from current observer and from the parents
        with the same event type without duplicates
        """
        registry: List[Type[BaseFilter]] = []

        for router in reversed(tuple(self.router.chain_head)):
            observer = router.observers[self.event_name]

            for filter_ in observer.filters:
                if filter_ in registry:
                    continue
                yield filter_
                registry.append(filter_)

    def _resolve_middlewares(self) -> List[MiddlewareType[TelegramObject]]:
        middlewares: List[MiddlewareType[TelegramObject]] = []
        for router in reversed(tuple(self.router.chain_head)):
            observer = router.observers[self.event_name]
            middlewares.extend(observer.middleware)

        return middlewares

    def resolve_filters(
        self,
        filters: Tuple[FilterType, ...],
        full_config: Dict[str, Any],
        ignore_default: bool = True,
    ) -> List[BaseFilter]:
        """
        Resolve keyword filters via filters factory

        :param filters: positional filters
        :param full_config: keyword arguments to initialize bounded filters for router/handler
        :param ignore_default: ignore to resolving filters with only default arguments that are not in full_config
        """
        bound_filters: List[BaseFilter] = []

        if ignore_default and not full_config:
            return bound_filters

        filter_types = set(type(f) for f in filters)

        validation_errors = []
        for bound_filter in self._resolve_filters_chain():
            # skip filter if filter was used as positional filter:
            if bound_filter in filter_types:
                continue

            # skip filter with no fields in full_config
            if ignore_default:
                full_config_keys = set(full_config.keys())
                filter_fields = set(bound_filter.__fields__.keys())

                if not full_config_keys.intersection(filter_fields):
                    continue

            # Try to initialize filter.
            try:
                f = bound_filter(**full_config)
            except ValidationError as e:
                validation_errors.append(e)
                continue

            # Clean full config to prevent to re-initialize another filter
            # with the same configuration
            for key in f.__fields__:
                full_config.pop(key, None)

            bound_filters.append(f)

        if full_config:
            possible_cases = []
            for error in validation_errors:
                for sum_error in error.errors():
                    if sum_error["loc"][0] in full_config:
                        possible_cases.append(error)
                        break

            raise FiltersResolveError(
                unresolved_fields=set(full_config.keys()), possible_cases=possible_cases
            )

        return bound_filters

    def register(
        self,
        callback: HandlerType,
        *filters: FilterType,
        flags: Optional[Dict[str, Any]] = None,
        **bound_filters: Any,
    ) -> HandlerType:
        """
        Register event handler
        """
        if flags is None:
            flags = {}
        resolved_filters = self.resolve_filters(filters, bound_filters, ignore_default=False)
        for resolved_filter in resolved_filters:
            resolved_filter.update_handler_flags(flags=flags)
        self.handlers.append(
            HandlerObject(
                callback=callback,
                filters=[FilterObject(filter_) for filter_ in chain(resolved_filters, filters)],
                flags=flags,
            )
        )
        return callback

    def wrap_outer_middleware(
        self, callback: Any, event: TelegramObject, data: Dict[str, Any]
    ) -> Any:
        wrapped_outer = self.middleware.wrap_middlewares(
            self.outer_middleware,
            callback,
        )
        return wrapped_outer(event, data)

    async def trigger(self, event: TelegramObject, **kwargs: Any) -> Any:
        """
        Propagate event to handlers and stops propagation on first match.
        Handler will be called when all its filters is pass.
        """
        # Check globally defined filters before any other handler will be checked
        result, data = await self._handler.check(event, **kwargs)
        if not result:
            return REJECTED
        kwargs.update(data)

        for handler in self.handlers:
            result, data = await handler.check(event, **kwargs)
            if result:
                kwargs.update(data, handler=handler)
                try:
                    wrapped_inner = self.outer_middleware.wrap_middlewares(
                        self._resolve_middlewares(),
                        handler.call,
                    )
                    return await wrapped_inner(event, kwargs)
                except SkipHandler:
                    continue

        return UNHANDLED

    def __call__(
        self, *args: FilterType, flags: Optional[Dict[str, Any]] = None, **bound_filters: Any
    ) -> Callable[[CallbackType], CallbackType]:
        """
        Decorator for registering event handlers
        """

        def wrapper(callback: CallbackType) -> CallbackType:
            self.register(callback, *args, flags=flags, **bound_filters)
            return callback

        return wrapper
