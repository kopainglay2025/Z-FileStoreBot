# ruff: noqa: ARG001

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

from bot.database import MongoDB
from bot.config import config
from bot.options import options

db = MongoDB()

class AdminsFilter:
    @staticmethod
    def admin(
        allow_global: bool = False,  # noqa: FBT001, FBT002
    ) -> filters.Filter:
        async def func(flt: None, client: Client, message: Message) -> bool:
            user_id = message.from_user.id
            global_mode = options.settings.GLOBAL_MODE
            
            is_admin = await db.is_admin(user_id)
            return is_admin or (global_mode and allow_global)

        return filters.create(func, "AdminFilter")
