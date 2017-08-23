import datetime

from .audio import Audio
from .base import Deserializable
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
from ..utils.exceptions import TelegramAPIError
from ..utils.helper import Item, HelperMode, Helper, ListItem


class Message(Deserializable):
    """
    This object represents a message.

    https://core.telegram.org/bots/api#message
    """

    def __init__(self, message_id, from_user, date, chat, forward_from, forward_from_chat, forward_from_message_id,
                 forward_signature, forward_date, reply_to_message, edit_date, author_signature, text, entities, audio,
                 document, game, photo, sticker, video, voice, video_note, new_chat_members, caption, contact, location,
                 venue, left_chat_member, new_chat_title, new_chat_photo, delete_chat_photo, group_chat_created,
                 supergroup_chat_created, channel_chat_created, migrate_to_chat_id, migrate_from_chat_id,
                 pinned_message, invoice, successful_payment, content_type):
        self.message_id: int = message_id
        self.from_user: User = from_user
        self.date: datetime.datetime = date
        self.chat: Chat = chat
        self.forward_from: User = forward_from
        self.forward_from_chat: Chat = forward_from_chat
        self.forward_from_message_id: int = forward_from_message_id
        self.forward_signature: str = forward_signature
        self.forward_date: datetime.datetime = forward_date
        self.reply_to_message: Message = reply_to_message
        self.edit_date: datetime.datetime = edit_date
        self.author_signature: str = author_signature
        self.text: str = text
        self.entities = entities
        self.audio = audio
        self.document = document
        self.game = game
        self.photo = photo
        self.sticker = sticker
        self.video = video
        self.voice = voice
        self.video_note = video_note
        self.new_chat_members = new_chat_members
        self.caption = caption
        self.contact = contact
        self.location = location
        self.venue = venue
        self.left_chat_member = left_chat_member
        self.new_chat_title = new_chat_title
        self.new_chat_photo = new_chat_photo
        self.delete_chat_photo = delete_chat_photo
        self.group_chat_created = group_chat_created
        self.supergroup_chat_created = supergroup_chat_created
        self.channel_chat_created = channel_chat_created
        self.migrate_to_chat_id = migrate_to_chat_id
        self.migrate_from_chat_id = migrate_from_chat_id
        self.pinned_message = pinned_message
        self.invoice = invoice
        self.successful_payment = successful_payment

        self.content_type = content_type

    @classmethod
    def de_json(cls, raw_data):
        message_id = raw_data.get('message_id')
        from_user = User.deserialize(raw_data.get('from'))
        date = cls._parse_date(raw_data.get('date', 0))
        chat = Chat.deserialize(raw_data.get('chat', {}))
        forward_from = User.deserialize(raw_data.get('forward_from', {}))
        forward_from_chat = Chat.deserialize(raw_data.get('forward_from_chat', {}))
        forward_from_message_id = raw_data.get('forward_from_message_id')
        forward_signature = raw_data.get('forward_signature')
        forward_date = cls._parse_date(raw_data.get('forward_date', 0))
        reply_to_message = Message.deserialize(raw_data.get('reply_to_message', {}))
        edit_date = cls._parse_date(raw_data.get('edit_date', 0))
        author_signature = raw_data.get('author_signature')
        text = raw_data.get('text')
        entities = MessageEntity.deserialize(raw_data.get('entities'))
        audio = Audio.deserialize(raw_data.get('audio'))
        document = Document.deserialize(raw_data.get('document'))
        game = Game.deserialize(raw_data.get('game'))
        photo = PhotoSize.deserialize(raw_data.get('photo'))
        sticker = Sticker.deserialize(raw_data.get('sticker'))
        video = Video.deserialize(raw_data.get('video'))
        voice = Voice.deserialize(raw_data.get('voice'))
        video_note = VideoNote.deserialize(raw_data.get('video_note'))
        new_chat_members = User.deserialize(raw_data.get('new_chat_members'))
        caption = raw_data.get('caption')
        contact = Contact.deserialize(raw_data.get('contact'))
        location = Location.deserialize(raw_data.get('location'))
        venue = Venue.deserialize(raw_data.get('venue'))
        left_chat_member = User.deserialize(raw_data.get('left_chat_member'))
        new_chat_title = raw_data.get('new_chat_title')
        new_chat_photo = raw_data.get('new_chat_photo')
        delete_chat_photo = PhotoSize.deserialize(raw_data.get('delete_chat_photo'))
        group_chat_created = raw_data.get('group_chat_created')
        supergroup_chat_created = raw_data.get('supergroup_chat_created')
        channel_chat_created = raw_data.get('channel_chat_created')
        migrate_to_chat_id = raw_data.get('migrate_to_chat_id')
        migrate_from_chat_id = raw_data.get('migrate_from_chat_id')
        pinned_message = Message.deserialize(raw_data.get('pinned_message'))
        invoice = Invoice.deserialize(raw_data.get('invoice'))
        successful_payment = SuccessfulPayment.deserialize(raw_data.get('successful_payment'))

        if text:
            content_type = ContentType.TEXT[0]
        elif audio:
            content_type = ContentType.AUDIO[0]
        elif document:
            content_type = ContentType.DOCUMENT[0]
        elif game:
            content_type = ContentType.GAME[0]
        elif photo:
            content_type = ContentType.PHOTO[0]
        elif sticker:
            content_type = ContentType.STICKER[0]
        elif video:
            content_type = ContentType.VIDEO[0]
        elif voice:
            content_type = ContentType.VOICE[0]
        elif new_chat_members:
            content_type = ContentType.NEW_CHAT_MEMBERS[0]
        elif left_chat_member:
            content_type = ContentType.LEFT_CHAT_MEMBER[0]
        elif invoice:
            content_type = ContentType.INVOICE[0]
        elif successful_payment:
            content_type = ContentType.SUCCESSFUL_PAYMENT[0]
        else:
            content_type = ContentType.UNKNOWN[0]

        return Message(message_id, from_user, date, chat, forward_from, forward_from_chat, forward_from_message_id,
                       forward_signature, forward_date, reply_to_message, edit_date, author_signature, text, entities,
                       audio, document, game, photo, sticker, video, voice, video_note, new_chat_members, caption,
                       contact, location, venue, left_chat_member, new_chat_title, new_chat_photo, delete_chat_photo,
                       group_chat_created, supergroup_chat_created, channel_chat_created, migrate_to_chat_id,
                       migrate_from_chat_id, pinned_message, invoice, successful_payment, content_type)

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
        try:
            await self.bot.delete_message(self.chat.id, self.message_id)
        except TelegramAPIError:
            return False
        return True

    async def pin(self, disable_notification: bool = False):
        return await self.chat.pin_message(self.message_id, disable_notification)


class ContentType(Helper):
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
    mode = HelperMode.snake_case

    TEXT = ListItem()  # text
    AUDIO = ListItem()  # audio
    DOCUMENT = ListItem()  # document
    GAME = ListItem()  # game
    PHOTO = ListItem()  # photo
    STICKER = ListItem()  # sticker
    VIDEO = ListItem()  # video
    VOICE = ListItem()  # voice
    NEW_CHAT_MEMBERS = ListItem()  # new_chat_members
    LEFT_CHAT_MEMBER = ListItem()  # left_chat_member
    INVOICE = ListItem()  # invoice
    SUCCESSFUL_PAYMENT = ListItem()  # successful_payment

    UNKNOWN = 'unknown'


class ParseMode(Helper):
    """
    Parse modes
    
    :key: MARKDOWN
    :key: HTML
    """

    mode = HelperMode.lowercase

    MARKDOWN = Item()
    HTML = Item()
