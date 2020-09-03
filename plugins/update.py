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
        return [message.reply("❏︙الديك اخر صدار بلفعل.")]
    else:
        utilities.config = utilities.get_config()
        utilities.config["updateChat"] = message.chat_id
        utilities.save_config()
        await message.reply(
            "❏︙تم تحديث السورس، جاري يعاده تشغيل البوت يرجى الانتظار."
        )
        restartBot()
    return []


plugin = {
    "name": "update",
    "desc": "امر تحديث السورس 👇",
    "usage": ["❏︙/تحديث السورس "],
    "run": run,
    "sudo": True,
    "patterns": ["^[!/#]تحديث السورس $"],
}
