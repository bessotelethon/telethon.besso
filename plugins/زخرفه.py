import asyncio
from utilities import utilities
import requests
from lxml import html
import re


async def getZakhrafa(text):
    url = "http://qaz.wtf/u/convert.cgi?text=" + text
    page = requests.get(url)
    tree = html.fromstring(page.content)
    td = tree.xpath("//td/text()")
    res = ""
    for x in td:
        if not (x.find("pseudoalphabet") == 1):
            res = res + re.sub("(\\r|)\\n$", "", x)
    return res


async def run(message, matches, chat_id, step, crons=None):
    response = []
    if not (message.out):
        message = await message.reply(matches)
    response.append(message.edit(await getZakhrafa(matches)))
    return response


plugin = {
    "name": "english zakhrfa",
    "desc": "امر زخرفه 👇",
    "usage": ["/زخرفه + الاسم بلنكلش"],
    "run": run,
    "sudo": True,
    "patterns": ["^[!/#]زخرفه (.+)$"],
}

