import asyncio
from utilities import utilities
from requests_futures.sessions import FuturesSession
import urllib.parse
from urllib.parse import parse_qs
from bs4 import BeautifulSoup
import re

loop = asyncio.get_event_loop()
session = FuturesSession()


def hook_factory(*factory_args, **factory_kwargs):
    def first_response(resp, *args, **kwargs):
        try:

            message = factory_kwargs["message"]
            word = factory_kwargs["word"]
            soup = BeautifulSoup(resp.content)
            ans = soup.findAll(
                lambda tag: tag.name == "div"
                and "class" in tag.attrs
                and len(tag.findChildren("a", recursive=False)) > 0
                and "/search?q=" in tag.a["href"]
            )
            if len(ans) > 0:
                tag = ans[0]

                href = tag.a["href"]
                parms = parse_qs(href)
                keys = list(parms.keys())
                key = keys[0]
                for k in keys:
                    if "q" in keys:
                        key = k
                if word.lower() == parms.get(key)[0].lower():
                    loop.create_task(message.edit("Your sentnece/word is correct."))
                else:
                    loop.create_task(
                        message.edit("Did you mean : \n" + parms.get(key)[0])
                    )
                return None
        except Exception as e:
            print(str(e))
            return None

    return first_response


async def run(msg, matches, chat_id, step, crons=None):
    if not (msg.out):
        message = await msg.reply("❏︙الرجاء الانتظار... ")
    else:
        message = msg
    if msg.is_reply and matches == "تصحيح":
        msg = await msg.get_reply_message()
        if msg.text:

            # file:///search?q=are+you+crazy&spell=1&sa=X&ved=2ahUKEwjr5ubE0_jqAhUQ26QKHcUFDCEQkeECKAB6BAgWECw

            url = "https://www.google.co.in/search?q=" + urllib.parse.quote(msg.text)
            session.get(
                url, hooks={"response": hook_factory(message=message, word=msg.text)},
            )
    return []


plugin = {
    "name": "spell check",
    "desc": "Use google did you mean check",
    "usage": ["❏︙تصحيح + برد ع كلام انكلش"],
    "run": run,
    "sudo": True,
    "patterns": ["^تصحيح$"],
}
