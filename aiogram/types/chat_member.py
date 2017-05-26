from . import Deserializable


class ChatMember(Deserializable):
    def __init__(self, user, status):
        self.user = user
        self.status = status

    @classmethod
    def de_json(cls, raw_data):
        raw_data = cls.check_json(raw_data)

        user = raw_data.get('user')
        status = raw_data.get('status')

        return ChatMember(user, status)


class ChatMemberStatus:
    CREATOR = 'creator'
    ADMINISTRATOR = 'administrator'
    MEMBER = 'member'
    LEFT = 'left'
    KICKED = 'kicked'

    @classmethod
    def is_admin(cls, role):
        return role in [cls.ADMINISTRATOR, cls.CREATOR]

    @classmethod
    def is_member(cls, role):
        return role in [cls.MEMBER, cls.ADMINISTRATOR, cls.CREATOR]
