import asyncio
from utilities import utilities
from Db.autoReply_sql import addAutoReply, getAutoReply, remAutoReplySetting
from Db.propSettings_sql import togglePropSettings, getPropSetting
from telethon import utils

propName = "autoReply"


async def run(message, matches, chat_id, step, crons=None):
    response = []
    if(utilities.check_sudo(message.sender_id)):
        if matches == "ea":
            isActive = getPropSetting(message.chat_id, propName) or None
            if isActive and isActive.active:
                response.append(message.reply("auto reply already activated."))
            else:
                if togglePropSettings(message.chat_id, propName):
                    response.append(message.reply("auto reply has been activated."))
                else:
                    response.append(message.reply("error while doing that."))
            return response
        elif matches == "da":
            isActive = getPropSetting(message.chat_id, propName) or None
            if not isActive or isActive.active:
                if togglePropSettings(message.chat_id, propName, False):
                    response.append(message.reply("auto reply has been deactivated."))
                else:
                    response.append(message.reply("error while doing that."))
            else:
                response.append(message.reply("auto reply already deactivated."))
            return response
        elif matches[0] == "ar":
            bot = utilities.config["isbot"]
            if message.is_reply:
                msg = await message.get_reply_message()
                if msg.media:
                    if bot:
                        file = utils.pack_bot_file_id(msg.media)
                        await utilities.client.send_file(msg.chat_id, file)
                    else:
                        downlodd_file = await msg.download_media("tmp/autoReply")
                        up_file = await utilities.client.upload_file(
                            downlodd_file, use_cache=True
                        )
                        sent_file = await utilities.client.send_file(msg.chat_id, up_file)
                        file = utils.pack_bot_file_id(sent_file.media)
                    addAutoReply(matches[1], "media", msg.text, file)
                else:
                    addAutoReply(matches[1], "text", msg.text)
                response.append(message.reply("reply has been added"))
            else:
                response.append(message.reply("please reply to a message."))
            return response
        elif matches[0] == "rar":
            if remAutoReplySetting(matches[1]):
                response.append(message.reply("reply has been deleted"))
            else:
                response.append(message.reply("no reply has that text"))
            return response
    
    isActive = getPropSetting(message.chat_id, propName) or None
    if isActive and isActive.active:
        rep = getAutoReply(message.text)
        if rep:
            if rep.msg_type == "media":
                return [message.reply(file=rep.file_id, message=rep.msg_content)]
            else:
                return [message.reply(rep.msg_content)]
        else:
            return response
    return response


plugin = {
    "name": "autoReply",
    "desc": "Do autoReply in chats",
    "run": run,
    "usage": [
        "/ea  to enable autoReply in a specific chat.",
        "/da to disable autoReply in a specific chat.",
        "/ar <text> reply to a message to save it.",
        "/rar <query> to delete reply.",
    ],
    "sudo": False,
    "patterns": [
        "^[!/#](ea)$",
        "^[!/#](da)$",
        "^[!/#](ar) (.+)$",
        "^[!/#](rar) (.+)$",
        "^(.+)$",
    ],
}
