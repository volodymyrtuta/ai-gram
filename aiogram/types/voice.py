from . import Deserializable


class Voice(Deserializable):
    __slots__ = ('file_id', 'duration', 'mime_type', 'file_size')

    def __init__(self, file_id, duration, mime_type, file_size):
        self.file_id = file_id
        self.duration = duration
        self.mime_type = mime_type
        self.file_size = file_size

    @classmethod
    def de_json(cls, raw_data):
        raw_data = cls.check_json(raw_data)

        file_id = raw_data.get('file_id')
        duration = raw_data.get('duration')
        mime_type = raw_data.get('mime_type')
        file_size = raw_data.get('file_size')

        return Voice(file_id, duration, mime_type, file_size)
