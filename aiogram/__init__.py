import warnings

try:
    from .bot import Bot
except ImportError as e:
    if e.name == 'aiohttp':
        warnings.warn('Dependencies is not installed!', category=ImportWarning)
    else:
        raise

from .utils.versions import Stage, Version

VERSION = Version(1, 0, 3, stage=Stage.DEV, build=0)
API_VERSION = Version(3, 5)

__version__ = VERSION.version
__api_version__ = API_VERSION.version
