import asyncio
from os.path import join, isfile
import os
import re
from utilities import utilities
response = []
if matches[1:] == "الاوامر":
for i in getallUsage(message.sender_id):
response.append(message.reply(i, parse_mode=None))
return response
else:
for i in getallUsage(message.sender_id,name=matches):
response.append(message.reply(i, parse_mode=None))
return response
plugin = {
"name": "الاوامر ",
"run": run,
"sudo": False,
}