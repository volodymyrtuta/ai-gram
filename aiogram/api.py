from aiogram import API_URL, log
from aiogram.exceptions import ValidationError, TelegramAPIError


def check_token(token):
    if any(x.isspace() for x in token):
        raise ValidationError('Token is invalid!')

    left, sep, right = token.partition(':')
    if (not sep) or (not left.isdigit()) or (len(left) < 3):
        raise ValidationError('Token is invalid!')

    return True


async def _check_result(method_name, response):
    """
    Checks whether `result` is a valid API response.
    A result is considered invalid if:
        - The server returned an HTTP response code other than 200
        - The content of the result is invalid JSON.
        - The method call was unsuccessful (The JSON 'ok' field equals False)

    :raises ApiException: if one of the above listed cases is applicable
    :param method_name: The name of the method called
    :param response: The returned response of the method request
    :return: The result parsed to a JSON dictionary.
    """
    if response.status != 200:
        body = await response.text()
        raise TelegramAPIError(f"The server returned HTTP {response.status}. Response body:\n[{body}]",
                               method_name, response.status, body)

    result_json = await response.json()

    if not result_json.get('ok'):
        body = await response.text()
        code = result_json.get('error_code')
        description = result_json.get('description')
        raise TelegramAPIError(f"Error code: {code} Description {description}",
                               method_name, response.status, body)
    return result_json.get('result')


async def request(session, token, method, data=None):
    log.debug(f"Make request: '{method}' with data: {data or {}}")
    url = API_URL.format(token=token, method=method)
    async with session.post(url, json=data) as response:
        return await _check_result(method, response)


class ApiMethods:
    GET_ME = 'getMe'
    SEND_MESSAGE = 'sendMessage'
    FORWARD_MESSAGE = 'forwardMessage'
    SEND_PHOTO = 'sendPhoto'
    SEND_AUDIO = 'sendAudio'
    SEND_DOCUMENT = 'sendDocument'
    SEND_STICKER = 'sendSticker'
    SEND_VIDEO = 'sendVideo'
    SEND_VOICE = 'sendVoice'
    SEND_VIDEO_NOTE = 'sendVideoNote'
    SEND_LOCATION = 'sendLocation'
    SEND_VENUE = 'sendVenue'
    SEND_CONTACT = 'sendContact'
    SEND_CHAT_ACTION = 'sendChatAction'
    GET_USER_PROFILE_PHOTOS = 'getUserProfilePhotos'
    GET_FILE = 'getFile'
    KICK_CHAT_MEMBER = 'kickChatMember'
    UNBAN_CHAT_MEMBER = 'unbanChatMember'
    LEAVE_CHAT = 'leaveChat'
    GET_CHAT = 'getChat'
    GET_CHAT_ADMINISTRATORS = 'getChatAdministrators'
    GET_CHAT_MEMBERS_COUNT = 'getChatMembersCount'
    GET_CHAT_MEMBER = 'getChatMember'
    ANSWER_CALLBACK_QUERY = 'answerCallbackQuery'
    EDIT_MESSAGE_TEXT = 'editMessageText'
    EDIT_MESSAGE_CAPTION = 'editMessageCaption'
    EDIT_MESSAGE_REPLY_MARKUP = 'editMessageReplyMarkup'
    DELETE_MESSAGE = 'deleteMessage'
