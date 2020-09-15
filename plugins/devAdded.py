import asyncio
from utilities import utilities
from Db.dev_sql import addDevUser, getDevsUsers, getDevUser, remDevUser
from telethon import utils, errors
import re


async def addDev_user(message, from_id):
    try:
        if getDevUser(from_id):
            return await message.reply("User already added as Dev.")
        addDevUser(from_id)
        utilities.devs.append(from_id)
        return await message.reply("❏︙تم رفع مطور")
    except Exception as e:
        utilities.prRed(str(type(e)) + " Error : " + str(e))
        return await message.reply(str(e))


async def remDev_user(message, from_id):
    try:
        if not getDevUser(from_id):
            return await message.reply("User already not dev.")
        remDevUser(from_id)
        utilities.devs.remove(from_id)
        return await message.reply("❏︙تم تنزيل مطور")
    except Exception as e:
        utilities.prRed(str(type(e)) + " Error : " + str(e))
        return await message.reply(str(e))


async def run(message, matches, chat_id, step, crons=None):

    response = []
    if message.sender_id not in utilities.config["sudo_members"]:
        return []
    if matches == "المطورين":
        devlist = getDevsUsers()
        res = ""
        i = 1
        for user in devlist:
            userId = int("%.0f" % user.user_id)
            try:
                _user = await utilities.client.get_entity(userId)
                strin = (
                    str(i)
                    + " - [%s](tg://user?id=%s)"
                    % (_user.first_name, int("%.0f" % userId))
                    + "\n"
                )
            except Exception as e:
                strin = (
                    str(i)
                    + " - [%s](tg://user?id=%s)"
                    % (("رفع مطور" + str(i)), int("%.0f" % userId))
                    + "\n"
                )
            i += 1
            res = res + strin
        return [message.reply(res if (len(res) != 0) else "❏︙لا يوجد مطورين")]
    if matches[0] == "رفع مطور":
        if re.match(r"@[a-zA-Z][\w\d]{3,30}[a-zA-Z\d]", matches[1]):
            user = await utilities.client.get_entity(matches[1])
            return [addDev_user(message, user.id)]
        elif re.match(r"(\d)", matches[1]):
            return [addDev_user(message, matches[1])]
        else:
            return [message.reply("please, use by reply or use valid username and id")]
    elif matches[0] == "rdev":
        if re.match(r"@[a-zA-Z][\w\d]{3,30}[a-zA-Z\d]", matches[1]):
            user = await utilities.client.get_entity(matches[1])
            name = user.first_name
            return [remDev_user(message, user.id)]
        elif re.match(r"(\d)", matches[1]):
            return [remDev_user(message, matches[1])]
        else:
            return [message.reply("please, use by reply or use valid username and id")]
    elif matches == "رفع مطور":
        if message.is_reply:
            msg = await message.get_reply_message()
            fromId = msg.from_id
            chat_id = msg.chat_id
            name = (await msg.get_sender()).first_name
            return [addDev_user(message, fromId)]

    elif matches == "rdev":
        if message.is_reply:
            msg = await message.get_reply_message()
            fromId = msg.from_id
            chat_id = msg.chat_id
            return [remDev_user(message, fromId)]
    elif matches == "مسح المطورين":
        devlist = getDevsUsers()
        for user in devlist:
            remDevUser(user.user_id)
            utilities.devs.remove(user.user_id)
        return [message.reply("❏︙تم تنزيل جميع المطورين")]
    return response


plugin = {
    "name": "",
    "desc": "Make someone dev",
    "usage": [
        "/مسح المطورين",
        "❏︙/المطورين",
        "❏︙/تنزيل مطور + برد",
        "❏︙/رفع مطور + برد",
    ],
    "run": run,
    "sudo": True,
    "patterns": [
        "^[!/#](مسح المطورين)$",
        "^[!/#](المطورين)",
        "^[!/#](رفع مطور)$",
        "^[!/#](تنزيل مطور)$",
        "^[!/#](رفع مطور) (.+)$",
        "^[!/#](rdev) (.+)$",
    ],
}
