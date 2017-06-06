from .base import Deserializable
from .photo_size import PhotoSize


class Animation(Deserializable):
    """
    You can provide an animation for your game so that it looks stylish in chats. 
    This object represents an animation file to be displayed in the message containing a game.
    
    https://core.telegram.org/bots/api#animation
    """
    def __init__(self, file_id, thumb, file_name, mime_type, file_size):
        self.file_id: str = file_id
        self.thumb: PhotoSize = thumb
        self.file_name: str = file_name
        self.mime_type: str = mime_type
        self.file_size: int = file_size

    @classmethod
    def de_json(cls, raw_data):
        raw_data = cls.check_json(raw_data)

        file_id = raw_data.get('file_id')
        thumb = PhotoSize.deserialize(raw_data.get('thumb'))
        file_name = raw_data.get('file_name')
        mime_type = raw_data.get('mime_type')
        file_size = raw_data.get('file_size')

        return Animation(file_id, thumb, file_name, mime_type, file_size)
