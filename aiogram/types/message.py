import typing

from aiogram.utils import helper
from aiogram.utils.exceptions import TelegramAPIError
from . import base
from . import fields
from .audio import Audio
from .chat import Chat
from .contact import Contact
from .document import Document
from .game import Game
from .invoice import Invoice
from .location import Location
from .message_entity import MessageEntity
from .photo_size import PhotoSize
from .sticker import Sticker
from .successful_payment import SuccessfulPayment
from .user import User
from .venue import Venue
from .video import Video
from .video_note import VideoNote
from .voice import Voice


class Message(base.TelegramObject):
    """
    This object represents a message.

    https://core.telegram.org/bots/api#message
    """
    message_id: base.Integer = fields.Field()
    from_user: User = fields.Field(alias='from', base=User)
    date: base.Integer = fields.Field()
    chat: Chat = fields.Field(base=Chat)
    forward_from: User = fields.Field(base=User)
    forward_from_chat: Chat = fields.Field(base=Chat)
    forward_from_message_id: base.Integer = fields.Field()
    forward_signature: base.String = fields.Field()
    forward_date: base.Integer = fields.Field()
    reply_to_message: 'Message' = fields.Field(base='Message')
    edit_date: base.Integer = fields.Field()
    author_signature: base.String = fields.Field()
    text: base.String = fields.Field()
    entities: typing.List[MessageEntity] = fields.ListField(base=MessageEntity)
    audio: Audio = fields.Field(base=Audio)
    document: Document = fields.Field(base=Document)
    game: Game = fields.Field(base=Game)
    photo: typing.List[PhotoSize] = fields.ListField(base=PhotoSize)
    sticker: Sticker = fields.Field(base=Sticker)
    video: Video = fields.Field(base=Video)
    voice: Voice = fields.Field(base=Voice)
    video_note: VideoNote = fields.Field(base=VideoNote)
    caption: base.String = fields.Field()
    contact: Contact = fields.Field(base=Contact)
    location: Location = fields.Field(base=Location)
    venue: Venue = fields.Field(base=Venue)
    new_chat_members: typing.List[User] = fields.ListField(base=User)
    left_chat_member: User = fields.Field(base=User)
    new_chat_title: base.String = fields.Field()
    new_chat_photo: typing.List[PhotoSize] = fields.ListField(base=PhotoSize)
    delete_chat_photo: base.Boolean = fields.Field()
    group_chat_created: base.Boolean = fields.Field()
    supergroup_chat_created: base.Boolean = fields.Field()
    channel_chat_created: base.Boolean = fields.Field()
    migrate_to_chat_id: base.Integer = fields.Field()
    migrate_from_chat_id: base.Integer = fields.Field()
    pinned_message: 'Message' = fields.Field(base='Message')
    invoice: Invoice = fields.Field(base=Invoice)
    successful_payment: SuccessfulPayment = fields.Field(base=SuccessfulPayment)

    @property
    def content_type(self):
        if self.text:
            return ContentType.TEXT[0]
        elif self.audio:
            return ContentType.AUDIO[0]
        elif self.document:
            return ContentType.DOCUMENT[0]
        elif self.game:
            return ContentType.GAME[0]
        elif self.photo:
            return ContentType.PHOTO[0]
        elif self.sticker:
            return ContentType.STICKER[0]
        elif self.video:
            return ContentType.VIDEO[0]
        elif self.voice:
            return ContentType.VOICE[0]
        elif self.new_chat_members:
            return ContentType.NEW_CHAT_MEMBERS[0]
        elif self.left_chat_member:
            return ContentType.LEFT_CHAT_MEMBER[0]
        elif self.invoice:
            return ContentType.INVOICE[0]
        elif self.successful_payment:
            return ContentType.SUCCESSFUL_PAYMENT[0]
        else:
            return ContentType.UNKNOWN[0]

    def is_command(self):
        """
        Check message text is command
        :return: bool
        """
        return self.text and self.text.startswith('/')

    def get_full_command(self):
        """
        Split command and args
        :return: tuple of (command, args)
        """
        if self.is_command():
            command, _, args = self.text.partition(' ')
            return command, args

    def get_command(self):
        command = self.get_full_command()
        if command:
            return command[0]

    def get_args(self):
        command = self.get_full_command()
        if command:
            return command[1].strip()

    @property
    def md_text(self):
        text = self.text

        if self.text and self.entities:
            for entity in reversed(self.entities):
                text = entity.apply_md(text)

        return text

    @property
    def html_text(self):
        text = self.text

        if self.text and self.entities:
            for entity in reversed(self.entities):
                text = entity.apply_html(text)

        return text

    async def reply(self, text, parse_mode=None, disable_web_page_preview=None,
                    disable_notification=None, reply_markup=None) -> 'Message':
        """
        Reply to this message

        :param text: str
        :param parse_mode: str
        :param disable_web_page_preview: bool
        :param disable_notification: bool
        :param reply_markup:
        :return: :class:`aoigram.types.Message`
        """
        return await self.bot.send_message(self.chat.id, text, parse_mode, disable_web_page_preview,
                                           disable_notification, self.message_id, reply_markup)

    async def forward(self, chat_id, disable_notification=None) -> 'Message':
        """
        Forward this message

        :param chat_id:
        :param disable_notification:
        :return:
        """
        return await self.bot.forward_message(chat_id, self.chat.id, self.message_id, disable_notification)

    async def delete(self):
        """
        Delete this message

        :return: bool
        """
        return await self.bot.delete_message(self.chat.id, self.message_id)

    async def pin(self, disable_notification: bool = False):
        return await self.chat.pin_message(self.message_id, disable_notification)


class ContentType(helper.Helper):
    """
    List of message content types

    :key: TEXT
    :key: AUDIO
    :key: DOCUMENT
    :key: GAME
    :key: PHOTO
    :key: STICKER
    :key: VIDEO
    :key: VOICE
    :key: NEW_CHAT_MEMBERS
    :key: LEFT_CHAT_MEMBER
    :key: INVOICE
    :key: SUCCESSFUL_PAYMENT
    :key: UNKNOWN
    """
    mode = helper.HelperMode.snake_case

    TEXT = helper.ListItem()  # text
    AUDIO = helper.ListItem()  # audio
    DOCUMENT = helper.ListItem()  # document
    GAME = helper.ListItem()  # game
    PHOTO = helper.ListItem()  # photo
    STICKER = helper.ListItem()  # sticker
    VIDEO = helper.ListItem()  # video
    VOICE = helper.ListItem()  # voice
    NEW_CHAT_MEMBERS = helper.ListItem()  # new_chat_members
    LEFT_CHAT_MEMBER = helper.ListItem()  # left_chat_member
    INVOICE = helper.ListItem()  # invoice
    SUCCESSFUL_PAYMENT = helper.ListItem()  # successful_payment

    UNKNOWN = 'unknown'


class ParseMode(helper.Helper):
    """
    Parse modes

    :key: MARKDOWN
    :key: HTML
    """

    mode = helper.HelperMode.lowercase

    MARKDOWN = helper.Item()
    HTML = helper.Item()
