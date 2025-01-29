from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

from bot.database import MongoDB
from bot.utilities.helpers import RateLimiter
from bot.utilities.pyrofilters import PyroFilters
from bot.utilities.pyrotools import HelpCmd

database = MongoDB()


@Client.on_message(
    filters.private & PyroFilters.admin() & filters.command("stats"),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def stats(_: Client, message: Message) -> Message:
    """A command to display links, users, and total chat count.

    **Usage:**
        /stats
    """

    link_count, users_count = await database.stats()
    chats = await database.total_chat_count()

    return await message.reply(
        f"> STATS:\n"
        f"**Users Count:** `{users_count}`\n"
        f"**Links Count:** `{link_count}`\n"
        f"**Total Chats:** `{chats}`"
    )


HelpCmd.set_help(
    command="stats",
    description=stats.__doc__,
    allow_global=False,
    allow_non_admin=False,
)
