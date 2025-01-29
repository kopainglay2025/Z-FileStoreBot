import time

from pyrogram import filters, enums, raw
from pyrogram.client import Client
from pyrogram import errors
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from bot.database import MongoDB
from bot.config import config

db = MongoDB()

channel_cache = {}
CACHE_DURATION = 3600
filter_text = filters.create(lambda _, __, message: bool(message.text and not message.text.startswith("/")))

async def get_invite_link(bot, chat_id):
   current_time = time.time()
   
   # Check if cached link exists and is still valid
   if chat_id in channel_cache:
       cached_data = channel_cache[chat_id]
       if current_time - cached_data['timestamp'] < CACHE_DURATION:
           return cached_data['link']
       
       # Revoke expired link
       try:
           await bot.invoke(
               raw.functions.messages.EditExportedChatInvite( # type: ignore[reportPrivateImportUsage]
                   peer=await bot.resolve_peer(chat_id),
                   link=cached_data['link'],
                   revoked=True
               )
           )
       except Exception as e:
           print(f"Error revoking link: {str(e)}")
   
   # Generate new permanent link
   try:
       invite_link = await bot.invoke(
           raw.functions.messages.ExportChatInvite( # type: ignore[reportPrivateImportUsage]
               peer=await bot.resolve_peer(chat_id),
               legacy_revoke_permanent=True,
               request_needed=False,
           )
       )
       
       if invite_link and invite_link.link:
           channel_cache[chat_id] = {
               'link': invite_link.link,
               'timestamp': current_time
           }
           return invite_link.link
   except errors.ChatAdminRequired as e:
       try:
           # Send error message to the log channel with chat details
           chat_info = await bot.get_chat(chat_id)
           chat_name = chat_info.title if hasattr(chat_info, 'title') else f"Chat ID: {chat_id}"
           await bot.send_message(
               config.LOG_CHANNEL,
               f"#Error generating invite link for {chat_name} ({chat_id}): Telegram says: [403 CHAT_ADMIN_REQUIRED] - The method requires chat admin privileges."
           )
       except Exception as log_error:
           print(f"Error logging the admin required issue: {str(log_error)}")
   except Exception as e:
       print(f"Error generating invite link: {str(e)}")
       
   return None


@Client.on_message(filters.command("channel") & filter_text)
async def search_channels(bot: Client, message: Message):
   try:
       search_text = message.text.split(maxsplit=1)[-1].lower().strip()
       if len(search_text) < 3:
           return

       chats = await db.get_all_chats()
       matched_channels = []

       async for chat in chats:
           try:
               channel = await bot.get_chat(chat['id'])
               channel_title = channel.title.lower()

               if search_text in channel_title:
                   link = await get_invite_link(bot, chat['id'])
                   
                   if link:
                       matched_channels.append({
                           'title': channel.title,
                           'link': link
                       })

           except errors.bad_request_400.ChannelInvalid as e:
               print(f"Channel {chat['id']} is invalid or inaccessible. Removing from DB.")
               await db.delete_chat(chat['id'])
               continue
           except Exception as e:
               if "CHANNEL_PRIVATE" in str(e):
                   print(f"Channel {chat['id']} is private or not accessible. Removing from DB.")
                   await db.delete_chat(chat['id'])
               else:
                   print(f"Error processing channel {chat['id']}: {str(e)}")
               continue

       for channel in matched_channels:
           buttons = [[
               InlineKeyboardButton(
                   text="ᴅᴏᴡɴʟᴏᴀᴅ",
                   url=channel['link']
               )
           ]]
           text = f"<b><a href='{channel['link']}'>{channel['title']}</a></b>"

           await message.reply_text(
               text=text,
               reply_markup=InlineKeyboardMarkup(buttons),
               disable_web_page_preview=True
           )

   except Exception as e:
       print(f"Error in search_channels: {str(e)}")
       await message.reply_text("An error occurred while processing your request.")
