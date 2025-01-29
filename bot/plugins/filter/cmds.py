from pyrogram import filters
from pyrogram.client import Client
from bot.database import MongoDB
from bot.utilities.pyrofilters import PyroFilters
from bot.config import config

db = MongoDB()

# --------------------------------------------------------------------------------------------------------------- #
# Admin Management
# --------------------------------------------------------------------------------------------------------------- #
@Client.on_message(filters.command("add_admin") & PyroFilters.admin() & filters.incoming)
async def add_admin(client, message):
    if len(message.command) < 2:
        await message.reply("ᴜꜱᴀɢᴇ: /add_admin ᴜꜱᴇʀ_ɪᴅ", reply_to_message_id=message.id)
        return

    try:
        user_id = int(message.command[1])
        if user_id in config.ROOT_ADMINS_ID:
            await message.reply("ᴛʜɪꜱ ᴜꜱᴇʀ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴄᴏɴꜰɪɢ", reply_to_message_id=message.id)
            return
            
        success = await db.add_admin(user_id)
        if success:
            await message.reply(f"ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴀᴅᴅᴇᴅ ᴜꜱᴇʀ {user_id} ᴀꜱ ᴀᴅᴍɪɴ.", reply_to_message_id=message.id)
        else:
            await message.reply(f"ᴜꜱᴇʀ {user_id} ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ.", reply_to_message_id=message.id)
    except ValueError:
        await message.reply("ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ.", reply_to_message_id=message.id)

@Client.on_message(filters.command("remove_admin") & PyroFilters.admin() & filters.incoming)
async def remove_admin(client, message):
    if len(message.command) < 2:
        await message.reply("ᴜꜱᴀɢᴇ: /remove_admin ᴜꜱᴇʀ_ɪᴅ", reply_to_message_id=message.id)
        return

    try:
        user_id = int(message.command[1])
        if user_id in config.ROOT_ADMINS_ID:
            await message.reply("ᴄᴀɴɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ ꜰʀᴏᴍ ᴄᴏɴꜰɪɢ ᴛʜʀᴏᴜɢʜ ʙᴏᴛ. ᴘʟᴇᴀꜱᴇ ᴍᴏᴅɪꜰʏ ᴄᴏɴꜰɪɢ ᴅɪʀᴇᴄᴛʟʏ.", reply_to_message_id=message.id)
            return
            
        success = await db.remove_admin(user_id)
        if success:
            await message.reply(f"ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ ᴜꜱᴇʀ {user_id} ꜰʀᴏᴍ ᴀᴅᴍɪɴꜱ.", reply_to_message_id=message.id)
        else:
            await message.reply(f"ᴜꜱᴇʀ {user_id} ɪꜱ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ.", reply_to_message_id=message.id)
    except ValueError:
        await message.reply("ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ.", reply_to_message_id=message.id)

@Client.on_message(filters.command("admin_list") & PyroFilters.admin() & filters.incoming)
async def list_admins(client, message):
    admins = await db.get_all_admins()
    
    if not admins:
        await message.reply("ɴᴏ ᴀᴅᴍɪɴꜱ ꜰᴏᴜɴᴅ.", reply_to_message_id=message.id)
        return

    admin_text = "👮 **ᴀᴅᴍɪɴ ʟɪꜱᴛ**:\n\n"
    admin_text += "**ᴄᴏɴꜰɪɢ ᴀᴅᴍɪɴꜱ:**\n"
    for idx, admin_id in enumerate(config.ROOT_ADMINS_ID, 1):
        admin_text += f"{idx}. `{admin_id}` (ꜰʀᴏᴍ ᴄᴏɴꜰɪɢ)\n"
    
    admin_text += "\n**ᴅᴀᴛᴀʙᴀꜱᴇ ᴀᴅᴍɪɴꜱ:**\n"
    db_admins = [admin for admin in admins if admin not in config.ROOT_ADMINS_ID]
    for idx, admin_id in enumerate(db_admins, 1):
        try:
            user = await client.get_users(admin_id)
            admin_text += f"{idx}. {user.mention} (`{admin_id}`)\n"
        except:
            admin_text += f"{idx}. ᴜɴᴋɴᴏᴡɴ ᴜꜱᴇʀ (`{admin_id}`)\n"
    
    await message.reply(admin_text, reply_to_message_id=message.id)
