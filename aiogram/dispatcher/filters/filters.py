import abc
import inspect
import typing

from ..handler import Handler
from ...types.base import TelegramObject


class FilterNotPassed(Exception):
    pass


def wrap_async(func):
    async def async_wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    if inspect.isawaitable(func) \
            or inspect.iscoroutinefunction(func) \
            or isinstance(func, AbstractFilter):
        return func
    return async_wrapper


async def check_filter(filter_, args):
    """
    Helper for executing filter

    :param filter_:
    :param args:
    :return:
    """
    if not callable(filter_):
        raise TypeError('Filter must be callable and/or awaitable!')

    if inspect.isawaitable(filter_) \
            or inspect.iscoroutinefunction(filter_) \
            or isinstance(filter_, AbstractFilter):
        return await filter_(*args)
    else:
        return filter_(*args)


async def check_filters(filters, args):
    """
    Check list of filters

    :param filters:
    :param args:
    :return:
    """
    data = {}
    if filters is not None:
        for filter_ in filters:
            f = await check_filter(filter_, args)
            if not f:
                raise FilterNotPassed()
            elif isinstance(f, dict):
                data.update(f)
    return data


class FilterRecord:
    """
    Filters record for factory
    """

    def __init__(self, callback: typing.Callable,
                 validator: typing.Optional[typing.Callable] = None,
                 event_handlers: typing.Optional[typing.Iterable[Handler]] = None,
                 exclude_event_handlers: typing.Optional[typing.Iterable[Handler]] = None):
        if event_handlers and exclude_event_handlers:
            raise ValueError("'event_handlers' and 'exclude_event_handlers' arguments cannot be used together.")

        self.callback = callback
        self.event_handlers = event_handlers
        self.exclude_event_handlers = exclude_event_handlers

        if validator is not None:
            if not callable(validator):
                raise TypeError(f"validator must be callable, not {type(validator)}")
            self.resolver = validator
        elif issubclass(callback, AbstractFilter):
            self.resolver = callback.validate
        else:
            raise RuntimeError('validator is required!')

    def resolve(self, dispatcher, event_handler, full_config):
        if not self._check_event_handler(event_handler):
            return
        config = self.resolver(full_config)
        if config:
            for key in config:
                if key in full_config:
                    full_config.pop(key)

            return self.callback(dispatcher, **config)

    def _check_event_handler(self, event_handler) -> bool:
        if self.event_handlers:
            return event_handler in self.event_handlers
        elif self.exclude_event_handlers:
            return event_handler not in self.exclude_event_handlers
        return True


class AbstractFilter(abc.ABC):
    """
    Abstract class for custom filters
    """

    key = None

    @classmethod
    @abc.abstractmethod
    def validate(cls, full_config: typing.Dict[str, typing.Any]) -> typing.Optional[typing.Dict[str, typing.Any]]:
        """
        Validate and parse config

        :param full_config:
        :return: config
        """
        pass

    @abc.abstractmethod
    async def check(self, *args) -> bool:
        """
        Check object

        :param args:
        :return:
        """
        pass

    async def __call__(self, obj: TelegramObject) -> bool:
        return await self.check(obj)

    def __invert__(self):
        return NotFilter(self)

    def __and__(self, other):
        return AndFilter(self, other)

    def __or__(self, other):
        return OrFilter(self, other)


class BaseFilter(AbstractFilter):
    """
    Base class for filters with default validator
    """
    key = None
    required = False
    default = None

    def __init__(self, dispatcher, **config):
        self.dispatcher = dispatcher
        self.config = config

    @classmethod
    def validate(cls, full_config: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        if cls.key is not None:
            if cls.key in full_config:
                return {cls.key: full_config[cls.key]}
            elif cls.required:
                return {cls.key: cls.default}


class Filter(AbstractFilter):
    @classmethod
    def validate(cls, full_config: typing.Dict[str, typing.Any]) -> typing.Optional[typing.Dict[str, typing.Any]]:
        raise RuntimeError('This filter can\'t be passed as kwargs')


class NotFilter(Filter):
    def __init__(self, target):
        self.target = wrap_async(target)

    async def check(self, *args):
        return await self.target(*args)


class AndFilter(Filter):
    def __init__(self, target, target2):
        self.target = wrap_async(target)
        self.target2 = wrap_async(target2)

    async def check(self, *args):
        return (await self.target(*args)) and (await self.target2(*args))


class OrFilter(Filter):
    def __init__(self, target, target2):
        self.target = wrap_async(target)
        self.target2 = wrap_async(target2)

    async def check(self, *args):
        return (await self.target(*args)) or (await self.target2(*args))
