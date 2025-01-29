from pyrogram import filters, enums, raw
from pyrogram.client import Client
from pyrogram import errors
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatMemberUpdated
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from pyrogram.errors import RPCError
from bot.config import config
from bot.database import MongoDB

db = MongoDB()


@Client.on_chat_member_updated()
async def handle_new_chat(client, chat_member_updated: ChatMemberUpdated):
    if chat_member_updated.new_chat_member and chat_member_updated.new_chat_member.user.id == client.me.id:
        chat_id = chat_member_updated.chat.id
        chat_title = chat_member_updated.chat.title
        try:
            if str(chat_id).startswith("-100") and not await db.get_chat(chat_id):
                total_members = await client.get_chat_members_count(chat_id)
                try:
                    get_link = await client.invoke(
                        raw.functions.messages.ExportChatInvite( # type: ignore[reportPrivateImportUsage]
                            peer=await client.resolve_peer(peer_id=chat_id),
                            legacy_revoke_permanent=True,
                            request_needed=False,
                        )
                    )
                    channel_link = get_link.link if get_link else "No link available"
                except RPCError:
                    channel_link = "Failed to generate invite link."
                
                is_private = bool(chat_member_updated.chat.username is None)
                channel_text = f"""<b>📢 NEW CHAT ALERT

- Name: {chat_title}
- ID: <code>{chat_id}</code>
- Type: {'Private' if is_private else 'Public'} Chat
- Members: {total_members}
- Link: {channel_link}
- Added by: {chat_member_updated.from_user.mention if chat_member_updated.from_user else 'Anonymous'}</b>"""
                
                await client.send_message(config.LOG_CHANNEL, channel_text, disable_web_page_preview=True)
                await db.add_chat(chat_id, chat_title)

        except Exception as e:
            await client.send_message(config.LOG_CHANNEL, f"<b>❌ Error adding chat {chat_title}\nError: {str(e)}</b>")

@Client.on_message(filters.command('leave') )
async def leave_a_chat(bot: Client, message: Message):
    r = message.text.split(None)
    if len(message.command) == 1:
        return await message.reply('<b>ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ʟɪᴋᴇ ᴛʜɪꜱ `/leave -100******`</b>')
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "ɴᴏ ʀᴇᴀꜱᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ..."
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        btn = [[
            InlineKeyboardButton('⚡️ ᴏᴡɴᴇʀ ⚡️', url=f'https://t.me/{config.USERNAME}')
        ]]
        reply_markup=InlineKeyboardMarkup(btn)
        await bot.send_message(
            chat_id=chat,
            text=f'😞 ʜᴇʟʟᴏ ᴅᴇᴀʀ,\nᴍʏ ᴏᴡɴᴇʀ ʜᴀꜱ ᴛᴏʟᴅ ᴍᴇ ᴛᴏ ʟᴇᴀᴠᴇ ꜰʀᴏᴍ ɢʀᴏᴜᴘ ꜱᴏ ɪ ɢᴏ 😔\n\n🚫 ʀᴇᴀꜱᴏɴ ɪꜱ - <code>{reason}</code>\n\nɪꜰ ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴀᴅᴅ ᴍᴇ ᴀɢᴀɪɴ ᴛʜᴇɴ ᴄᴏɴᴛᴀᴄᴛ ᴍʏ ᴏᴡɴᴇʀ 👇',
            reply_markup=reply_markup,
        )
        await bot.leave_chat(chat)
        await db.delete_chat(chat)
        await message.reply(f"<b>ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʟᴇꜰᴛ ꜰʀᴏᴍ ɢʀᴏᴜᴘ - `{chat}`</b>")
    except Exception as e:
        await message.reply(f'<b>🚫 ᴇʀʀᴏʀ - `{e}`</b>')

@Client.on_message(filters.command('groups') )
async def groups_list(bot: Client, message: Message):
    msg = await message.reply('<b>Searching...</b>')
    chats = await db.get_all_chats()
    out = "Groups saved in the database:\n\n"
    count = 1
    async for chat in chats:
        try:
            chat_info = await bot.get_chat(chat['id'])
            members_count = chat_info.members_count if chat_info.members_count else "Unknown"
            out += f"<b>{count}. Title - `{chat['title']}`\nID - `{chat['id']}`\nMembers - `{members_count}`</b>\n\n"
            count += 1
        except errors.ChannelPrivate:
            await db.delete_chat(chat['id'])
        except Exception as e:
            print(f"An error occurred: {e}")
    try:
        if count > 1:
            await msg.edit_text(out)
        else:
            await msg.edit_text("<b>No groups found</b>")
    except MessageTooLong:
        with open('chats.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('chats.txt', caption="<b>List of all groups</b>")


