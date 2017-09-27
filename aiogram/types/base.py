import typing
import ujson

from .fields import BaseField

PROPS_ATTR_NAME = '_props'
VALUES_ATTR_NAME = '_values'
ALIASES_ATTR_NAME = '_aliases'

__all__ = ('MetaTelegramObject', 'TelegramObject')


class MetaTelegramObject(type):
    """
    Metaclass for telegram objects
    """
    _objects = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super(MetaTelegramObject, mcs).__new__(mcs, name, bases, namespace)

        props = {}
        values = {}
        aliases = {}

        # Get props, values, aliases from parent objects
        for base in bases:
            if not isinstance(base, MetaTelegramObject):
                continue
            props.update(getattr(base, PROPS_ATTR_NAME))
            values.update(getattr(base, VALUES_ATTR_NAME))
            aliases.update(getattr(base, ALIASES_ATTR_NAME))

        # Scan current object for props
        for name, prop in ((name, prop) for name, prop in namespace.items() if isinstance(prop, BaseField)):
            props[prop.alias] = prop
            if prop.default is not None:
                values[prop.alias] = prop.default
            aliases[name] = prop.alias

        # Set attributes
        setattr(cls, PROPS_ATTR_NAME, props)
        setattr(cls, VALUES_ATTR_NAME, values)
        setattr(cls, ALIASES_ATTR_NAME, aliases)

        mcs._objects[cls.__name__] = cls
        return cls

    @property
    def telegram_types(cls):
        return cls._objects


class TelegramObject(metaclass=MetaTelegramObject):
    """
    Abstract class for telegram objects
    """

    def __init__(self, conf=None, **kwargs):
        """
        Deserialize object

        :param conf:
        :param kwargs:
        """
        if conf is None:
            conf = {}
        for key, value in kwargs.items():
            if key in self.props:
                self.props[key].set_value(self, value)
            else:
                self.values[key] = value
        self._conf = conf

    @property
    def conf(self) -> typing.Dict[str, typing.Any]:
        return self.conf

    @property
    def props(self) -> typing.Dict[str, BaseField]:
        """
        Get props

        :return: dict with props
        """
        return getattr(self, PROPS_ATTR_NAME, {})

    @property
    def props_aliases(self) -> typing.Dict[str, str]:
        """
        Get aliases for props

        :return:
        """
        return getattr(self, ALIASES_ATTR_NAME, {})

    @property
    def values(self):
        """
        Get values

        :return:
        """
        return getattr(self, VALUES_ATTR_NAME, {})

    @property
    def telegram_types(self):
        return type(self).telegram_types

    @classmethod
    def to_object(cls, data):
        """
        Deserialize object

        :param data:
        :return:
        """
        return cls(**data)

    def to_python(self) -> typing.Dict:
        """
        Get object as JSON serializable

        :return:
        """
        self.clean()
        result = {}
        for name, value in self.values.items():
            if name in self.props:
                value = self.props[name].export(self)
            if isinstance(value, TelegramObject):
                value = value.to_python()
            result[self.props_aliases.get(name, name)] = value
        return result

    def clean(self):
        """
        Remove empty values
        """
        for key, value in self.values.copy().items():
            if value is None:
                del self.values[key]

    def as_json(self) -> str:
        """
        Get object as JSON string

        :return: JSON
        :rtype: :obj:`str`
        """
        return ujson.dumps(self.to_python())

    def __str__(self) -> str:
        """
        Return object as string. Alias for '.as_json()'

        :return: str
        """
        return self.as_json()

    def __getitem__(self, item):
        if item in self.props:
            return getattr(self, item)
        elif item in self.values:
            return self.values[item]

    def __setitem__(self, key, value):
        if key in self.props:
            setattr(self, key, value)
        else:
            self.values[key] = value
