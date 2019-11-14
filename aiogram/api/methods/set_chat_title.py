from typing import Any, Dict, Union

from .base import Request, TelegramMethod


class SetChatTitle(TelegramMethod[bool]):
    """
    Use this method to change the title of a chat. Titles can't be changed for private chats. The bot must be an administrator in the chat for this to work and must have the appropriate admin rights. Returns True on success.

    Source: https://core.telegram.org/bots/api#setchattitle
    """

    __returning__ = bool

    chat_id: Union[int, str]
    """Unique identifier for the target chat or username of the target channel (in the format @channelusername)"""

    title: str
    """New chat title, 1-255 characters"""

    def build_request(self) -> Request:
        data: Dict[str, Any] = self.dict()

        return Request(method="setChatTitle", data=data)
