"""
TelegramAPIError
    ValidationError
    Throttled
    BadRequest
        MessageError
            MessageNotModified
            MessageToForwardNotFound
            MessageToDeleteNotFound
            MessageIdentifierNotSpecified
        ChatNotFound
        InvalidQueryID
        InvalidPeerID
        InvalidHTTPUrlContent
        WrongFileIdentifier
        GroupDeactivated
        BadWebhook
            WebhookRequireHTTPS
            BadWebhookPort
        CantParseUrl
        NotFound
            MethodNotKnown
        PhotoAsInputFileRequired
        ToMuchMessages
        InvalidStickersSet
        ChatAdminRequired
        PhotoDimensions
        UnavailableMembers
        TypeOfFileMismatch
    ConflictError
        TerminatedByOtherGetUpdates
        CantGetUpdates
    Unauthorized
        BotKicked
        BotBlocked
        UserDeactivated
        CantInitiateConversation
    NetworkError
    RetryAfter
    MigrateToChat

AIOGramWarning
    TimeoutWarning
"""
import time

_PREFIXES = ['Error: ', '[Error]: ', 'Bad Request: ', 'Conflict: ', 'Not Found: ']


def _clean_message(text):
    for prefix in _PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix):]
    return (text[0].upper() + text[1:]).strip()


class TelegramAPIError(Exception):
    def __init__(self, message=None):
        super(TelegramAPIError, self).__init__(_clean_message(message))


class _MatchErrorMixin:
    match = ''
    text = None

    __subclasses = []

    def __init_subclass__(cls, **kwargs):
        super(_MatchErrorMixin, cls).__init_subclass__(**kwargs)
        # cls.match = cls.match.lower() if cls.match else ''
        if not hasattr(cls, f"_{cls.__name__}__group"):
            cls.__subclasses.append(cls)

    @classmethod
    def check(cls, message) -> bool:
        """
        Compare pattern with message

        :param message: always must be in lowercase
        :return: bool
        """
        return cls.match.lower() in message

    @classmethod
    def throw(cls):
        """
        Throw a error

        :raise: this
        """
        raise cls(cls.text or cls.match)

    @classmethod
    def detect(cls, description):
        description = description.lower()
        for err in cls.__subclasses:
            if err is cls:
                continue
            if err.check(description):
                err.throw()
        raise cls(description)


class AIOGramWarning(Warning):
    pass


class TimeoutWarning(AIOGramWarning):
    pass


class FSMStorageWarning(AIOGramWarning):
    pass


class ValidationError(TelegramAPIError):
    pass


class BadRequest(TelegramAPIError, _MatchErrorMixin):
    __group = True


class MessageError(BadRequest):
    __group = True
    pass


class MessageNotModified(MessageError):
    """
    Will be raised when you try to set new text is equals to current text.
    """
    match = 'message is not modified'


class MessageToForwardNotFound(MessageError):
    """
    Will be raised when you try to forward very old or deleted or unknown message.
    """
    match = 'message to forward not found'


class MessageToDeleteNotFound(MessageError):
    """
    Will be raised when you try to delete very old or deleted or unknown message.
    """
    match = 'message to delete not found'


class MessageIdentifierNotSpecified(MessageError):
    match = 'message identifier is not specified'


class ChatNotFound(BadRequest, _MatchErrorMixin):
    match = 'chat not found'


class InvalidQueryID(BadRequest):
    match = 'QUERY_ID_INVALID'
    text = 'Invalid query ID'


class InvalidPeerID(BadRequest):
    match = 'PEER_ID_INVALID'
    text = 'Invalid peer ID'


class InvalidHTTPUrlContent(BadRequest):
    match = 'Failed to get HTTP URL content'


class WrongFileIdentifier(BadRequest):
    match = 'wrong file identifier/HTTP URL specified'


class GroupDeactivated(BadRequest):
    match = 'group is deactivated'


class PhotoAsInputFileRequired(BadRequest):
    """
    Will be raised when you try to set chat photo from file ID.
    """
    match = 'Photo should be uploaded as an InputFile'


class ToMuchMessages(BadRequest):
    """
    Will be raised when you try to send media group with more than 10 items.
    """
    match = 'Too much messages to send as an album'


class InvalidStickersSet(BadRequest):
    match = 'STICKERSET_INVALID'
    text = 'Stickers set is invalid'


class ChatAdminRequired(BadRequest):
    match = 'CHAT_ADMIN_REQUIRED'
    text = 'Admin permissions is required!'


class PhotoDimensions(BadRequest):
    match = 'PHOTO_INVALID_DIMENSIONS'
    text = 'Invalid photo dimensions'


class UnavailableMembers(BadRequest):
    match = 'supergroup members are unavailable'


class TypeOfFileMismatch(BadRequest):
    match = 'type of file mismatch'


class BadWebhook(BadRequest):
    __group = True


class WebhookRequireHTTPS(BadWebhook):
    match = 'HTTPS url must be provided for webhook'
    text = 'bad webhook: ' + match


class BadWebhookPort(BadWebhook):
    match = 'Webhook can be set up only on ports 80, 88, 443 or 8443'
    text = 'bad webhook: ' + match


class CantParseUrl(BadRequest):
    match = 'can\'t parse URL'


class NotFound(TelegramAPIError, _MatchErrorMixin):
    __group = True


class MethodNotKnown(NotFound):
    match = 'method not found'


class ConflictError(TelegramAPIError, _MatchErrorMixin):
    __group = True


class TerminatedByOtherGetUpdates(ConflictError):
    match = 'terminated by other getUpdates request'
    text = 'Terminated by other getUpdates request; ' \
           'Make sure that only one bot instance is running'


class CantGetUpdates(ConflictError):
    match = 'can\'t use getUpdates method while webhook is active'


class Unauthorized(TelegramAPIError, _MatchErrorMixin):
    __group = True


class BotKicked(Unauthorized):
    match = 'Bot was kicked from a chat'


class BotBlocked(Unauthorized):
    match = 'bot was blocked by the user'


class UserDeactivated(Unauthorized):
    match = 'user is deactivated'


class CantInitiateConversation(Unauthorized):
    match = 'bot can\'t initiate conversation with a user'


class NetworkError(TelegramAPIError):
    pass


class RetryAfter(TelegramAPIError):
    def __init__(self, retry_after):
        super(RetryAfter, self).__init__(f"Flood control exceeded. Retry in {retry_after} seconds.")
        self.timeout = retry_after


class MigrateToChat(TelegramAPIError):
    def __init__(self, chat_id):
        super(MigrateToChat, self).__init__(f"The group has been migrated to a supergroup. New id: {chat_id}.")
        self.migrate_to_chat_id = chat_id


class Throttled(TelegramAPIError):
    def __init__(self, **kwargs):
        from ..dispatcher.storage import DELTA, EXCEEDED_COUNT, KEY, LAST_CALL, RATE_LIMIT, RESULT
        self.key = kwargs.pop(KEY, '<None>')
        self.called_at = kwargs.pop(LAST_CALL, time.time())
        self.rate = kwargs.pop(RATE_LIMIT, None)
        self.result = kwargs.pop(RESULT, False)
        self.exceeded_count = kwargs.pop(EXCEEDED_COUNT, 0)
        self.delta = kwargs.pop(DELTA, 0)
        self.user = kwargs.pop('user', None)
        self.chat = kwargs.pop('chat', None)

    def __str__(self):
        return f"Rate limit exceeded! (Limit: {self.rate} s, " \
               f"exceeded: {self.exceeded_count}, " \
               f"time delta: {round(self.delta, 3)} s)"
