import asyncio
import logging

from aiogram.utils.deprecated import deprecated
from .filters import CommandsFilter, RegexpFilter, ContentTypeFilter, generate_default_filters
from .handler import Handler, NextStepHandler
from .. import types
from ..bot import Bot
from ..types.message import ContentType

log = logging.getLogger(__name__)


# TODO: Fix functions (functools.wraps(func))

class Dispatcher:
    """
    Simple Updates dispatcher

    It will be can process incoming updates, messages, edited messages, channel posts, edited channels posts,
    inline query, chosen inline result, callback query, shipping query, pre-checkout query.
    Provide next step handler and etc.
    """

    def __init__(self, bot, loop=None):
        self.bot: 'Bot' = bot
        if loop is None:
            loop = self.bot.loop

        self.loop = loop

        self.last_update_id = 0

        self.updates_handler = Handler(self)
        self.message_handlers = Handler(self)
        self.edited_message_handlers = Handler(self)
        self.channel_post_handlers = Handler(self)
        self.edited_channel_post_handlers = Handler(self)
        self.inline_query_handlers = Handler(self)
        self.chosen_inline_result_handlers = Handler(self)
        self.callback_query_handlers = Handler(self)
        self.shipping_query_handlers = Handler(self)
        self.pre_checkout_query_handlers = Handler(self)

        self.next_step_message_handlers = NextStepHandler(self)
        self.updates_handler.register(self.process_update)
        # self.message_handlers.register(self._notify_next_message)

        self._pooling = False

    def __del__(self):
        self._pooling = False

    async def skip_updates(self):
        """
        You can skip old incoming updates from queue.
        This method is not recomended to use if you use payments or you bot has high-load.

        :return: count of skipped updates
        """
        total = 0
        updates = await self.bot.get_updates(offset=self.last_update_id, timeout=1)
        while updates:
            total += len(updates)
            for update in updates:
                if update.update_id > self.last_update_id:
                    self.last_update_id = update.update_id
            updates = await self.bot.get_updates(offset=self.last_update_id + 1, timeout=1)
        return total

    async def process_updates(self, updates):
        """
        Process list of updates

        :param updates:
        :return:
        """
        for update in updates:
            self.loop.create_task(self.updates_handler.notify(update))

    async def process_update(self, update):
        """
        Process single update object

        :param update:
        :return:
        """
        self.last_update_id = update.update_id
        if update.message:
            if not await self.next_step_message_handlers.notify(update.message):
                await self.message_handlers.notify(update.message)
        if update.edited_message:
            await self.edited_message_handlers.notify(update.edited_message)
        if update.channel_post:
            await self.channel_post_handlers.notify(update.channel_post)
        if update.edited_channel_post:
            await self.edited_channel_post_handlers.notify(update.edited_channel_post)
        if update.inline_query:
            await self.inline_query_handlers.notify(update.inline_query)
        if update.chosen_inline_result:
            await self.chosen_inline_result_handlers.notify(update.chosen_inline_result)
        if update.callback_query:
            await self.callback_query_handlers.notify(update.callback_query)
        if update.shipping_query:
            await self.shipping_query_handlers.notify(update.shipping_query)
        if update.pre_checkout_query:
            await self.pre_checkout_query_handlers.notify(update.pre_checkout_query)

    async def start_pooling(self, timeout=20, relax=0.1):
        """
        Start long-pooling

        :param timeout:
        :param relax:
        :return:
        """
        if self._pooling:
            raise RuntimeError('Pooling already started')
        log.info('Start pooling.')

        self._pooling = True
        offset = None
        while self._pooling:
            try:
                updates = await self.bot.get_updates(offset=offset, timeout=timeout)
            except Exception as e:
                log.exception('Cause exception while getting updates')
                await asyncio.sleep(relax)
                continue

            if updates:
                log.info("Received {0} updates.".format(len(updates)))
                offset = updates[-1].update_id + 1
                await self.process_updates(updates)

            await asyncio.sleep(relax)

        log.warning('Pooling is stopped.')

    def stop_pooling(self):
        """
        Break long-pooling process.
        :return:
        """
        self._pooling = False

    def message_handler(self, commands=None, regexp=None, content_types=None, func=None, custom_filters=None, **kwargs):
        """
        Decorator for messages handler

        Examples:

        Simple commands handler:
        .. code-block:: python3
            @dp.messages_handler(commands=['start', 'welcome', 'about'])
            async def cmd_handler(message: types.Message):

        Filter messages by regular expression:
        .. code-block:: python3
            @dp.messages_handler(rexexp='^[a-z]+-[0-9]+')
            async def msg_handler(message: types.Message):

        Filter by content type:
        .. code-block:: python3
            @dp.messages_handler(content_types=ContentType.PHOTO | ContentType.DOCUMENT)
            async def audio_handler(message: types.Message):

        Filter by custom function:
        .. code-block:: python3
            @dp.messages_handler(func=lambda message: message.text and 'hello' in message.text.lower())
            async def text_handler(message: types.Message):

        Use multiple filters:
        .. code-block:: python3
            @dp.messages_handler(commands=['command'], content_types=ContentType.TEXT)
            async def text_handler(message: types.Message):

        Register multiple filters set for one handler:
        .. code-block:: python3
        p.messages_handler(commands=['command'])
            @dp.messages_handler(func=lambda message: demojize(message.text) == ':new_moon_with_face:')
            async def text_handler(message: types.Message):
        This handler will be called if the message starts with '/command' OR is some emoji

        By default content_type is :class:`ContentType.TEXT`

        :param commands: list of commands
        :param regexp: REGEXP
        :param content_types: List of content types.
        :param func: custom any callable object
        :param custom_filters: list of custom filters
        :param kwargs:
        :return: decorated function
        """
        if commands is None:
            commands = []
        if content_types is None:
            content_types = ContentType.TEXT
        if custom_filters is None:
            custom_filters = []

        filters_set = generate_default_filters(*custom_filters,
                                               commands=commands,
                                               regexp=regexp,
                                               content_types=content_types,
                                               func=func,
                                               **kwargs)

        def decorator(handler):
            self.message_handlers.register(handler, filters_set)
            return handler

        return decorator

    def edited_message_handler(self, commands=None, regexp=None, content_types=None, func=None, custom_filters=None,
                               **kwargs):
        """
        Analog of message_handler but only for edited messages

        You can use combination of different handlers
        .. code-block:: python3
        @dp.message_handler()
        @dp.edited_message_handler()
        async def msg_handler(message: types.Message):

        :param commands: list of commands
        :param regexp: REGEXP
        :param content_types: List of content types.
        :param func: custom any callable object
        :param custom_filters: list of custom filters
        :param kwargs:
        :return: decorated function
        """
        if commands is None:
            commands = []
        if content_types is None:
            content_types = ContentType.TEXT
        if custom_filters is None:
            custom_filters = []

        filters_set = generate_default_filters(*custom_filters,
                                               commands=commands,
                                               regexp=regexp,
                                               content_types=content_types,
                                               func=func,
                                               **kwargs)

        def decorator(handler):
            self.edited_message_handlers.register(handler, filters_set)
            return handler

        return decorator

    def channel_post_handler(self, commands=None, regexp=None, content_types=None, func=None, *custom_filters,
                             **kwargs):
        """
        Register channels posts handler

        :param commands: list of commands
        :param regexp: REGEXP
        :param content_types: List of content types.
        :param func: custom any callable object
        :param custom_filters: list of custom filters
        :param kwargs:
        :return: decorated function
        """
        if commands is None:
            commands = []
        if content_types is None:
            content_types = ContentType.TEXT
        if custom_filters is None:
            custom_filters = []

        filters_set = generate_default_filters(*custom_filters,
                                               commands=commands,
                                               regexp=regexp,
                                               content_types=content_types,
                                               func=func,
                                               **kwargs)

        def decorator(handler):
            self.channel_post_handlers.register(handler, filters_set)
            return handler

        return decorator

    def edited_channel_post_handler(self, commands=None, regexp=None, content_types=None, func=None, *custom_filters,
                                    **kwargs):
        """
        Register handler for edited channels posts

        :param commands: list of commands
        :param regexp: REGEXP
        :param content_types: List of content types.
        :param func: custom any callable object
        :param custom_filters: list of custom filters
        :param kwargs:
        :return: decorated function
        """
        if commands is None:
            commands = []
        if content_types is None:
            content_types = ContentType.TEXT
        if custom_filters is None:
            custom_filters = []

        filters_set = generate_default_filters(*custom_filters,
                                               commands=commands,
                                               regexp=regexp,
                                               content_types=content_types,
                                               func=func,
                                               **kwargs)

        def decorator(handler):
            self.edited_channel_post_handlers.register(handler, filters_set)
            return handler

        return decorator

    def inline_handler(self, func=None, *custom_filters, **kwargs):
        """
        Handle inline query

        Example:
        .. code-block:: python3
            @dp.inline_handler(func=lambda inline_query: True)
            async def handler(inline_query: types.InlineQuery)

        :param func: custom any callable object
        :param custom_filters: list of custom filters
        :param kwargs:
        :return: decorated function
        """
        if custom_filters is None:
            custom_filters = []
        filters_set = generate_default_filters(*custom_filters,
                                               func=func,
                                               **kwargs)

        def decorator(handler):
            self.inline_query_handlers.register(handler, filters_set)
            return handler

        return decorator

    def chosen_inline_handler(self, func=None, *custom_filters, **kwargs):
        """
        Register chosen inline handler

        Example:
        .. code-block:: python3
            @dp.chosen_inline_handler(func=lambda chosen_inline_query: True)
            async def handler(chosen_inline_query: types.ChosenInlineResult)

        :param func: custom any callable object
        :param custom_filters:
        :param kwargs:
        :return:
        """
        if custom_filters is None:
            custom_filters = []
        filters_set = generate_default_filters(*custom_filters,
                                               func=func,
                                               **kwargs)

        def decorator(handler):
            self.chosen_inline_result_handlers.register(handler, filters_set)
            return handler

        return decorator

    def callback_query_handler(self, func=None, *custom_filters, **kwargs):
        """
        Add callback query handler

        Example:
        .. code-block:: python3
            @dp.callback_query_handler(func=lambda callback_query: True)
            async def handler(callback_query: types.CallbackQuery)

        :param func: custom any callable object
        :param custom_filters:
        :param kwargs:
        """
        if custom_filters is None:
            custom_filters = []
        filters_set = generate_default_filters(*custom_filters,
                                               func=func,
                                               **kwargs)

        def decorator(handler):
            self.chosen_inline_result_handlers.register(handler, filters_set)
            return handler

        return decorator

    def shipping_query_handler(self, func=None, *custom_filters, **kwargs):
        """
        Add shipping query handler

        Example:
        .. code-block:: python3
            @dp.shipping_query_handler(func=lambda shipping_query: True)
            async def handler(shipping_query: types.ShippingQuery)

        :param func: custom any callable object
        :param custom_filters:
        :param kwargs:
        """
        if custom_filters is None:
            custom_filters = []
        filters_set = generate_default_filters(*custom_filters,
                                               func=func,
                                               **kwargs)

        def decorator(handler):
            self.shipping_query_handlers.register(handler, filters_set)
            return handler

        return decorator

    def pre_checkout_query_handler(self, func=None, *custom_filters, **kwargs):
        """
        Add shipping query handler

        Example:
        .. code-block:: python3
            @dp.shipping_query_handler(func=lambda shipping_query: True)
            async def handler(shipping_query: types.ShippingQuery)

        :param func: custom any callable object
        :param custom_filters:
        :param kwargs:
        """
        if custom_filters is None:
            custom_filters = []
        filters_set = generate_default_filters(*custom_filters,
                                               func=func,
                                               **kwargs)

        def decorator(handler):
            self.pre_checkout_query_handlers.register(handler, filters_set)
            return handler

        return decorator

    @deprecated("Use FSM instead of next step message handler.")
    async def next_message(self, message: types.Message, otherwise=None, once=False, include_cancel=True,
                           regexp=None, content_types=None, func=None, custom_filters=None, **kwargs):
        if content_types is None:
            content_types = []
        if custom_filters is None:
            custom_filters = []

        filters_set = generate_default_filters(*custom_filters,
                                               regexp=regexp,
                                               content_types=content_types,
                                               func=func,
                                               **kwargs)
        self.next_step_message_handlers.register(message, otherwise, once, include_cancel, filters_set)
        return await self.next_step_message_handlers.wait(message)
