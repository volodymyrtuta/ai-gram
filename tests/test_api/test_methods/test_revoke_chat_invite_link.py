import pytest

from aiogram.methods import Request, RevokeChatInviteLink
from aiogram.types import ChatInviteLink, User
from tests.mocked_bot import MockedBot


class TestRevokeChatInviteLink:
    @pytest.mark.asyncio
    async def test_method(self, bot: MockedBot):
        prepare_result = bot.add_result_for(
            RevokeChatInviteLink,
            ok=True,
            result=ChatInviteLink(
                invite_link="https://t.me/username",
                creator=User(id=42, is_bot=False, first_name="User"),
                is_primary=False,
                is_revoked=True,
            ),
        )

        response: ChatInviteLink = await RevokeChatInviteLink(
            chat_id=-42,
            invite_link="https://t.me/username",
        )
        request: Request = bot.get_request()
        assert request.method == "revokeChatInviteLink"
        # assert request.data == {}
        assert response == prepare_result.result

    @pytest.mark.asyncio
    async def test_bot_method(self, bot: MockedBot):
        prepare_result = bot.add_result_for(
            RevokeChatInviteLink,
            ok=True,
            result=ChatInviteLink(
                invite_link="https://t.me/username",
                creator=User(id=42, is_bot=False, first_name="User"),
                is_primary=False,
                is_revoked=True,
            ),
        )

        response: ChatInviteLink = await bot.revoke_chat_invite_link(
            chat_id=-42,
            invite_link="https://t.me/username",
        )
        request: Request = bot.get_request()
        assert request.method == "revokeChatInviteLink"
        # assert request.data == {}
        assert response == prepare_result.result
