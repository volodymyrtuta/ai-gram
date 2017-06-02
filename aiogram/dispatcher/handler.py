from asyncio import Event

from aiogram import types
from .filters import check_filters


class Handler:
    def __init__(self, dispatcher, once=True):
        self.dispatcher = dispatcher
        self.once = once

        self.handlers = []

    def register(self, handler, filters=None):
        if filters and not isinstance(filters, (list, tuple, set)):
            filters = [filters]
        self.handlers.append((filters, handler))

    def unregister(self, handler):
        for handler_with_filters in self.handlers:
            _, registered = handler_with_filters
            if handler is registered:
                self.handlers.remove(handler_with_filters)
                return True
        raise ValueError('This handler is not registered!')

    async def notify(self, *args, **kwargs):
        for filters, handler in self.handlers:
            if await check_filters(filters, args, kwargs):
                await handler(*args, **kwargs)
                if self.once:
                    break


class NextStepHandler:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.handlers = {}

    def register(self, message, otherwise=None, once=False, filters=None):
        identifier = gen_identifier(message.chat.id, message.chat.id)

        if identifier not in self.handlers:
            self.handlers[identifier] = {'event': Event(), 'filters': filters,
                                         'otherwise': otherwise, 'once': once}
            return True
        raise RuntimeError('Dialog already wait message.')
        # return False

    async def notify(self, message):
        identifier = gen_identifier(message.chat.id, message.chat.id)
        if identifier not in self.handlers:
            return False
        handler = self.handlers[identifier]
        if handler['filters'] and not await check_filters(handler['filters'], [message], {}):
            otherwise = handler['otherwise']
            if otherwise:
                await otherwise(message)
            if not handler['once']:
                return False
        handler['message'] = message
        handler['event'].set()
        return True

    async def wait(self, message) -> types.Message:
        identifier = gen_identifier(message.chat.id, message.chat.id)

        handler = self.handlers[identifier]
        event = handler.get('event')

        await event.wait()
        message = self.handlers[identifier]['message']
        self.reset(identifier)
        return message

    def reset(self, identifier):
        del self.handlers[identifier]


def gen_identifier(chat_id, from_user_id):
    return f"{chat_id}:{from_user_id}"
