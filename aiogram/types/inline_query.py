from aiogram.types.location import Location
from aiogram.types.user import User
from . import Deserializable


class InlineQuery(Deserializable):
    def __init__(self, id, from_user, location, query, offset):
        self.id: int = id
        self.from_user: User = from_user
        self.location: Location = location
        self.query: str = query
        self.offset: str = offset

    @classmethod
    def de_json(cls, raw_data):
        raw_data = cls.check_json(raw_data)

        id = raw_data.get('id')
        from_user = User.deserialize(raw_data.get('from'))
        location = Location.deserialize(raw_data.get('location'))
        query = raw_data.get('query')
        offset = raw_data.get('offset')

        return InlineQuery(id, from_user, location, query, offset)
