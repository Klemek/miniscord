[![Total alerts](https://img.shields.io/lgtm/alerts/g/Klemek/miniscord.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Klemek/miniscord/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Klemek/miniscord.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Klemek/miniscord/context:python)
[![Coverage Status](https://coveralls.io/repos/github/Klemek/miniscord/badge.svg?branch=master)](https://coveralls.io/github/Klemek/miniscord?branch=master)

# Miniscord
*A minimalist discord bot API*

```python
from miniscord import Bot
import discord


async def hello(client: discord.client, message: discord.Message, *args: str):
    await message.channel.send("Hello!")


bot = Bot(  
    "test-app",     # name
    "0.1-alpha",    # version
    alias="|"       # respond to '|command' messages
)  
bot.register_command(
    "hello",                    # command text (regex) 
    hello,                      # command function
    "hello: says 'Hello!'",     # short help
    f"```\n"                    # long help
    f"* |help\n"
    f"\tSays 'Hello!'.\n"
    f"```"
)
bot.start()
# this bot respond to "|help", "|info" and "|hello"
```

![](./sample.jpg)

> **⚠ Disclaimer:** I intend to use this project personally, I'm open to ideas but I don't care if it doesn't work for you. Same for the name, feel free to use it, I'm not registering it on PyPI

## Features

*TODO*

## Installation

*TODO*

## Documentation

*TODO*

## Versions

*TODO*

## TODO

* Finish README.md
* Write more tests
* Add comments to code
* Separate branches
* Working CI
* Fix bugs