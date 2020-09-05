import os

os.system("sudo service redis-server start")
from telethon import TelegramClient, events, Button, extensions, functions, types
from os.path import dirname, realpath, join
import re
import asyncio
import datetime
from utilities import utilities
import json

loop = asyncio.get_event_loop()
utilities.client = None


def sort_key(p):
    return p["name"]


def run_client():
    utilities.config = utilities.get_config()
    config = utilities.config
    utilities.client = TelegramClient(
        "sessions_bot", config["api_id"], config["api_hash"], loop=loop
    )
    utilities.client.start()
    utilities.load_plugins()
    utilities.plugins.sort(key=sort_key)
    utilities.public_plugins.sort(key=sort_key)


run_client()

from Db.mute_sql import getMutedUser, remMuteUser
from Db.dev_sql import getDevsUsers

for dev in getDevsUsers():
    utilities.devs.append(int("%.0f" % dev.user_id))


async def saveBotId():
    me = await utilities.client.get_me()
    utilities.prLightGray("name : " + me.first_name)
    if me.username:
        utilities.prYellow("username : https://t.me/" + me.username)
    if me.bot:
        utilities.prGreen("botType : API")
    else:
        utilities.prGreen("botType : CLI")
    utilities.prBlack("---------------------------")
    utilities.config["bot_id"] = (me).id
    utilities.config["isbot"] = (me).bot
    utilities.save_config()


@utilities.client.on(events.ChatAction)
async def my_event_handler(event):

    try:
        if event.user_joined or event.user_added:
            from_user = event.added_by
            target_user = event.user
            plugins = utilities.plugins
            for plugin in plugins:
                if "added" not in plugin:
                    continue
                if "bot" in plugin and utilities.config["isbot"] != plugin["bot"]:
                    if plugin["bot"]:
                        await event.reply("for bot-api only")
                    else:
                        await event.reply("for bot-cli only")
                    return

                # if plugin["sudo"]:
                #     if check_sudo(event.sender_id):
                #         return_values = await plugin["added"](
                #             event,
                #             event.chat_id,
                #             0
                #             if (target_user.id in utilities.user_steps)
                #             else utilities.user_steps[target_user.id]["step"],
                #             crons=utilities.crons,
                #         )

                #         for return_value in return_values:
                #             if return_value:
                #                 await (return_value)
                #     else:
                #         await event.reply("for sudores")

                # else:
                return_values = await plugin["added"](
                    event,
                    event.chat_id,
                    0
                    if (target_user.id not in utilities.user_steps)
                    else utilities.user_steps[target_user.id]["step"],
                )
                if return_values:
                    for return_value in return_values:
                        await (return_value)
    except Exception as e:
        print("chat_handler : %s" % (e))


@utilities.client.on(events.NewMessage)
async def command_interface(event):
    try:

        message = event.message

        prefix = "send"
        if message.is_reply:
            prefix = "reply"
        if message.out:
            return
        from_id = message.from_id
        to_id = message.chat_id
        if event.is_private:
            pr = utilities.prGreen
        else:
            pr = utilities.prPurple
        if message.raw_text and not message.via_bot_id:
            stri = (
                str(from_id)
                + ": "
                + prefix
                + " text message : "
                + message.raw_text
                + " to "
                + str(to_id)
            )
            pr(stri)
        elif message.media and not message.via_bot_id:
            pr(str(from_id) + ": " + prefix + " media message to " + str(to_id))
        elif message.via_bot_id:
            pr(str(from_id) + ": " + prefix + " inline message to " + str(to_id))
        else:
            utilities.prRed(
                str(from_id) + ": " + prefix + " unknown message to " + str(to_id)
            )
    except Exception as e:
        print(str(e))


@utilities.client.on(events.MessageEdited)
@utilities.client.on(events.NewMessage)
async def my_event_handler(event):
    try:
        message = event.message
        chat_id = event.chat_id
        from_id = event.sender_id
        plugins = utilities.plugins
        mutedUsers = getMutedUser(chat_id, from_id)
        if mutedUsers:
            remMuteUser(chat_id, from_id)
        if message.raw_text:
            matches = re.findall("^[#/!](cancel)$", event.raw_text, re.IGNORECASE)
            if len(matches) > 0 and matches[0] == "cancel":
                if from_id in utilities.user_steps:
                    del utilities.user_steps[from_id]
                    return await message.reply("Canceling successfully !")
        if from_id in utilities.user_steps:
            for plugin in plugins:
                if plugin["name"] == utilities.user_steps[from_id]["name"]:
                    for pattern in plugin["patterns"]:
                        if re.search(
                            pattern, event.raw_text, re.IGNORECASE | re.MULTILINE
                        ):
                            matches = re.findall(
                                pattern, event.raw_text, re.IGNORECASE | re.DOTALL
                            )
                            break
                        else:
                            matches = ["xxxxxxxxxx"]
                    if plugin["sudo"]:
                        if utilities.check_sudo(from_id):
                            return_values = await plugin["run"](
                                message,
                                matches[0],
                                chat_id,
                                utilities.user_steps[from_id]["step"],
                            )
                            for return_value in return_values:
                                if return_value:
                                    try:
                                        await (return_value)
                                    except Exception as e:
                                        print("step :" + str(e))
                        else:
                            return
                    else:
                        return_values = await plugin["run"](
                            message,
                            matches[0],
                            chat_id,
                            utilities.user_steps[from_id]["step"],
                        )
                        if return_values:
                            for return_value in return_values:
                                await (return_value)
                    break
            return
        elif message.raw_text is not None and message.raw_text != "":
            if "flood" not in utilities.config:
                utilities.config["flood"] = True
                utilities.save_config()
            if utilities.config["flood"]:
                pv = utilities.red.get("flood-" + str(message.sender_id)) or 0
                # print("flood-" + str(message.sender_id), pv)
                if pv == 0:
                    utilities.flood[message.sender_id] = True
                utilities.red.set(
                    "flood-" + str(message.sender_id), (int(pv) + 1), ex=1
                )
                if (int(pv) + 1) == 5 and utilities.flood[message.sender_id]:
                    await message.reply("please do not flood...")
                    utilities.prRed(
                        str(message.sender_id) + " : is causing flood please stop..."
                    )
                    utilities.flood[message.sender_id] = False
                    return
                elif (int(pv) + 1) >= 5:
                    return
            for plugin in plugins:
                for pattern in plugin["patterns"]:
                    if re.search(pattern, event.raw_text, re.IGNORECASE | re.MULTILINE):
                        if (
                            "bot" in plugin
                            and utilities.config["isbot"] != plugin["bot"]
                        ):
                            if plugin["bot"]:
                                await event.reply("for bot-api only")
                            else:
                                await event.reply("for bot-cli only")
                            return
                        matches = re.findall(
                            pattern,
                            event.raw_text,
                            re.IGNORECASE | re.MULTILINE | re.DOTALL,
                        )
                        if plugin["sudo"]:
                            if utilities.check_sudo(event.sender_id):
                                return_values = await plugin["run"](
                                    event, matches[0], chat_id, 0, crons=utilities.crons
                                )

                                for return_value in return_values:
                                    if return_value:
                                        try:
                                            await (return_value)
                                        except Exception as e:
                                            print("text main :" + str(e))
                            else:
                                continue

                        else:
                            return_values = await plugin["run"](
                                event, matches[0], chat_id, 0, crons=utilities.crons
                            )
                            if return_values:
                                for return_value in return_values:
                                    await (return_value)
        elif message.media is not None or message.file is not None:
            match = ""
            if message.photo:
                match = "__photo__"
            if message.gif:
                match = "__gif__"
            for plugin in plugins:
                for pattern in plugin["patterns"]:
                    if re.search(pattern, match, re.IGNORECASE | re.MULTILINE):
                        matches = re.findall(pattern, match, re.IGNORECASE)
                        if plugin["sudo"]:
                            if utilities.check_sudo(event.sender_id):
                                return_values = await plugin["run"](
                                    event, matches[0], chat_id, 0
                                )
                                for return_value in return_values:
                                    try:
                                        await (return_value)
                                    except Exception as e:
                                        print("media :" + str(e))
                            else:
                                return
                        else:
                            return_values = await plugin["run"](
                                event, matches[0], chat_id, 0
                            )
                            if return_values:
                                for return_value in return_values:
                                    await (return_value)

    except Exception as e:
        print(str(e))
        await event.reply("Error : " + str(e))


@utilities.client.on(events.InlineQuery)
async def my_event_handler(event):
    builder = event.builder
    try:
        plugins = utilities.plugins
        for plugin in plugins:
            if "inlineQuery" not in plugin:
                continue
            for pattern in plugin["inlineData"]:
                if re.search(pattern, str(event.text), re.IGNORECASE | re.MULTILINE):
                    matches = re.findall(
                        pattern,
                        str(event.text),
                        re.IGNORECASE | re.MULTILINE | re.DOTALL,
                    )
                    if plugin["sudo"]:
                        if utilities.check_sudo(event.sender_id):
                            return_values = await plugin["inlineQuery"](
                                event,
                                matches[0],
                                event.chat_id,
                                0
                                if (event.sender_id not in utilities.user_steps)
                                else utilities.user_steps[event.sender_id]["step"],
                                crons=utilities.crons,
                            )

                            for return_value in return_values:
                                if return_value:
                                    try:
                                        await (return_value)
                                    except Exception as e:
                                        print("inline :" + str(e))
                        else:
                            await event.answer(
                                [
                                    builder.article(
                                        "for sudors only", text="for sudors only"
                                    )
                                ]
                            )

                    else:
                        return_values = await plugin["inlineQuery"](
                            event,
                            matches[0],
                            event.chat_id,
                            0
                            if (event.sender_id not in utilities.user_steps)
                            else utilities.user_steps[event.sender_id]["step"],
                        )
                        if return_values:
                            for return_value in return_values:
                                await (return_value)
    except Exception as e:
        print(str(e))


@utilities.client.on(events.CallbackQuery)
async def handler(event):
    try:

        plugins = utilities.plugins
        for plugin in plugins:
            if "callbackQuery" not in plugin:
                continue
            for pattern in plugin["callbackData"]:
                if re.search(
                    pattern, str(event.data.decode()), re.IGNORECASE | re.MULTILINE
                ):
                    matches = re.findall(
                        pattern,
                        str(event.data.decode()),
                        re.IGNORECASE | re.MULTILINE | re.DOTALL,
                    )
                    if plugin["sudo"]:
                        if utilities.check_sudo(event.sender_id):
                            return_values = await plugin["callbackQuery"](
                                event,
                                matches[0],
                                event.chat_id,
                                0
                                if (event.sender_id not in utilities.user_steps)
                                else utilities.user_steps[event.sender_id]["step"],
                                crons=utilities.crons,
                            )

                            for return_value in return_values:
                                if return_value:
                                    try:
                                        await (return_value)
                                    except Exception as e:
                                        print("callback :" + str(e))
                        else:
                            await event.answer("Sudors only!")

                    else:
                        return_values = await plugin["callbackQuery"](
                            event,
                            matches[0],
                            event.chat_id,
                            0
                            if (event.sender_id not in utilities.user_steps)
                            else utilities.user_steps[event.sender_id]["step"],
                        )
                        if return_values:
                            for return_value in return_values:
                                await (return_value)
    except Exception as e:
        print(str(e))


async def clock():
    while True:
        for _data in utilities.red.lrange("crons", 0, -1):
            data = json.loads(_data)
            if datetime.datetime.fromisoformat(data["time"]) < datetime.datetime.now():
                for plugin in utilities.plugins:
                    if "cron" in plugin and plugin["name"] == data["name"]:
                        return_values = await plugin["cron"](data)
                        for return_value in return_values:
                            if return_value:
                                try:
                                    await (return_value)
                                except Exception as e:
                                    print("clock :" + str(e))
                utilities.red.lrem("crons", 0, _data)
        if len(utilities.crons) != 0:
            for data in utilities.crons:
                if data["time"] < datetime.datetime.now():
                    for plugin in utilities.plugins:
                        if "cron" in plugin and plugin["name"] == data["name"]:
                            return_values = await plugin["cron"](data)
                            for return_value in return_values:
                                if return_value:
                                    try:
                                        await (return_value)
                                    except Exception as e:
                                        print("clock local :" + str(e))
                    utilities.crons.remove(data)
        await asyncio.sleep(1)


if "updateChat" in utilities.config:
    loop.create_task(
        utilities.client.send_message(
            utilities.config["updateChat"], "The bot restart successfully."
        )
    )
    del utilities.config["updateChat"]
    utilities.save_config()
loop.create_task(clock())
loop.create_task(saveBotId())
utilities.prCyan("Started Receveving Messages ...")
utilities.client.run_until_disconnected()
