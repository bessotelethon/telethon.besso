import asyncio
from utilities import utilities
from Db.welcome_sql import getWelcomeSettings, addWelcomeSetting, remWelcomeSetting
from telethon import utils


async def added(event, chat_id, step):
    ws = getWelcomeSettings(chat_id)
    if ws:
        from_user = event.added_by
        target_user = event.user
        if ws.msg_type == "media":
            return [event.reply(file=ws.file_id, message=ws.msg_content)]
        else:
            return [event.reply(ws.msg_content)]


async def run(message, matches, chat_id, step, crons=None):
    if matches[1:] == "وضع الترحيب":
        if message.is_reply:
            msg = await message.get_reply_message()
            if msg.media:
                file = await msg.download_media("tmp")
                addWelcomeSetting(chat_id, "media", msg.text, file)
            else:
                addWelcomeSetting(chat_id, "text", msg.text)
            return [message.reply("❏︙تم إضافة رسالة ترحيب بنجاح.")]
        else:
            return [message.reply("❏︙يرجى الرد على رسالة الوضع ترحيب. ")]
    elif matches[1:] == "حذف الترحيب":
        ws = getWelcomeSettings(chat_id)
        if ws:
            remWelcomeSetting(chat_id)
            return [message.reply("❏︙تم مسح رساله ترحيب بنجاح.. ")]
        else:
            return [message.reply("❏︙لا يوجد ترحيب بلفعل..")]


plugin = {
    "name": "",
    "desc": "",
    "usage": [
        "/وضع الترحيب + برد ع رساله",
        "❏︙ /حذف الترحيب",
    ],
    "run": run,
    "added": added,
    "sudo": True,
    "patterns": ["^[!/#]وضع الترحيب$", "^[!/#]حذف الترحيب$"],
}
