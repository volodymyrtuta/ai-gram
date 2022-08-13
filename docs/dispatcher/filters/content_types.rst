==================
ContentTypesFilter
==================

.. autoclass:: aiogram.filters.content_types.ContentTypesFilter
    :members:
    :member-order: bysource
    :undoc-members: False

Can be imported:

- :code:`from aiogram.filters.content_types import ContentTypesFilter`
- :code:`from aiogram.filters import ContentTypesFilter`

Or used from filters factory by passing corresponding arguments to handler registration line

Usage
=====

1. Single content type: :code:`ContentTypesFilter(content_types=["sticker"])` or :code:`ContentTypesFilter(content_types="sticker")`
2. Multiple content types: :code:`ContentTypesFilter(content_types=["sticker", "photo"])`
3. Recommended: With usage of `ContentType` helper: :code:`ContentTypesFilter(content_types=[ContentType.PHOTO])`
4. Any content type: :code:`ContentTypesFilter(content_types=[ContentType.ANY])`

Allowed handlers
================

Allowed update types for this filter:

- :code:`message`
- :code:`edited_message`
- :code:`channel_post`
- :code:`edited_channel_post`
