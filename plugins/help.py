import asyncio
from os.path import join, isfile
import os
import re
from utilities import utilities


def getallUsage(id,name=None):
    response_text = ""

    plugin_files = [name]
    if name == None:
        plugin_files = [
            files
            for files in os.listdir(join(utilities.WD, "plugins"))
            if re.search("^(.*)\.py$", files)
        ]
        plugin_files.sort()
    msgs = []
    for plugin_file in plugin_files:
        plugin_file = plugin_file.replace(".py", "")
        if plugin_file == "__init__" :
            continue
        if plugin_file in utilities.config["plugins"]:
            plugin = utilities.load_plugin(plugin_file)
            if ( not utilities.check_sudo(id) and plugin["sudo"]):
                continue
            if "usage" in plugin:
                response_text += (
                    
                    + plugin["name"]
                    
                    + "".join(((i + "\n")) for i in plugin["usage"])
                    + "\n"
                    + ("" if name == None else "Description : " + plugin["desc"])
                )
            else:
                response_text += (
                    "ℹ️ "
                    + plugin["name"]
                    + "'s patterns :\n"
                    + "".join((i + "\n") for i in plugin["patterns"])
                    + "\n"
                )
            if len(response_text) > 3500:
                msgs.append(response_text)
                response_text = ""
        else:
            if name != None:
                msgs.append("no such a plugin")
                return msgs
    if len(response_text) > 0:
        msgs.append(response_text)
    return msgs


async def run(message, matches, chat_id, step, crons=None):
    response = []
    if matches == "الاوامر":
        for i in getallUsage(message.sender_id):
            response.append(message.reply(i, parse_mode=None))
        return response
    else:
        for i in getallUsage(message.sender_id,name=matches):
            response.append(message.reply(i, parse_mode=None))
        return response


plugin = {
    "name": "ء————× 𝑩𝒆𝒔𝒔𝒐 ×————",
    "desc": "Show Help of plugins",
    "usage": ["`الاوامر`", "`الاوامر <plugin_file_name>`"],
    "run": run,
    "sudo": False,
    "patterns": ["^الاوامر (.*)$",
    "^الاوامر$",],
}
