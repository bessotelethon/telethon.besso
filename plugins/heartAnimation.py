import asyncio
from utilities import utilities
import random


async def run(message, matches, chat_id, step, crons=None):
    key = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "❣️", "💗"]
    if not (message.out):
        message = await message.reply(str("please wait."))
    if matches == "h":
        random.shuffle(key)
        for j in range(0, 10):
            for i in key:
                await message.edit(i)
                await asyncio.sleep(0.3)
        await message.edit("❤️")
    else:
        for j in range(0, 20):
            text = matches + "🧡."
            for i in key:
                text = text.replace(i, "%s")
            textsplit = text.split("%s")
            random.shuffle(key)
            await message.edit(text % tuple(key[: len(textsplit) - 1]))
            await asyncio.sleep(0.3)

    return []


plugin = {
    "name": "",
    "desc": "Heart replacement animation",
    "usage": [
        "/قلبي",
    ],
    "run": run,
    "sudo": True,
    "patterns": ["^[!/#]قلبي (.*)$", "^[!/#](قلبي)$"],
}
