import logging

__version__ = '0.1b'

log = logging.getLogger(__name__)

API_URL = "https://api.telegram.org/bot{token}/{method}"
FILE_URL = "https://api.telegram.org/file/bot{token}/{file_id}"
