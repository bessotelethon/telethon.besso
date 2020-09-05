import asyncio
import subprocess
import os
import sys
from utilities import utilities


def runGitPull():
    p = subprocess.Popen(
        "git pull", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,
    )
    return iter(p.stdout.readline, b"")


def restartBot():
    p = subprocess.call("bash run.sh", shell=True)


async def run(message, matches, chat_id, step, crons=None):
    upd = ""
    for line in runGitPull():
        upd = upd + line.decode("utf-8")
    if "Already" in upd:
        return [message.reply("❏︙تم عاده تشغيل البوت وتم تحديث السورس")]
    else:
        utilities.config = utilities.get_config()
        utilities.config["updateChat"] = message.chat_id
        utilities.save_config()
        await message.reply(
            "❏︙جاري تحديث السورس رجاء الانتضار منفضلك"
        )
        restartBot()
    return []


plugin = {
    "name": "",
    "desc": "",
    "usage": ["/تحديث + امر تحديث السورس "],
    "run": run,
    "sudo": True,
    "patterns": ["^[!/#]تحديث$"],
}
