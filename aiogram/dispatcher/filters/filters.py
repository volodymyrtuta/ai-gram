import abc
import inspect
import typing

from ..handler import Handler
from ...types.base import TelegramObject
from ...utils.deprecated import deprecated


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
            or isinstance(filter_, (Filter, AbstractFilter)):
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
    if filters is not None:
        for filter_ in filters:
            f = await check_filter(filter_, args)
            if not f:
                return False
    return True


class FilterRecord:
    """
    Filters record for factory
    """

    def __init__(self, callback: typing.Callable,
                 validator: typing.Optional[typing.Callable] = None,
                 event_handlers: typing.Optional[typing.Iterable[Handler]] = None):
        self.callback = callback
        self.event_handlers = event_handlers
        if validator is not None:
            if not callable(validator):
                raise TypeError(f"validator must be callable, not {type(validator)}")
            self.resolver = validator
        elif issubclass(callback, AbstractFilter):
            self.resolver = callback.validate
        else:
            raise RuntimeError('validator is required!')

    def resolve(self, dispatcher, event_observer, full_config):
        if not self._check_event_handler(event_observer):
            return
        config = self.resolver(full_config)
        if config:
            return self.callback(dispatcher, **config)

    def _check_event_handler(self, event_handler) -> bool:
        if not self.event_handlers:
            return True
        return event_handler in self.event_handlers


class AbstractFilter(abc.ABC):
    """
    Abstract class for custom filters
    """

    key = None

    def __init__(self, dispatcher, **config):
        self.dispatcher = dispatcher
        self.config = config

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


class BaseFilter(AbstractFilter):
    """
    Abstract class for filters with default validator
    """

    @property
    @abc.abstractmethod
    def key(self):
        pass

    @classmethod
    def validate(cls, full_config: typing.Dict[str, typing.Any]) -> typing.Optional[typing.Dict[str, typing.Any]]:
        if cls.key is not None and cls.key in full_config:
            return {cls.key: full_config.pop(cls.key)}


class Filter(abc.ABC):
    """
    Base class for filters
    Subclasses of this class can't be used with FiltersFactory by default.

    (Backward capability)
    """

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def __call__(self, *args, **kwargs):
        return self.check(*args, **kwargs)

    @abc.abstractmethod
    def check(self, *args, **kwargs):
        pass


@deprecated
class AsyncFilter(Filter):
    """
    Base class for asynchronous filters
    """

    def __aiter__(self):
        return None

    def __await__(self):
        return self.check

    async def check(self, *args, **kwargs):
        pass
