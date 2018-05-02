import asyncio

from .bot import Bot

try:
    import uvloop
except ImportError:
    uvloop = None
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

__version__ = '1.3.1.dev1'
__api_version__ = '3.6'
