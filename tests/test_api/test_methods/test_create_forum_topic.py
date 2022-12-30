from aiogram.methods import CreateForumTopic, Request
from aiogram.types import ForumTopic
from tests.mocked_bot import MockedBot


class TestCreateForumTopic:
    async def test_method(self, bot: MockedBot):
        prepare_result = bot.add_result_for(
            CreateForumTopic,
            ok=True,
            result=ForumTopic(message_thread_id=42, name="test", icon_color=0xFFD67E),
        )

        response: ForumTopic = await CreateForumTopic(
            chat_id=42,
            name="test",
        )
        request: Request = bot.get_request()
        assert request.method == "createForumTopic"
        # assert request.data == {}
        assert response == prepare_result.result

    async def test_bot_method(self, bot: MockedBot):
        prepare_result = bot.add_result_for(
            CreateForumTopic,
            ok=True,
            result=ForumTopic(message_thread_id=42, name="test", icon_color=0xFFD67E),
        )

        response: ForumTopic = await bot.create_forum_topic(
            chat_id=42,
            name="test",
        )
        request: Request = bot.get_request()
        assert request.method == "createForumTopic"
        # assert request.data == {}
        assert response == prepare_result.result
