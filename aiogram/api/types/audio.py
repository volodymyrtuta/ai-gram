from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .base import TelegramObject

if TYPE_CHECKING:  # pragma: no cover
    from .photo_size import PhotoSize


class Audio(TelegramObject):
    """
    This object represents an audio file to be treated as music by the Telegram clients.

    Source: https://core.telegram.org/bots/api#audio
    """

    file_id: str
    """Identifier for this file, which can be used to download or reuse the file"""
    file_unique_id: str
    """Unique identifier for this file, which is supposed to be the same over time and for
    different bots. Can't be used to download or reuse the file."""
    duration: int
    """Duration of the audio in seconds as defined by sender"""
    performer: Optional[str] = None
    """Performer of the audio as defined by sender or by audio tags"""
    title: Optional[str] = None
    """Title of the audio as defined by sender or by audio tags"""
    mime_type: Optional[str] = None
    """MIME type of the file as defined by sender"""
    file_size: Optional[int] = None
    """File size"""
    thumb: Optional[PhotoSize] = None
    """Thumbnail of the album cover to which the music file belongs"""
