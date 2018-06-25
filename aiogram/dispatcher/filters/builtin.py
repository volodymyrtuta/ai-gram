import re
import typing
from _contextvars import ContextVar

from aiogram import types
from aiogram.dispatcher.filters.filters import BaseFilter
from aiogram.types import CallbackQuery, ContentType, Message


class CommandsFilter(BaseFilter):
    """
    Check commands in message
    """
    key = 'commands'

    def __init__(self, dispatcher, commands):
        super().__init__(dispatcher)
        self.commands = commands

    async def check(self, message):
        if not message.is_command():
            return False

        command = message.text.split()[0][1:]
        command, _, mention = command.partition('@')

        if mention and mention != (await message.bot.me).username:
            return False

        if command not in self.commands:
            return False

        return True


class RegexpFilter(BaseFilter):
    """
    Regexp filter for messages and callback query
    """
    key = 'regexp'

    def __init__(self, dispatcher, regexp):
        super().__init__(dispatcher)
        self.regexp = re.compile(regexp, flags=re.IGNORECASE | re.MULTILINE)

    async def check(self, obj):
        if isinstance(obj, Message):
            if obj.text:
                match = self.regexp.search(obj.text)
            elif obj.caption:
                match = self.regexp.search(obj.caption)
            else:
                return False
        elif isinstance(obj, CallbackQuery) and obj.data:
            match = self.regexp.search(obj.data)
        else:
            return False

        if match:
            return {'regexp': match}
        return False


class RegexpCommandsFilter(BaseFilter):
    """
    Check commands by regexp in message
    """

    key = 'regexp_commands'

    def __init__(self, dispatcher, regexp_commands):
        super().__init__(dispatcher)
        self.regexp_commands = [re.compile(command, flags=re.IGNORECASE | re.MULTILINE) for command in regexp_commands]

    async def check(self, message):
        if not message.is_command():
            return False

        command = message.text.split()[0][1:]
        command, _, mention = command.partition('@')

        if mention and mention != (await message.bot.me).username:
            return False

        for command in self.regexp_commands:
            search = command.search(message.text)
            if search:
                return {'regexp_command': search}
        return False


class ContentTypeFilter(BaseFilter):
    """
    Check message content type
    """

    key = 'content_types'

    def __init__(self, dispatcher, content_types):
        super().__init__(dispatcher)
        self.content_types = content_types

    @classmethod
    def validate(cls, full_config: typing.Dict[str, typing.Any]):
        result = super(ContentTypeFilter, cls).validate(full_config)
        if not result:
            return {cls.key: types.ContentType.TEXT}

    async def check(self, message):
        return ContentType.ANY[0] in self.content_types or \
               message.content_type in self.content_types


class StateFilter(BaseFilter):
    """
    Check user state
    """
    key = 'state'

    ctx_state = ContextVar('user_state')

    def __init__(self, dispatcher, state):
        super().__init__(dispatcher)
        if isinstance(state, str) or state is None:
            state = (state,)
        self.state = state

    def get_target(self, obj):
        return getattr(getattr(obj, 'chat', None), 'id', None), getattr(getattr(obj, 'from_user', None), 'id', None)

    @classmethod
    def validate(cls, full_config: typing.Dict[str, typing.Any]):
        result = super(StateFilter, cls).validate(full_config)
        if not result:
            return {cls.key: None}

    async def check(self, obj):
        if '*' in self.state:
            return {'state': self.dispatcher.current_state()}

        try:
            state = self.ctx_state.get()
        except LookupError:
            chat, user = self.get_target(obj)

            if chat or user:
                state = await self.dispatcher.storage.get_state(chat=chat, user=user)
                self.ctx_state.set(state)
                if state in self.state:
                    return {'state': self.dispatcher.current_state(), 'raw_state': state}

        else:
            if state in self.state:
                return {'state': self.dispatcher.current_state(), 'raw_state': state}

        return False


class ExceptionsFilter(BaseFilter):
    """
    Filter for exceptions
    """

    key = 'exception'

    def __init__(self, dispatcher, exception):
        super().__init__(dispatcher)
        self.exception = exception

    async def check(self, dispatcher, update, exception):
        try:
            raise exception
        except self.exception:
            return True
        except:
            return False
