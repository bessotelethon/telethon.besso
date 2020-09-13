import asyncio
from utilities import utilities
from Db.autoReply_sql import addAutoReply, getAutoReply, remAutoReplySetting
from Db.propSettings_sql import togglePropSettings, getPropSetting
from telethon import utils

propName = "autoReply"


async def run(message, matches, chat_id, step, crons=None):
    response = []
    if(utilities.check_sudo(message.sender_id)):
        if matches == "تفعيل الردود":
            isActive = getPropSetting(message.chat_id, propName) or None
            if isActive and isActive.active:
                response.append(message.reply("auto reply already activated."))
            else:
                if togglePropSettings(message.chat_id, propName):
                    response.append(message.reply("❏︙تم تفعيل الردود بنجاح"))
                else:
                    response.append(message.reply("error while doing that."))
            return response
        elif matches == "تعطيل الردود":
            isActive = getPropSetting(message.chat_id, propName) or None
            if not isActive or isActive.active:
                if togglePropSettings(message.chat_id, propName, False):
                    response.append(message.reply("❏︙تم تعطيل الردود"))
                else:
                    response.append(message.reply("error while doing that."))
            else:
                response.append(message.reply("auto reply already deactivated."))
            return response
        elif matches[0] == "اضف رد":
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
                response.append(message.reply("❏︙تم اضافه رد بنجاح"))
            else:
                response.append(message.reply("please reply to a message."))
            return response
        elif matches[0] == "حذف رد":
            if remAutoReplySetting(matches[1]):
                response.append(message.reply("❏︙تم حذف رد بنجاح"))
            else:
                response.append(message.reply("❏︙لا يوجد هاكذا رد "))
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
    "name": "",
    "desc": "Do autoReply in chats",
    "run": run,
    "usage": [
        "/تفعيل الردود",
        "❏︙/تعطيل الردود",
        "❏︙/اضف رد + برد ع رساله",
        "❏︙/حذف رد + الاسم رد",
    ],
    "sudo": False,
    "patterns": [
        "^[!/#](تفعيل الردود)$",
        "^[!/#](تعطيل الردود)$",
        "^[!/#](اضف رد) (.+)$",
        "^[!/#](حذف رد) (.+)$",
        "^(.+)$",
    ],
}
