import datetime

from aiogram.exceptions import TelegramAPIError
from . import Deserializable
from .chat import Chat
from .message_entity import MessageEntity
from .user import User


class Message(Deserializable):
    def __init__(self, message_id, from_user, date, chat, forward_from, forward_from_chat,
                 forward_from_message_id, forward_date, reply_to_message, edit_date, text, entities, audio, document,
                 game, photo, sticker, video, voice, video_note, new_chat_members, caption, contact, location, venue,
                 new_chat_member, left_chat_member, new_chat_title, new_chat_photo, delete_chat_photo,
                 group_chat_created, supergroup_chat_created, channel_chat_created, migrate_to_chat_id,
                 migrate_from_chat_id, pinned_message, invoice, successful_payment, content_type):
        self.message_id: int = message_id
        self.from_user: User = from_user
        self.date: datetime.datetime = date
        self.chat: Chat = chat
        self.forward_from: User = forward_from
        self.forward_from_chat: Chat = forward_from_chat
        self.forward_from_message_id: int = forward_from_message_id
        self.forward_date: datetime.datetime = forward_date
        self.reply_to_message: Message = reply_to_message
        self.edit_date: datetime.datetime = edit_date
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
        self.new_chat_member = new_chat_member
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
    def _parse_date(cls, unix_time):
        return datetime.datetime.fromtimestamp(unix_time)

    @classmethod
    def _parse_user(cls, user):
        return User.de_json(user) if user else None

    @classmethod
    def _parse_chat(cls, chat):
        return Chat.de_json(chat) if chat else None

    @classmethod
    def _parse_message(cls, message):
        return Message.de_json(message) if message else None

    @classmethod
    def _parse_entities(cls, entities):
        return [MessageEntity.de_json(entity) for entity in entities] if entities else None

    @classmethod
    def de_json(cls, raw_data):
        raw_data = cls.check_json(raw_data)

        message_id = raw_data.get('message_id')
        from_user = cls._parse_user(raw_data.get('from'))
        date = cls._parse_date(raw_data.get('date', 0))
        chat = cls._parse_chat(raw_data.get('chat', {}))
        forward_from = cls._parse_user(raw_data.get('forward_from', {}))
        forward_from_chat = cls._parse_chat(raw_data.get('forward_from_chat', {}))
        forward_from_message_id = raw_data.get('forward_from_message_id')
        forward_date = cls._parse_date(raw_data.get('forward_date', 0))
        reply_to_message = cls._parse_message(raw_data.get('reply_to_message', {}))
        edit_date = cls._parse_date(raw_data.get('edit_date', 0))
        text = raw_data.get('text')
        entities = cls._parse_entities(raw_data.get('entities'))

        audio = raw_data.get('audio')
        document = raw_data.get('document')
        game = raw_data.get('game')
        photo = raw_data.get('photo')
        sticker = raw_data.get('sticker')
        video = raw_data.get('video')
        voice = raw_data.get('voice')
        video_note = raw_data.get('video_note')
        new_chat_members = raw_data.get('new_chat_members')
        caption = raw_data.get('caption')
        contact = raw_data.get('contact')
        location = raw_data.get('location')
        venue = raw_data.get('venue')
        new_chat_member = raw_data.get('new_chat_member')
        left_chat_member = raw_data.get('left_chat_member')
        new_chat_title = raw_data.get('new_chat_title')
        new_chat_photo = raw_data.get('new_chat_photo')
        delete_chat_photo = raw_data.get('delete_chat_photo')
        group_chat_created = raw_data.get('group_chat_created')
        supergroup_chat_created = raw_data.get('supergroup_chat_created')
        channel_chat_created = raw_data.get('channel_chat_created')
        migrate_to_chat_id = raw_data.get('migrate_to_chat_id')
        migrate_from_chat_id = raw_data.get('migrate_from_chat_id')
        pinned_message = raw_data.get('pinned_message')
        invoice = raw_data.get('invoice')
        successful_payment = raw_data.get('successful_payment')

        if text:
            content_type = ContentType.TEXT
        elif audio:
            content_type = ContentType.AUDIO
        elif document:
            content_type = ContentType.DOCUMENT
        elif game:
            content_type = ContentType.GAME
        elif photo:
            content_type = ContentType.PHOTO
        elif sticker:
            content_type = ContentType.STICKER
        elif video:
            content_type = ContentType.VIDEO
        elif voice:
            content_type = ContentType.VOICE
        elif new_chat_member or new_chat_members:
            content_type = ContentType.NEW_CHAT_MEMBERS
        elif left_chat_member:
            content_type = ContentType.LEFT_CHAT_MEMBER
        elif invoice:
            content_type = ContentType.INVOICE
        elif successful_payment:
            content_type = ContentType.SUCCESSFUL_PAYMENT
        else:
            content_type = ContentType.UNKNOWN

        return Message(message_id, from_user, date, chat, forward_from, forward_from_chat,
                       forward_from_message_id, forward_date, reply_to_message, edit_date, text, entities, audio,
                       document, game, photo, sticker, video, voice, video_note, new_chat_members, caption, contact,
                       location, venue, new_chat_member, left_chat_member, new_chat_title, new_chat_photo,
                       delete_chat_photo, group_chat_created, supergroup_chat_created, channel_chat_created,
                       migrate_to_chat_id, migrate_from_chat_id, pinned_message, invoice, successful_payment,
                       content_type)

    def is_command(self):
        return self.text and self.text.startswith('/')

    async def reply(self, text, parse_mode=None, disable_web_page_preview=None,
                    disable_notification=None, reply_markup=None) -> 'Message':
        return await self.bot.send_message(self.chat.id, text, parse_mode, disable_web_page_preview,
                                           disable_notification, self.message_id, reply_markup)

    async def delete(self):
        try:
            await self.bot.delete_message(self.chat.id, self.message_id)
        except TelegramAPIError:
            return False
        return True


class ContentType:
    TEXT = 'text'
    AUDIO = 'audio'
    DOCUMENT = 'document'
    GAME = 'game'
    PHOTO = 'photo'
    STICKER = 'sticker'
    VIDEO = 'video'
    VOICE = 'voice'
    NEW_CHAT_MEMBERS = 'new_chat_members'
    LEFT_CHAT_MEMBER = 'left_chat_member'
    INVOICE = 'invoice'
    SUCCESSFUL_PAYMENT = 'successful_payment'

    UNKNOWN = 'unknown'


class ParseMode:
    MARKDOWN = 'markdown'
    HTML = 'html'
