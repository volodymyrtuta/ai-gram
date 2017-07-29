from .base import Deserializable
from .user import User
from ..utils import markdown
from ..utils.helper import Helper, Item, HelperMode


class MessageEntity(Deserializable):
    """
    This object represents one special entity in a text message. For example, hashtags, usernames, URLs, etc.
    
    https://core.telegram.org/bots/api#messageentity
    """

    def __init__(self, type, offset, length, url, user):
        self.type: str = type
        self.offset: int = offset
        self.length: int = length
        self.url: str = url
        self.user: User = user

    @classmethod
    def de_json(cls, raw_data):
        type = raw_data.get('type')
        offset = raw_data.get('offset')
        length = raw_data.get('length')
        url = raw_data.get('url')
        user = User.deserialize(raw_data.get('user'))

        return MessageEntity(type, offset, length, url, user)

    def _apply(self, text, func):
        return text[:self.offset] + \
               func(text[self.offset:self.offset + self.length]) + \
               text[self.offset + self.length:]

    def apply_md(self, text):
        if self.type == MessageEntityType.BOLD:
            return self._apply(text, markdown.bold)
        elif self.type == MessageEntityType.ITALIC:
            return self._apply(text, markdown.italic)
        elif self.type == MessageEntityType.PRE:
            return self._apply(text, markdown.pre)
        elif self.type == MessageEntityType.CODE:
            return self._apply(text, markdown.code)
        elif self.type == MessageEntityType.URL:
            return self._apply(text, lambda url: markdown.link(url, url))
        elif self.type == MessageEntityType.TEXT_LINK:
            return self._apply(text, lambda url: markdown.link(url, self.url))
        return text

    def apply_html(self, text):
        if self.type == MessageEntityType.BOLD:
            return self._apply(text, markdown.hbold)
        elif self.type == MessageEntityType.ITALIC:
            return self._apply(text, markdown.hitalic)
        elif self.type == MessageEntityType.PRE:
            return self._apply(text, markdown.hpre)
        elif self.type == MessageEntityType.CODE:
            return self._apply(text, markdown.hcode)
        elif self.type == MessageEntityType.URL:
            return self._apply(text, lambda url: markdown.hlink(url, url))
        elif self.type == MessageEntityType.TEXT_LINK:
            return self._apply(text, lambda url: markdown.hlink(url, self.url))
        return text


class MessageEntityType(Helper):
    """
    List of entity types
    
    :key: MENTION 
    :key: HASHTAG 
    :key: BOT_COMMAND 
    :key: URL 
    :key: EMAIL 
    :key: BOLD 
    :key: ITALIC 
    :key: CODE 
    :key: PRE 
    :key: TEXT_LINK 
    :key: TEXT_MENTION 
    """
    mode = HelperMode.lower_case

    MENTION = Item()  # mention - @username
    HASHTAG = Item()  # hashtag
    BOT_COMMAND = Item()  # bot_command
    URL = Item()  # url
    EMAIL = Item()  # email
    BOLD = Item()  # bold -  bold text
    ITALIC = Item()  # italic -  italic text
    CODE = Item()  # code -  monowidth string
    PRE = Item()  # pre -  monowidth block
    TEXT_LINK = Item()  # text_link -  for clickable text URLs
    TEXT_MENTION = Item()  # text_mention -  for users without usernames
